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


def highlight_text_in_pdf(file_path, output_path, sentences):
    """
    Highlights occurrences of multiple sentences in a PDF and returns the pages where any sentence was highlighted.
    
    Args:
        file_path (str): Path to the PDF file.
        output_path (str): Path where the modified PDF will be saved.
        sentences (list of str): List of sentences to search for and highlight in the PDF.

    Returns:
        dict: A dictionary where keys are page numbers and values are lists of sentences highlighted on that page.
    """
    document = fitz.open(file_path)
    highlighted_pages = {}  # Dictionary to store page numbers and the sentences highlighted on them

    # Loop through each page in the PDF
    for page_number, page in enumerate(document, start=1):  # type: ignore # start=1 for human-readable page numbers
        found_sentences = []  # List to store sentences found on the current page

        # Check each sentence in the list
        for sentence in sentences:
            # print(sentence)
            # Search for the sentence in the current page
            sentence = normalize_text(sentence)

            text_instances = page.search_for(sentence)
            
            # If text instances are found, highlight them
            if text_instances:
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.update()  # Apply the highlighting
                
                # Add the sentence to the list of found sentences for this page
                if sentence not in found_sentences:
                    found_sentences.append(sentence)

        # If any sentences were found and highlighted, add to the highlighted_pages dictionary
        if found_sentences:
            highlighted_pages[page_number] = found_sentences

    # Save the modified PDF with highlights
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


def get_ranked_page_source(highlighted_page_references, normalized_references):
    """
    Searches for text snippets from the 'highlighted_page_references' within the 'normalized_references' list,
    ranks them according to their position in 'normalized_references', and returns a sorted list of these rankings
    along with the corresponding file path and page number where each snippet was found.

    Args:
        highlighted_page_references (list of tuples): A list where each tuple contains a file path and a dictionary.
            The dictionary keys are page numbers (int), and values are lists of text snippets (str) found on that page.
        normalized_references (list of str): A list of normalized reference strings. These strings are checked against
            the snippets found in 'highlighted_page_references'.

    Returns:
        list of lists: A sorted list where each sublist contains:
            - index (int): The zero-based index of the snippet in 'normalized_references' indicating the rank.
            - path (str): The path of the PDF file where the snippet was found.
            - page_num (int): The page number where the snippet was found.
            - snippet (str): The text snippet that matched the normalized reference.

    The return list is sorted by 'index', meaning snippets are ranked in the order they appear in 'normalized_references'.
    """
    import os
    results = []

    for path, content_dict in highlighted_page_references:
        path = os.path.basename(path)
        for page_num, snippets in content_dict.items():
            for snippet in snippets:
                if snippet in normalized_references:
                    index = normalized_references.index(snippet)
                    results.append([index, path, page_num, snippet])

    results.sort(key=lambda x:x[0])
    
    return results