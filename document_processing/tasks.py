import mimetypes

from background_task import background

from document_processing.models import File
from image2text import image_to_text
from text_processor import TextProcessor


@background
def process_file(file_id):
    file = File.objects.get(pk=file_id)
    print('MIME', mimetypes.MimeTypes().guess_type(file.origin_file.path)[0])
    file.origin_mime = mimetypes.MimeTypes().guess_type(file.origin_file.path)[0] or ''
    file.progress += 20
    file.save()

    mime_type, _ = file.origin_mime.split('/')
    if mime_type == 'image':
        text = image_to_text(file.origin_file.path)
    else:
        text = 'привет'

    file.progress += 50
    file.save()

    text_processor = TextProcessor()
    file.processed_text = text_processor.process(text)

    file.progress += 30
    file.save()

    file.save()






