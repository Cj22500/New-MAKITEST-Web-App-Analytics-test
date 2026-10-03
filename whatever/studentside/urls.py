from django.urls import path, include
from . import views

urlpatterns = [
    path('start-exam/', views.start_exam, name='start_exam'),
    path('reset-setup/', views.reset_preparation, name='reset_preparation'),
    path('attempt/<int:attempt_id>/state/', views.attempt_state, name='attempt_state'),
    path('attempt/<int:attempt_id>/answers/', views.save_exam_answers, name='save_exam_answers'),
    path('', views.student_home, name='student_home'),
    path('camera/', include('camera.urls')),
    path('exam_details/', views.exam_details, name='exam_details'),
    path('exam_session/', views.exam_session, name='exam_session'),
    path('save-tracking-thresholds/', views.save_tracking_thresholds, name='save_tracking_thresholds'),
    path('submit_exam/', views.submit_exam, name='submit_exam'),
    path('exam_results/<int:attempt_id>/', views.exam_results, name='exam_results'),
    path('my_scores/', views.my_scores, name='my_scores'),
]