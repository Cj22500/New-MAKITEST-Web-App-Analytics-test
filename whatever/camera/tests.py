from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

from asgiref.sync import async_to_sync
from channels.routing import URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser
from django.test import SimpleTestCase, TransactionTestCase, override_settings
from django.utils import timezone
from homepage.models import CustomUser
from studentside.models import ExamPreparation, StudentExamAttempt
from teacherside.models import Exam

from . import registry
from .routing import websocket_urlpatterns


class WebSocketAuthorizationTests(TransactionTestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            "student", role="student", class_designation="10-A"
        )
        self.other = CustomUser.objects.create_user(
            "other", role="student", class_designation="10-A"
        )
        self.teacher = CustomUser.objects.create_user(
            "teacher", role="teacher", authorized=True
        )
        self.exam = Exam.objects.create(
            title="Science",
            description="Practice",
            deadline=timezone.now() + timedelta(hours=1),
            timelimit=timedelta(minutes=30),
            attempt_limit=2,
            class_designation="10-A",
            access_status=True,
            created_by=self.teacher,
        )
        self.prep = ExamPreparation.objects.create(
            student=self.student, exam=self.exam, session_id="1" * 32
        )
        self.pipeline = Mock()
        self.pipeline.calibration_status.return_value = {
            "stage": -1,
            "calibrated": False,
        }
        self.entry = SimpleNamespace(session=self.pipeline, connection=None)

    async def communicate(self, user, phase="setup", token="", messages=()):
        application = URLRouter(websocket_urlpatterns)
        communicator = WebsocketCommunicator(
            application,
            f"/ws/proctor/{self.prep.session_id}/?phase={phase}&token={token}",
        )
        communicator.scope["user"] = user

        def attach(session_id, phase, connection):
            self.entry.connection = connection
            return self.entry

        with (
            patch("camera.registry.attach", side_effect=attach),
            patch("camera.registry.detach"),
            patch(
                "camera.registry.process",
                return_value={
                    "type": "frame_result",
                    "face_detected": True,
                    "eyes_detected": True,
                    "calibration": {"calibrated": False},
                    "suspicion": {"cheating": True},
                    "debug_face": "private",
                    "weighted_screen_pos": [1, 1],
                },
            ),
        ):
            connected, _ = await communicator.connect()
            responses = []
            if connected:
                responses.append(await communicator.receive_json_from())
                for message in messages:
                    await communicator.send_to(bytes_data=message)
                    responses.append(await communicator.receive_json_from())
                await communicator.disconnect()
            return connected, responses

    def test_unauthenticated_wrong_owner_and_teacher_denied(self):
        for user in (AnonymousUser(), self.other, self.teacher):
            self.assertFalse(async_to_sync(self.communicate)(user)[0])

    def test_setup_owner_receives_health_without_diagnostic_fields(self):
        connected, responses = async_to_sync(self.communicate)(
            self.student, messages=(b"jpeg",)
        )
        self.assertTrue(connected)
        self.assertTrue(responses[1]["face_detected"])
        for key in ("suspicion", "debug_face", "weighted_screen_pos"):
            self.assertNotIn(key, responses[1])

    def test_exam_requires_active_writer_and_refuses_setup_channel(self):
        StudentExamAttempt.objects.create(
            student=self.student,
            exam=self.exam,
            attempt_number=1,
            proctoring_session_id=self.prep.session_id,
            expires_at=timezone.now() + timedelta(minutes=20),
            writer_token="a" * 32,
        )
        self.assertFalse(async_to_sync(self.communicate)(self.student)[0])
        self.assertFalse(
            async_to_sync(self.communicate)(self.student, phase="exam", token="b" * 32)[
                0
            ]
        )
        self.assertTrue(
            async_to_sync(self.communicate)(self.student, phase="exam", token="a" * 32)[
                0
            ]
        )

    @override_settings(ALLOWED_HOSTS=["localhost"])
    def test_foreign_origin_denied(self):
        async def check():
            application = AllowedHostsOriginValidator(URLRouter(websocket_urlpatterns))
            communicator = WebsocketCommunicator(
                application,
                f"/ws/proctor/{self.prep.session_id}/",
                headers=[(b"origin", b"https://untrusted.example")],
            )
            communicator.scope["user"] = self.student
            return await communicator.connect()

        self.assertFalse(async_to_sync(check)()[0])

    def test_lost_registry_will_not_overwrite_existing_exam_artifacts(self):
        attempt = StudentExamAttempt.objects.create(
            student=self.student,
            exam=self.exam,
            attempt_number=1,
            proctoring_session_id=self.prep.session_id,
            monitoring_started=True,
        )
        with self.assertRaises(RuntimeError):
            registry.attach(self.prep.session_id, "exam", "connection")
        attempt.refresh_from_db()
        self.assertTrue(attempt.monitoring_interrupted)

    def test_reconnect_reuses_pipeline_and_obsolete_disconnect_is_ignored(self):
        key = (self.prep.session_id, "exam")
        entry = registry.Entry(Mock(), "old")
        timer = Mock()
        entry.timer = timer
        with patch.dict(registry._entries, {key: entry}, clear=True):
            self.assertIs(registry.attach(self.prep.session_id, "exam", "new"), entry)
            timer.cancel.assert_called_once()
            registry.detach(self.prep.session_id, "exam", "old")
            self.assertIsNone(entry.timer)


