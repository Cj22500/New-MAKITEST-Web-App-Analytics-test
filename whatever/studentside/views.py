from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from teacherside.models import Exam
import os
from .models import StudentExamAttempt, StudentAnswer, ProctoringSessionFiles
import heatmap_feature_extractor as hfe
import json

# Every student page sits behind a login: an exam session has to be attributable
# to a named student, and the proctoring log is worthless if it is not.
@login_required
def student_home(request):
    # Access role directly on the user
    if not request.user.is_student():
        messages.error(request, 'Access denied: Students only')
        return redirect('landing_page')
    
    # Get exams for the student's class
    student_class = request.user.class_designation
    
    if student_class:
        exams = Exam.objects.filter(class_designation=student_class).order_by('-created_at')
    else:
        exams = []
    
    # Add access information to each exam
    now = timezone.now()
    for exam in exams:
        exam.is_accessible = exam.access_status and exam.deadline > now
        exam.deadline_passed = exam.deadline <= now
        
        # Calculate attempts
        exam.attempts_used = StudentExamAttempt.objects.filter(
            student=request.user,
            exam=exam
        ).count()
        
        if exam.attempt_limit:
            exam.remaining_attempts = exam.attempt_limit - exam.attempts_used
            exam.attempts_exhausted = exam.attempts_used >= exam.attempt_limit
        else:
            exam.remaining_attempts = None  # Unlimited
            exam.attempts_exhausted = False
    
    return render(request, 'studentside/student_landing_page.html', {
        'exams': exams,
        'student_class': student_class,
    })


@login_required
def exam_details(request):
    """Show exam instructions before starting calibration/proctoring."""
    import uuid
    
    exam_id = request.GET.get('exam_id')
    
    if not exam_id:
        messages.error(request, 'No exam specified')
        return redirect('student_home')
    
    try:
        exam = Exam.objects.get(exam_id=exam_id)
    except Exam.DoesNotExist:
        messages.error(request, 'Exam not found')
        return redirect('student_home')
    
    # Check attempt limit
    previous_attempts = StudentExamAttempt.objects.filter(
        student=request.user,
        exam=exam
    ).count()
    
    if exam.attempt_limit and previous_attempts >= exam.attempt_limit:
        messages.error(request, f'You have already used all {exam.attempt_limit} attempt(s) for this exam.')
        return redirect('student_home')
    
    # Calculate remaining attempts for display
    if exam.attempt_limit:
        remaining_attempts = exam.attempt_limit - previous_attempts
    else:
        remaining_attempts = None  # Unlimited
    
    # Store exam_id in session for downstream pages
    request.session['current_exam_id'] = exam_id
    
    # Generate unique proctoring session ID
    proctoring_session_id = uuid.uuid4().hex[:12]
    request.session['proctoring_session_id'] = proctoring_session_id
    
    return render(request, 'studentside/test_exam.html', {
        'exam': exam,
        'attempts_used': previous_attempts,
        'remaining_attempts': remaining_attempts,
        'session_id': proctoring_session_id,
    })


@login_required
def exam_session(request):
    """Display the exam questions for the student to answer WITH continuous proctoring."""
    exam_id = request.session.get('current_exam_id')
    proctoring_session_id = request.session.get('proctoring_session_id')
    
    if not exam_id:
        messages.error(request, 'No exam selected. Please start from the exam details page.')
        return redirect('student_home')
    
    if not proctoring_session_id:
        messages.error(request, 'Proctoring not initialized. Please complete calibration first.')
        return redirect('exam_details') + f'?exam_id={exam_id}'
    
    try:
        exam = Exam.objects.get(exam_id=exam_id)
        
        # Check attempt limit (backup check)
        previous_attempts = StudentExamAttempt.objects.filter(
            student=request.user,
            exam=exam
        ).count()
        
        if exam.attempt_limit and previous_attempts >= exam.attempt_limit:
            messages.error(request, f'You have already used all {exam.attempt_limit} attempt(s) for this exam.')
            return redirect('student_home')
        
        questions = exam.questions.all().order_by('question_id')
        
        # Ensure choices is properly formatted
        for question in questions:
            if question.choices and isinstance(question.choices, str):
                question.choices = json.loads(question.choices)
        
        # Track exam start time (only set once per exam attempt)
        session_key = f'exam_{exam_id}_start_time'
        if session_key not in request.session:
            request.session[session_key] = timezone.now().isoformat()
            
            # CREATE EXAM ATTEMPT NOW (not at submission)
            attempt_number = previous_attempts + 1
            exam_attempt = StudentExamAttempt.objects.create(
                student=request.user,
                exam=exam,
                attempt_number=attempt_number,
                proctoring_session_id=proctoring_session_id,
                proctoring_started_at=timezone.now()
            )
            request.session['current_attempt_id'] = exam_attempt.id
        
        # Calculate remaining time
        start_time = timezone.datetime.fromisoformat(request.session[session_key])
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)
        
        elapsed = (timezone.now() - start_time).total_seconds()
        total_seconds = exam.timelimit.total_seconds()
        remaining_seconds = max(0, int(total_seconds - elapsed))
        
        # If time is up, prevent access
        if remaining_seconds <= 0:
            messages.warning(request, 'Time is up for this exam.')
            # Clear the start time since the exam time has expired
            del request.session[session_key]
            return redirect('student_home')
        
        return render(request, 'studentside/exam_session.html', {
            'exam': exam,
            'questions': questions,
            'remaining_seconds': remaining_seconds,
            'proctoring_session_id': proctoring_session_id,
        })
    except Exam.DoesNotExist:
        messages.error(request, 'Exam not found')
        return redirect('student_home')


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import StudentTrackingThresholds
from web_session_predict import predict_session_files


