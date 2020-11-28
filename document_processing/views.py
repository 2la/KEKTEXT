import json

from django.http import HttpResponse
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from document_processing.forms import MultipleFileUploadForm
from document_processing.models import File
from document_processing.tasks import process_file


class MultipleFileUploadView(CreateView):
    form_class = MultipleFileUploadForm
    template_name = 'document_processing/upload-files.html'

    def get_success_url(self):
        return '/'

    def form_valid(self, form):
        print('FORM IS VALID')
        result = super().form_valid(form)
        for file in self.object:
            process_file(file_id=file.pk)
        print('FILE SENT TO PROCESSING')
        return result


# class ProcessedFile(DetailView):
#     model = File
#     template_name = 'document_processing/processed-file.html'


class Processed(ListView):
    model = File
    template_name = 'document_processing/processed-file.html'
    context_object_name = 'files'

    def get_queryset(self):
        return File.objects.all()


def get_file_progress(request, pk):
    file = File.objects.get(pk=pk)
    return HttpResponse(json.dumps({
        'progress': file.progress,
    }), content_type="application/json")






