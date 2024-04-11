import os
from openai import OpenAI
from dotenv import load_dotenv

class EmbeddingClient:
    """Base class for embedding models."""
    def create_embeddings(self, text_chunks):
        raise NotImplementedError("Subclasses must implement this method.")

class BlockEntropyEmbedder(EmbeddingClient):
    """A class to handle embeddings using BlockEntropy API."""
    
    def __init__(self):
        load_dotenv()
        self.model = 'be-bge-embeddings'
        self.api_key = os.getenv("BE_API_KEY", "YOUR_DEFAULT_API_KEY")
        self.base_url = 'https://api.blockentropy.ai/v1'
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def create_embeddings(self, text_chunks):
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

class EmbeddingModel:
    """Facade to handle embedding models based on specified provider."""
    
    def __init__(self, model_type='blockentropy'):
        if model_type == 'blockentropy':
            self.embedder = BlockEntropyEmbedder()
        else:
            raise ValueError(f"{model_type} embedder has not been implemented.")

    def create_embeddings(self, text_chunks):
        """Interface method to create embeddings through the embedder object.

        Args:
            text_chunks (List[str]): List of text strings to be embedded.

        Returns:
            List: Embeddings created by the embedder.
        """
        return self.embedder.create_embeddings(text_chunks)
