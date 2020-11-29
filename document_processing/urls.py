from django.urls import path
from document_processing import views

app_name = 'document_processing'

urlpatterns = [
    path('textbox-processing/', views.TextboxProcessingView.as_view(), name='textbox_processing'),
    path('processed-files/', views.FileProcessingView.as_view(), name='processed_file'),
    path('progress/<int:pk>', views.get_file_progress, name='get_file_progress'),
]
