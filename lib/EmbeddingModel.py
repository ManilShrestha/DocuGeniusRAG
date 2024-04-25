import os
from openai import OpenAI
from dotenv import load_dotenv

class EmbeddingClient:
    """Base class for embedding models."""
    def create_embeddings(self, text_chunks):
        raise NotImplementedError("Subclasses must implement this method.")
    
    def bge_rerank(self, query, chunks):
        raise NotImplementedError("Subclasses must implement this method.")
        

class BlockEntropyEmbedder(EmbeddingClient):
    """A class to handle embeddings using BlockEntropy API."""
    
    def __init__(self):
        load_dotenv()
        self.model = 'be-bge-embeddings'
        api_key = os.getenv("BE_API_KEY")
        base_url = 'https://api.blockentropy.ai/v1'

        try:
            self.client = OpenAI(base_url=base_url, api_key=api_key)
        except Exception as e:
            raise ConnectionError("Failed to connect to BlockEntropy API. Please check your API key and network connection.") from e


    def create_chunk_embeddings(self, text_chunks):
        """Creates embeddings of the provided text chunks using BlockEntropy API.

        Args:
            text_chunks (List[str]): List of text strings to be embedded.

        Returns:
            List: A list of embeddings.
        """
        embeddings = []
        for text in text_chunks:
            cleaned_text = text.replace("\n", " ")
            response = self.client.embeddings.create(input=[cleaned_text], model=self.model)
            embeddings.append(response.data[0].embedding)
        return embeddings
    
    def create_embeddings(self, text):
        """Creates embeddings of the provided text chunks using BlockEntropy API.

        Args:
            text_chunks (List[str]): List of text strings to be embedded.

        Returns:
            List: A list of embeddings.
        """
        cleaned_text = text.replace("\n", " ")
        response = self.client.embeddings.create(input=[cleaned_text], model=self.model)
        return response.data[0].embedding
    
    def bge_rerank(self, query, chunks):
        pairs = [[query, x] for x in chunks]
        response = self.client.embeddings.create(
            input= pairs,
            model="be-bge-reranker"
        )
        rank_scores = response.data[0].scores

        # Zip the lists together and sort by rank in descending order
        sorted_pairs = sorted(zip(rank_scores, chunks), reverse=True, key=lambda x: x[0])

        # Extract the elements from the sorted pairs
        reranked_rank_scores, reranked_similar_chunks = zip(*sorted_pairs)
        return reranked_rank_scores, reranked_similar_chunks


class EmbeddingModel:
    """Facade to handle embedding models based on specified provider."""
    
    def __init__(self, model_type='blockentropy'):
        if model_type == 'blockentropy':
            self.embedder = BlockEntropyEmbedder()
        else:
            raise ValueError(f"{model_type} embedder has not been implemented.")

    def create_embeddings(self, texts):
        """Interface method to create embeddings through the embedder object.

        Args:
            text_chunks (List[str]): List of text strings to be embedded.

        Returns:
            List: Embeddings created by the embedder.
        """
        if isinstance(texts, list):
            return self.embedder.create_chunk_embeddings(texts)
        elif isinstance(texts, str):
            return self.embedder.create_embeddings(texts)
        else:
            raise TypeError("Input should either be string or list of strings.")
    
    def bge_rerank(self, query, text_chunks):
        """Reranks the text chunks based on the query and returns the reordered chunks for further processing

        Args:
            query: Query text
            text_chunks (List[str]): List of text strings to be embedded.

        Returns:
            List: Reranked chunks so that highest score is at index 0
        """
        return self.embedder.bge_rerank(query, text_chunks)
        