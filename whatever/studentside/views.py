import json
import os
import secrets
import uuid

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from homepage.access import student_required
from teacherside.models import Exam

from .lifecycle import (
    active_attempt,
    claim_writer,
    effective_expiry,
    eligibility_error,
    save_answers,
    verify_writer,
)
from .lifecycle import finish_attempt as finish_state
from .models import (
    ExamPreparation,
    ProctoringSessionFiles,
    StudentExamAttempt,
)


def finish_attempt(attempt_id, student, answers=None, token=None):
    attempt, created = finish_state(attempt_id, student, answers, token)
    # All completion paths finalize evidence, including expiry during a heartbeat.
    claimed = StudentExamAttempt.objects.filter(
        pk=attempt.pk, prediction_status="pending"
    ).update(prediction_status="running")
    if claimed:
        try:
            from camera.registry import finalize_attempt_sync

            finalize_attempt_sync(attempt.proctoring_session_id)
            attempt.refresh_from_db()
            files = ProctoringSessionFiles.create_or_update_from_session(
                attempt.proctoring_session_id, attempt
            )
            _predict_exam_attempt(attempt, files)
        except Exception:
            attempt.prediction_status = "unavailable"
            attempt.prediction_error = "Monitoring artifacts could not be finalized."
            attempt.save(update_fields=["prediction_status", "prediction_error"])
    return attempt, created


def _exam(request, exam_id):
    return get_object_or_404(
        Exam, pk=exam_id, class_designation=request.user.class_designation
    )


