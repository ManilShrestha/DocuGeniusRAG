from lib.DocLoader import DocLoader

from lib.EmbeddingModel import EmbeddingModel

dl = DocLoader('data/CVPR-Paper.pdf')
# dl = DocLoader('data/FPA Review.docx')
# dl = DocLoader('data/Candidacy-Manil-Presentation-Final.pptx')

print(dl.get_doc_text())

text_chunks = dl.chunkify_document(256)

print(text_chunks)

embedding_model = EmbeddingModel()

embeddings = embedding_model.create_embeddings(text_chunks)

print(embeddings)