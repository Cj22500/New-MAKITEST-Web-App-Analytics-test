"""
URL configuration for whatever project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
]

# Session evidence is served exclusively by authenticated, owner-scoped views.
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.static import serve


@login_required
def uploaded_image(request, path):
    if path.split("/")[0] not in {"question_images", "choice_images", "answer_images"}:
        raise Http404("File not found")
    return serve(request, path, document_root=settings.MEDIA_ROOT)


urlpatterns += [path("media/<path:path>", uploaded_image, name="uploaded_image")]
