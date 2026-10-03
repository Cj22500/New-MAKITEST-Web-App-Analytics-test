from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from homepage.models import CustomUser
from studentside.models import ProctoringSessionFiles, StudentExamAttempt

from .models import Exam, Question


class TeacherAccessAndEditingTests(TestCase):
    def setUp(self):
        self.teacher = CustomUser.objects.create_user("teacher", role="teacher")
        self.other = CustomUser.objects.create_user("other", role="teacher")
        self.student = CustomUser.objects.create_user(
            "student", role="student", class_designation="10-A"
        )
        self.exam = Exam.objects.create(
            title="Science",
            description="Practice",
            deadline=timezone.now() + timedelta(hours=1),
            timelimit=timedelta(minutes=30),
            attempt_limit=2,
            class_designation="10-A",
            created_by=self.teacher,
        )
        self.question = Question.objects.create(
            exam=self.exam,
            question_text="Water is wet",
            question_type="TF",
            correct_answer_text="True",
        )
        self.client.force_login(self.teacher)

    def settings_data(self, **kwargs):
        data = {
            "title": "New title",
            "description": "Practice",
            "deadline": self.exam.deadline.strftime("%Y-%m-%dT%H:%M"),
            "timelimit": 30,
            "attempt_limit": 2,
            "class_designation": "10-A",
            "access_status": "on",
        }
        data.update(kwargs)
        return data

    def test_teacher_pages_render(self):
        for name, args in [
            ("teacher_home", []),
            ("exams_list", []),
            ("manage_students", []),
            ("create_exam", []),
            ("modify_exam", [self.exam.pk]),
            ("add_questions", [self.exam.pk]),
            ("exam_attempts_list", [self.exam.pk]),
            ("student_attempt_detail", [self.exam.pk, self.student.pk]),
        ]:
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name, args=args)).status_code, 200
                )

    def test_owner_scope_for_every_exam_action(self):
        self.client.force_login(self.other)
        for name, args in [
            ("modify_exam", [self.exam.pk]),
            ("add_questions", [self.exam.pk]),
            ("exam_attempts_list", [self.exam.pk]),
            ("student_attempt_detail", [self.exam.pk, self.student.pk]),
            ("edit_question", [self.exam.pk, self.question.pk]),
        ]:
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name, args=args)).status_code, 404
                )
        self.assertEqual(
            self.client.post(
                reverse("delete_question", args=[self.question.pk])
            ).status_code,
            404,
        )
        self.assertNotContains(self.client.get(reverse("exams_list")), "Science")

    def test_new_exam_stays_closed_and_bound_errors_preserve_values(self):
        self.client.post(reverse("create_exam"), self.settings_data())
        self.assertFalse(Exam.objects.exclude(pk=self.exam.pk).get().access_status)
        response = self.client.post(
            reverse("create_exam"),
            self.settings_data(title="Keep this title", timelimit=1),
        )
        self.assertContains(response, "Keep this title")
        self.assertContains(response, "20")

    def test_empty_or_legacy_image_exam_cannot_open(self):
        self.question.delete()
        self.client.post(
            reverse("modify_exam", args=[self.exam.pk]), self.settings_data()
        )
        self.exam.refresh_from_db()
        self.assertFalse(self.exam.access_status)
        Question.objects.create(
            exam=self.exam,
            question_text="Legacy image",
            question_type="IMG",
            correct_answer_text="answer",
        )
        self.client.post(
            reverse("modify_exam", args=[self.exam.pk]), self.settings_data()
        )
        self.exam.refresh_from_db()
        self.assertFalse(self.exam.access_status)

    def test_supported_exam_can_open(self):
        self.client.post(
            reverse("modify_exam", args=[self.exam.pk]), self.settings_data()
        )
        self.exam.refresh_from_db()
        self.assertTrue(self.exam.access_status)

    def test_sparse_choice_indexes_and_correct_answer(self):
        response = self.client.post(
            reverse("add_questions", args=[self.exam.pk]),
            {
                "question_text": "Choose water",
                "question_type": "MCQ",
                "choice_text_2": "Water",
                "choice_text_5": "Stone",
                "correct_choice": "2",
            },
        )
        self.assertEqual(response.status_code, 302)
        question = self.exam.questions.get(question_type="MCQ")
        self.assertEqual(question.correct_answer_text, "Water")
        self.assertEqual([c["text"] for c in question.choices], ["Water", "Stone"])

    def test_duplicate_choices_rejected(self):
        response = self.client.post(
            reverse("add_questions", args=[self.exam.pk]),
            {
                "question_text": "Duplicate choices",
                "question_type": "MCQ",
                "choice_text_1": "Same",
                "choice_text_2": "Same",
                "correct_choice": "1",
            },
        )
        self.assertContains(response, "two different choices")
        self.assertContains(response, 'value="1" checked')
        self.assertEqual(self.exam.questions.count(), 1)

    def test_freeze_questions_after_attempt_but_allow_settings(self):
        StudentExamAttempt.objects.create(
            student=self.student, exam=self.exam, attempt_number=1
        )
        self.client.post(reverse("delete_question", args=[self.question.pk]))
        self.assertTrue(Question.objects.filter(pk=self.question.pk).exists())
        self.client.post(
            reverse("edit_question", args=[self.exam.pk, self.question.pk]),
            {
                "question_text": "Changed",
                "question_type": "TF",
                "correct_answer_text": "False",
            },
        )
        self.question.refresh_from_db()
        self.assertEqual(self.question.question_text, "Water is wet")
        self.client.post(
            reverse("modify_exam", args=[self.exam.pk]), self.settings_data()
        )
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.title, "New title")

    def test_evidence_scope_and_raw_media_block(self):
        attempt = StudentExamAttempt.objects.create(
            student=self.student, exam=self.exam, attempt_number=1
        )
        files = ProctoringSessionFiles.objects.create(
            exam_attempt=attempt,
            session_id="test-session",
            session_directory="sessions/test-session",
            calibration_file="sessions/test-session/eye_calibration.json",
        )
        self.client.force_login(self.other)
        for name in ("download_session_file", "view_session_file"):
            self.assertEqual(
                self.client.get(
                    reverse(name, args=[files.session_id, "calibration"])
                ).status_code,
                404,
            )
        self.assertEqual(
            self.client.get(
                reverse("download_all_session_files", args=[files.session_id])
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(
                "/media/sessions/test-session/eye_calibration.json"
            ).status_code,
            404,
        )

    def test_shared_directory_class_update_is_post_only(self):
        url = reverse("update_student_class", args=[self.student.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url, {"class_designation": "10-B"})
        self.student.refresh_from_db()
        self.assertEqual(self.student.class_designation, "10-B")
