from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
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

        print(*self.files.getlist('origin_file'), sep='\n')

        self.instance.origin_file, *files = self.files.getlist('origin_file')
        first_file = super().save(*args, **kwargs)
        print('KEK')
        other_files = [File(origin_file=file) for file in files]
        if commit:
            for file in other_files:
                file.save()
        print([first_file, *other_files])
        return [first_file, *other_files]



# class FileForm(forms.ModelForm):
#     image = forms.ImageField(widget=forms.FileInput(attrs={'multiple': True}), required=True)
#
#     class Meta:
#         model = File
#         fields = ('file',)
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.add_input(Submit('submit', 'Загрузить'))
#
#
#     def save(self, *args, **kwargs):
#         # multiple file upload
#         # NB: does not respect 'commit' kwarg
#         file_list = natsorted(self.files.getlist('{}-image'.format(self.prefix)), key=lambda file: file.name)
#
#         self.instance.image = file_list[0]
#         for file in file_list[1:]:
#             ProductImage.objects.create(
#                 product=self.cleaned_data['product'],
#                 image=file,
#                 position=self.cleaned_data['position'],
#             )
#
#         return super().save(*args, **kwargs)




