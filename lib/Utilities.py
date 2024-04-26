import fitz  # PyMuPDF


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
            # Search for the sentence in the current page
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