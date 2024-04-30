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
    file = request.files['file']
    if file:
        
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
        text_chunks = dl.chunkify_document(chunk_size=384)

        for t in text_chunks:
            print(len(t))

        chroma_db = VectorDBManager(db_type='chromadb',collection_name=uploadFileName)
        
        log_info(f'Loading the document into vector DB.')
        
        chroma_db.process_documents(text_chunks)
        
        log_info(f'The document has been chunked and stored in vectorDB.')

        return url_for('uploaded_file', filename=file.filename)
    return '', 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/retrieve_generate', methods=['POST'])
def retrieve_generate():
    
    data = request.get_json()
    query = data.get('query')
    uploadFileName = data.get('filename')

    log_info(f'uploadFilePath: {uploadFileName}')
    chroma_db = VectorDBManager(db_type='chromadb',collection_name=uploadFileName)
    similar_chunks = chroma_db.retrieve(query, n_results=30)

    log_info(f'Similar chunks retrieved now re-ranking.')
    log_info(f'Similar Chunks: {similar_chunks}')
    
    embedding_model = EmbeddingModel()
    rank_scores, reranked_similar_chunks  = embedding_model.bge_rerank(query, similar_chunks[0]) # type: ignore
    
    
    # chroma_db.cleanup()

    references = list(reranked_similar_chunks)[:10]
    log_info(f'Chunks reranked, now generating the answer.')
    generator = LLMGenerator()
    generated_answer = generator.generate_answer(query, references, temperature=0)
    
    return jsonify({'generated_text': generated_answer, 'reference_texts': "\n\n--".join(references)}), 200

if __name__ == '__main__':
    app.run(debug=True, port=9874)
