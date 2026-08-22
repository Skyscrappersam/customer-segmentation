from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect


def home(request):
    return redirect("analytics:dashboard")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("analytics/", include("analytics.urls")),
    path("", home, name="home"),
]