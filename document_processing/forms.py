from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django import forms

from document_processing.models import File


class MultipleFileUploadForm(forms.ModelForm):
    origin_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=True,
        label='Файлы'
    )

    class Meta:
        model = File
        fields = ('origin_file',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Загрузить'))

    def save(self, *args, **kwargs):
        commit = kwargs.get('commit', True)
        self.instance.origin_file, *files = self.files.getlist('origin_file')
        first_file = super().save(*args, **kwargs)
        other_files = [File(origin_file=file) for file in files]
        if commit:
            for file in other_files:
                file.save()
        return [first_file, *other_files]


class TextboxForm(forms.ModelForm):
    processed = forms.CharField(widget=forms.Textarea(attrs={'readonly': True}), required=False)

    class Meta:
        model = File
        fields = ('origin_text',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('origin_text'), Column('processed')),
            Row(Submit('submit', 'Загрузить')),
        )


