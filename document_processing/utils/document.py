import docx
import pdf2docx


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

    def docx_writer(self, old_text, new_text, new_name):
        p_start = self.text.find(self.text_params['start'])
        p_stop = self.text.find(self.text_params['stop'])
        self.docx