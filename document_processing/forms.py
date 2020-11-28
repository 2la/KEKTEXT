from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from document_processing.models import File


class FileForm(forms.ModelForm):

    class Meta:
        model = File
        fields = ('file',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Загрузить'))




