from django.shortcuts import render, redirect, get_object_or_404
from .create_exam_forms import ExamForm, QuestionForm
from django.contrib import messages
from .models import Exam, Question
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from homepage.models import CustomUser
from django.db.models import Q, Count, Max, Avg
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from studentside.models import StudentExamAttempt, ProctoringSessionFiles
from django.contrib.auth.decorators import login_required, user_passes_test
import os
import time
import mimetypes
import zipfile
import json
from io import BytesIO

from .analytics_utils import (
    compute_aggregate_analytics,
    predict_suspicion_for_attempt,
    parse_session_csv,
    get_model_and_features
)


def is_teacher_or_admin(user):
    return user.is_authenticated and (user.role in ['teacher', 'admin'] or user.is_staff or user.is_superuser)


# Create your views here.
def teacher_home(request):
    return render(request, 'teacherside/teacher_landing_page.html')

def manage_students(request):
    """View to list and search students with their class designations."""
    search_query = request.GET.get('search', '')
    
    # Get all students
    students = CustomUser.objects.filter(role='student')
    
    # Apply search filter if query exists
    if search_query:
        students = students.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(class_designation__icontains=search_query)
        )
    
    # Order by username
    students = students.order_by('username')
    
    context = {
        'students': students,
        'search_query': search_query,
        'total_count': CustomUser.objects.filter(role='student').count(),
        'filtered_count': students.count()
    }
    
    return render(request, 'teacherside/manage_students.html', context)

def update_student_class(request, user_id):
    """View to update a student's class designation."""
    if request.method == 'POST':
        student = get_object_or_404(CustomUser, id=user_id, role='student')
        class_designation = request.POST.get('class_designation', '').strip()
        
        student.class_designation = class_designation
        student.save()
        
        messages.success(request, f"Class designation updated for {student.username}")
        return redirect('manage_students')
    
    return redirect('manage_students')

