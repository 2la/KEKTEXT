import os
import docx
# import PyPDF2
import pdf2docx
from docx2python import docx2python


class Document:
    """
    Class 'Document' gets data_file_path
    Method 'parse' returns text from 'data_file_path' file
    """
    def __init__(self, data_file_path, text_params):
        self.data_file_path = data_file_path
        self.filetype = data_file_path.rsplit('.')[-1]
        self.text_params = text_params
        self.text = ''
        self.docx = None

    def pdf2docx(self):
        pdf2docx.parse(self.data_file_path, self.data_file_path + '.docx')
        self.data_file_path = self.data_file_path + '.docx'
        self.filetype = 'docx'
        return None

    def docx_parser(self):
        doc = docx.Document(self.data_file_path)
        self.docx = doc
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        self.text = text

    # def pdf_parser(self):
    #     doc = PyPDF2.PdfFileReader(open(self.data_file_path, 'rb'))
    #     page = doc.getPage(0)
    #     text = page.extractText().encode('utf-8')
    #     self.text = text

    def txt_parser(self):
        text = open(self.data_file_path, 'r', encoding='utf-8').read()
        self.text = text

    def parse(self, remove_wrap=True, clear_paragraph=True, ignore_text_params=False, void=True):
        if self.filetype == 'docx':
            self.docx_parser()
        elif self.filetype == 'pdf':
            self.pdf2docx()
            self.docx_parser()
            # self.pdf_parser()
        elif self.filetype == 'txt':
            self.txt_parser()
        if remove_wrap:
            self.text = self.text.replace('-\n', '')
        if clear_paragraph:
            self.text = self.text.replace(' \n', '\n').replace('\n', ' ').replace('\t', '\n')
        if not ignore_text_params:
            p_start = self.text.find(self.text_params['start'])
            p_stop = self.text.find(self.text_params['stop'])
            print(f'p_start: {p_start}\np_stop:  {p_stop}')
            self.text = self.text[p_start:p_stop]
        if void:
            return None
        else:
            return self.text

    # def find_text(self):
    #     self.parse()
    #     p_start = self.text.find(self.text_params['start'])
    #     p_stop = self.text.find(self.text_params['stop'])
    #     print(f'p_start: {p_start}\np_stop:  {p_stop}')
    #     return self.text[p_start:p_stop]

    def docx_writer(self, old_text, new_text, new_name):
        p_start = self.text.find(self.text_params['start'])
        p_stop = self.text.find(self.text_params['stop'])
        self.docx


if __name__ == '__main__':
    text_params = {'start': 'По прибытию на станцию Омск', #'307 УК РФ предупрежден',
                   'stop': 'от 8 000 до 10 000 рублей' #'Перед началом, в ходе либо по окончании'
                   }
    file_path = os.path.join('data', 'file3.pdf.docx')
    d = Document(file_path, text_params)
    txt = d.parse(void=False, ignore_text_params=False)
    # txt = d.find_text()
    print(txt)
