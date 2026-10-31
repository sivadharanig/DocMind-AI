from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.app.core.config import settings

class ChromaService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(settings.CHROMA_PERSIST_DIR),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        self._initialized = True

    def store_chunks(
        self,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        texts: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        if not chunk_ids:
            return
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def delete_by_document_id(self, document_uuid: str):
        """Purges all vector embeddings associated with the document_uuid."""
        try:
            self.collection.delete(
                where={"document_uuid": document_uuid}
            )
        except Exception as e:
            # If collection has no matching or empty, log and continue
            print(f"[ChromaService] Note on delete_by_document_id: {e}")

    def query_vectors(
        self,
        query_vector: List[float],
        where_filter: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Executes metadata pre-filtered vector similarity query.
        Returns list of matched chunks with metadata, text, and distance.
        """
        total_items = self.collection.count()
        if total_items == 0:
            return []

        n_results = min(top_k, total_items)
        kwargs: Dict[str, Any] = {
            "query_embeddings": [query_vector],
            "n_results": n_results
        }
        if where_filter:
            kwargs["where"] = where_filter

        try:
            results = self.collection.query(**kwargs)
        except Exception as e:
            print(f"[ChromaService] Query execution error with filter {where_filter}: {e}")
            return []

        matched_records = []
        if results and results.get("ids") and len(results["ids"]) > 0:
            ids = results["ids"][0]
            docs = results["documents"][0] if results.get("documents") else []
            metas = results["metadatas"][0] if results.get("metadatas") else []
            distances = results["distances"][0] if results.get("distances") else []

            for i in range(len(ids)):
                matched_records.append({
                    "chunk_id": ids[i],
                    "chunk_text": docs[i] if i < len(docs) else "",
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": distances[i] if i < len(distances) else 0.0,
                })
        return matched_records

    def count(self) -> int:
        return self.collection.count()

chroma_service = ChromaService()
