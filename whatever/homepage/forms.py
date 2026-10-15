from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class SignUpForm(UserCreationForm):
    """Registration form for site users (restricted to Student/Teacher)."""

    email = forms.EmailField(
        required=True,
        help_text='Use the email address you use for school.',
    )

    class Meta:
        model = CustomUser
        # User details with first name and last name
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2')
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Restrict role choices to Student and Teacher
        self.fields['role'].choices = [
            ('student', 'Student'),
            ('teacher', 'Teacher'),
        ]

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_role(self):
        role = self.cleaned_data['role']
        if role not in ['student', 'teacher']:
            raise forms.ValidationError("Invalid role selection.")
        return role

