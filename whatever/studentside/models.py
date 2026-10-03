import os
import glob
from django.db import models
from django.conf import settings

# Create your models here.

class StudentExamAttempt(models.Model):
    student = models.ForeignKey('homepage.CustomUser', on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    exam = models.ForeignKey('teacherside.Exam', on_delete=models.CASCADE)
    attempt_number = models.PositiveIntegerField()
    started_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    writer_token = models.CharField(max_length=64, blank=True, default='')
    writer_seen_at = models.DateTimeField(null=True, blank=True)
    monitoring_interrupted = models.BooleanField(default=False)
    monitoring_started = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Proctoring integration fields
    proctoring_session_id = models.CharField(max_length=100, null=True, blank=True,
                                              help_text="WebSocket session ID for proctoring")
    proctoring_started_at = models.DateTimeField(null=True, blank=True)
    proctoring_ended_at = models.DateTimeField(null=True, blank=True)
    suspicion_score = models.FloatField(default=0.0, help_text="Cumulative suspicion score")
    violation_count = models.IntegerField(default=0, help_text="Number of flagged violations")

    prediction_label = models.CharField(max_length=30, null=True, blank=True)
    prediction_confidence = models.FloatField(null=True, blank=True)
    probability_cheating = models.FloatField(null=True, blank=True)
    probability_non_cheating = models.FloatField(null=True, blank=True)
    prediction_status = models.CharField(max_length=20, default='pending')
    prediction_error = models.TextField(null=True, blank=True)
    prediction_model_version = models.CharField(max_length=100, null=True, blank=True)
    prediction_completed_at = models.DateTimeField(null=True, blank=True)
    prediction_artifact = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'exam', 'attempt_number')

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} (Attempt {self.attempt_number})"

# Use to store the answers for each question in a student's exam attempt in a JSON format. This allows for flexibility in storing different types of answers (text, image, etc.) depending on the question type.
class StudentAnswer(models.Model):
    student_exam_attempt = models.ForeignKey(StudentExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('teacherside.Question', on_delete=models.CASCADE)
    answer_text = models.TextField(null=True, blank=True)
    answer_image = models.ImageField(upload_to='student_answers/', null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['student_exam_attempt', 'question'], name='one_answer_per_question'
        )]

    def __str__(self):
        return f"Answer for {self.question} by {self.student_exam_attempt.student.username}"

# Student Gaze Tracking Thresholds
class StudentTrackingThresholds(models.Model):
    student = models.OneToOneField('homepage.CustomUser', on_delete=models.CASCADE, limit_choices_to={'role': 'student'})

    # Individual calibration threshold fields
    calibration_up = models.FloatField()
    calibration_down = models.FloatField()
    calibration_center = models.FloatField()
    calibration_left = models.FloatField()
    calibration_right = models.FloatField()
    calibration_v_center = models.FloatField()
    iris_boxheight_center = models.FloatField()
    iris_boxheight_up = models.FloatField()
    iris_boxheight_down = models.FloatField()

    calibrated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thresholds for {self.student.username}"