def create_exam(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user  # Manually set the creator
            exam.save()
            return redirect('add_questions', exam_id=exam.exam_id)
        else:
            messages.error(request, "There was an error creating the exam. Please check the form for errors.")
            return render(request, 'teacherside/create_exam.html', {'form': form})
    else:
        form = ExamForm()
    return render(request, 'teacherside/create_exam.html', {'form': form})

def exams_list(request):
    exams = Exam.objects.all().order_by('-created_at')
    return render(request, 'teacherside/exams_list.html', {'exams': exams})

def add_questions(request, exam_id):
    exam = Exam.objects.get(exam_id=exam_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            
            # Handle MCQ choices from dynamic form fields
            if question.question_type == 'MCQ':
                choices = []
                choice_num = 1
                correct_choice_num = request.POST.get('correct_choice')
                
                # Collect all choice fields
                while f'choice_text_{choice_num}' in request.POST:
                    choice_text = request.POST.get(f'choice_text_{choice_num}')
                    choice_image = request.FILES.get(f'choice_image_{choice_num}')
                    
                    if choice_text:
                        choice_data = {
                            'text': choice_text,
                            'image': None
                        }
                        
                        # Handle choice image upload to media storage
                        if choice_image:
                            # Create a unique filename to avoid conflicts
                            timestamp = int(time.time() * 1000)
                            ext = os.path.splitext(choice_image.name)[1]
                            filename = f'choice_images/exam_{exam_id}_choice_{choice_num}_{timestamp}{ext}'
                            # Save the file
                            path = default_storage.save(filename, ContentFile(choice_image.read()))
                            choice_data['image'] = path
                        
                        choices.append(choice_data)
                        
                        # Set correct answer text if this choice is marked as correct
                        if correct_choice_num and int(correct_choice_num) == choice_num:
                            question.correct_answer_text = choice_text
                    
                    choice_num += 1
                
                question.choices = json.dumps(choices)
                
                # Validate that a correct answer was selected
                if not question.correct_answer_text:
                    messages.error(request, "Please select which choice is the correct answer.")
                    return render(request, 'teacherside/add_questions.html', {
                        'form': form,
                        'exam': exam,
                        'questions': Question.objects.filter(exam=exam).order_by('created_at')
                    })
            
            question.save()
            messages.success(request, "Question added successfully!")
            return redirect('add_questions', exam_id=exam_id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = QuestionForm()
    
    # Get existing questions for this exam
    questions = Question.objects.filter(exam=exam).order_by('created_at')
    
    return render(request, 'teacherside/add_questions.html', {
        'form': form,
        'exam': exam,
        'questions': questions
    })

def modify_exam(request, exam_id):
    exam = Exam.objects.get(exam_id=exam_id)
    
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam details updated successfully!")
            return redirect('modify_exam', exam_id=exam_id)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        # Convert timelimit back to minutes for display
        initial_data = {
            'timelimit': int(exam.timelimit.total_seconds() / 60) if exam.timelimit else 60
        }
        form = ExamForm(instance=exam, initial=initial_data)
    
    questions = Question.objects.filter(exam=exam).order_by('created_at')
    
    # Parse JSON choices for each MCQ question
    for question in questions:
        if question.question_type == 'MCQ' and question.choices:
            try:
                question.choices = json.loads(question.choices) if isinstance(question.choices, str) else question.choices
            except:
                question.choices = []
    
    return render(request, 'teacherside/modify_exam.html', {
        'exam': exam,
        'form': form,
        'questions': questions
    })

def delete_question(request, question_id):
    if request.method == 'POST':
        question = Question.objects.get(question_id=question_id)
        exam_id = question.exam.exam_id
        question.delete()
        messages.success(request, "Question deleted successfully!")
        return redirect('modify_exam', exam_id=exam_id)
    return redirect('exams_list')


# Proctoring Session File Views

def exam_attempts_list(request, exam_id):
    """List all students who attempted a specific exam"""
    exam = get_object_or_404(Exam, exam_id=exam_id)
    
    # Get all attempts for this exam with related data
    attempts_summary = StudentExamAttempt.objects.filter(exam=exam).values(
        'student__id',
        'student__username', 
        'student__first_name',
        'student__last_name',
        'student__class_designation'
    ).annotate(
        total_attempts=Count('id'),
        best_score=Max('score'),
        avg_score=Avg('score'),
        avg_suspicion=Avg('suspicion_score'),
        total_violations=Count('violation_count')
    ).order_by('student__username')
    
    context = {
        'exam': exam,
        'attempts_summary': attempts_summary,
    }
    
    return render(request, 'teacherside/exam_attempts_list.html', context)


def student_attempt_detail(request, exam_id, student_id):
    """Show all attempts by a specific student for an exam"""
    exam = get_object_or_404(Exam, exam_id=exam_id)
    student = get_object_or_404(CustomUser, id=student_id, role='student')
    
    # Get all attempts by this student for this exam
    attempts = StudentExamAttempt.objects.filter(
        exam=exam, 
        student=student
    ).order_by('-attempt_number')
    
    # Attach session files to each attempt
    for attempt in attempts:
        if attempt.proctoring_session_id:
            try:
                attempt.files = ProctoringSessionFiles.objects.get(
                    session_id=attempt.proctoring_session_id
                )
            except ProctoringSessionFiles.DoesNotExist:
                attempt.files = None
        else:
            attempt.files = None
    
    context = {
        'exam': exam,
        'student': student,
        'attempts': attempts,
    }
    
    return render(request, 'teacherside/student_attempt_detail.html', context)


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
    
    file_path = None
    filename = None
    
    if file_type == 'calibration':
        file_path = session_files.get_calibration_path()
        filename = 'eye_calibration.json'
    
    elif file_type == 'heatmap':
        file_path = session_files.get_heatmap_path()
        filename = f'heatmap_{session_id}.png'
    
    elif file_type == 'csv':
        if index is None:
            raise Http404("CSV index is required")
        csv_paths = session_files.get_all_csv_paths()
        if not csv_paths or not (0 <= index < len(csv_paths)):
            raise Http404("CSV file not found at specified index")
        file_path = csv_paths[index]
        filename = os.path.basename(file_path) if file_path else None
    
    elif file_type == 'video':
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
        content_type = 'application/octet-stream'
    
    # Open and serve the file
    try:
        file_handle = open(file_path, 'rb')
        response = FileResponse(file_handle, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except IOError:
        raise Http404("Error reading file")


def view_session_file(request, session_id, file_type, index=None):
    """View file in browser (for images, JSON, CSV)"""
    try:
        session_files = ProctoringSessionFiles.objects.get(session_id=session_id)
    except ProctoringSessionFiles.DoesNotExist:
        raise Http404("Session files not found")
    
    file_path = None
    content_type = 'text/plain'
    
    if file_type == 'calibration':
        file_path = session_files.get_calibration_path()
        content_type = 'application/json'
    
    elif file_type == 'heatmap':
        file_path = session_files.get_heatmap_path()
        content_type = 'image/png'
    
    elif file_type == 'csv':
        if index is None:
            raise Http404("CSV index is required")
        csv_paths = session_files.get_all_csv_paths()
        if not csv_paths or not (0 <= index < len(csv_paths)):
            raise Http404("CSV file not found")
        file_path = csv_paths[index]
        content_type = 'text/csv'
    
    else:
        raise Http404("Invalid file type for viewing")
    
    if not file_path or not os.path.exists(file_path):
        raise Http404("File not found on server")
    
    try:
        file_handle = open(file_path, 'rb')
        response = FileResponse(file_handle, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        return response
    except IOError:
        raise Http404("Error reading file")


def download_all_session_files(request, session_id):
    """Create a ZIP file with all session files for download"""
    try:
        session_files = ProctoringSessionFiles.objects.get(session_id=session_id)
    except ProctoringSessionFiles.DoesNotExist:
        raise Http404("Session files not found")
    
    # Create in-memory ZIP file
    zip_buffer = BytesIO()
    file_count = 0
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
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
    response = HttpResponse(zip_buffer.getvalue(), content_type='attachment; filename="session_%s_files.zip"' % session_id)
    response['Content-Disposition'] = f'attachment; filename="session_{session_id}_files.zip"'
    
    return response


# ==========================================
# Comprehensive Suspicious Behavior Analytics Views
# ==========================================

@login_required
@user_passes_test(is_teacher_or_admin)
def analytics_dashboard(request):
    """
    Main Suspicious Behavior Analytics Dashboard page.
    Provides high-level KPIs, risk distribution, violation breakdowns,
    and filterable list of student exam attempts with ML model prediction results.
    """
    selected_exam_id = request.GET.get('exam_id')
    selected_risk = request.GET.get('risk')
    search_q = request.GET.get('search', '').strip()

    exams = Exam.objects.all().order_by('-created_at')
    attempts = StudentExamAttempt.objects.select_related('student', 'exam').order_by('-completed_at', '-id')

    # Apply filters
    if selected_exam_id:
        attempts = attempts.filter(exam_id=selected_exam_id)

    if search_q:
        attempts = attempts.filter(
            Q(student__username__icontains=search_q) |
            Q(student__first_name__icontains=search_q) |
            Q(student__last_name__icontains=search_q) |
            Q(exam__title__icontains=search_q)
        )

    # Build SessionFiles mapping
    session_ids = [a.proctoring_session_id for a in attempts if a.proctoring_session_id]
    sfiles_list = ProctoringSessionFiles.objects.filter(session_id__in=session_ids)
    session_files_map = {sf.session_id: sf for sf in sfiles_list}

    # Attach predictions & files
    attempt_list = []
    for attempt in attempts:
        sf = session_files_map.get(attempt.proctoring_session_id)
        pred = predict_suspicion_for_attempt(attempt, sf)

        # Risk level determination
        score = attempt.suspicion_score or 0.0
        if score >= 50.0 or attempt.violation_count >= 5 or pred['is_suspicious']:
            risk_level = 'High'
        elif score >= 20.0 or attempt.violation_count >= 2:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'

        # Filter by risk level if selected
        if selected_risk and risk_level.lower() != selected_risk.lower():
            continue

        attempt_list.append({
            'attempt': attempt,
            'prediction': pred,
            'risk_level': risk_level,
            'session_files': sf,
        })

    # Compute aggregate metrics
    metrics = compute_aggregate_analytics(attempts, session_files_map)

    model, feature_cols = get_model_and_features()

    context = {
        'exams': exams,
        'selected_exam_id': selected_exam_id,
        'selected_risk': selected_risk,
        'search_q': search_q,
        'attempt_list': attempt_list,
        'metrics': metrics,
        'model_loaded': model is not None,
        'feature_count': len(feature_cols) if feature_cols else 0,
    }

    return render(request, 'teacherside/analytics_dashboard.html', context)


@login_required
@user_passes_test(is_teacher_or_admin)
def attempt_analytics_detail(request, attempt_id):
    """
    Detailed analytics page for a specific student exam attempt.
    Includes time-series event log, gaze heatmap, video evidence player,
    and ML model feature breakdown.
    """
    attempt = get_object_or_404(StudentExamAttempt.objects.select_related('student', 'exam'), id=attempt_id)

    session_files = None
    events = []
    if attempt.proctoring_session_id:
        try:
            session_files = ProctoringSessionFiles.objects.get(session_id=attempt.proctoring_session_id)
            csv_paths = session_files.get_all_csv_paths()
            for csv_p in csv_paths:
                if csv_p and os.path.exists(csv_p):
                    events.extend(parse_session_csv(csv_p))
        except ProctoringSessionFiles.DoesNotExist:
            session_files = None

    prediction = predict_suspicion_for_attempt(attempt, session_files)

    # Violation videos list
    video_list = []
    if session_files:
        video_paths = session_files.get_all_video_paths()
        for idx, vp in enumerate(video_paths):
            if vp and os.path.exists(vp):
                video_list.append({
                    'index': idx,
                    'filename': os.path.basename(vp),
                    'download_url': f"/teacherside/session/{attempt.proctoring_session_id}/download/video/{idx}/",
                    'view_url': f"/teacherside/session/{attempt.proctoring_session_id}/view/video/{idx}/",
                })

    context = {
        'attempt': attempt,
        'session_files': session_files,
        'events': events,
        'prediction': prediction,
        'video_list': video_list,
    }

    return render(request, 'teacherside/attempt_analytics_detail.html', context)


@login_required
@user_passes_test(is_teacher_or_admin)
def run_model_inference_ajax(request, attempt_id):
    """
    AJAX endpoint to trigger ML model inference on an attempt's session log files.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=405)

    attempt = get_object_or_404(StudentExamAttempt, id=attempt_id)
    session_files = None
    if attempt.proctoring_session_id:
        try:
            session_files = ProctoringSessionFiles.objects.get(session_id=attempt.proctoring_session_id)
        except ProctoringSessionFiles.DoesNotExist:
            pass

    prediction = predict_suspicion_for_attempt(attempt, session_files)

    return JsonResponse({
        'status': 'success',
        'attempt_id': attempt.id,
        'prediction': prediction,
    })
