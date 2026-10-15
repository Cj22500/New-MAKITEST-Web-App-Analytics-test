import json
from datetime import timedelta

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from homepage.models import CustomUser
from teacherside.models import Exam, Question

from .lifecycle import finish_attempt, save_answers
from .models import ExamPreparation, StudentExamAttempt


class ExamFlowTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            "student", role="student", class_designation="10-A"
        )
        self.teacher = CustomUser.objects.create_user(
            "teacher", role="teacher", authorized=True
        )
        self.other = CustomUser.objects.create_user(
            "other", role="student", class_designation="10-B"
        )
        self.exam = Exam.objects.create(
            title="Science",
            description="Practice",
            deadline=timezone.now() + timedelta(hours=1),
            timelimit=timedelta(minutes=30),
            attempt_limit=2,
            class_designation="10-A",
            access_status=True,
            access_code="CLASS",
            created_by=self.teacher,
        )
        self.question = Question.objects.create(
            exam=self.exam,
            question_text="Choose four",
            question_type="MCQ",
            choices=[{"text": "3"}, {"text": "4"}],
            correct_answer_text="4",
        )
        self.client.force_login(self.student)

    def attempt(self, **kwargs):
        values = dict(
            student=self.student,
            exam=self.exam,
            attempt_number=1,
            started_at=timezone.now(),
            expires_at=timezone.now() + timedelta(minutes=30),
            writer_token="a" * 32,
            proctoring_session_id="1" * 32,
        )
        values.update(kwargs)
        return StudentExamAttempt.objects.create(**values)

    def post_json(self, name, attempt, data):
        return self.client.post(
            reverse(name, args=[attempt.pk]),
            json.dumps(data),
            content_type="application/json",
        )

    def test_code_required_before_setup_and_no_attempt_consumed(self):
        response = self.client.post(
            reverse("exam_details"), {"exam_id": self.exam.pk, "access_code": "wrong"}
        )
        self.assertContains(response, "That code does not match")
        self.assertFalse(ExamPreparation.objects.exists())
        response = self.client.post(
            reverse("exam_details"), {"exam_id": self.exam.pk, "access_code": "CLASS"}
        )
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(ExamPreparation.objects.count(), 1)
        self.assertFalse(StudentExamAttempt.objects.exists())

    def test_start_requires_server_verified_calibration(self):
        self.client.post(
            reverse("exam_details"), {"exam_id": self.exam.pk, "access_code": "CLASS"}
        )
        self.client.post(reverse("start_exam"))
        self.assertFalse(StudentExamAttempt.objects.exists())
        prep = ExamPreparation.objects.get()
        prep.calibrated_at = prep.finalized_at = timezone.now()
        prep.save()
        self.client.post(reverse("start_exam"))
        self.client.post(reverse("start_exam"))
        self.assertEqual(StudentExamAttempt.objects.count(), 1)
        self.assertEqual(
            StudentExamAttempt.objects.get().proctoring_session_id, prep.session_id
        )

    def test_availability_deadline_caps_time(self):
        self.exam.deadline = timezone.now() + timedelta(minutes=3)
        self.exam.save()
        self.client.post(
            reverse("exam_details"), {"exam_id": self.exam.pk, "access_code": "CLASS"}
        )
        ExamPreparation.objects.update(
            calibrated_at=timezone.now(), finalized_at=timezone.now()
        )
        self.client.post(reverse("start_exam"))
        self.assertEqual(
            StudentExamAttempt.objects.get().expires_at, self.exam.deadline
        )

    def test_class_and_role_restrictions(self):
        self.client.force_login(self.other)
        self.assertEqual(
            self.client.get(
                reverse("exam_details"), {"exam_id": self.exam.pk}
            ).status_code,
            404,
        )
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(reverse("student_home")).status_code, 403)
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse("teacher_home")).status_code, 403)

    def test_closed_expired_and_unsupported_exams_cannot_prepare(self):
        for changes in (
            {"access_status": False},
            {"deadline": timezone.now() - timedelta(seconds=1)},
        ):
            with self.subTest(changes=changes):
                Exam.objects.filter(pk=self.exam.pk).update(**changes)
                self.client.post(
                    reverse("exam_details"),
                    {"exam_id": self.exam.pk, "access_code": "CLASS"},
                )
                self.assertFalse(ExamPreparation.objects.exists())
                Exam.objects.filter(pk=self.exam.pk).update(
                    access_status=True, deadline=timezone.now() + timedelta(hours=1)
                )
        self.question.question_type = "IMG"
        self.question.save()
        self.client.post(
            reverse("exam_details"), {"exam_id": self.exam.pk, "access_code": "CLASS"}
        )
        self.assertFalse(ExamPreparation.objects.exists())

    def test_autosave_replace_clear_restore_and_atomic_invalid_save(self):
        attempt = self.attempt()
        for value in ("1", "0", ""):
            response = self.post_json(
                "save_exam_answers",
                attempt,
                {"token": "a" * 32, "answers": {str(self.question.pk): value}},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(attempt.answers.count(), 1)
            self.assertEqual(attempt.answers.get().answer_text, value)
        state = self.client.get(
            reverse("attempt_state", args=[attempt.pk]), {"token": "a" * 32}
        ).json()
        self.assertEqual(state["answers"], {str(self.question.pk): ""})
        response = self.post_json(
            "save_exam_answers",
            attempt,
            {
                "token": "a" * 32,
                "answers": {str(self.question.pk): "1", "99999": "bad"},
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(attempt.answers.get().answer_text, "")

    def test_writer_conflict_refresh_rotation_and_takeover(self):
        attempt = self.attempt(writer_seen_at=timezone.now())
        data = {"token": "b" * 32}
        self.assertEqual(
            self.post_json("attempt_state", attempt, data).status_code, 409
        )
        data["previous_token"] = "a" * 32
        self.assertEqual(
            self.post_json("attempt_state", attempt, data).status_code, 200
        )
        attempt.refresh_from_db()
        self.assertFalse(attempt.monitoring_interrupted)
        self.assertEqual(
            self.post_json(
                "save_exam_answers", attempt, {"token": "a" * 32, "answers": {}}
            ).status_code,
            409,
        )
        self.assertEqual(
            self.post_json(
                "attempt_state", attempt, {"token": "c" * 32, "takeover": True}
            ).status_code,
            200,
        )
        attempt.refresh_from_db()
        self.assertTrue(attempt.monitoring_interrupted)

    def test_foreign_attempt_state_and_answers_denied(self):
        attempt = self.attempt()
        self.client.force_login(self.other)
        self.assertEqual(
            self.post_json("attempt_state", attempt, {"token": "a" * 32}).status_code,
            404,
        )
        self.assertEqual(
            self.post_json(
                "save_exam_answers", attempt, {"token": "a" * 32, "answers": {}}
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("exam_results", args=[attempt.pk])).status_code, 404
        )

    def test_submit_partial_once_and_keep_score_zero(self):
        attempt = self.attempt()
        response = self.client.post(
            reverse("submit_exam"), {"attempt_id": attempt.pk, "writer_token": "a" * 32}
        )
        self.assertRedirects(response, reverse("exam_results", args=[attempt.pk]))
        attempt.refresh_from_db()
        ended = attempt.completed_at
        self.assertEqual(attempt.score, 0)
        self.assertEqual(attempt.prediction_status, "unavailable")
        self.client.post(
            reverse("submit_exam"),
            {
                "attempt_id": attempt.pk,
                "writer_token": "a" * 32,
                f"question_{self.question.pk}": "1",
            },
        )
        attempt.refresh_from_db()
        self.assertEqual(attempt.completed_at, ended)
        self.assertEqual(attempt.score, 0)
        self.assertContains(
            self.client.get(reverse("exam_results", args=[attempt.pk])), "Unanswered"
        )

    def test_expiry_grades_only_saved_answers_and_finalizes_prediction(self):
        attempt = self.attempt(expires_at=timezone.now() - timedelta(seconds=1))
        save_answers(attempt, {str(self.question.pk): "1"})
        response = self.client.get(
            reverse("attempt_state", args=[attempt.pk]), {"token": "a" * 32}
        )
        self.assertTrue(response.json()["completed"])
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 100)
        self.assertEqual(attempt.completed_at, attempt.expires_at)
        self.assertEqual(attempt.prediction_status, "unavailable")
        self.assertEqual(
            self.post_json(
                "save_exam_answers",
                attempt,
                {"token": "a" * 32, "answers": {str(self.question.pk): "0"}},
            ).status_code,
            409,
        )

    def test_deadline_change_applies_to_active_attempt(self):
        attempt = self.attempt()
        self.exam.deadline = timezone.now() - timedelta(seconds=1)
        self.exam.save()
        response = self.client.get(
            reverse("attempt_state", args=[attempt.pk]), {"token": "a" * 32}
        )
        self.assertTrue(response.json()["completed"])

    def test_text_tf_numeric_and_legacy_mcq_grading(self):
        attempt = self.attempt()
        questions = [self.question]
        for kind, correct in [("TF", "False"), ("NUM", "12"), ("FIB", "Water")]:
            questions.append(
                Question.objects.create(
                    exam=self.exam,
                    question_text=kind,
                    question_type=kind,
                    correct_answer_text=correct,
                )
            )
        self.question.choices = json.dumps(self.question.choices)
        self.question.save()
        save_answers(
            attempt,
            {
                str(q.pk): value
                for q, value in zip(questions, ["1", "False", "12", " water "])
            },
        )
        ended, _ = finish_attempt(attempt.pk, self.student, token="a" * 32)
        self.assertEqual(ended.score, 100)

    def test_student_exam_screens_render_without_diagnostics(self):
        attempt = self.attempt()
        session = self.client.session
        session["current_attempt_id"] = attempt.pk
        session.save()
        response = self.client.get(reverse("exam_session"))
        self.assertContains(response, "Review and submit")
        self.assertNotContains(response, "weighted_screen_pos")
        self.assertNotContains(response, "Suspicion score")
        for name in ("student_home", "my_scores"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_attempt_limit_rechecked_at_start(self):
        self.client.post(
            reverse("exam_details"), {"exam_id": self.exam.pk, "access_code": "CLASS"}
        )
        ExamPreparation.objects.update(
            calibrated_at=timezone.now(), finalized_at=timezone.now()
        )
        self.attempt(completed_at=timezone.now())
        self.attempt(attempt_number=2, completed_at=timezone.now())
        self.client.post(reverse("start_exam"))
        self.assertEqual(StudentExamAttempt.objects.count(), 2)


class LegacyMigrationTests(TransactionTestCase):
    def test_existing_duplicate_answers_and_running_attempt_upgrade(self):
        before = [
            ("studentside", "0004_studentexamattempt_prediction"),
            ("teacherside", "0003_exam_created_by"),
        ]
        after = [
            (
                "studentside",
                "0005_exampreparation_studentexamattempt_expires_at_and_more",
            ),
            ("teacherside", "0004_question_correct_answer_description_and_more"),
        ]
        try:
            executor = MigrationExecutor(connection)
            executor.migrate(before)
            apps = executor.loader.project_state(before).apps
            User = apps.get_model("homepage", "CustomUser")
            old_student = User.objects.create(username="legacy-student", role="student")
            old_teacher = User.objects.create(username="legacy-teacher", role="teacher")
            exam = apps.get_model("teacherside", "Exam").objects.create(
                title="Legacy",
                description="Test",
                deadline=timezone.now() + timedelta(hours=1),
                timelimit=timedelta(minutes=30),
                attempt_limit=2,
                class_designation="A",
                created_by=old_teacher,
            )
            question = apps.get_model("teacherside", "Question").objects.create(
                exam=exam,
                question_text="Test",
                question_type="TF",
                correct_answer_text="True",
            )
            start = timezone.now() - timedelta(minutes=5)
            attempt = apps.get_model(
                "studentside", "StudentExamAttempt"
            ).objects.create(
                student=old_student,
                exam=exam,
                attempt_number=1,
                proctoring_started_at=start,
            )
            Answer = apps.get_model("studentside", "StudentAnswer")
            Answer.objects.create(
                student_exam_attempt=attempt, question=question, answer_text="True"
            )
            Answer.objects.create(
                student_exam_attempt=attempt, question=question, answer_text=""
            )
            MigrationExecutor(connection).migrate(after)
            upgraded = StudentExamAttempt.objects.get(pk=attempt.pk)
            self.assertEqual(upgraded.started_at, start)
            self.assertEqual(upgraded.expires_at, start + timedelta(minutes=30))
            self.assertTrue(upgraded.monitoring_interrupted)
            self.assertTrue(upgraded.monitoring_started)
            self.assertEqual(upgraded.answers.count(), 1)
            self.assertEqual(upgraded.answers.get().answer_text, "")
        finally:
            MigrationExecutor(connection).migrate(after)
