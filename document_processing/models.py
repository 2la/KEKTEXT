from django.db import models


class File(models.Model):

    class InputTypes(models.TextChoices):
        DOCX = 'docx'
        TXT = 'txt'
        IMAGE = 'image'
        PDF = 'pdf'
        TEXTBOX = 'textbox'

    input_type = models.CharField(max_length=50, choices=InputTypes.choices, blank=True, default='')
    origin_file = models.FileField(upload_to='origins', null=True)
    origin_mime = models.CharField(max_length=120, blank=True, default='')
    origin_text = models.TextField(blank=True, default='')
    processed_text = models.TextField(blank=True, default='')
    processed_file = models.FileField(upload_to='processed', null=True)
    progress = models.PositiveSmallIntegerField(default=0)

    @property
    def short_origin_name(self):
        if self.input_type == self.InputTypes.TEXTBOX:
            return f'{self.origin_text[:50]}...'
        try:
            return self.origin_file.path.split('/')[-1]
        except ValueError:
            return ''

    @property
    def short_processed_name(self):
        if self.input_type == self.InputTypes.TEXTBOX:
            return f'{self.processed_text[:50]}...'
        try:
            return self.processed_file.path.split('/')[-1]
        except ValueError:
            return ''

