from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import datetime
from homepage.models import CustomUser
from teacherside.models import Exam
from studentside.models import StudentExamAttempt, ProctoringSessionFiles
from teacherside.analytics_utils import (
    parse_session_csv,
    extract_features_from_events,
    predict_suspicion_for_attempt,
    compute_aggregate_analytics
)
import os
import tempfile
import csv


class AnalyticsUtilsTestCase(TestCase):
    def setUp(self):
        # Create temp CSV file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self.temp_dir.name, "session_log_test.csv")
        headers = [
            "Gaze direction",
            "Timestamp start",
            "Timestamp finish",
            "Violation label",
            "Numerical behavioural score",
            "Video Evidence File"
        ]
        rows = [
            ["Center", "2025-01-01 10:00:00.000", "2025-01-01 10:00:05.000", "normal", "0", ""],
            ["Down", "2025-01-01 10:00:05.000", "2025-01-01 10:00:15.000", "looking_off_screen", "100", "test_video.mp4"]
        ]
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_session_csv(self):
        events = parse_session_csv(self.csv_path)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['direction'], 'Center')
        self.assertEqual(events[0]['duration_s'], 5.0)
        self.assertEqual(events[1]['direction'], 'Down')
        self.assertEqual(events[1]['duration_s'], 10.0)
        self.assertEqual(events[1]['violation_label'], 'looking_off_screen')

    def test_extract_features_from_events(self):
        events = parse_session_csv(self.csv_path)
        df = extract_features_from_events(events)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['total_events'], 2)
        self.assertEqual(df.iloc[0]['violation_count'], 1)

    def test_predict_suspicion_for_attempt(self):
        teacher = CustomUser.objects.create_user(username="teacher1", password="password", role="teacher")
        student = CustomUser.objects.create_user(username="student1", password="password", role="student")
        deadline = timezone.now() + datetime.timedelta(days=1)
        timelimit = datetime.timedelta(minutes=60)
        exam = Exam.objects.create(title="Math Exam", created_by=teacher, deadline=deadline, timelimit=timelimit, attempt_limit=1)
        attempt = StudentExamAttempt.objects.create(
            student=student,
            exam=exam,
            attempt_number=1,
            proctoring_session_id="session_123",
            suspicion_score=60.0,
            violation_count=1
        )
        prediction = predict_suspicion_for_attempt(attempt, None)
        self.assertIn('probability', prediction)
        self.assertIn('prediction_label', prediction)
        self.assertIn('is_suspicious', prediction)


class AnalyticsViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = CustomUser.objects.create_user(username="teacher_user", password="password123", role="teacher")
        self.student = CustomUser.objects.create_user(username="student_user", password="password123", role="student")
        deadline = timezone.now() + datetime.timedelta(days=1)
        timelimit = datetime.timedelta(minutes=60)
        self.exam = Exam.objects.create(title="Science Exam", created_by=self.teacher, deadline=deadline, timelimit=timelimit, attempt_limit=1)
        self.attempt = StudentExamAttempt.objects.create(
            student=self.student,
            exam=self.exam,
            attempt_number=1,
            proctoring_session_id="test_sess_001",
            suspicion_score=35.0,
            violation_count=2
        )

    def test_student_cannot_access_analytics(self):
        self.client.login(username="student_user", password="password123")
        res = self.client.get(reverse('analytics_dashboard'))
        self.assertNotEqual(res.status_code, 200)

    def test_teacher_can_access_analytics_dashboard(self):
        self.client.login(username="teacher_user", password="password123")
        res = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Suspicious Behavior Analytics Dashboard")
        self.assertContains(res, "Science Exam")

    def test_teacher_can_access_attempt_analytics_detail(self):
        self.client.login(username="teacher_user", password="password123")
        res = self.client.get(reverse('attempt_analytics_detail', args=[self.attempt.id]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "ML Model Suspicion Analysis")

    def test_run_model_inference_ajax(self):
        self.client.login(username="teacher_user", password="password123")
        res = self.client.post(reverse('run_model_inference_ajax', args=[self.attempt.id]))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('prediction', data)
