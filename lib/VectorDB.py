from abc import ABC, abstractmethod
from lib.EmbeddingModel import EmbeddingModel

class BaseVectorDB(ABC):
	"""Abstract base class for all vector databases."""
	
	def __init__(self, db_name, collection_name):
		self.db_name = db_name
		self.collection_name = collection_name

	@abstractmethod
	def connect(self):
		pass

	@abstractmethod
	def load_documents(self, documents):
		pass

	@abstractmethod
	def query(self, query_text):
		pass

	@abstractmethod
	def delete_collection(self):
		pass


class ChromaDB(BaseVectorDB):
	def __init__(self, collection_name='test_collection'):
		super().__init__('chromadb', collection_name)
		self.connect()

	def connect(self):
		import chromadb

		#TODO: Path of db needs to come from the config file.
		self.client = chromadb.PersistentClient(path='../database/chromadb.db')
		self.collection = self.client.get_or_create_collection(
			name=self.collection_name,
			#TODO: Distance should also come from the config file.
			metadata={'hnsw:space': 'cosine'}
		)

	def load_documents(self, text_chunks):
		"""This loads the document text chunks into the vector db

        Args:
            text_chunks (list[str]): text chunks of the document.
        """
		embeddings = EmbeddingModel().create_embeddings(text_chunks)
		ids = [f'chunk{i}' for i in range(len(embeddings))]
		
		self.collection.add(    
            documents = text_chunks,
            embeddings=embeddings,
            ids=ids
        )

	def query(self, query_text, n_results):
		"""Queries the vector DB based on the passed query_text

        Args:
            query_text (str): Query from the user.

        Returns:
            _type_: list of string. This would be the text chunks most similar to the query based on the distance.
        """
		query_embedding = EmbeddingModel().create_embeddings(query_text)
		result = self.collection.query(
			query_embeddings=query_embedding,
			n_results=n_results
		)
		return result['documents']


	def delete_collection(self):
		"""This needs to be called as soon as the session ends in the WebUI to clear out the information.
		"""
		self.client.delete_collection(name=self.collection_name)
		print(f'Collection {self.collection_name} has been cleared.')



class VectorDBManager:
    def __init__(self, db_type='chromadb', collection_name='test_collection'):
        if db_type == 'chromadb':
            self.db = ChromaDB(collection_name=collection_name)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def process_documents(self, text_chunks):
        self.db.load_documents(text_chunks)

    def retrieve(self, query_text, n_results=20):
        return self.db.query(query_text, n_results)

    def cleanup(self):
        self.db.delete_collection()