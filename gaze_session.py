"""
gaze_session.py — server-side, per-connection wrapper around the tracking pipeline.

This is the headless equivalent of main_trackerprocess.py. Where that script owns a
webcam, a `while True` loop and three cv2 windows, this class owns nothing global:
one GazeSession == one student == one WebSocket connection. Frames are pushed in
from the browser instead of pulled from cv2.VideoCapture, and every result comes
back as a plain dict ready for json.dumps().

Nothing in here draws to a window or reads the keyboard. `{` / `}` are replaced by
begin_calibration_stage() / finalize(); the keyboard hook is replaced by
note_keystrokes(), fed from the browser.

Typical use from a Channels consumer:

    session = GazeSession(session_id="abc123")
    result  = session.process_frame(jpeg_bytes)   # -> dict, send as JSON
    session.begin_calibration_stage()             # on a "calibrate_next" message
    session.note_keystrokes(["alt+tab"])          # on a "keystrokes" message
    session.finalize()                            # on disconnect
"""

from __future__ import annotations

import base64
import inspect
import os
import time
from datetime import datetime

import cv2
import numpy as np

import eye_calibrationprocessor as ecp
import eye_screenposprocessor as esp
import eye_trackprocessor as etp
import face_axisprocessor as fap
import face_trackprocessor as ftp
import gaze_directionprocessor as gdp
import heatmap_processor as hp
import suspicion_scoringprocessor as ssp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# The processors default to a bare "face_landmarker.task", which only resolves when
# the process was launched from this folder. Django runs from the project root, so
# the path has to be absolute.
MODEL_PATH = os.path.join(BASE_DIR, "face_landmarker.task")

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# What the student should be doing at each calibration stage. Stage -1 is the head
# pose baseline (no eye samples collected); 0-4 each collect `sample_count` frames.
STAGE_PROMPTS = {
    -1: "Sit straight and look at the camera, then start calibration.",
    0: "Look at the centre of the screen.",
    1: "Look at the top of the screen.",
    2: "Look at the bottom of the screen.",
    3: "Look at the left edge of the screen.",
    4: "Look at the right edge of the screen.",
    5: "Calibration complete.",
}

CALIBRATED_STAGE = 5


