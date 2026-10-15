from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended User model with role-based access."""
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='student',
        help_text='User role for access control'
    )

    authorized = models.BooleanField(
        default=False,
        help_text='Whether this account is authorized to use teacher features',
    )
    
    class_designation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Class or grade designation (e.g., Grade 10-A, CS101)'
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_student(self):
        return self.role == 'student'
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser