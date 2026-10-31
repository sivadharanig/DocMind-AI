from typing import List
from backend.app.core.config import settings


class EmbeddingService:
    """
    Embedding service that exclusively uses the OpenAI Embeddings API
    (model: text-embedding-3-small by default).

    Raises RuntimeError if:
      - The OpenAI API key is not configured, or
      - The API call fails for any reason.

    No local / deterministic fallback is used.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.VECTOR_DIMENSION
        self.client = None
        if self.api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        self._initialized = True

    def update_api_key(self, new_key: str):
        """Hot-swap the OpenAI API key without restarting the service."""
        self.api_key = new_key.strip()
        settings.OPENAI_API_KEY = self.api_key
        if self.api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def _require_client(self):
        """Raise a descriptive RuntimeError when no valid API key is present."""
        if not self.client or not self.api_key:
            raise RuntimeError(
                "[EmbeddingService] OpenAI API key is not configured. "
                "Please provide a valid OPENAI_API_KEY in your .env file or via the Admin panel."
            )

    def generate_embedding(self, text: str) -> List[float]:
        """Return the OpenAI embedding vector for a single text string."""
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Return OpenAI embedding vectors for a batch of text strings.

        Raises
        ------
        RuntimeError
            If the API key is missing or the OpenAI API call fails.
        """
        if not texts:
            return []

        self._require_client()

        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            print(
                f"[EmbeddingService] Generated {len(texts)} embedding(s) "
                f"via OpenAI model '{self.model}'."
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise RuntimeError(
                f"[EmbeddingService] OpenAI Embedding API call failed: {e}"
            ) from e


# Singleton accessor
embedding_service = EmbeddingService()

