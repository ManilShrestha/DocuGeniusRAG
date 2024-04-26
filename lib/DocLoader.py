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
        """This method will chunkify the document into chunks that do not exceed the specified number of characters and end at the end of a sentence.

        Args:
            chunk_size (int, optional): The maximum number of characters per chunk. Defaults to 1000.
        """
        import re
        # Initialize variables
        chunks = []
        start = 0
        
        # Regular expression to find sentence boundaries
        while start < len(self.doc_text):
            # Check if remaining text is less than the chunk size
            if len(self.doc_text) - start <= chunk_size:
                chunks.append(self.doc_text[start:])
                break
            
            # Find the last sentence ending within the current chunk size
            end = start + chunk_size
            # Search backwards from the chunk end for a sentence boundary
            boundary = re.search(r'[.!?]\s', self.doc_text[start:end])
            
            while boundary is None and end > start:
                end -= 1
                boundary = re.search(r'[.!?]\s', self.doc_text[start:end])
            
            # If no boundary is found within the chunk, force end at chunk_size
            if boundary is None:
                end = start + chunk_size
            else:
                end = start + boundary.end()  # Adjust end to include the space after punctuation
            
            # Append the chunk from start to the new end
            chunks.append(self.doc_text[start:end])
            # Update start to the new end
            start = end
        
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
