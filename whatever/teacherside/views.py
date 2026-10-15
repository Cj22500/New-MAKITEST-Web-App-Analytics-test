import csv
import mimetypes
import os
import uuid
import zipfile
from collections import Counter
from io import BytesIO

from django.contrib import messages
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Avg, Count, Max, Q, Sum
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from homepage.access import teacher_required
from homepage.models import CustomUser
from studentside.lifecycle import SUPPORTED_TYPES, choices_for, question_ready
from studentside.models import (
    ExamPreparation,
    ProctoringSessionFiles,
    StudentExamAttempt,
)

from .create_exam_forms import ExamForm, QuestionForm
from .models import Exam, Question


def owned_exam(request, exam_id):
    return get_object_or_404(Exam, pk=exam_id, created_by=request.user)


def violation_counts_for_session(files):
    if not files:
        return []
    exam_csv_path = files.get_exam_csv_path()
    if not exam_csv_path:
        return []

    counts = Counter()
    try:
        with open(exam_csv_path, newline="", encoding="utf-8-sig") as csv_file:
            for row in csv.DictReader(csv_file):
                violation_type = (row.get("Violation label") or "").strip()
                if violation_type and violation_type.casefold() != "normal":
                    counts[violation_type] += 1
    except (OSError, UnicodeError, csv.Error):
        return []

    return [
        {"type": violation_type, "count": count}
        for violation_type, count in sorted(counts.items())
    ]


def publication_error(exam):
    questions = list(exam.questions.all())
    if not questions:
        return "Add questions before opening this exam."
    if any(q.question_type not in SUPPORTED_TYPES for q in questions):
        return "Convert image-based questions to a supported answer type before opening this exam."
    if any(not question_ready(q) for q in questions):
        return "Finish each question and its correct answer before opening this exam."
    return None


@teacher_required
def teacher_home(request):
    exams = Exam.objects.filter(created_by=request.user)
    return render(
        request,
        "teacherside/teacher_landing_page.html",
        {
            "exam_count": exams.count(),
            "open_count": exams.filter(access_status=True).count(),
            "attempt_count": StudentExamAttempt.objects.filter(
                exam__created_by=request.user
            ).count(),
        },
    )


@teacher_required
def manage_students(request):
    search_query = request.GET.get("search", "")
    students = CustomUser.objects.filter(role="student")
    total = students.count()
    if search_query:
        students = students.filter(
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(class_designation__icontains=search_query)
        )
    return render(
        request,
        "teacherside/manage_students.html",
        {
            "students": students.order_by("username"),
            "search_query": search_query,
            "total_count": total,
            "filtered_count": students.count(),
        },
    )


@teacher_required
@require_POST
def update_student_class(request, user_id):
    student = get_object_or_404(CustomUser, pk=user_id, role="student")
    designation = request.POST.get("class_designation", "").strip()
    if len(designation) > 100:
        messages.error(request, "Class names must be 100 characters or shorter.")
    else:
        student.class_designation = designation
        student.save(update_fields=["class_designation"])
        messages.success(
            request, f"Class saved for {student.get_full_name() or student.username}."
        )
    return redirect("manage_students")


@teacher_required
def create_exam(request):
    form = ExamForm(request.POST or None)
    form.fields.pop("access_status")
    if request.method == "POST" and form.is_valid():
        exam = form.save(commit=False)
        exam.created_by = request.user
        exam.access_status = False
        exam.save()
        messages.success(
            request, "Exam created and kept closed while you add questions."
        )
        return redirect("add_questions", exam_id=exam.pk)
    return render(request, "teacherside/create_exam.html", {"form": form})


@teacher_required
def exams_list(request):
    exams = (
        Exam.objects.filter(created_by=request.user)
        .annotate(question_count=Count("questions"))
        .order_by("-created_at")
    )
    return render(request, "teacherside/exams_list.html", {"exams": exams})


