import json
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from studentside.lifecycle import effective_expiry, verify_writer
from studentside.models import (
    ExamPreparation,
    StudentExamAttempt,
    StudentTrackingThresholds,
)

from . import registry


class ProctorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.entry = None
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        query = parse_qs(self.scope.get("query_string", b"").decode())
        self.phase = query.get("phase", ["setup"])[0]
        self.token = query.get("token", [""])[0]
        user = self.scope.get("user")
        if not user or not user.is_authenticated or user.role != "student":
            await self.close(code=4401)
            return
        if not await sync_to_async(self.authorized)():
            await self.close(code=4403)
            return
        await self.accept()
        try:
            self.entry = await sync_to_async(registry.attach, thread_sensitive=False)(
                self.session_id, self.phase, self.channel_name
            )
            await self.send_json(
                {
                    "type": "ready",
                    "calibration": self.entry.session.calibration_status(),
                }
            )
        except Exception:
            await sync_to_async(self.mark_interrupted)()
            await self.send_json(
                {
                    "type": "error",
                    "message": "Monitoring could not start. Your answers can still be saved.",
                }
            )
            await self.close(code=4500)

    def authorized(self):
        user = self.scope["user"]
        if self.phase == "setup":
            return (
                ExamPreparation.objects.filter(
                    session_id=self.session_id,
                    student=user,
                    finalized_at__isnull=True,
                    exam__deadline__gt=timezone.now(),
                    exam__access_status=True,
                    exam__class_designation=user.class_designation,
                ).exists()
                and not StudentExamAttempt.objects.filter(
                    proctoring_session_id=self.session_id
                ).exists()
            )
        if self.phase == "exam":
            attempt = (
                StudentExamAttempt.objects.filter(
                    proctoring_session_id=self.session_id, student=user
                )
                .select_related("exam")
                .first()
            )
            return bool(
                attempt
                and not attempt.completed_at
                and timezone.now() < effective_expiry(attempt)
                and verify_writer(attempt, self.token)
            )
        return False

    def mark_interrupted(self):
        if self.phase == "exam":
            StudentExamAttempt.objects.filter(
                proctoring_session_id=self.session_id
            ).update(monitoring_interrupted=True)

    async def receive(self, text_data=None, bytes_data=None):
        if self.entry is None or self.entry.connection != self.channel_name:
            await self.close(code=4409)
            return
        if self.phase == "exam" and not await sync_to_async(self.authorized)():
            await self.close(code=4403)
            return
        try:
            if bytes_data is not None:
                if len(bytes_data) > 2_000_000:
                    return
                result = await sync_to_async(registry.process, thread_sensitive=False)(
                    self.entry, bytes_data
                )
                if self.phase == "setup" and result.get("calibration", {}).get(
                    "calibrated"
                ):
                    await sync_to_async(self.save_calibration)()
                safe = {
                    k: result[k]
                    for k in ("type", "face_detected", "eyes_detected", "calibration")
                    if k in result
                }
                await self.send_json(safe)
            else:
                data = json.loads(text_data or "{}")
                command = data.get("type")
                if command == "calibrate_next" and self.phase == "setup":
                    result = await sync_to_async(
                        registry.calibrate, thread_sensitive=False
                    )(self.entry)
                    await self.send_json({"type": "calibration", **result})
                elif command == "calibrate_pause" and self.phase == "setup":
                    result = await sync_to_async(
                        registry.pause_calibration, thread_sensitive=False
                    )(self.entry)
                    await self.send_json({"type": "calibration", **result})
                elif command == "camera_selected" and self.phase == "setup":
                    await sync_to_async(self.select_camera)(
                        str(data.get("camera_id", ""))[:256]
                    )
                elif command == "keystrokes" and self.phase == "exam":
                    keys = data.get("keys")
                    if (
                        isinstance(keys, list)
                        and len(keys) <= 12
                        and all(isinstance(k, str) and len(k) < 64 for k in keys)
                    ):
                        await sync_to_async(
                            registry.keystrokes, thread_sensitive=False
                        )(self.entry, keys)
                elif command == "ping":
                    await self.send_json({"type": "pong"})
                elif command == "finalize_session":
                    result = await sync_to_async(
                        registry.finalize, thread_sensitive=False
                    )(self.session_id, self.phase)
                    if self.phase == "setup":
                        await sync_to_async(self.finalize_setup)()
                    await self.send_json(result)
                    await self.close(code=1000)
        except (ValueError, TypeError, AttributeError):
            await self.send_json(
                {
                    "type": "error",
                    "message": "The setup command could not be read. Try again.",
                }
            )
        except Exception:
            await self.send_json(
                {
                    "type": "error",
                    "message": "Camera processing was interrupted. Check your camera and try again.",
                }
            )

    def select_camera(self, camera_id):
        ExamPreparation.objects.filter(
            session_id=self.session_id, student=self.scope["user"]
        ).update(camera_id=camera_id)

    def save_calibration(self):
        prep = ExamPreparation.objects.get(
            session_id=self.session_id, student=self.scope["user"]
        )
        if prep.calibrated_at:
            return
        thresholds = self.entry.session.eye_calibrator.calibrated_thresholds
        fields = {
            "calibration_up": "up",
            "calibration_down": "down",
            "calibration_center": "center",
            "calibration_left": "left",
            "calibration_right": "right",
            "calibration_v_center": "v_center",
            "iris_boxheight_center": "iris_boxheight_center",
            "iris_boxheight_up": "iris_boxheight_up",
            "iris_boxheight_down": "iris_boxheight_down",
        }
        StudentTrackingThresholds.objects.update_or_create(
            student=self.scope["user"],
            defaults={key: thresholds.get(value, 0.0) for key, value in fields.items()},
        )
        prep.calibrated_at = timezone.now()
        prep.save(update_fields=["calibrated_at"])

    def finalize_setup(self):
        ExamPreparation.objects.filter(
            session_id=self.session_id, calibrated_at__isnull=False
        ).update(finalized_at=timezone.now())

    async def disconnect(self, code):
        if self.entry:
            registry.detach(self.session_id, self.phase, self.channel_name)

    async def send_json(self, data):
        await self.send(text_data=json.dumps(data))
