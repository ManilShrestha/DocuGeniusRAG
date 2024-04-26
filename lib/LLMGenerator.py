import os
from openai import OpenAI
from dotenv import load_dotenv

class LLMGeneratorFactory:
    """Base class for embedding models."""
    def generate_answer(self, query, context):
        raise NotImplementedError("Subclasses must implement this method.")
        

class BlockEntropyGenerator(LLMGeneratorFactory):
    """A class to handle embeddings using BlockEntropy API."""
    
    def __init__(self):
        load_dotenv()
        self.model = 'be-pro-v1.0'
        api_key = os.getenv("BE_API_KEY")
        base_url = 'https://api.blockentropy.ai/v1'

        try:
            self.client = OpenAI(base_url=base_url, api_key=api_key)
        except Exception as e:
            raise ConnectionError("Failed to connect to BlockEntropy API. Please check your API key and network connection.") from e


    def generate_answer(self, query, context, temperature=0):
        """Creates embeddings of the provided text chunks using BlockEntropy API.

        Args:
            text_chunks (List[str]): List of text strings to be embedded.

        Returns:
            List: A list of embeddings.
        """
        context_combined = "\n".join(context)
        prompt = f"""Question: {query}
        Context: {context_combined}
        Generate an anwer based on the context provided.
        """

        print(prompt)

        completion = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {'role': 'system', 'content': 'You are an expert in answering questions based on the provided context.'},
                            {'role': 'user', 'content': prompt}
                        ],
                        temperature=temperature
                    )
        response=completion.choices[0].message.content

        return response

    
class LLMGenerator:
    """Facade to handle embedding models based on specified provider."""
    
    def __init__(self, model_type='blockentropy'):
        if model_type == 'blockentropy':
            self.generator = BlockEntropyGenerator()
        else:
            raise ValueError(f"{model_type} embedder has not been implemented.")

    def generate_answer(self, query, context, temperature=0):
        """Interface method to create embeddings through the embedder object.

        Args:
            text_chunks (List[str]): List of text strings to be embedded.

        Returns:
            List: Embeddings created by the embedder.
        """
        if isinstance(context, list):
            return self.generator.generate_answer(query, context, temperature=temperature)
        else:
            raise TypeError("Context should be list of strings.")