from django.contrib import admin

from .models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'origin_file', 'origin_mime', 'processed_file', 'progress', 'origin_text', 'processed_text')
