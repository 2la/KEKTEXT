from django.db import models


class File(models.Model):
    origin_file = models.FileField(upload_to='', null=True)
    origin_mime = models.CharField(max_length=120, blank=True, default='')
    origin_text = models.TextField(blank=True, default='')
    processed_text = models.TextField()
    progress = models.PositiveSmallIntegerField(default=0)