@teacher_required
def modify_exam(request, exam_id):
    exam = owned_exam(request, exam_id)
    form = ExamForm(
        request.POST or None,
        instance=exam,
        initial={"timelimit": int(exam.timelimit.total_seconds() // 60)},
    )
    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["access_status"] and publication_error(exam):
            form.add_error("access_status", publication_error(exam))
        else:
            form.save()
            messages.success(request, "Exam settings saved.")
            return redirect("modify_exam", exam_id=exam.pk)
    questions = list(exam.questions.order_by("question_id"))
    for question in questions:
        question.choices = choices_for(question)
    return render(
        request,
        "teacherside/modify_exam.html",
        {
            "exam": exam,
            "form": form,
            "questions": questions,
            "frozen": StudentExamAttempt.objects.filter(exam=exam).exists(),
        },
    )


@teacher_required
def add_questions(request, exam_id, question_id=None):
    exam = owned_exam(request, exam_id)
    question = (
        get_object_or_404(Question, pk=question_id, exam=exam) if question_id else None
    )
    if StudentExamAttempt.objects.filter(exam=exam).exists():
        messages.error(
            request, "Questions are locked because students have started this exam."
        )
        return redirect("modify_exam", exam_id=exam.pk)
    form = QuestionForm(request.POST or None, request.FILES or None, instance=question)
    choices = (
        choices_for(question)
        if question
        else [{"text": "", "image": None}, {"text": "", "image": None}]
    )
    for choice in choices:
        choice["selected"] = bool(
            question and choice.get("text") == question.correct_answer_text
        )
    if request.method == "POST":
        choices = []
        for key in sorted(
            (k for k in request.POST if k.startswith("choice_text_")),
            key=lambda k: int(k.rsplit("_", 1)[1]),
        ):
            index = key.rsplit("_", 1)[1]
            choices.append(
                {
                    "text": request.POST[key].strip(),
                    "image": request.POST.get("choice_existing_" + index) or None,
                    "description": request.POST.get("choice_description_" + index, ""),
                    "source_index": index,
                    "selected": index == request.POST.get("correct_choice"),
                }
            )
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.exam = exam
            if candidate.question_type == "MCQ":
                selected = request.POST.get("correct_choice")
                selected_choice = next(
                    (c for c in choices if c["source_index"] == selected), None
                )
                texts = [c["text"] for c in choices]
                if (
                    len(choices) < 2
                    or any(not text for text in texts)
                    or len(set(texts)) != len(texts)
                    or not selected_choice
                ):
                    form.add_error(
                        None,
                        "Add at least two different choices and select the correct answer.",
                    )
                else:
                    # Existing file paths must come from this question, never arbitrary POST paths.
                    allowed_images = (
                        {c.get("image") for c in choices_for(question)}
                        if question
                        else set()
                    )
                    for choice in choices:
                        upload = request.FILES.get(
                            "choice_image_" + choice["source_index"]
                        )
                        if upload:
                            from django.core.files.images import get_image_dimensions

                            try:
                                valid_image = bool(get_image_dimensions(upload)[0])
                                upload.seek(0)
                            except Exception:
                                valid_image = False
                            if not valid_image or upload.size > 10_000_000:
                                form.add_error(
                                    None, "Use a valid choice image smaller than 10 MB."
                                )
                                break
                            if not choice["description"].strip():
                                form.add_error(
                                    None, "Add a description for each choice image."
                                )
                                break
                            suffix = os.path.splitext(upload.name)[1].lower()
                            choice["image"] = default_storage.save(
                                f"choice_images/{uuid.uuid4().hex}{suffix}", upload
                            )
                        elif choice["image"] not in allowed_images:
                            choice["image"] = None
                        choice.pop("source_index", None)
                    candidate.correct_answer_text = selected_choice["text"]
                    candidate.choices = [
                        {
                            key: value
                            for key, value in choice.items()
                            if key in {"text", "image", "description"}
                        }
                        for choice in choices
                    ]
            elif not candidate.correct_answer_text:
                form.add_error("correct_answer_text", "Enter the correct answer.")
            elif (
                candidate.question_type == "TF"
                and candidate.correct_answer_text not in ("True", "False")
            ):
                form.add_error("correct_answer_text", "Enter True or False.")
            if not form.errors:
                with transaction.atomic():
                    Exam.objects.select_for_update().get(pk=exam.pk)
                    if StudentExamAttempt.objects.filter(exam=exam).exists():
                        form.add_error(
                            None,
                            "A student has started this exam. Questions are now locked.",
                        )
                    else:
                        candidate.save()
                        messages.success(request, "Question saved.")
                        return (
                            redirect("modify_exam", exam_id=exam.pk)
                            if question
                            else redirect("add_questions", exam_id=exam.pk)
                        )
    return render(
        request,
        "teacherside/add_questions.html",
        {
            "exam": exam,
            "form": form,
            "choices": choices,
            "editing": question,
            "questions": exam.questions.order_by("question_id"),
        },
    )


@teacher_required
@require_POST
def delete_question(request, question_id):
    question = get_object_or_404(
        Question, pk=question_id, exam__created_by=request.user
    )
    with transaction.atomic():
        Exam.objects.select_for_update().get(pk=question.exam_id)
        if StudentExamAttempt.objects.filter(exam=question.exam).exists():
            messages.error(
                request, "Questions are locked because students have started this exam."
            )
        else:
            question.delete()
            if publication_error(question.exam):
                Exam.objects.filter(pk=question.exam_id).update(access_status=False)
            messages.success(request, "Question deleted.")
    return redirect("modify_exam", exam_id=question.exam_id)


@teacher_required
def exam_attempts_list(request, exam_id):
    exam = owned_exam(request, exam_id)
    summary = (
        StudentExamAttempt.objects.filter(exam=exam)
        .values(
            "student__id",
            "student__username",
            "student__first_name",
            "student__last_name",
            "student__class_designation",
        )
        .annotate(
            total_attempts=Count("id"),
            best_score=Max("score"),
            avg_score=Avg("score"),
            total_violations=Sum("violation_count"),
        )
    )
    return render(
        request,
        "teacherside/exam_attempts_list.html",
        {"exam": exam, "attempts_summary": summary.order_by("student__username")},
    )


@teacher_required
def student_attempt_detail(request, exam_id, student_id):
    exam = owned_exam(request, exam_id)
    student = get_object_or_404(CustomUser, pk=student_id, role="student")
    attempts = list(
        StudentExamAttempt.objects.filter(exam=exam, student=student).order_by(
            "-attempt_number"
        )
    )
    for attempt in attempts:
        attempt.has_preparation = ExamPreparation.objects.filter(
            session_id=attempt.proctoring_session_id
        ).exists()
        attempt.files = ProctoringSessionFiles.objects.filter(
            exam_attempt=attempt
        ).first()
        attempt.violation_type_counts = violation_counts_for_session(attempt.files)
        attempt.video_filenames = (
            [os.path.basename(path) for path in attempt.files.violation_videos]
            if attempt.files
            else []
        )
        attempt.model_display = {
            "cheating": "Cheating",
            "non_cheating": "Non-cheating",
        }.get(attempt.prediction_label, "Unavailable")
        attempt.confidence_percent = (
            attempt.prediction_confidence * 100
            if attempt.prediction_confidence is not None
            else None
        )
    return render(
        request,
        "teacherside/student_attempt_detail.html",
        {"exam": exam, "student": student, "attempts": attempts},
    )


@teacher_required
def diagnostics(request, session_id):
    prep = get_object_or_404(
        ExamPreparation, session_id=session_id, exam__created_by=request.user
    )
    from camera.registry import diagnostics as read_diagnostics

    if request.GET.get("format") == "json":
        result = read_diagnostics(prep.session_id)
        return JsonResponse(result)
    return render(request, "teacherside/diagnostics.html", {"prep": prep})


@teacher_required
def download_session_file(request, session_id, file_type, index=None):
    """
    Download a specific file from a proctoring session
    file_type: 'calibration', 'heatmap', 'csv', 'video'
    index: required for 'csv' and 'video' types (0-based)
    """
    try:
        session_files = ProctoringSessionFiles.objects.get(session_id=session_id)
    except ProctoringSessionFiles.DoesNotExist:
        raise Http404("Session files not found")

    if (
        not session_files.exam_attempt
        or session_files.exam_attempt.exam.created_by_id != request.user.pk
    ):
        raise Http404("Session not found")
    file_path = None
    filename = None

    if file_type == "calibration":
        file_path = session_files.get_calibration_path()
        filename = "eye_calibration.json"

    elif file_type == "heatmap":
        file_path = session_files.get_heatmap_path()
        filename = f"heatmap_{session_id}.png"

    elif file_type == "csv":
        if index is None:
            raise Http404("CSV index is required")
        csv_paths = session_files.get_all_csv_paths()
        if not csv_paths or not (0 <= index < len(csv_paths)):
            raise Http404("CSV file not found at specified index")
        file_path = csv_paths[index]
        filename = os.path.basename(file_path) if file_path else None

    elif file_type == "video":
        if index is None:
            raise Http404("Video index is required")
        video_paths = session_files.get_all_video_paths()
        if not video_paths or not (0 <= index < len(video_paths)):
            raise Http404("Video file not found at specified index")
        file_path = video_paths[index]
        filename = os.path.basename(file_path) if file_path else None

    else:
        raise Http404("Invalid file type")

    if not file_path or not os.path.exists(file_path):
        raise Http404("File not found on server")

    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"

    # Open and serve the file
    try:
        file_handle = open(file_path, "rb")
        response = FileResponse(file_handle, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
    except IOError:
        raise Http404("Error reading file")


@teacher_required
def view_session_file(request, session_id, file_type, index=None):
    """View a session file in the browser, including video clips."""
    try:
        session_files = ProctoringSessionFiles.objects.get(session_id=session_id)
    except ProctoringSessionFiles.DoesNotExist:
        raise Http404("Session files not found")

    if (
        not session_files.exam_attempt
        or session_files.exam_attempt.exam.created_by_id != request.user.pk
    ):
        raise Http404("Session not found")
    file_path = None
    content_type = "text/plain"

    if file_type == "calibration":
        file_path = session_files.get_calibration_path()
        content_type = "application/json"

    elif file_type == "heatmap":
        file_path = session_files.get_heatmap_path()
        content_type = "image/png"

    elif file_type == "csv":
        if index is None:
            raise Http404("CSV index is required")
        csv_paths = session_files.get_all_csv_paths()
        if not csv_paths or not (0 <= index < len(csv_paths)):
            raise Http404("CSV file not found")
        file_path = csv_paths[index]
        content_type = "text/csv"

    elif file_type == "video":
        if index is None:
            raise Http404("Video index is required")
        video_paths = session_files.get_all_video_paths()
        if not video_paths or not (0 <= index < len(video_paths)):
            raise Http404("Video file not found")
        file_path = video_paths[index]
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or "video/mp4"

    else:
        raise Http404("Invalid file type for viewing")

    if not file_path or not os.path.exists(file_path):
        raise Http404("File not found on server")

    try:
        file_handle = open(file_path, "rb")
        response = FileResponse(file_handle, content_type=content_type)
        response["Content-Disposition"] = (
            f'inline; filename="{os.path.basename(file_path)}"'
        )
        return response
    except IOError:
        raise Http404("Error reading file")


@teacher_required
def download_all_session_files(request, session_id):
    """Create a ZIP file with all session files for download"""
    try:
        session_files = ProctoringSessionFiles.objects.get(session_id=session_id)
    except ProctoringSessionFiles.DoesNotExist:
        raise Http404("Session files not found")

    if (
        not session_files.exam_attempt
        or session_files.exam_attempt.exam.created_by_id != request.user.pk
    ):
        raise Http404("Session not found")
    # Create in-memory ZIP file
    zip_buffer = BytesIO()
    file_count = 0

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add calibration JSON
        if session_files.calibration_file:
            path = session_files.get_calibration_path()
            if path and os.path.exists(path):
                zip_file.write(path, os.path.basename(path))
                file_count += 1

        # Add heatmap
        if session_files.heatmap_image:
            path = session_files.get_heatmap_path()
            if path and os.path.exists(path):
                zip_file.write(path, os.path.basename(path))
                file_count += 1

        # Add all CSVs
        for csv_path in session_files.get_all_csv_paths():
            if csv_path and os.path.exists(csv_path):
                zip_file.write(csv_path, os.path.basename(csv_path))
                file_count += 1

        # Add all videos
        for video_path in session_files.get_all_video_paths():
            if video_path and os.path.exists(video_path):
                zip_file.write(video_path, os.path.basename(video_path))
                file_count += 1

    if file_count == 0:
        raise Http404("No files found for this session")

    # Prepare response
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = (
        f'attachment; filename="session_{session_id}_files.zip"'
    )

    return response
