"""
ChromaDB manager for Sports Quiz AI.

Provides a clean, typed wrapper around a persistent ChromaDB collection
used to store and retrieve sports knowledge for Retrieval-Augmented
Generation (RAG).
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4

import chromadb
from chromadb.api.models.Collection import Collection

from src.config.settings import CHROMA_DB_PATH

COLLECTION_NAME = "sports_knowledge"


class ChromaManager:
    """
    Manages a persistent ChromaDB collection used by the Sports Quiz AI.
    """

    def __init__(self, db_path: str = CHROMA_DB_PATH) -> None:
        """
        Initialize the ChromaManager.

        Args:
            db_path: Filesystem path where ChromaDB persists its data.
        """
        self._db_path = db_path
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection: Optional[Collection] = None

    def initialize(self) -> None:
        """
        Create the ChromaDB client and load (or create) the collection.
        """
        if self._client is not None:
            return

        self._client = chromadb.PersistentClient(path=self._db_path)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME
        )

    @property
    def collection(self) -> Collection:
        """
        Return the active ChromaDB collection.

        Raises:
            RuntimeError:
                If initialize() has not been called.
        """
        if self._collection is None:
            raise RuntimeError(
                "ChromaManager is not initialized. "
                "Call initialize() before using the collection."
            )

        return self._collection

    def reset_collection(self) -> None:
        """
        Delete and recreate the collection.

        Useful when rebuilding the vector database from scratch so old
        chunks are removed before inserting updated ones.
        """
        if self._client is None:
            raise RuntimeError(
                "Initialize ChromaManager before resetting the collection."
            )

        try:
            self._client.delete_collection(COLLECTION_NAME)
        except Exception:
            # Ignore if the collection doesn't exist yet.
            pass

        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME
        )

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Store documents inside ChromaDB.

        Args:
            documents:
                Documents to embed and store.

            metadatas:
                Optional metadata dictionaries.

            ids:
                Optional unique IDs.

        Returns:
            IDs assigned to the stored documents.

        Raises:
            ValueError:
                If inputs are invalid.
        """
        if not documents:
            raise ValueError("documents must not be empty.")

        if metadatas is not None and len(metadatas) != len(documents):
            raise ValueError(
                "metadatas must have the same length as documents."
            )

        if ids is not None and len(ids) != len(documents):
            raise ValueError(
                "ids must have the same length as documents."
            )

        document_ids = ids or [str(uuid4()) for _ in documents]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=document_ids,
        )

        return document_ids

    def retrieve_documents(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Retrieve documents most relevant to a query.

        Args:
            query_text:
                Natural language search query.

            n_results:
                Maximum number of matching documents.

            where:
                Optional metadata filter.

        Returns:
            List of retrieved document strings.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
        )

        documents = results.get("documents")

        if not documents:
            return []

        return documents[0]