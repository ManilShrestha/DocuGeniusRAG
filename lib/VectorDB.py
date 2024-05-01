from abc import ABC, abstractmethod
from lib.EmbeddingModel import EmbeddingModel
from lib.Utilities import *

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

	@abstractmethod
	def reset(self):
		pass


class ChromaDB(BaseVectorDB):
	def __init__(self, collection_name='test_collection'):
		super().__init__('chromadb', collection_name)
		config = load_config(config_file_path)
		database_path = config['environment']['database_path']

		self.db_path = database_path
		self.embedding_model = EmbeddingModel()
		self.existing_collections=[]

		self.history_exists=False

		self.connect()

	def connect(self):
		import chromadb

		#TODO: Path of db needs to come from the config file.
		self.client = chromadb.PersistentClient(path=self.db_path)
		
		self.existing_collections = [collection.name for collection in self.client.list_collections()]
		log_info(f"List of collections {self.existing_collections}")

		if self.collection_name in self.existing_collections:
			self.history_exists = True

		# 	# Clear the collection if it exists
		# 	log_info(f"Deleting existing collection: {self.collection_name}")
		# 	self.delete_collection(self.collection_name)

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
		print(self.collection_name, self.existing_collections, self.history_exists)

		if not self.history_exists:
			embeddings = self.embedding_model.create_embeddings(text_chunks)
			ids = [f'chunk{i}' for i in range(len(embeddings))]
			
			self.collection.add(    
				documents=text_chunks,
				embeddings=embeddings,
				ids=ids
			)
		
		else:
			log_info(f'{self.collection_name} already exists. Load not required' )

	def query(self, query_text, n_results):
		"""Queries the vector DB based on the passed query_text

		Args:
			query_text (str): Query from the user.

		Returns:
			_type_: list of string. This would be the text chunks most similar to the query based on the distance.
		"""
		query_embedding = self.embedding_model.create_embeddings(query_text)
		
		result = self.collection.query(
			query_embeddings=query_embedding,
			n_results=n_results
		)
		return result['documents']


	def delete_collection(self, collection_name):
		"""This needs to be called as soon as the session ends in the WebUI to clear out the information.
		"""
		self.client.delete_collection(name=collection_name)
		log_info(f'Collection {collection_name} has been cleared.')

	def reset(self):
		self.client.reset()



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

	def cleanup(self, collection_name):
		self.db.delete_collection(collection_name)

	def reset(self):
		self.db.reset()