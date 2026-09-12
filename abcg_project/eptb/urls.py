from django.urls import path
from . import views

app_name = 'eptb'

urlpatterns = [
    path('', views.eptb_questions, name='questions'),
]