@student_required
def student_home(request):
    exams = (
        list(
            Exam.objects.filter(
                class_designation=request.user.class_designation
            ).order_by("deadline")
        )
        if request.user.class_designation
        else []
    )
    for exam in exams:
        exam.attempts_used = StudentExamAttempt.objects.filter(
            student=request.user, exam=exam
        ).count()
        exam.remaining_attempts = (
            max(0, exam.attempt_limit - exam.attempts_used)
            if exam.attempt_limit
            else None
        )
        exam.active_attempt = active_attempt(exam, request.user)
        if exam.active_attempt and timezone.now() >= effective_expiry(
            exam.active_attempt
        ):
            finish_attempt(exam.active_attempt.pk, request.user)
            exam.active_attempt = None
        exam.availability_reason = eligibility_error(exam, request.user)
        exam.is_accessible = exam.availability_reason is None
        exam.duration_minutes = int(exam.timelimit.total_seconds() // 60)
    return render(
        request,
        "studentside/student_landing_page.html",
        {"exams": exams, "student_class": request.user.class_designation},
    )


@student_required
def exam_details(request):
    exam = _exam(request, request.GET.get("exam_id") or request.POST.get("exam_id"))
    current = active_attempt(exam, request.user)
    if current:
        request.session["current_attempt_id"] = current.pk
        return redirect("exam_session")
    error = eligibility_error(exam, request.user)
    if error:
        messages.error(request, error)
        return redirect("student_home")
    if request.method == "POST":
        code = request.POST.get("access_code", "")
        if exam.access_code and not secrets.compare_digest(
            code.strip(), exam.access_code
        ):
            error = "That code does not match. Check the code from your teacher."
        else:
            prep = ExamPreparation.objects.create(
                student=request.user, exam=exam, session_id=uuid.uuid4().hex
            )
            request.session["preparation_id"] = prep.pk
            return redirect("home")
    return render(
        request,
        "studentside/test_exam.html",
        {
            "exam": exam,
            "error": error,
            "duration_minutes": int(exam.timelimit.total_seconds() // 60),
            "attempts_used": StudentExamAttempt.objects.filter(
                student=request.user, exam=exam
            ).count(),
        },
    )


@student_required
@require_POST
def start_exam(request):
    prep = get_object_or_404(
        ExamPreparation, pk=request.session.get("preparation_id"), student=request.user
    )
    with transaction.atomic():
        exam = Exam.objects.select_for_update().get(pk=prep.exam_id)
        current = active_attempt(exam, request.user)
        if not current:
            error = eligibility_error(exam, request.user)
            if error or not prep.calibrated_at or not prep.finalized_at:
                messages.error(
                    request, error or "Complete camera setup before starting your exam."
                )
                return redirect("home")
            now = timezone.now()
            current = StudentExamAttempt.objects.create(
                student=request.user,
                exam=exam,
                attempt_number=StudentExamAttempt.objects.filter(
                    student=request.user, exam=exam
                ).count()
                + 1,
                started_at=now,
                expires_at=min(now + exam.timelimit, exam.deadline),
                proctoring_started_at=now,
                proctoring_session_id=prep.session_id,
            )
    request.session["current_attempt_id"] = current.pk
    return redirect("exam_session")


@student_required
@require_POST
def reset_preparation(request):
    previous = get_object_or_404(
        ExamPreparation, pk=request.session.get("preparation_id"), student=request.user
    )
    if active_attempt(previous.exam, request.user):
        return JsonResponse(
            {"error": "Setup cannot restart during an exam."}, status=409
        )
    if eligibility_error(previous.exam, request.user):
        return JsonResponse({"error": "This exam is no longer available."}, status=409)
    prep = ExamPreparation.objects.create(
        student=request.user, exam=previous.exam, session_id=uuid.uuid4().hex
    )
    request.session["preparation_id"] = prep.pk
    return JsonResponse({"session_id": prep.session_id})


@student_required
def exam_session(request):
    attempt = get_object_or_404(
        StudentExamAttempt.objects.select_related("exam"),
        pk=request.session.get("current_attempt_id"),
        student=request.user,
    )
    if attempt.completed_at:
        return redirect("exam_results", attempt_id=attempt.pk)
    if timezone.now() >= effective_expiry(attempt):
        finish_attempt(attempt.pk, request.user)
        return redirect("exam_results", attempt_id=attempt.pk)
    questions = list(attempt.exam.questions.order_by("question_id"))
    answers = {a.question_id: a.answer_text or "" for a in attempt.answers.all()}
    for question in questions:
        if isinstance(question.choices, str):
            question.choices = json.loads(question.choices)
        question.saved_answer = answers.get(question.pk, "")
    prep = ExamPreparation.objects.filter(
        session_id=attempt.proctoring_session_id
    ).first()
    return render(
        request,
        "studentside/exam_session.html",
        {
            "exam": attempt.exam,
            "attempt": attempt,
            "questions": questions,
            "camera_id": prep.camera_id if prep else "",
            "expiry": effective_expiry(attempt).isoformat(),
            "server_now": timezone.now().isoformat(),
        },
    )


@student_required
def attempt_state(request, attempt_id):
    attempt = get_object_or_404(
        StudentExamAttempt.objects.select_related("exam"),
        pk=attempt_id,
        student=request.user,
    )
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = data["token"]
            if not isinstance(token, str) or len(token) != 32:
                raise ValueError("Invalid browser identifier.")
        except (ValueError, KeyError, TypeError):
            return JsonResponse({"error": "Invalid browser identifier."}, status=400)
        with transaction.atomic():
            attempt = (
                StudentExamAttempt.objects.select_for_update()
                .select_related("exam")
                .get(pk=attempt.pk)
            )
            if not attempt.completed_at and not claim_writer(
                attempt, token, data.get("takeover") is True, data.get("previous_token")
            ):
                return JsonResponse(
                    {"error": "Your exam is active in another tab or device."},
                    status=409,
                )
    elif request.method != "GET":
        return JsonResponse({"error": "Method not allowed."}, status=405)
    else:
        token = request.GET.get("token", "")
        if not attempt.completed_at and not verify_writer(attempt, token):
            return JsonResponse(
                {"error": "Another tab is controlling this attempt."}, status=409
            )
        if not attempt.completed_at:
            attempt.writer_seen_at = timezone.now()
            attempt.save(update_fields=["writer_seen_at"])
    if not attempt.completed_at and timezone.now() >= effective_expiry(attempt):
        attempt, _ = finish_attempt(attempt.pk, request.user)
    return JsonResponse(
        {
            "expires_at": effective_expiry(attempt).isoformat(),
            "server_now": timezone.now().isoformat(),
            "completed": bool(attempt.completed_at),
            "results_url": reverse("exam_results", args=[attempt.pk]),
            "answers": {
                str(a.question_id): a.answer_text or "" for a in attempt.answers.all()
            },
        }
    )


@student_required
@require_POST
def save_exam_answers(request, attempt_id):
    try:
        data = json.loads(request.body)
        with transaction.atomic():
            attempt = get_object_or_404(
                StudentExamAttempt.objects.select_for_update().select_related("exam"),
                pk=attempt_id,
                student=request.user,
            )
            if not verify_writer(attempt, data.get("token")):
                return JsonResponse(
                    {"error": "This exam is active in another tab."}, status=409
                )
            if attempt.completed_at or timezone.now() >= effective_expiry(attempt):
                return JsonResponse(
                    {"error": "The answer deadline has passed."}, status=409
                )
            save_answers(attempt, data.get("answers"))
            attempt.writer_seen_at = timezone.now()
            attempt.save(update_fields=["writer_seen_at"])
        return JsonResponse({"saved": True})
    except (ValueError, TypeError, AttributeError):
        return JsonResponse(
            {"error": "Check your answers and try saving again."}, status=400
        )


@student_required
@require_POST
def submit_exam(request):
    attempt_id = request.POST.get("attempt_id") or request.session.get(
        "current_attempt_id"
    )
    existing = get_object_or_404(
        StudentExamAttempt, pk=attempt_id, student=request.user
    )
    answers = {
        key.removeprefix("question_"): value
        for key, value in request.POST.items()
        if key.startswith("question_")
    }
    try:
        attempt, created = finish_attempt(
            existing.pk, request.user, answers, request.POST.get("writer_token", "")
        )
    except (PermissionError, ValueError) as error:
        messages.error(request, str(error))
        return redirect("exam_session")
    return redirect("exam_results", attempt_id=attempt.pk)


@student_required
@require_POST
def save_tracking_thresholds(request):
    # Calibration is acknowledged by the authenticated WebSocket consumer only.
    return JsonResponse(
        {"error": "Complete guided camera setup to save calibration."}, status=409
    )


def _predict_exam_attempt(exam_attempt, session_files):
    """Run prediction from the files registered for an exam attempt."""
    if (
        session_files is None
        or exam_attempt.monitoring_interrupted
        or not exam_attempt.monitoring_started
    ):
        exam_attempt.prediction_status = "unavailable"
        exam_attempt.prediction_error = (
            "Monitoring was incomplete or session files were unavailable."
        )
        exam_attempt.save(update_fields=["prediction_status", "prediction_error"])
        return

    try:
        import heatmap_feature_extractor as hfe
        from web_session_predict import predict_session_files
    except ImportError:
        exam_attempt.prediction_status = "unavailable"
        exam_attempt.prediction_error = "Prediction dependencies are not installed."
        exam_attempt.save(update_fields=["prediction_status", "prediction_error"])
        return
    heatmap_path = session_files.get_heatmap_path()
    csv_path = session_files.get_exam_csv_path()
    if (
        not heatmap_path
        or not csv_path
        or not os.path.isfile(heatmap_path)
        or not os.path.isfile(csv_path)
    ):
        exam_attempt.prediction_status = "unavailable"
        exam_attempt.prediction_error = (
            "Complete exam heatmap and log artifacts are unavailable."
        )
        exam_attempt.save(update_fields=["prediction_status", "prediction_error"])
        return

    if csv_path and os.path.isfile(csv_path):
        csv_features = hfe.extract_csv_features(csv_path)
        exam_attempt.violation_count = sum(
            csv_features[f"violation_count_{category}"]
            for category in hfe.VIOLATION_CATEGORIES
        )
        exam_attempt.save(update_fields=["violation_count"])

    exam_attempt.prediction_status = "running"
    exam_attempt.prediction_error = None
    exam_attempt.save(update_fields=["prediction_status", "prediction_error"])

    try:
        result = predict_session_files(
            heatmap_path=heatmap_path,
            csv_path=csv_path,
            session_directory=session_files.get_full_path(
                session_files.session_directory
            ),
        )
        exam_attempt.suspicion_score = result["confidence"]
        exam_attempt.prediction_label = result["predicted_label"]
        exam_attempt.prediction_confidence = result["confidence"]
        exam_attempt.probability_cheating = result["probability_cheating"]
        exam_attempt.probability_non_cheating = result["probability_non_cheating"]
        exam_attempt.prediction_model_version = result["model_version"]
        exam_attempt.prediction_artifact = result.get("artifact_path")
        exam_attempt.prediction_status = "completed"
        exam_attempt.prediction_completed_at = timezone.now()
        exam_attempt.save(
            update_fields=[
                "suspicion_score",
                "prediction_label",
                "prediction_confidence",
                "probability_cheating",
                "probability_non_cheating",
                "prediction_model_version",
                "prediction_artifact",
                "prediction_status",
                "prediction_completed_at",
            ]
        )
    except Exception as error:
        exam_attempt.prediction_status = "failed"
        exam_attempt.prediction_error = str(error)
        exam_attempt.save(update_fields=["prediction_status", "prediction_error"])


@student_required
def exam_results(request, attempt_id):
    """Display results"""
    exam_attempt = get_object_or_404(
        StudentExamAttempt, id=attempt_id, student=request.user
    )

    if not exam_attempt.completed_at and timezone.now() >= effective_expiry(
        exam_attempt
    ):
        exam_attempt, _ = finish_attempt(exam_attempt.pk, request.user)
    if not exam_attempt.completed_at:
        request.session["current_attempt_id"] = exam_attempt.pk
        return redirect("exam_session")
    answers = exam_attempt.answers.all().select_related("question")
    answer_dict = {answer.question.question_id: answer for answer in answers}

    questions_with_answers = []
    for question in exam_attempt.exam.questions.all().order_by("question_id"):
        if question.choices and isinstance(question.choices, str):
            question.choices = json.loads(question.choices)

        student_answer = answer_dict.get(question.question_id)
        is_correct = False
        student_answer_text = None

        if student_answer:
            student_answer_text = student_answer.answer_text

            if question.question_type == "MCQ":
                try:
                    idx = int(student_answer.answer_text)
                    if 0 <= idx < len(question.choices):
                        choice = question.choices[idx]
                        student_answer_text = choice.get("text")
                        is_correct = choice.get("text") == question.correct_answer_text
                except:
                    pass
            elif question.question_type == "TF":
                is_correct = student_answer.answer_text == question.correct_answer_text
            elif question.question_type in ["NUM", "FIB"]:
                if question.correct_answer_text:
                    is_correct = (
                        student_answer.answer_text or ""
                    ).strip().lower() == question.correct_answer_text.strip().lower()

        questions_with_answers.append(
            {
                "question": question,
                "student_answer": student_answer_text,
                "is_correct": is_correct,
            }
        )

    return render(
        request,
        "studentside/exam_results.html",
        {
            "exam_attempt": exam_attempt,
            "questions_with_answers": questions_with_answers,
            "can_retake": eligibility_error(exam_attempt.exam, request.user) is None,
        },
    )


@student_required
def my_scores(request):
    """Group the signed-in student's own exam attempts by exam, one directory per exam."""
    attempts = (
        StudentExamAttempt.objects.filter(student=request.user)
        .select_related("exam")
        .order_by("-attempt_number", "-id")
    )

    exams = {}
    for attempt in attempts:
        if not attempt.completed_at and timezone.now() >= effective_expiry(attempt):
            attempt, _ = finish_attempt(attempt.pk, request.user)
        exam = attempt.exam
        if exam.exam_id not in exams:
            exams[exam.exam_id] = {
                "exam": exam,
                "attempts": [],
                "best_score": None,
            }
        group = exams[exam.exam_id]
        group["attempts"].append(attempt)
        if attempt.score is not None and (
            group["best_score"] is None or attempt.score > group["best_score"]
        ):
            group["best_score"] = attempt.score

    def latest_attempt_id(group):
        return group["attempts"][0].id

    exam_groups = sorted(exams.values(), key=latest_attempt_id, reverse=True)

    return render(
        request,
        "studentside/my_scores.html",
        {
            "exam_groups": exam_groups,
        },
    )
