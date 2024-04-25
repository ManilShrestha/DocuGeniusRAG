from lib.DocLoader import DocLoader
from lib.VectorDB import VectorDBManager

from lib.EmbeddingModel import EmbeddingModel
from lib.LLMGenerator import LLMGenerator

source_filename = 'CVPR-Paper.pdf'
dl = DocLoader('data/'+source_filename)
# dl = DocLoader('data/FPA Review.docx')
# dl = DocLoader('data/Candidacy-Manil-Presentation-Final.pptx')


query  = "What is the novelty of E3?"
print(dl.get_doc_text())

text_chunks = dl.chunkify_document(chunk_size=512)

chroma_db = VectorDBManager(db_type='chromadb',collection_name=source_filename)

chroma_db.process_documents(text_chunks)

similar_chunks = chroma_db.retrieve(query, n_results=20)

rank_scores, reranked_similar_chunks  = EmbeddingModel().bge_rerank(query, similar_chunks[0])

chroma_db.cleanup()

generator = LLMGenerator()

generated_answer = generator.generate_answer(query, list(reranked_similar_chunks)[:10])

print(generated_answer)

