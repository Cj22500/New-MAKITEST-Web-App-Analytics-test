from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def role_required(role, require_authorized=False):
    def decorate(view):
        @login_required
        @wraps(view)
        def guarded(request, *args, **kwargs):
            role_mismatch = request.user.role != role and not (
                role == "admin" and request.user.is_admin()
            )
            if role_mismatch or (
                require_authorized and not request.user.authorized
            ):
                return HttpResponseForbidden(
                    "This page is not available for your account."
                )
            return view(request, *args, **kwargs)

        return guarded

    return decorate


student_required = role_required("student")
teacher_required = role_required("teacher", require_authorized=True)
admin_required = role_required("admin")
