from django.urls import path

from . import views

urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path(
        'teacher/<int:user_id>/authorization/',
        views.set_teacher_authorization,
        name='set_teacher_authorization',
    ),
]