import json

from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import CreateView, ListView, DetailView

from document_processing.forms import MultipleFileUploadForm, TextboxForm
from document_processing.models import File
from document_processing.tasks import process_file
from text_processor import TextProcessor


class TextboxProcessingView(CreateView):
    model = File
    form_class = TextboxForm
    template_name = 'document_processing/textbox_processing.html'
    context_object_name = 'files'
    object_list = None

    def get_success_url(self):
        return reverse('document_processing:textbox', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        text_processor = TextProcessor()
        form.instance.processed_text = text_processor.process(form.cleaned_data['origin_text'])
        return super().form_valid(form)


class TextboxView(DetailView):
    model = File
    template_name = 'document_processing/textbox.html'


class FileProcessingView(CreateView, ListView):
    model = File
    form_class = MultipleFileUploadForm
    template_name = 'document_processing/file_processing.html'
    context_object_name = 'files'

    def get_success_url(self):
        return self.request.path

    def get_queryset(self):
        return File.objects.exclude(input_type=File.InputTypes.TEXTBOX).order_by('-pk')

    def form_valid(self, form):
        result = super().form_valid(form)
        for file in self.object:
            process_file(file_id=file.pk)
        return result


def get_file_progress(request, pk):
    file = File.objects.get(pk=pk)
    try:
        processed_url = file.processed_file.url
    except ValueError:
        processed_url = '#'
    return HttpResponse(json.dumps({
        'progress': file.progress,
        'processed_url': processed_url,
        'processed_name': file.short_processed_name,
    }), content_type="application/json")






