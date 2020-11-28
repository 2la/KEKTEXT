from django.urls import path
from document_processing import views

app_name = 'document_processing'

urlpatterns = [
    path('', views.LoadFileView.as_view(), name='load_file'),
    path('processed-file/<int:pk>', views.ProcessedFile.as_view(), name='processed_file'),
]
