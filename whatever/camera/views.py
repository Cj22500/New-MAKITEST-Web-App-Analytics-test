from django.shortcuts import get_object_or_404, redirect, render
from homepage.access import student_required
from studentside.lifecycle import eligibility_error
from studentside.models import ExamPreparation


@student_required
def home(request):
    prep = get_object_or_404(
        ExamPreparation.objects.select_related("exam"),
        pk=request.session.get("preparation_id"),
        student=request.user,
    )
    if eligibility_error(prep.exam, request.user):
        return redirect("student_home")
    return render(request, "camera/home.html", {"prep": prep, "exam": prep.exam})
