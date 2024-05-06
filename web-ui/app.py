from flask import Flask, render_template, request, send_from_directory, url_for, jsonify

import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.DocLoader import DocLoader
from lib.VectorDB import VectorDBManager

from lib.EmbeddingModel import EmbeddingModel
from lib.LLMGenerator import LLMGenerator
from lib.Utilities import *

app = Flask(__name__)

uploadFileName=""

# Directory to store uploaded files
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    config = load_config(config_file_path)
    chunk_size_doc = config['environment']['chunk_size']

    files = request.files.getlist('files[]')  # Get a list of all files uploaded
    if not files:
        return "No files uploaded", 400  # Return error if no files were uploaded
    
    log_info(f"Files sent from front end: {files}")
    
    for file in files:
        # Save the uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename) # type: ignore
        file.save(filepath)
        uploadFileName=file.filename

        if not uploadFileName:
            # Error handling, if no filename, then it is placeholder
            uploadFileName='placeholder'

        log_info(f'uploadFilePath: {uploadFileName}')
        
        # Chunkify and store in vector DB
        uploadFilePath = f'static/uploads/{uploadFileName}'
        dl = DocLoader(uploadFilePath)
        # log_info(dl.get_doc_text())
        text_chunks = dl.chunkify_document(chunk_size=chunk_size_doc)

        chroma_db = VectorDBManager(db_type='chromadb',collection_name=uploadFileName)
        
        log_info(f'Loading the document into vector DB.')
        
        chroma_db.process_documents(text_chunks)
        
        log_info(f'The document successfully stored in vectorDB.')

    return url_for('uploaded_file', filename=file.filename)
    

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/retrieve_generate', methods=['POST'])
def retrieve_generate():
    config = load_config(config_file_path)
    num_of_references_to_use = config['environment']['max_num_refs']
    vectordb_max_return_num_chunks = config['environment']['vectordb_max_return_num_chunks']
    # num_of_references_to_use = 10

    data = request.get_json()
    query = data.get('query')
    uploadFileNames = data.get('filenames')
    similar_chunks_dict = {}

    log_info(f"Upload Files are:{uploadFileNames}")
    
    # Retrieving similar chunks from all the files
    for uploadFileName in uploadFileNames:
        log_info(f'uploadFileName: {uploadFileName}')
        chroma_db = VectorDBManager(db_type='chromadb',collection_name=uploadFileName)
        similar_chunks = chroma_db.retrieve(query, n_results=vectordb_max_return_num_chunks)
        
        if similar_chunks:
            similar_chunks_dict[uploadFileName] = similar_chunks
            log_info(f'Similar chunks retrieved now re-ranking.')
        else:
            return jsonify({'error': 'No similar chunks retrieved.'}), 500
    

    # Need to rerank the 30 chunks per file that was retrieved to be re-ranked and top-K selected for generation.
    embedding_model = EmbeddingModel()
    all_reranked = []
    for uploadFileName, chunks in similar_chunks_dict.items():
        for chunk in chunks:
            rank_scores, reranked_similar_chunks = embedding_model.bge_rerank(query, chunk)
            all_reranked.extend([(score, chunk, uploadFileName) for 
                                 score, chunk in zip(rank_scores, reranked_similar_chunks)])

    # Sort all reranked results by score, slice to use only the top N references
    all_reranked.sort(key=lambda x: x[0], reverse=True)
    # print("ALL_RERANKED ",all_reranked)
    references = [chunk for _, chunk, _ in all_reranked[:num_of_references_to_use]]
    reference_source = [source for _, _, source in all_reranked[:num_of_references_to_use]]

    log_info(f'Chunks reranked, now generating the answer...')

    # Generate the response based on the top-k reference chunks
    generator = LLMGenerator()
    generated_answer = generator.generate_answer(query, references, temperature=0)
    log_info('Answer generated. Highlighting the chunks...')
    
    highlighted_page_references = []

    for source in distinct_ordered(reference_source):
        output_path, pages = highlight_text_in_pdf(f'static/uploads/{source}', f'static/highlighted/{source}', references)
        highlighted_page_references.append((output_path, pages))
        # highlighted_page_nums.extend([(page, source) for page in pages])
 
    normalized_references = [normalize_text(r) for r in references]

    # The pages and source are not ranked as per the ranking scores, get_ranked_page_source reranks them based on the reference indices
    ranked_page_references = get_ranked_page_source(highlighted_page_references, normalized_references)
    highlighted_page_nums = [(item[2], item[1]) for item in ranked_page_references]

    log_info('Highlighting complete. Preparing response...')

    return jsonify({
        'generated_text': generated_answer,
        'highlighted_page_nums': highlighted_page_nums,
        'highlighted_file_paths': highlighted_page_references
    }), 200


def distinct_ordered(items):
    return list(dict.fromkeys(items))

if __name__ == '__main__':
    app.run(debug=True, port=9874)
    # app.run(port=9874)