import pyocr
from PIL import Image
import mimetypes


def is_image(file_path):
    try:
        Image.open(file_path)
    except OSError:
        return False
    return True


def image_to_text(img_path) -> str:
    T = pyocr.get_available_tools()[0]
    L = 'rus'
    return T.image_to_string(
        Image.open(img_path),
        lang=L,
        builder=pyocr.builders.TextBuilder()
    )
