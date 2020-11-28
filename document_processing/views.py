from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView

from document_processing.forms import FileForm
from document_processing.models import File
from document_processing.tasks import process_file


class LoadFileView(CreateView):
    form_class = FileForm
    template_name = 'document_processing/load-file.html'

    def get_success_url(self):
        return reverse('document_processing:processed_file', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        print('FORM IS VALID')
        result = super().form_valid(form)
        process_file(file_id=self.object.pk)
        print('FILE SENT TO PROCESSING')
        return result


class ProcessedFile(DetailView):
    model = File
    template_name = 'document_processing/processed-file.html'




