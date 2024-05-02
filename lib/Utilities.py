import fitz  # PyMuPDF
from datetime import datetime
import yaml
import unicodedata
import re



# Path to your YAML file
config_file_path = '/home/ms5267@drexel.edu/DocuGeniusRAG/config.yaml'



def normalize_text(text):
    text = unicodedata.normalize('NFKC', text)  # Normalize Unicode characters
    text = text.replace('-\n', '').replace('-\r', '').replace('\n', ' ').replace('\t', ' ')
    # text = ' '.join(text.split())  # Remove extra spaces
    return text 


def highlight_text_in_pdf(file_path, output_path, sentences, consecutive_words=7):
    """Highlights occurrences of any sequence of n consecutive words from the sentences in a PDF and returns the pages where any sentence was highlighted.

    Args:
        file_path (Str): filepath of the pdf to highlight
        output_path (Str): filepath of output pdf that has been highlighted
        sentences (List[Str]): List of strings that needs to be highlighted
        consecutive_words (int, optional): The overlap needed to be considered match. Defaults to 7.

    Returns:
        _type_: _description_
    """
    document = fitz.open(file_path)
    highlighted_pages = {}

    # Normalize sentences before searching
    normalized_sentences = [normalize_text(sentence) for sentence in sentences]

    for page_number, page in enumerate(document, start=1): #type:ignore
        page_text = normalize_text(page.get_text("text"))
        found_sentences = []

        # Generate sliding windows of 4 words for each sentence
        for sentence in normalized_sentences:
            words = sentence.split()

            if len(words) < consecutive_words:
                continue  # Skip sentences with fewer than 4 words
            windows = [' '.join(words[i:i+consecutive_words]) for i in range(len(words) - consecutive_words-1)]

            for window in windows:
                instances = page.search_for(window)
                for inst in instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.update()
                    if window not in found_sentences:
                        found_sentences.append(window)

        if found_sentences:
            highlighted_pages[page_number] = found_sentences

    document.save(output_path)
    document.close()
    return output_path, highlighted_pages


def log_info(log_message):
	print( datetime.now().strftime("%H:%M:%S"),":\t ", log_message , "\n")


# Function to load YAML configuration
def load_config(path=config_file_path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)


def preprocess_collection_name(name):
    # Remove leading and trailing non-alphanumeric characters
    name = name.strip()
    
    # Replace spaces and invalid characters with underscores
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    
    # Replace consecutive non-alphanumeric characters (including underscores and hyphens) with a single underscore
    name = re.sub(r'[_-]{2,}', '_', name)
    
    # Ensure the collection name is between 3 and 63 characters
    name = name[:63] if len(name) > 63 else name
    if len(name) < 3:
        raise ValueError("Collection name must be at least 3 characters long after preprocessing.")
    
    # Ensure the name starts and ends with an alphanumeric character
    if not name[0].isalnum():
        name = 'a' + name[1:]  # prepend 'a' if the first character is not alphanumeric
    if not name[-1].isalnum():
        name = name[:-1] + 'a'  # append 'a' if the last character is not alphanumeric
    
    return name