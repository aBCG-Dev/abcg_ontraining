from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("questions.urls")),  # This correctly directs clean root traffic to our questions app!
    path("eptb/", include("eptb.urls")),
]