class ProctoringSessionFiles(models.Model):
    """Tracks all files generated during a proctoring session"""

    # ForeignKey allows flexibility, nullable to handle edge cases
    exam_attempt = models.ForeignKey(
        StudentExamAttempt,
        on_delete=models.CASCADE,
        related_name='session_files',
        null=True,
        blank=True
    )

    session_id = models.CharField(max_length=100, db_index=True, unique=True)
    session_directory = models.CharField(max_length=500)

    # Single files
    calibration_file = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Path to eye_calibration.json from calibration phase"
    )
    heatmap_image = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Path to heatmap image (exam session only)"
    )

    # Multiple files (JSON arrays)
    session_log_csvs = models.JSONField(
        default=list,
        blank=True,
        help_text="CSV logs - typically 2: calibration + exam session"
    )
    violation_videos = models.JSONField(
        default=list,
        blank=True,
        help_text="Violation video clips from exam session"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proctoring Session Files"
        verbose_name_plural = "Proctoring Session Files"
        ordering = ['-created_at']

    def __str__(self):
        if self.exam_attempt:
            return f"Files for {self.exam_attempt.student.username} - {self.session_id}"
        return f"Files for session {self.session_id}"

    @classmethod
    def create_or_update_from_session(cls, session_id, exam_attempt=None):
        """
        Scan the session directory and create/update file tracking record.
        Call this after exam submission when all files exist.

        Args:
            session_id: The proctoring session ID
            exam_attempt: StudentExamAttempt instance
        """
        # Build paths
        session_dir = os.path.join('sessions', session_id)
        full_dir = os.path.join(settings.MEDIA_ROOT, session_dir)

        # Check if directory exists
        if not os.path.exists(full_dir):
            return None

        # Scan for files
        calibration = None
        heatmap = None
        csvs = []
        videos = []

        # Find calibration file
        calib_path = os.path.join(full_dir, 'eye_calibration.json')
        if os.path.exists(calib_path):
            calibration = os.path.join(session_dir, 'eye_calibration.json')

        # Find heatmap (only created at exam session end)
        heatmap_path = os.path.join(full_dir, f'heatmap_{session_id}.png')
        if os.path.exists(heatmap_path):
            heatmap = os.path.join(session_dir, f'heatmap_{session_id}.png')

        # Find all CSVs (sorted by timestamp in filename)
        for csv_file in sorted(glob.glob(os.path.join(full_dir, 'session_log_*.csv'))):
            filename = os.path.basename(csv_file)
            csvs.append(os.path.join(session_dir, filename))

        # Find all violation videos
        for video_file in sorted(glob.glob(os.path.join(full_dir, '*_violation_*.mp4'))):
            filename = os.path.basename(video_file)
            videos.append(os.path.join(session_dir, filename))

        # Create or update the record
        defaults = {
            'session_directory': session_dir,
            'calibration_file': calibration,
            'heatmap_image': heatmap,
            'session_log_csvs': csvs,
            'violation_videos': videos,
        }

        if exam_attempt is not None:
            defaults['exam_attempt'] = exam_attempt

        obj, created = cls.objects.update_or_create(
            session_id=session_id,
            defaults=defaults
        )

        return obj

    def get_full_path(self, relative_path):
        """Convert relative path to full filesystem path"""
        if relative_path:
            return os.path.join(settings.MEDIA_ROOT, relative_path)
        return None

    def get_calibration_path(self):
        return self.get_full_path(self.calibration_file)

    def get_heatmap_path(self):
        """Returns path to exam session heatmap"""
        return self.get_full_path(self.heatmap_image)

    def get_all_csv_paths(self):
        """Returns paths to both CSV files (calibration + exam session)"""
        return [self.get_full_path(csv) for csv in self.session_log_csvs if csv]

    def get_calibration_csv_path(self):
        """First CSV - from calibration phase"""
        if self.session_log_csvs:
            return self.get_full_path(self.session_log_csvs[0])
        return None

    def get_exam_csv_path(self):
        """Return the final CSV, which is the exam session log.

        Calibration and exam use separate WebSocket sessions with the same
        session ID. The calibration log is created first, so the final log is
        the only one eligible for exam prediction.
        """
        if len(self.session_log_csvs) >= 2:
            return self.get_full_path(self.session_log_csvs[-1])
        return None

    def get_all_video_paths(self):
        """Returns paths to all violation videos from exam session"""
        return [self.get_full_path(video) for video in self.violation_videos if video]


class ExamPreparation(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey('teacherside.Exam', on_delete=models.CASCADE)
    session_id = models.CharField(max_length=32, unique=True)
    camera_id = models.CharField(max_length=256, blank=True)
    calibrated_at = models.DateTimeField(null=True, blank=True)
    finalized_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
