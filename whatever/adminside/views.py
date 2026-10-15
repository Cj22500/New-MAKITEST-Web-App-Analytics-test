from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from homepage.access import admin_required
from homepage.models import CustomUser


@admin_required
def admin_home(request):
    teachers = CustomUser.objects.filter(role='teacher').order_by(
        'last_name', 'first_name', 'username'
    )
    return render(request, 'adminside/teacher_authorization.html', {'teachers': teachers})


@admin_required
@require_POST
def set_teacher_authorization(request, user_id):
    authorized_value = request.POST.get('authorized')
    if authorized_value not in {'true', 'false'}:
        messages.error(request, 'Choose whether to authorize this teacher account.')
        return redirect('admin_home')

    teacher = get_object_or_404(CustomUser, pk=user_id, role='teacher')
    teacher.authorized = authorized_value == 'true'
    teacher.save(update_fields=['authorized'])
    status = 'authorized' if teacher.authorized else 'unauthorized'
    messages.success(request, f'{teacher.username} is now {status}.')
    return redirect('admin_home')