class FreshCalibrationTests(SimpleTestCase):
    def test_returning_to_camera_check_discards_partial_point_samples(self):
        session = Mock(is_collecting_samples=True, calibration_samples=[1, 2, 3])
        session.calibration_status.return_value = {"stage": 2, "collecting": False}
        result = registry.pause_calibration(registry.Entry(session, "connection"))
        self.assertFalse(session.is_collecting_samples)
        self.assertEqual(session.calibration_samples, [])
        self.assertEqual(result["stage"], 2)

    def test_only_fresh_face_and_eye_frames_count_toward_sixty_samples(self):
        import numpy as np

        from gaze_session import GazeSession

        session = GazeSession.__new__(GazeSession)
        session._closed = False
        session._tick_fps = Mock()
        session._fps = 0
        session.frame_count = 0
        session.session_id = "freshness-test"
        session.screen_width = 1920
        session.screen_height = 1080
        session.include_debug_frames = False
        session.last_raw_eye_data = {"cached": True}
        session.last_avg_direction = [0, 0, 1]
        session.is_collecting_samples = True
        session.calibration_samples = []
        session.face_processor = Mock()
        session.eye_processor = Mock()
        session.axis_processor = Mock()
        session.axis_processor.process.return_value = (0, 0)
        session.axis_processor.get_estimated_screen_position.return_value = (1, 2)
        session.eye_calibrator = Mock(
            calibration_stage=0, sample_count=60, calibrated=False
        )
        frame = np.zeros((16, 16, 3), dtype=np.uint8)
        session.face_processor.process_frame.return_value = None
        session.eye_processor.process_frame.return_value = None
        for _ in range(61):
            result = session.process_frame(frame)
        self.assertFalse(result["face_detected"])
        self.assertEqual(session.calibration_samples, [])
        self.assertTrue(session.begin_calibration_stage()["collecting"])
        session.face_processor.process_frame.return_value = SimpleNamespace(
            face_landmarks=[1]
        )
        session.eye_processor.process_frame.return_value = SimpleNamespace(
            face_landmarks=[1]
        )
        session.face_processor._draw_landmarks.return_value = (frame, [0, 0, 1], (8, 8))
        session.eye_processor._draw_landmarks.return_value = (frame, {"fresh": True})
        for _ in range(59):
            session.process_frame(frame)
        session.eye_calibrator.calibrate.assert_not_called()
        self.assertEqual(len(session.calibration_samples), 59)
        session.process_frame(frame)
        self.assertEqual(len(session.eye_calibrator.calibrate.call_args.args[0]), 60)
        self.assertFalse(session.is_collecting_samples)

    def test_baseline_cannot_use_a_cached_face(self):
        from gaze_session import GazeSession

        session = GazeSession.__new__(GazeSession)
        session.is_collecting_samples = False
        session.calibration_samples = []
        session.current_face_detected = False
        session.last_avg_direction = [0, 0, 1]
        session.eye_calibrator = Mock(
            calibration_stage=-1, sample_count=60, calibrated=False
        )
        session.axis_processor = Mock()
        self.assertFalse(session.begin_calibration_stage()["ok"])
        session.axis_processor.calibrate.assert_not_called()