@login_required
@require_http_methods(["POST"])
def save_tracking_thresholds(request):
    """Save calibrated eye tracking thresholds for the logged-in student."""
    try:
        data = json.loads(request.body)
        thresholds = data.get('thresholds')
        
        if not thresholds:
            return JsonResponse({'success': False, 'error': 'No thresholds provided'})
        
        # Validate that user is a student
        if not request.user.is_student():
            return JsonResponse({'success': False, 'error': 'Only students can save thresholds'})
        
        # Create or update thresholds for this student
        obj, created = StudentTrackingThresholds.objects.update_or_create(
            student=request.user,
            defaults={
                'calibration_up': thresholds.get('up', 0.0),
                'calibration_down': thresholds.get('down', 0.0),
                'calibration_center': thresholds.get('center', 0.0),
                'calibration_left': thresholds.get('left', 0.0),
                'calibration_right': thresholds.get('right', 0.0),
                'calibration_v_center': thresholds.get('v_center', 0.0),
                'iris_boxheight_center': thresholds.get('iris_boxheight_center', 0.0),
                'iris_boxheight_up': thresholds.get('iris_boxheight_up', 0.0),
                'iris_boxheight_down': thresholds.get('iris_boxheight_down', 0.0),
            }
        )
        
        action = "created" if created else "updated"
        return JsonResponse({
            'success': True, 
            'message': f'Thresholds {action} successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def submit_exam(request):
    """Handle exam submission and save answers with proctoring finalization"""
    if request.method != 'POST':
        return redirect('student_home')
    
    exam_id = request.session.get('current_exam_id')
    attempt_id = request.session.get('current_attempt_id')
    
    if not exam_id or not attempt_id:
        messages.error(request, 'No active exam found.')
        return redirect('student_home')
    
    try:
        exam = Exam.objects.get(exam_id=exam_id)
        exam_attempt = StudentExamAttempt.objects.get(id=attempt_id, student=request.user)
        
        # Save answers
        questions = exam.questions.all()
        for question in questions:
            field_name = f'question_{question.question_id}'
            answer_value = request.POST.get(field_name)
            
            if answer_value:
                StudentAnswer.objects.create(
                    student_exam_attempt=exam_attempt,
                    question=question,
                    answer_text=answer_value
                )
        
        # Auto-grade
        grade_exam_attempt(exam_attempt)
        
        # Finalize proctoring
        exam_attempt.completed_at = timezone.now()
        exam_attempt.proctoring_ended_at = timezone.now()
        exam_attempt.save()
        
        # Scan and save session files
        proctoring_session_id = request.session.get('proctoring_session_id')
        if proctoring_session_id:
            session_files = ProctoringSessionFiles.create_or_update_from_session(
                session_id=proctoring_session_id,
                exam_attempt=exam_attempt
            )
            _predict_exam_attempt(exam_attempt, session_files)
        
        # Clear session
        session_key = f'exam_{exam_id}_start_time'
        if session_key in request.session:
            del request.session[session_key]
        if 'current_exam_id' in request.session:
            del request.session['current_exam_id']
        if 'current_attempt_id' in request.session:
            del request.session['current_attempt_id']
        if 'proctoring_session_id' in request.session:
            del request.session['proctoring_session_id']
        
        messages.success(request, f'Exam submitted! Score: {exam_attempt.score}%')
        return redirect('exam_results', attempt_id=exam_attempt.id)
        
    except (Exam.DoesNotExist, StudentExamAttempt.DoesNotExist):
        messages.error(request, 'Exam or attempt not found.')
        return redirect('student_home')


def _predict_exam_attempt(exam_attempt, session_files):
    """Run prediction from the files registered for an exam attempt."""
    if session_files is None:
        exam_attempt.prediction_status = 'unavailable'
        exam_attempt.prediction_error = 'No proctoring session files were found.'
        exam_attempt.save(update_fields=['prediction_status', 'prediction_error'])
        return

    heatmap_path = session_files.get_heatmap_path()
    csv_path = session_files.get_exam_csv_path()

    if csv_path and os.path.isfile(csv_path):
        csv_features = hfe.extract_csv_features(csv_path)
        exam_attempt.violation_count = sum(
            csv_features[f'violation_count_{category}']
            for category in hfe.VIOLATION_CATEGORIES
        )
        exam_attempt.save(update_fields=['violation_count'])

    exam_attempt.prediction_status = 'running'
    exam_attempt.prediction_error = None
    exam_attempt.save(update_fields=['prediction_status', 'prediction_error'])

    try:
        result = predict_session_files(
            heatmap_path=heatmap_path,
            csv_path=csv_path,
            session_directory=session_files.get_full_path(session_files.session_directory),
        )
        exam_attempt.suspicion_score = result['confidence']
        exam_attempt.prediction_label = result['predicted_label']
        exam_attempt.prediction_confidence = result['confidence']
        exam_attempt.probability_cheating = result['probability_cheating']
        exam_attempt.probability_non_cheating = result['probability_non_cheating']
        exam_attempt.prediction_model_version = result['model_version']
        exam_attempt.prediction_artifact = result.get('artifact_path')
        exam_attempt.prediction_status = 'completed'
        exam_attempt.prediction_completed_at = timezone.now()
        exam_attempt.save(update_fields=[
            'suspicion_score',
            'prediction_label', 'prediction_confidence',
            'probability_cheating', 'probability_non_cheating',
            'prediction_model_version', 'prediction_artifact',
            'prediction_status', 'prediction_completed_at',
        ])
    except Exception as error:
        exam_attempt.prediction_status = 'failed'
        exam_attempt.prediction_error = str(error)
        exam_attempt.save(update_fields=['prediction_status', 'prediction_error'])


def grade_exam_attempt(exam_attempt):
    """Auto-grade the exam"""
    questions = exam_attempt.exam.questions.all()
    total_questions = questions.count()
    correct_answers = 0
    
    for question in questions:
        # Parse choices if string
        if question.choices and isinstance(question.choices, str):
            question.choices = json.loads(question.choices)
        
        try:
            student_answer = StudentAnswer.objects.get(
                student_exam_attempt=exam_attempt,
                question=question
            )
            
            if question.question_type == 'MCQ':
                try:
                    selected_index = int(student_answer.answer_text)
                    if 0 <= selected_index < len(question.choices):
                        selected_choice = question.choices[selected_index]
                        if selected_choice.get('text') == question.correct_answer_text:
                            correct_answers += 1
                except (ValueError, IndexError, TypeError):
                    pass
            
            elif question.question_type == 'TF':
                if student_answer.answer_text == question.correct_answer_text:
                    correct_answers += 1
            
            elif question.question_type in ['NUM', 'FIB']:
                if student_answer.answer_text and question.correct_answer_text:
                    if student_answer.answer_text.strip().lower() == question.correct_answer_text.strip().lower():
                        correct_answers += 1
        
        except StudentAnswer.DoesNotExist:
            pass
    
    if total_questions > 0:
        exam_attempt.score = (correct_answers / total_questions) * 100
    else:
        exam_attempt.score = 0
    
    exam_attempt.save()


@login_required
def exam_results(request, attempt_id):
    """Display results"""
    exam_attempt = get_object_or_404(
        StudentExamAttempt, 
        id=attempt_id, 
        student=request.user
    )
    
    answers = exam_attempt.answers.all().select_related('question')
    answer_dict = {answer.question.question_id: answer for answer in answers}
    
    questions_with_answers = []
    for question in exam_attempt.exam.questions.all().order_by('question_id'):
        if question.choices and isinstance(question.choices, str):
            question.choices = json.loads(question.choices)
        
        student_answer = answer_dict.get(question.question_id)
        is_correct = False
        student_answer_text = None
        
        if student_answer:
            student_answer_text = student_answer.answer_text
            
            if question.question_type == 'MCQ':
                try:
                    idx = int(student_answer.answer_text)
                    if 0 <= idx < len(question.choices):
                        choice = question.choices[idx]
                        student_answer_text = choice.get('text')
                        is_correct = (choice.get('text') == question.correct_answer_text)
                except:
                    pass
            elif question.question_type == 'TF':
                is_correct = (student_answer.answer_text == question.correct_answer_text)
            elif question.question_type in ['NUM', 'FIB']:
                if question.correct_answer_text:
                    is_correct = (student_answer.answer_text.strip().lower() == 
                                question.correct_answer_text.strip().lower())
        
        questions_with_answers.append({
            'question': question,
            'student_answer': student_answer_text,
            'is_correct': is_correct
        })
    
    return render(request, 'studentside/exam_results.html', {
        'exam_attempt': exam_attempt,
        'questions_with_answers': questions_with_answers,
    })


@login_required
def my_scores(request):
    """Group the signed-in student's own exam attempts by exam, one directory per exam."""
    attempts = StudentExamAttempt.objects.filter(
        student=request.user
    ).select_related('exam').order_by('-attempt_number', '-id')

    exams = {}
    for attempt in attempts:
        exam = attempt.exam
        if exam.exam_id not in exams:
            exams[exam.exam_id] = {
                'exam': exam,
                'attempts': [],
                'best_score': None,
            }
        group = exams[exam.exam_id]
        group['attempts'].append(attempt)
        if attempt.score is not None and (group['best_score'] is None or attempt.score > group['best_score']):
            group['best_score'] = attempt.score

    exam_groups = sorted(
        exams.values(),
        key=lambda group: group['attempts'][0].id,
        reverse=True
    )

    return render(request, 'studentside/my_scores.html', {
        'exam_groups': exam_groups,
    })
