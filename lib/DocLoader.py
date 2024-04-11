from abc import ABC, abstractmethod
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


class MasterDocumentLoader(ABC):
    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path
        self.doc_text = ""

    @abstractmethod
    def read_contents(self):
        pass

class PDFDocLoader(MasterDocumentLoader):
    def read_contents(self):
        from pdfminer.high_level import extract_text
        self.doc_text = extract_text(self.doc_path)
        return self.doc_text

class DOCXDocLoader(MasterDocumentLoader):
    def read_contents(self):
        import docx
        doc = docx.Document(self.doc_path)
        self.doc_text = " ".join([para.text for para in doc.paragraphs])
        # Handle table text similarly as shown previously
        return self.doc_text

class PPTXDocLoader(MasterDocumentLoader):
    def read_contents(self):
        import pptx
        prs = pptx.Presentation(self.doc_path)
        self.doc_text = " ".join([run.text for slide in prs.slides for shape in slide.shapes if shape.has_text_frame for paragraph in shape.text_frame.paragraphs for run in paragraph.runs])
        return self.doc_text
