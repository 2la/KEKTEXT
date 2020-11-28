from background_task import background

from document_processing.models import File
from text_processor import TextProcessor


@background
def process_file(file_id):
    file = File.objects.get(pk=file_id)

    with open(file.file.path) as txt_file:
        text = txt_file.read()

    text_processor = TextProcessor()
    file.processed_text = text_processor.process(text)
    file.save()






