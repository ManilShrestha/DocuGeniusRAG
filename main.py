from lib.DocLoader import DocLoader
from lib.VectorDB import VectorDBManager

from lib.EmbeddingModel import EmbeddingModel
from lib.LLMGenerator import LLMGenerator

import datetime

def log_msg(message):
    # Get the current date and time
    current_time = datetime.datetime.now()
    # Format the datetime object as a string in the desired format
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    # Print the formatted time and message
    print(f'{formatted_time} : {message}')


source_filename = 'E3.pdf' #'CVPR-Paper.pdf' #'case_study_medicine_llm.pdf'
dl = DocLoader('data/'+source_filename)
# dl = DocLoader('data/FPA Review.docx')
# dl = DocLoader('data/Candidacy-Manil-Presentation-Final.pptx')


query  = "What is E3?"
print(dl.get_doc_text())

text_chunks = dl.chunkify_document(chunk_size=512)

for t in text_chunks:
    print(len(t))

log_msg("Loading into vector db...")
chroma_db = VectorDBManager(db_type='chromadb',collection_name=source_filename)

chroma_db.process_documents(text_chunks)

log_msg("Retrieving similar chunks...")
similar_chunks = chroma_db.retrieve(query, n_results=20)


log_msg("Reranking chunks...")
rank_scores, reranked_similar_chunks  = EmbeddingModel().bge_rerank(query, similar_chunks[0])
print(list(reranked_similar_chunks)[:10])
# chroma_db.cleanup(source_filename)

log_msg("Generating answer...")
generator = LLMGenerator()

generated_answer = generator.generate_answer(query, list(reranked_similar_chunks)[:10], temperature=0)

print(generated_answer)

