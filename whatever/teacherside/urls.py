from django.urls import path
from . import views

urlpatterns = [
    path('exam/<int:exam_id>/question/<int:question_id>/edit/', views.add_questions, name='edit_question'),
    path('session/<str:session_id>/diagnostics/', views.diagnostics, name='diagnostics'),
    path('', views.teacher_home, name='teacher_home'),
    path('exams/', views.exams_list, name='exams_list'),
    path('create_exam/', views.create_exam, name='create_exam'),
    path('exam/<int:exam_id>/add_questions/', views.add_questions, name='add_questions'),
    path('exam/<int:exam_id>/modify/', views.modify_exam, name='modify_exam'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('students/', views.manage_students, name='manage_students'),
    path('student/<int:user_id>/update-class/', views.update_student_class, name='update_student_class'),
    
    # Proctoring file views
    path('exam/<int:exam_id>/attempts/', views.exam_attempts_list, name='exam_attempts_list'),
    path('exam/<int:exam_id>/student/<int:student_id>/attempts/', views.student_attempt_detail, name='student_attempt_detail'),
    
    # Single file downloads (no index needed)
    path('session/<str:session_id>/download/<str:file_type>/', views.download_session_file, name='download_session_file'),
    path('session/<str:session_id>/view/<str:file_type>/', views.view_session_file, name='view_session_file'),
    
    # List file downloads (with index)
    path('session/<str:session_id>/download/<str:file_type>/<int:index>/', views.download_session_file, name='download_session_file_indexed'),
    path('session/<str:session_id>/view/<str:file_type>/<int:index>/', views.view_session_file, name='view_session_file_indexed'),
    
    # Download all files as ZIP
    path('session/<str:session_id>/download-all/', views.download_all_session_files, name='download_all_session_files'),
]
