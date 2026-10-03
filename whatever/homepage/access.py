from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def role_required(role):
    def decorate(view):
        @login_required
        @wraps(view)
        def guarded(request, *args, **kwargs):
            if request.user.role != role:
                return HttpResponseForbidden(
                    "This page is not available for your account."
                )
            return view(request, *args, **kwargs)

        return guarded

    return decorate


student_required = role_required("student")
teacher_required = role_required("teacher")