class GazeSession:
    """One student's tracking pipeline. Not thread-safe: call from one thread at a time.

    The Channels consumer guarantees this by only ever having one frame in flight
    per connection.
    """

    def __init__(
        self,
        session_id: str | None = None,
        output_dir: str | None = None,
        screen_width: int = SCREEN_WIDTH,
        screen_height: int = SCREEN_HEIGHT,
        include_debug_frames: bool = False,
    ):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.include_debug_frames = include_debug_frames

        # Every artefact for this session lands in its own folder, so two students
        # recording at the same second cannot overwrite each other.
        self.output_dir = output_dir or os.path.join(BASE_DIR, "sessions", self.session_id)
        os.makedirs(self.output_dir, exist_ok=True)

        # Per-session pipeline. These were module-level globals in
        # main_trackerprocess.py; holding them here is what makes concurrent
        # students possible.
        self.face_processor = ftp.FaceLandmarkerProcessor(model_path=MODEL_PATH)
        self.eye_processor = etp.EyeLandmarkerProcessor(model_path=MODEL_PATH)
        self.axis_processor = fap.FaceAxisProcessor()
        self.eye_calibrator = ecp.EyeCalibrationProcessor(session_folder=self.output_dir)
        
        # Restore face axis offsets if calibration was loaded
        if self.eye_calibrator.calibrated:
            face_yaw = self.eye_calibrator.calibrated_thresholds.get('face_offset_yaw', 0.0)
            face_pitch = self.eye_calibrator.calibrated_thresholds.get('face_offset_pitch', 0.0)
            self.axis_processor.calibration_offset_yaw = face_yaw
            self.axis_processor.calibration_offset_pitch = face_pitch
            print(f"✓ Restored face axis offsets: yaw={face_yaw:.2f}, pitch={face_pitch:.2f}")
        
        self.gaze_processor = gdp.GazeDirectionProcessor()
        blend = inspect.signature(self.gaze_processor.weighted_screen_position).parameters
        self.blend_weights = [blend['weight_face'].default, blend['weight_eye'].default]
        self.screen_pos_processor = esp.EyeScreenPosProcessor(screen_width, screen_height)
        self.scoring_processor = ssp.SuspicionScoringProcessor(
            screen_width=screen_width,
            screen_height=screen_height,
            output_dir=self.output_dir,
        )
        self.heatmap_processor = hp.HeatmapProcessor(screen_width, screen_height)

        # Rolling state carried between frames.
        self.last_avg_direction = None
        self.last_raw_eye_data = None
        self.current_gaze = "Center"

        self.is_collecting_samples = False
        self.calibration_samples: list = []

        self.pending_keystrokes: list[str] = []

        self.frame_count = 0
        self.started_at = time.time()
        self._last_frame_at = None
        self._fps = 0.0
        self._closed = False

    # ------------------------------------------------------------------ frames

    def process_frame(self, frame) -> dict:
        """Run one frame through the pipeline.

        `frame` is either raw JPEG bytes (what the browser sends) or an already
        decoded BGR ndarray. Never raises on a bad frame — a broken frame just
        produces a result with face_detected False, because dropping one frame of
        a live exam must not kill the connection.
        """
        if self._closed:
            return self._error("session is closed")

        frame = self._decode(frame)
        if frame is None:
            return self._error("could not decode frame")

        self._tick_fps()
        self.frame_count += 1

        face_screenpos = None
        eye_screenpos = None
        directionsval = None
        yaw = pitch = None
        face_debug = None
        eye_debug = None

        fresh_eye_data = None
        fresh_face_direction = None

        # ---------------------------------------------------------- face pass
        # _draw_landmarks does the geometry as well as the drawing, so it is still
        # the call that produces avg_direction and the face centre. It is handed a
        # copy and its annotated output is only kept when debug frames are on.
        face_results = self.face_processor.process_frame(frame)
        if face_results is not None and getattr(face_results, "face_landmarks", None):
            try:
                annotated, avg_direction, face_center = self.face_processor._draw_landmarks(
                    frame.copy(), face_results
                )
                if avg_direction is not None and face_center is not None:
                    self.last_avg_direction = avg_direction
                    fresh_face_direction = avg_direction
                    # Deliberately the *source* frame's dimensions: _draw_landmarks
                    # returns a 600x300 resize, but face_center is in original
                    # coordinates, so mixing the two would skew the anchor offset.
                    self.axis_processor.update_anchor_from_face_position(
                        face_center[0], face_center[1], frame.shape[1], frame.shape[0]
                    )
                    yaw, pitch = self.axis_processor.process(avg_direction)
                    face_screenpos = self.axis_processor.get_estimated_screen_position()
                if self.include_debug_frames:
                    face_debug = self._encode(annotated)
            except Exception:
                # A malformed landmark set should cost one frame, not the session.
                pass
        else:
            # No face detected - still send the original frame so frontend keeps updating
            if self.include_debug_frames:
                face_debug = self._encode(frame)

        # ----------------------------------------------------------- eye pass
        eye_results = self.eye_processor.process_frame(frame)
        if eye_results is not None and getattr(eye_results, "face_landmarks", None):
            try:
                eye_frame, raw_eye_data = self.eye_processor._draw_landmarks(
                    frame.copy(), eye_results
                )
                if raw_eye_data is not None:
                    self.last_raw_eye_data = raw_eye_data
                    fresh_eye_data = raw_eye_data
                if self.include_debug_frames:
                    eye_debug = self._encode(eye_frame)
            except Exception:
                pass

        face_detected = fresh_face_direction is not None
        self.current_face_detected = face_detected
        self.current_eyes_detected = fresh_eye_data is not None

        # ------------------------------------------------- calibration sampling
        if self.is_collecting_samples:
            if fresh_eye_data is not None and face_detected:
                self.calibration_samples.append(fresh_eye_data)
            if len(self.calibration_samples) >= self.eye_calibrator.sample_count:
                self.eye_calibrator.calibrate(self.calibration_samples)
                # Pass face axis offsets when completing calibration
                self.eye_calibrator.next_stage(
                    face_offset_yaw=self.axis_processor.calibration_offset_yaw,
                    face_offset_pitch=self.axis_processor.calibration_offset_pitch
                )
                self.calibration_samples = []
                self.is_collecting_samples = False

        # --------------------------------------------- gaze + scoring (post-cal)
        if self.eye_calibrator.calibration_stage == CALIBRATED_STAGE:
            result = self.screen_pos_processor.process(
                self.eye_calibrator.calibrated_thresholds, self.last_raw_eye_data
            )
            if result is not None:
                eye_screenpos, directionsval = result

            weighted, directionsval = self.gaze_processor.weighted_screen_position(face_screenpos, eye_screenpos)
            if weighted is not None:
                self.heatmap_processor.add_point(weighted)

            if directionsval is not None:
                self.current_gaze = directionsval

            keystrokes = self._drain_keystrokes()
            suspicion = self.scoring_processor.update(
                frame, self.current_gaze, eye_screenpos, face_screenpos, keystrokes
            )
        else:
            weighted = None
            suspicion = {"is_recording": False, "current_violation": ""}

        return {
            "type": "frame_result",
            "session_id": self.session_id,
            "frame": self.frame_count,
            "fps": round(self._fps, 1),
            "face_detected": bool(face_detected),
            "eyes_detected": fresh_eye_data is not None,
            "yaw": self._num(yaw),
            "pitch": self._num(pitch),
            "face_screen_pos": self._pos(face_screenpos),
            "eye_screen_pos": self._pos(eye_screenpos),
            "weighted_screen_pos": self._pos(weighted),
            "blend_weights": getattr(self, 'blend_weights', [0.4, 0.6]),
            "screen_size": [self.screen_width, self.screen_height],
            "gaze_direction": list(directionsval) if directionsval else None,
            "calibration": self.calibration_status(),
            "suspicion": suspicion,
            "debug_face": face_debug,
            "debug_eye": eye_debug,
        }

    # ------------------------------------------------------------- calibration

    def begin_calibration_stage(self) -> dict:
        """Advance calibration — the WebSocket equivalent of pressing `{`.

        The first call zeroes the head pose; each later call starts collecting
        `sample_count` eye samples for the current stage, which then complete on
        their own as frames arrive.
        """
        cal = self.eye_calibrator

        if self.is_collecting_samples:
            return self.calibration_status(message="Still collecting samples for this stage.")

        if cal.calibration_stage >= CALIBRATED_STAGE:
            return self.calibration_status(message="Calibration is already complete.")

        if cal.calibration_stage == -1:
            # Needs a face on screen: the head pose baseline is taken from the
            # most recent frame, so this cannot run before tracking has started.
            if not getattr(self, "current_face_detected", False):
                return self.calibration_status(
                    ok=False, message="No face detected yet — cannot set the head pose baseline."
                )
            self.axis_processor.calibrate(self.last_avg_direction)
            cal.next_stage()
            return self.calibration_status(message=STAGE_PROMPTS.get(cal.calibration_stage, ""))

        if not getattr(self, "current_eyes_detected", False):
            return self.calibration_status(ok=False, message="No eyes detected yet — hold still and retry.")

        self.calibration_samples = []
        self.is_collecting_samples = True
        return self.calibration_status(message=f"Collecting samples — {STAGE_PROMPTS.get(cal.calibration_stage, '')}")

    def calibration_status(self, ok: bool = True, message: str = "") -> dict:
        cal = self.eye_calibrator
        return {
            "ok": ok,
            "stage": cal.calibration_stage,
            "prompt": STAGE_PROMPTS.get(cal.calibration_stage, ""),
            "collecting": self.is_collecting_samples,
            "collected": len(self.calibration_samples),
            "needed": cal.sample_count,
            "calibrated": bool(cal.calibrated),
            "message": message,
        }

    # ---------------------------------------------------------------- keyboard

    def note_keystrokes(self, keys) -> None:
        """Record suspicious keys reported by the browser.

        Replaces KeypressTrackProcessor, whose global hook would read the server's
        keyboard rather than the student's. Buffered here and drained on the next
        frame so the scorer sees them exactly as it did before.
        """
        if not keys:
            return
        if isinstance(keys, str):
            keys = [keys]
        self.pending_keystrokes.extend(str(k) for k in keys)

    def _drain_keystrokes(self) -> list[str]:
        keys, self.pending_keystrokes = self.pending_keystrokes, []
        return keys

    # ---------------------------------------------------------------- teardown

    def finalize(self) -> dict:
        """Close the session and write out the artefacts. Safe to call twice."""
        if self._closed:
            return {"type": "session_closed", "session_id": self.session_id, "already_closed": True}
        self._closed = True

        for processor, attribute in ((self.face_processor, 'face_landmarker'), (self.eye_processor, 'eye_landmarker')):
            try:
                getattr(processor, attribute).close()
            except Exception:
                pass

        try:
            self.scoring_processor.cleanup()
        except Exception:
            pass

        heatmap_path = None
        try:
            heatmap_path = self.heatmap_processor.generate_heatmap(
                os.path.join(self.output_dir, f"heatmap_{self.session_id}.png")
            )
        except Exception:
            pass

        return {
            "type": "session_closed",
            "session_id": self.session_id,
            "frames": self.frame_count,
            "duration_s": round(time.time() - self.started_at, 1),
            "output_dir": self.output_dir,
            "csv": getattr(self.scoring_processor, "csv_filename", None),
            "heatmap": heatmap_path,
        }

    # ----------------------------------------------------------------- helpers

    @staticmethod
    def _decode(frame):
        if frame is None:
            return None
        if isinstance(frame, np.ndarray):
            return frame
        try:
            buf = np.frombuffer(frame, dtype=np.uint8)
            return cv2.imdecode(buf, cv2.IMREAD_COLOR)
        except Exception:
            return None

    @staticmethod
    def _encode(frame):
        if frame is None:
            return None
        ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if not ok:
            return None
        return "data:image/jpeg;base64," + base64.b64encode(buf).decode("ascii")

    @staticmethod
    def _pos(pos):
        """Screen positions carry numpy floats, which json.dumps refuses."""
        if pos is None:
            return None
        return [int(pos[0]), int(pos[1])]

    @staticmethod
    def _num(value):
        if value is None:
            return None
        return round(float(value), 2)

    def _tick_fps(self):
        now = time.time()
        if self._last_frame_at is not None:
            dt = now - self._last_frame_at
            if dt > 0:
                self._fps = 0.9 * self._fps + 0.1 * (1.0 / dt) if self._fps else 1.0 / dt
        self._last_frame_at = now

    def _error(self, message: str) -> dict:
        self.current_face_detected = False
        self.current_eyes_detected = False
        return {
            "type": "frame_result",
            "session_id": self.session_id,
            "error": message,
            "face_detected": False,
            "calibration": self.calibration_status(),
            "suspicion": {"is_recording": False, "current_violation": ""},
        }
