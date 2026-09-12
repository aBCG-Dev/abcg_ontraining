from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('auth/login/', views.CentralObtainAuthToken.as_view(), name='api_login'),
    path('sync/bulk/', views.BulkSyncView.as_view(), name='bulk_sync'),
    path('sync/media/', views.MediaUploadView.as_view(), name='media_sync'),
    path('questions/', views.QuestionListView.as_view(), name='questions_list'),
]
