"""Durable attempt state, separate from browser navigation and tracking."""

import json
import secrets
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import StudentAnswer, StudentExamAttempt

SUPPORTED_TYPES = {"MCQ", "TF", "NUM", "FIB"}


def choices_for(question):
    choices = question.choices or []
    try:
        choices = json.loads(choices) if isinstance(choices, str) else choices
    except (ValueError, TypeError):
        return []
    return (
        choices
        if isinstance(choices, list)
        and all(isinstance(choice, dict) for choice in choices)
        else []
    )


def question_ready(question):
    if (
        question.question_type not in SUPPORTED_TYPES
        or not question.correct_answer_text
    ):
        return False
    if question.question_type == "MCQ":
        texts = [choice.get("text") for choice in choices_for(question)]
        return (
            len(texts) >= 2
            and all(isinstance(text, str) and text.strip() for text in texts)
            and len(set(texts)) == len(texts)
            and question.correct_answer_text in texts
        )
    if question.question_type == "TF":
        return question.correct_answer_text in ("True", "False")
    return True


def eligibility_error(exam, student, *, new_attempt=True):
    if (
        not student.class_designation
        or exam.class_designation != student.class_designation
    ):
        return "This exam is not assigned to your class."
    if exam.deadline <= timezone.now():
        return "The exam deadline has passed."
    if not exam.access_status:
        return "Your teacher has not opened this exam."
    questions = list(exam.questions.all())
    if not questions or any(not question_ready(q) for q in questions):
        return "Your teacher needs to finish preparing this exam."
    if (
        new_attempt
        and exam.attempt_limit
        and StudentExamAttempt.objects.filter(student=student, exam=exam).count()
        >= exam.attempt_limit
    ):
        return "You have used all attempts for this exam."
    return None


def active_attempt(exam, student):
    return (
        StudentExamAttempt.objects.filter(
            student=student, exam=exam, completed_at__isnull=True
        )
        .order_by("-id")
        .first()
    )


def effective_expiry(attempt):
    # Legacy attempts have no start timestamp; do not grant fresh exam time.
    start = attempt.started_at or attempt.proctoring_started_at
    if attempt.expires_at:
        return min(attempt.expires_at, attempt.exam.deadline)
    return (
        min(start + attempt.exam.timelimit, attempt.exam.deadline)
        if start
        else attempt.exam.deadline
    )


def verify_writer(attempt, token):
    return isinstance(token, str) and bool(
        token and secrets.compare_digest(attempt.writer_token or "", token)
    )


def claim_writer(attempt, token, takeover=False, previous_token=None):
    now = timezone.now()
    occupied = attempt.writer_token and not verify_writer(attempt, token)
    refreshing = occupied and verify_writer(attempt, previous_token)
    recent = attempt.writer_seen_at and attempt.writer_seen_at > now - timedelta(
        seconds=60
    )
    if occupied and recent and not takeover and not refreshing:
        return False
    if occupied and not refreshing:
        attempt.monitoring_interrupted = True
    attempt.writer_token = token
    attempt.writer_seen_at = now
    attempt.save(
        update_fields=["writer_token", "writer_seen_at", "monitoring_interrupted"]
    )
    return True


def save_answers(attempt, answers):
    questions = {str(q.pk): q for q in attempt.exam.questions.all()}
    if not isinstance(answers, dict) or set(answers) - set(questions):
        raise ValueError("Answers must belong to this exam.")
    validated = {}
    for question_id, value in answers.items():
        question = questions[question_id]
        if not isinstance(value, str) or len(value) > 10000:
            raise ValueError("Enter an answer shorter than 10,000 characters.")
        if value and question.question_type == "MCQ":
            if not value.isdigit() or int(value) >= len(choices_for(question)):
                raise ValueError("Choose one of the available answers.")
        if value and question.question_type == "TF" and value not in ("True", "False"):
            raise ValueError("Choose True or False.")
        validated[question_id] = value
    for question_id, value in validated.items():
        StudentAnswer.objects.update_or_create(
            student_exam_attempt=attempt,
            question=questions[question_id],
            defaults={"answer_text": value},
        )


def grade(attempt):
    answers = {a.question_id: a.answer_text or "" for a in attempt.answers.all()}
    questions = list(attempt.exam.questions.all())
    correct = 0
    for question in questions:
        value = answers.get(question.pk, "")
        if question.question_type == "MCQ" and value.isdigit():
            choices = choices_for(question)
            if int(value) < len(choices):
                value = choices[int(value)].get("text", "")
        if value and question.correct_answer_text:
            correct += (
                value.strip().lower() == question.correct_answer_text.strip().lower()
            )
    return correct / len(questions) * 100 if questions else 0


@transaction.atomic
def finish_attempt(attempt_id, student, answers=None, token=None):
    attempt = (
        StudentExamAttempt.objects.select_for_update()
        .select_related("exam")
        .get(pk=attempt_id, student=student)
    )
    if attempt.completed_at:
        return attempt, False
    if token is not None and not verify_writer(attempt, token):
        raise PermissionError(
            "This exam is active in another tab. Take over to continue."
        )
    now = timezone.now()
    expired = now >= effective_expiry(attempt)
    if answers is not None and not expired:
        save_answers(attempt, answers)
    attempt.score = grade(attempt)
    attempt.completed_at = min(now, effective_expiry(attempt))
    attempt.proctoring_ended_at = now
    attempt.save(update_fields=["score", "completed_at", "proctoring_ended_at"])
    return attempt, True
