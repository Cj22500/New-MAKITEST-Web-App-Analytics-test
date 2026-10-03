from datetime import timedelta

from django.db import models
from django.conf import settings  # Add this import at the top

# Create your models here.
class Exam(models.Model):
    # Exam ID is automatically generated and set as the primary key
    exam_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    class_designation = models.CharField(max_length=100)
    timelimit = models.DurationField(help_text="Enter the time limit for the exam (e.g., 1:30:00 for 1 hour 30 minutes).")
    attempt_limit = models.PositiveIntegerField(help_text="Enter the maximum number of attempts allowed for this exam.")
    # Access code can be blank if the exam is open to all students, otherwise it can be set to a specific code for restricted access
    access_code = models.CharField(max_length=20, null=True, blank=True, help_text="Enter a unique access code for the exam.")
    access_status = models.BooleanField(default=False, help_text="Indicates whether the exam is currently accessible to students.")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

# Exam Questions Database
# Each question is linked to an exam
# A question can have a supporting image in addition to the text
# The questions can be multiple choice, true/false, numerical, images or fill in the blanks
# Answers can be text or images depending on the question type
# Choices can be empty depending on the question type
# All questions have a unique question_id are all placed in the same json file for the each exam
# Example: Exam1 {
#     "questions": [
#         {
#             "question_id": 1,
#             "question_text": "What is 2 + 2?",
#             "question_image": null,
#             "question_type": "MCQ",
#             "choices": [
#                 {"text": "3", "image": null},
#                 {"text": "4", "image": null},
#                 {"text": "5", "image": null}
#             ],
#             "correct_answer_text": "4",
#             "correct_answer_image": null
#         }
#     ]
# }


class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice Question'),
        ('TF', 'True/False'),
        ('NUM', 'Numerical'),
        ('IMG', 'Image-based'),
        ('FIB', 'Fill in the Blanks'),
    ]

    question_id = models.AutoField(primary_key=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    image_description = models.TextField(blank=True)
    question_image = models.ImageField(upload_to='question_images/', null=True, blank=True)
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)
    
    # Choices for MCQ type questions
    choices = models.JSONField(null=True, blank=True, help_text="Enter choices as a JSON array for MCQ type questions.")
    
    correct_answer_text = models.TextField(null=True, blank=True)
    correct_answer_image = models.ImageField(upload_to='answer_images/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Question {self.question_id} for Exam {self.exam.title}"

