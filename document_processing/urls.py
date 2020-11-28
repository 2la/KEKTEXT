from django.urls import path
from document_processing import views

app_name = 'document_processing'

urlpatterns = [
    path('', views.MultipleFileUploadView.as_view(), name='load_file'),
    path('processed-files/', views.Processed.as_view(), name='processed_file'),
    path('progress/<int:pk>', views.get_file_progress, name='get_file_progress'),
]
