import os
from pathlib import Path
from typing import List
from backend.app.services.chroma_service import chroma_service
from backend.app.services.parser_factory import ParserFactory
from backend.app.services.chunker import RecursiveTextChunker
from backend.app.services.embedding_service import embedding_service
from backend.app.core.config import settings

class VectorSyncService:
    def __init__(self):
        self.chunker = RecursiveTextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def purge_vectors(self, document_uuid: str) -> bool:
        """Purge all vector embeddings associated with document_uuid from ChromaDB."""
        try:
            chroma_service.delete_by_document_id(document_uuid)
            return True
        except Exception as e:
            print(f"[VectorSyncService] Error during vector purge for {document_uuid}: {e}")
            return False

    def index_document_content(
        self,
        document_uuid: str,
        owner_id: int,
        visibility: str,
        filename: str,
        file_bytes: bytes,
        file_ext: str
    ) -> int:
        """
        Parses, chunks, embeds, and stores vectors for a document.
        Returns the number of chunks indexed.
        """
        parser = ParserFactory.get_parser_for_extension(file_ext)
        clean_text = parser.extract_text(file_bytes)

        if not clean_text or not clean_text.strip():
            # If empty file or no extractable text, create at least a placeholder or return 0
            clean_text = f"Document: {filename} (No extractable text content)."

        chunks = self.chunker.chunk_text(clean_text)
        if not chunks:
            chunks = [clean_text[:settings.CHUNK_SIZE]]

        chunk_ids = [f"{document_uuid}_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "document_uuid": document_uuid,
                "owner_id": int(owner_id),
                "visibility": str(visibility),
                "chunk_index": i,
                "filename": filename
            }
            for i in range(len(chunks))
        ]

        embeddings = embedding_service.generate_embeddings(chunks)
        chroma_service.store_chunks(
            chunk_ids=chunk_ids,
            embeddings=embeddings,
            texts=chunks,
            metadatas=metadatas
        )
        return len(chunks)

    def reindex_document(
        self,
        document_uuid: str,
        owner_id: int,
        visibility: str,
        filename: str,
        new_file_bytes: bytes,
        file_ext: str
    ) -> bool:
        """
        Observer / Sync Hook: Flushes stale vectors then parses and re-indexes new content.
        """
        self.purge_vectors(document_uuid)
        indexed_count = self.index_document_content(
            document_uuid=document_uuid,
            owner_id=owner_id,
            visibility=visibility,
            filename=filename,
            file_bytes=new_file_bytes,
            file_ext=file_ext
        )
        return indexed_count > 0

    def remove_physical_file(self, file_path_str: str) -> bool:
        """Safely removes physical file from disk storage."""
        try:
            path = Path(file_path_str)
            if path.exists() and path.is_file():
                os.remove(path)
                return True
        except Exception as e:
            print(f"[VectorSyncService] Failed removing file {file_path_str}: {e}")
        return False

vector_sync_service = VectorSyncService()
