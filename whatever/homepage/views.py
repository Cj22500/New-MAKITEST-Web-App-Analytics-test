from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import SignUpForm


def landing_page(request):
    return render(request, "homepage/landing_page.html")


def signup_view(request):
    """Create a student account, then send them to the login page."""
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect("admin_home")
        return redirect(
            "teacher_home" if request.user.role == "teacher" else "student_home"
        )

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.username}.")
            return redirect("login")
    else:
        form = SignUpForm()

    return render(request, "homepage/signup_page.html", {"form": form})


def login_view(request):
    # Only check role if the user is already authenticated
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect("admin_home")
        elif request.user.role == "student":
            return redirect("student_home")
        elif request.user.role == "teacher":
            return redirect("teacher_home")

    # Otherwise, show login form
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if user.role == "teacher" and not user.authorized:
            messages.error(
                request,
                "This teacher account is not authorized yet. Contact an administrator.",
            )
        else:
            auth_login(request, user)

            next_url = request.POST.get("next", "")
            from django.utils.http import url_has_allowed_host_and_scheme

            if next_url and url_has_allowed_host_and_scheme(
                next_url, {request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(next_url)

            if user.is_admin():
                return redirect("admin_home")
            elif user.role == "student":
                return redirect("student_home")
            elif user.role == "teacher":
                return redirect("teacher_home")

            return redirect("landing_page")

    return render(
        request,
        "homepage/login_page.html",
        {
            "form": form,
            "next": request.POST.get("next", request.GET.get("next", "")),
        },
    )


@require_POST
def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been signed out.")
    return redirect(reverse("landing_page"))
