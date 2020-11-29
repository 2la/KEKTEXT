import mimetypes
import os
from time import sleep

from background_task import background

from doc_work.doc_work import Document
from document_processing.models import File
from image2text import image_to_text
from text_processor import TextProcessor


text_params = {
    'start': '307 УК РФ предупрежден',
    'stop': 'Перед началом, в ходе либо по окончании',
    'fio': 'Фамилия, имя, отчество',
}


def get_output_field(file):
    output_name = file.processed_file.storage.get_available_name(file.short_origin_name)
    output_name = os.path.join(file.processed_file.field.upload_to, output_name)
    return file.processed_file.storage.path(output_name)


def get_input_type(file):
    try:
        mime = mimetypes.MimeTypes().guess_type(file.origin_file.path)[0] or ''
    except ValueError:
        return File.InputTypes.TEXTBOX
    if mime.startswith('image'):
        return File.InputTypes.IMAGE
    if mime.startswith('text'):
        return File.InputTypes.TXT
    if file.short_origin_name.split('.')[1] == 'docx':
        return File.InputTypes.DOCX
    if file.short_origin_name.split('.')[1] == 'pdf':
        return File.InputTypes.PDF
    return ''


@background
def process_file(file_id):
    file = File.objects.get(pk=file_id)
    print(file)
    try:
        origin_path = file.origin_file.path
    except ValueError:
        origin_path = None
    file.input_type = get_input_type(file)
    print(file.input_type)
    file.progress += 10
    file.save()

    sleep(.5)
    file.progress += 10
    file.save()



    document = None
    if file.input_type == File.InputTypes.IMAGE:
        text = image_to_text(origin_path)
    elif file.input_type == File.InputTypes.TEXTBOX:
        text = file.origin_text
    else:
        document = Document(origin_path, text_params)
        text = document.parse()
    # file.progress += 50
    file.progress += 20
    file.save()

    sleep(.5)
    file.progress += 10
    file.save()
    sleep(.5)
    file.progress += 10
    file.save()

    text_processor = TextProcessor()
    processed_text = text_processor.process(text)
    # file.progress += 30
    file.progress += 20
    file.save()

    sleep(.5)
    file.progress += 10
    file.save()

    if file.input_type in (File.InputTypes.IMAGE, File.InputTypes.TEXTBOX):
        file.processed_text = processed_text
    else:
        if document is None:
            raise ValueError('Error with document')
        output_name = get_output_field(file)
        document.change_text(processed_text)
        document.save(output_name)
        file.processed_file = output_name
    sleep(.5)
    file.progress = 100
    file.save()
    print(file)
