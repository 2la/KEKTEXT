import os
import docx


class Parser:
    """
    Class 'Parser' gets data_file_path
    It has 1 method:
        - docx_parser() read file 'data_file_path' and returns text
    """
    def __init__(self, data_file_path):
        self.data_file_path = data_file_path
        self.filetype = data_file_path.rsplit('.')[-1]

    def docx_parser(self):
        doc = docx.Document(self.data_file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text

    def parse(self):
        if self.filetype == 'docx':
            return self.docx_parser()


if __name__ == '__main__':
    file_path = os.path.join('data', 'file.docx')
    parser = Parser(file_path)
    txt = parser.parse()
    print(txt)
