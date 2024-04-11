from pdfminer.high_level import extract_text
from abc import ABC, abstractmethod
import docx, pptx 

import os

class DocLoader:
    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path
        self.doc_text = ""

        if not os.path.exists(self.doc_path):
            raise FileNotFoundError(f"File {self.doc_path} does not exist.")
        
        # Determine the correct loader based on the file extension
        _, ext = os.path.splitext(doc_path)
        if ext.lower() == '.pdf':
            self.loader = PDFDocLoader(doc_path)
        elif ext.lower() == '.docx':
            self.loader = DOCXDocLoader(doc_path)
        elif ext.lower() =='.pptx':
            self.loader = PPTXDocLoader(doc_path)
        else:
            raise NotImplementedError(f"No loader implemented for {ext} files.")
        
        self.doc_text = self.loader.read_contents()
    
    def chunkify_document(self, chunk_size=1000):
        """This method will chunkify the document as per the chunk size

        Args:
            chunk_size (int, optional): This is number of characters per chunk. Defaults to 1000.
        """
        chunks = [self.doc_text[i:i+chunk_size] for i in range(0, len(self.doc_text), chunk_size)]
        return chunks
    
    def get_doc_text(self):
        return self.doc_text


class PDFDocLoader():

    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path
    def read_contents(self):
        return extract_text(self.doc_path)

        
class DOCXDocLoader():
    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path

    def read_contents(self):
        doc_text = ""
        # Load the .docx file
        doc = docx.Document(self.doc_path)

        # Read paragraphs and tables
        for para in doc.paragraphs:
            doc_text+=para.text

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    doc_text+=cell.text

        return doc_text
        

class PPTXDocLoader():
    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path

    def read_contents(self):
        doc_text = ""
        prs = pptx.Presentation(self.doc_path)
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            doc_text += run.text

        return doc_text
