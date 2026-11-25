from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def health_check(request):
    """Lightweight process-level health endpoint; database health is tested separately."""
    return JsonResponse({"status": "ok", "service": "dwellora-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
]
