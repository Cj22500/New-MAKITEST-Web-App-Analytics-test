"""Single-process tracking continuity. One serialized pipeline per phase/session."""

import threading
from dataclasses import dataclass, field

from django.conf import settings
from django.db import close_old_connections
from studentside.models import StudentExamAttempt


@dataclass
class Entry:
    session: object
    connection: str
    lock: object = field(default_factory=threading.RLock)
    timer: object = None
    last_result: dict = field(default_factory=dict)


_entries = {}
_lock = threading.RLock()


def attach(session_id, phase, connection):
    with _lock:
        key = (session_id, phase)
        entry = _entries.get(key)
        if entry is None:
            if phase == "exam":
                attempt = StudentExamAttempt.objects.get(
                    proctoring_session_id=session_id
                )
                if attempt.monitoring_started:
                    attempt.monitoring_interrupted = True
                    attempt.save(update_fields=["monitoring_interrupted"])
                    raise RuntimeError(
                        "Tracking state was lost; artifacts must not be overwritten."
                    )
            from gaze_session import GazeSession

            session = GazeSession(
                session_id=session_id,
                output_dir=str(settings.SESSION_OUTPUT_DIR / session_id),
                include_debug_frames=settings.GAZE_DEBUG_FRAMES,
            )
            entry = Entry(session, connection)
            _entries[key] = entry
            if phase == "exam":
                StudentExamAttempt.objects.filter(
                    proctoring_session_id=session_id
                ).update(monitoring_started=True)
        if entry.timer:
            entry.timer.cancel()
            entry.timer = None
        entry.connection = connection
        return entry


def process(entry, frame):
    with entry.lock:
        entry.last_result = entry.session.process_frame(frame)
        return entry.last_result


def calibrate(entry):
    with entry.lock:
        return entry.session.begin_calibration_stage()


def pause_calibration(entry):
    with entry.lock:
        entry.session.is_collecting_samples = False
        entry.session.calibration_samples = []
        return entry.session.calibration_status()


def keystrokes(entry, keys):
    with entry.lock:
        entry.session.note_keystrokes(keys)


def finalize(session_id, phase):
    with _lock:
        entry = _entries.pop((session_id, phase), None)
        if entry:
            if entry.timer:
                entry.timer.cancel()
            with entry.lock:
                return entry.session.finalize()
        return {"type": "session_closed", "session_id": session_id}


def finalize_attempt_sync(session_id):
    return finalize(session_id, "exam")


def _expire(session_id, phase, connection):
    close_old_connections()
    try:
        with _lock:
            entry = _entries.get((session_id, phase))
            if not entry or entry.connection != connection:
                return
            if phase == "exam":
                StudentExamAttempt.objects.filter(
                    proctoring_session_id=session_id, completed_at__isnull=True
                ).update(monitoring_interrupted=True)
            finalize(session_id, phase)
    finally:
        close_old_connections()


def detach(session_id, phase, connection):
    with _lock:
        entry = _entries.get((session_id, phase))
        if entry and entry.connection == connection:
            entry.timer = threading.Timer(60, _expire, (session_id, phase, connection))
            entry.timer.daemon = True
            entry.timer.start()


def diagnostics(session_id):
    with _lock:
        entry = _entries.get((session_id, "exam")) or _entries.get(
            (session_id, "setup")
        )
        return dict(entry.last_result) if entry else {}
