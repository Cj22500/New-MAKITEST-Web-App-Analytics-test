"""Run explicitly with MAKITEST_BROWSER_TESTS=1; tracking is simulated here."""

import asyncio
import json
import os
import unittest
from datetime import timedelta
from pathlib import Path

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from homepage.models import CustomUser
from teacherside.models import Exam, Question

from studentside.models import ExamPreparation, StudentAnswer, StudentExamAttempt


@unittest.skipUnless(
    os.environ.get("MAKITEST_BROWSER_TESTS") == "1", "Browser suite is opt-in"
)
class BrowserFlowTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if os.name == "nt":
            # Daphne uses a Selector loop on Windows; browser subprocesses need Proactor.
            cls.previous_loop_policy = asyncio.get_event_loop_policy()
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        cls.previous_async_setting = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
        # Playwright's synchronous greenlet retains a running loop in this test thread.
        # This applies only to the isolated test database, never application startup.
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        from playwright.sync_api import sync_playwright

        cls.playwright = sync_playwright().start()
        options = {
            "headless": True,
            "args": [
                "--use-fake-device-for-media-stream",
                "--use-fake-ui-for-media-stream",
            ],
        }
        if os.environ.get("MAKITEST_BROWSER_EXECUTABLE"):
            options["executable_path"] = os.environ["MAKITEST_BROWSER_EXECUTABLE"]
        cls.browser = cls.playwright.chromium.launch(**options)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        if os.name == "nt":
            asyncio.set_event_loop_policy(cls.previous_loop_policy)
        if cls.previous_async_setting is None:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE", None)
        else:
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = cls.previous_async_setting
        super().tearDownClass()

    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            "qa-teacher", password="Temporary-QA-2026", role="teacher", authorized=True
        )
        self.student = CustomUser.objects.create_user(
            "qa-student",
            password="Temporary-QA-2026",
            role="student",
            class_designation="10-A",
        )
        self.exam = Exam.objects.create(
            title="Science practice",
            description="Choose your answers",
            deadline=timezone.now() + timedelta(hours=1),
            timelimit=timedelta(minutes=30),
            attempt_limit=2,
            class_designation="10-A",
            access_status=True,
            created_by=self.teacher,
        )
        self.question = Question.objects.create(
            exam=self.exam,
            question_text="Water freezes at 0 degrees Celsius.",
            question_type="MCQ",
            choices=[{"text": "True"}, {"text": "False"}],
            correct_answer_text="True",
        )
        self.text_question = Question.objects.create(
            exam=self.exam,
            question_text="Name the liquid in oceans.",
            question_type="FIB",
            correct_answer_text="Water",
        )
        self.context = self.browser.new_context(viewport={"width": 1366, "height": 900})
        self.context.add_init_script("""navigator.mediaDevices.getUserMedia = async () => {
          const canvas=document.createElement('canvas');canvas.width=640;canvas.height=480;
          const ctx=canvas.getContext('2d');setInterval(()=>{ctx.fillStyle='#cbd5e1';ctx.fillRect(0,0,640,480);},100);
          return canvas.captureStream(10);
        }; navigator.mediaDevices.enumerateDevices = async () => [{kind:'videoinput',deviceId:'synthetic',label:'Synthetic test camera'}];""")
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.tracking = {
            "stage": -1,
            "collecting": False,
            "calibrated": False,
            "commands": 0,
        }
        self.socket = None
        self.page.route_web_socket("**/ws/proctor/**", self.route_tracking)
        self.login("qa-student")

    def tearDown(self):
        self.assertEqual(self.errors, [])
        self.context.close()

    def login(self, username):
        self.page.goto(self.live_server_url + "/login/")
        self.page.locator("[name=username]").fill(username)
        self.page.locator("[name=password]").fill("Temporary-QA-2026")
        self.page.locator("button.primary").click()
        self.page.wait_for_url(
            "**/studentside/" if username == "qa-student" else "**/teacherside/"
        )

    def calibration(self):
        return {
            "ok": True,
            "stage": self.tracking["stage"],
            "collecting": self.tracking["collecting"],
            "collected": 0,
            "needed": 60,
            "calibrated": self.tracking["calibrated"],
        }

    def route_tracking(self, socket):
        self.socket = socket
        socket.send(json.dumps({"type": "ready", "calibration": self.calibration()}))
        socket.send(
            json.dumps(
                {
                    "type": "frame_result",
                    "face_detected": True,
                    "eyes_detected": True,
                    "calibration": self.calibration(),
                }
            )
        )

        def message(data):
            if isinstance(data, bytes):
                socket.send(
                    json.dumps(
                        {
                            "type": "frame_result",
                            "face_detected": True,
                            "eyes_detected": True,
                            "calibration": self.calibration(),
                        }
                    )
                )
                return
            command = json.loads(data)["type"]
            if command == "calibrate_next":
                self.tracking["commands"] += 1
                if self.tracking["stage"] == -1:
                    self.tracking["stage"] = 0
                else:
                    self.tracking["collecting"] = True
                socket.send(json.dumps({"type": "calibration", **self.calibration()}))
            elif command == "finalize_session":
                socket.send(json.dumps({"type": "session_closed"}))

        socket.on_message(message)

    def complete_point(self):
        self.tracking["collecting"] = False
        self.tracking["stage"] += 1
        self.tracking["calibrated"] = self.tracking["stage"] == 5
        self.socket.send(
            json.dumps(
                {
                    "type": "frame_result",
                    "face_detected": True,
                    "eyes_detected": True,
                    "calibration": self.calibration(),
                }
            )
        )

    def open_attempt(self, seconds=1800):
        prep = ExamPreparation.objects.create(
            student=self.student,
            exam=self.exam,
            session_id="1" * 32,
            calibrated_at=timezone.now(),
            finalized_at=timezone.now(),
        )
        attempt = StudentExamAttempt.objects.create(
            student=self.student,
            exam=self.exam,
            attempt_number=1,
            started_at=timezone.now(),
            expires_at=timezone.now() + timedelta(seconds=seconds),
            proctoring_session_id=prep.session_id,
        )
        self.page.goto(
            self.live_server_url + f"/studentside/exam_details/?exam_id={self.exam.pk}"
        )
        self.page.wait_for_function(
            "document.querySelector('#review-submit') && !document.querySelector('#review-submit').disabled && !document.querySelector('[name^=question_]').disabled"
        )
        return attempt

    def test_autosave_clear_refresh_takeover_and_partial_submit(self):
        attempt = self.open_attempt()
        radio = self.page.locator(f'[name=question_{self.question.pk}][value="0"]')
        radio.check()
        self.page.locator(f"[name=question_{self.text_question.pk}]").fill("Water")
        self.page.wait_for_function(
            "document.querySelector('#save-status').textContent==='Saved'"
        )
        self.assertEqual(
            StudentAnswer.objects.get(
                student_exam_attempt=attempt, question=self.question
            ).answer_text,
            "0",
        )
        self.page.reload()
        self.page.wait_for_function(
            "!document.querySelector('[name^=question_]').disabled"
        )
        self.assertTrue(radio.is_checked())
        self.assertEqual(
            self.page.locator(f"[name=question_{self.text_question.pk}]").input_value(),
            "Water",
        )
        self.page.locator(f'[data-clear="{self.text_question.pk}"]').click()
        self.page.wait_for_function(
            "document.querySelector('#save-status').textContent==='Saved'"
        )
        self.assertEqual(
            StudentAnswer.objects.get(
                student_exam_attempt=attempt, question=self.text_question
            ).answer_text,
            "",
        )
        second = self.context.new_page()
        second.route_web_socket("**/ws/proctor/**", self.route_tracking)
        second.goto(self.page.url)
        second.locator("#writer-conflict").wait_for(state="visible")
        self.assertTrue(second.locator("[name^=question_]").first.is_disabled())
        second.locator("#takeover").click()
        second.wait_for_function(
            "!document.querySelector('[name^=question_]').disabled"
        )
        self.assertTrue(
            second.locator(
                f'[name=question_{self.question.pk}][value="0"]'
            ).is_checked()
        )
        second.locator("#review-submit").click()
        self.assertIn("1 unanswered", second.locator("#review-summary").inner_text())
        second.locator("#confirm-submit").click()
        second.wait_for_url("**/exam_results/**")
        self.assertIn("50.0%", second.locator(".score").inner_text())
        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.completed_at)
        second.close()

    def test_timeout_submits_without_confirmation(self):
        attempt = self.open_attempt(seconds=4)
        self.page.wait_for_url("**/exam_results/**", timeout=20000)
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 0)

    def test_space_calibration_only_advances_completed_points(self):
        self.page.goto(
            self.live_server_url + f"/studentside/exam_details/?exam_id={self.exam.pk}"
        )
        self.page.locator("button.primary").click()
        self.page.wait_for_url("**/camera/")
        self.page.locator("#enable-camera").click()
        self.page.wait_for_function("!document.querySelector('#begin').disabled")
        self.page.locator("#begin").click()
        self.page.keyboard.press("Space")
        self.page.wait_for_function(
            "document.querySelector('#cal-status').textContent.includes('captured')"
        )
        for index in range(5):
            if index:
                self.page.keyboard.press("Space")
                self.page.wait_for_function(
                    "document.querySelector('#cal-status').textContent.includes('captured')"
                )
            commands = self.tracking["commands"]
            self.page.keyboard.press("Space")
            self.assertEqual(self.tracking["commands"], commands)
            self.complete_point()
            self.page.wait_for_function(
                "document.querySelector('#cal-status').textContent.includes('complete')"
            )
            self.page.evaluate(
                "document.dispatchEvent(new KeyboardEvent('keydown',{code:'Space',repeat:true,bubbles:true}))"
            )
            self.assertEqual(self.tracking["commands"], commands)
        self.page.keyboard.press("Space")
        self.page.locator("#ready").wait_for(state="visible")
        self.assertFalse(StudentExamAttempt.objects.exists())
        self.assertEqual(self.tracking["commands"], 6)

    def test_responsive_screens_and_screenshots(self):
        output = Path(__file__).resolve().parents[2] / ".validation" / "screenshots"
        output.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(output / "student-desktop.png"), full_page=True)
        self.open_attempt()
        self.page.screenshot(path=str(output / "exam-desktop.png"), full_page=True)
        self.context.clear_cookies()
        self.login("qa-teacher")
        self.page.goto(self.live_server_url + "/teacherside/exams/")
        self.page.screenshot(path=str(output / "teacher-desktop.png"), full_page=True)
        for path in ["/teacherside/exams/", "/teacherside/students/"]:
            self.page.set_viewport_size({"width": 390, "height": 844})
            self.page.goto(self.live_server_url + path)
            self.assertTrue(
                self.page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            )
        self.page.screenshot(path=str(output / "teacher-mobile.png"), full_page=True)
