import cv2
import time
import threading
import csv
import collections
import os
from datetime import datetime

class SuspicionScoringProcessor:
    def __init__(self, side_threshold=3.0, down_threshold=5.0, off_screen_threshold=1.5, freq_threshold=6, screen_width=1920, screen_height=1080, output_dir=None):
        # Configuration
        self.side_threshold = side_threshold
        self.down_threshold = down_threshold
        self.off_screen_threshold = off_screen_threshold
        self.freq_threshold = freq_threshold
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Where the CSV and video evidence are written. Defaults to the working
        # directory (desktop use); the server passes a per-session folder so two
        # students recording in the same second cannot overwrite each other.
        self.output_dir = output_dir or "."
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Event-Based CSV Logging Initialization
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.csv_filename = os.path.join(self.output_dir, f"session_log_{self.session_timestamp}.csv")
        self._init_csv()
        
        # State Tracking for CSV
        self.current_state_direction = "Center"
        self.state_start_time = time.time()
        self.current_violation_label = "normal"
        self.current_score = 0
        self.current_video_file = ""
        
        # Off-screen Tracking
        self.face_off_start_time = None
        self.eyes_off_start_time = None
        
        # State Machine Tracking
        self.shift_timestamps = collections.deque()
        
        # Optimized Video Capture
        self.frame_buffer = collections.deque(maxlen=30)  # 3 seconds at 10 fps (pre-roll)
        self.is_recording = False
        self.post_roll = []
        self.pre_roll_copy = []
        self.recording_reason = ""
        self.recording_filename = ""
        
        # Threading
        self.active_threads = []
        self._threads_lock = threading.Lock()

    def _init_csv(self):
        headers = [
            "Gaze direction", 
            "Timestamp start", 
            "Timestamp finish", 
            "Violation label", 
            "Numerical behavioural score", 
            "Video Evidence File"
        ]
        with open(self.csv_filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def _log_state_to_csv(self, direction, start_time, finish_time, label, score, video_file):
        start_str = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        finish_str = datetime.fromtimestamp(finish_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        with open(self.csv_filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([direction, start_str, finish_str, label, score, video_file])

    def _is_off_screen(self, pos):
        """Helper to determine if a given coordinate tuple is outside screen bounds."""
        if pos is None:
            return True
        if not isinstance(pos, (tuple, list)) or len(pos) < 2:
            return True
        x, y = pos
        return x < 0 or x > self.screen_width or y < 0 or y > self.screen_height

    def update(self, frame, raw_gaze_direction, eye_screen_pos: tuple, face_screen_pos: tuple, keystrokes: list):
        current_time = time.time()
        
        # Continuous Pre-roll buffer
        self.frame_buffer.append(frame)
        
        # Data Sanitization
        gaze_direction = "Center" # Default fallback
        if isinstance(raw_gaze_direction, (list, tuple)) and len(raw_gaze_direction) == 2:
            vert, horiz = raw_gaze_direction
            if vert == "Center" and horiz == "Center":
                gaze_direction = "Center"
            else:
                gaze_direction = f"{vert}-{horiz}"
        elif isinstance(raw_gaze_direction, (list, tuple)) and len(raw_gaze_direction) > 0:
            gaze_direction = str(raw_gaze_direction[0])
        elif isinstance(raw_gaze_direction, str):
            gaze_direction = raw_gaze_direction
            
        # Handle state transitions for CSV Logging
        if gaze_direction != self.current_state_direction:
            # Gaze state has finished, log it
            self._log_state_to_csv(
                self.current_state_direction,
                self.state_start_time,
                current_time,
                self.current_violation_label,
                self.current_score,
                self.current_video_file
            )
            
            # Record shifts from Center to anything else for frequency tracking
            if self.current_state_direction == "Center" and gaze_direction != "Center":
                self.shift_timestamps.append(current_time)
                
            # Reset state for new direction
            self.current_state_direction = gaze_direction
            self.state_start_time = current_time
            self.current_violation_label = "normal"
            self.current_score = 0
            self.current_video_file = ""

        # Maintain 60-second rolling window for shifts
        while self.shift_timestamps and current_time - self.shift_timestamps[0] > 60.0:
            self.shift_timestamps.popleft()

        # Track off-screen durations
        if self._is_off_screen(face_screen_pos):
            if self.face_off_start_time is None:
                self.face_off_start_time = current_time
        else:
            self.face_off_start_time = None
            
        if self._is_off_screen(eye_screen_pos):
            if self.eyes_off_start_time is None:
                self.eyes_off_start_time = current_time
        else:
            self.eyes_off_start_time = None

        violation_reason = None

        # Check thresholds only if not currently recording post-roll
        if not self.is_recording:
            
            # 1. Keystrokes (Highest Priority)
            if keystrokes and len(keystrokes) > 0:
                # Take the first forbidden key for the reason, formatting + to _
                key_name = keystrokes[0].replace('+', '_')
                violation_reason = f"forbidden_key_{key_name}"
            
            # 2. Face Boundaries
            elif self.face_off_start_time and (current_time - self.face_off_start_time) > self.off_screen_threshold:
                violation_reason = "face_off_screen"
                
            # 3. Eye Boundaries
            elif self.eyes_off_start_time and (current_time - self.eyes_off_start_time) > self.off_screen_threshold:
                violation_reason = "eyes_off_screen"
                
            # 4. Frequency
            elif len(self.shift_timestamps) > self.freq_threshold:
                violation_reason = "frantic_eye_movement"
                
            # 5. Duration (Lowest Priority)
            else:
                duration = current_time - self.state_start_time
                if "Down" in gaze_direction and duration > self.down_threshold:
                    violation_reason = f"{gaze_direction}_duration"
                elif gaze_direction != "Center" and duration > self.side_threshold:
                    violation_reason = f"{gaze_direction}_duration"
                    
            # Trigger Execution
            if violation_reason:
                self.is_recording = True
                self.recording_reason = violation_reason
                
                # Update CSV logic state
                self.current_violation_label = violation_reason
                self.current_score = 100
                
                # Define video filename early for linkage in CSV
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"{timestamp_str}_violation_{violation_reason}.mp4"
                self.current_video_file = filename
                self.recording_filename = filename
                
                # Force CSV log write immediately so every video has a corresponding row
                self._log_state_to_csv(
                    self.current_state_direction,
                    self.state_start_time,
                    current_time,
                    self.current_violation_label,
                    self.current_score,
                    self.current_video_file
                )
                
                # Reset the tracking state so the next block is fresh
                self.state_start_time = current_time
                self.current_violation_label = "normal"
                self.current_score = 0
                self.current_video_file = ""
                
                # Snapshot the pre-roll (90 frames)
                self.pre_roll_copy = [f.copy() for f in self.frame_buffer]
                
                # Clear shift history to avoid back-to-back frantic triggers
                self.shift_timestamps.clear()
        else:
            # Post-roll Capture
            self.post_roll.append(frame.copy())
            
            if len(self.post_roll) >= 30:  # 3 seconds at 10 fps
                # Trigger Threading for Video Save
                t = threading.Thread(
                    target=self._save_video_async,
                    args=(self.pre_roll_copy, self.post_roll, self.recording_reason, self.recording_filename),
                    daemon=True
                )
                with self._threads_lock:
                    self.active_threads.append(t)
                t.start()
                
                # Reset recording state
                self.is_recording = False
                self.post_roll = []
                self.pre_roll_copy = []
                self.recording_reason = ""
                self.recording_filename = ""
                
                # Reset off-screen and gaze timers so it doesn't instantly re-trigger
                if self._is_off_screen(face_screen_pos):
                    self.face_off_start_time = time.time()
                if self._is_off_screen(eye_screen_pos):
                    self.eyes_off_start_time = time.time()
                self.state_start_time = time.time()
                
        return {
            "is_recording": self.is_recording,
            "current_violation": self.recording_reason if self.is_recording else ""
        }

    def _save_video_async(self, pre_frames, post_frames, reason, filename):
        if not pre_frames and not post_frames:
            return
            
        all_frames = pre_frames + post_frames
        
        # Dynamically extract resolution from the first frame
        first_frame = all_frames[0]
        height, width = first_frame.shape[:2]
        
        # Force dimensions to be even numbers to prevent "green tinge" / alignment issues with H.264 codec
        width = width if width % 2 == 0 else width - 1
        height = height if height % 2 == 0 else height - 1
        
        # Use cv2.VideoWriter with H.264 codec
        # The CSV stores the bare filename for readability; resolve it against the
        # session's output folder here.
        filename = os.path.join(self.output_dir, filename)

        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(filename, fourcc, 10.0, (width, height))
        
        for f in all_frames:
            # Ensure frame matches the exact even dimensions
            if f.shape[1] != width or f.shape[0] != height:
                f = cv2.resize(f, (width, height))
            out.write(f)
            
        out.release()
        
        abs_path = os.path.abspath(filename)
        print(f"[SuspicionScoring] Video evidence saved successfully to: {abs_path}")
        
        # Thread cleanup
        with self._threads_lock:
            current_thread = threading.current_thread()
            if current_thread in self.active_threads:
                self.active_threads.remove(current_thread)

    def cleanup(self):
        # Log the final state
        self._log_state_to_csv(
            self.current_state_direction,
            self.state_start_time,
            time.time(),
            self.current_violation_label,
            self.current_score,
            self.current_video_file
        )
        
        # Graceful Shutdown
        with self._threads_lock:
            threads_copy = list(self.active_threads)
        for t in threads_copy:
            if t.is_alive():
                print(f"[SuspicionScoring] Waiting for video save to finish for thread {t.name}...")
                t.join()
