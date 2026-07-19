"""
ChromaDB manager for Sports Quiz AI.

Provides a thin, well-typed wrapper around a persistent ChromaDB
collection used to store and retrieve sports knowledge for
Retrieval-Augmented Generation (RAG).
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4

import chromadb
from chromadb.api.models.Collection import Collection

from src.config.settings import CHROMA_DB_PATH

# Name of the collection used to store sports knowledge documents.
COLLECTION_NAME: str = "sports_knowledge"


class ChromaManager:
    """
    Manages a persistent ChromaDB collection for storing and retrieving
    sports knowledge documents used in the quiz generation pipeline.
    """

    def __init__(self, db_path: str = CHROMA_DB_PATH) -> None:
        """
        Initialize the ChromaManager.

        Args:
            db_path: Filesystem path where ChromaDB persists its data.
                     Defaults to the path configured in settings.py.
        """
        self._db_path = db_path
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection: Optional[Collection] = None

    def initialize(self) -> None:
        """
        Initialize the persistent ChromaDB client and create or load the
        "sports_knowledge" collection.

        Must be called before any other read/write operations.
        """
        self._client = chromadb.PersistentClient(path=self._db_path)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME
        )

    @property
    def collection(self) -> Collection:
        """
        Return the active ChromaDB collection.

        Raises:
            RuntimeError: If the manager has not been initialized yet.
        """
        if self._collection is None:
            raise RuntimeError(
                "ChromaManager is not initialized. Call initialize() first."
            )
        return self._collection

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to the sports knowledge collection.

        Args:
            documents: List of text documents to store.
            metadatas: Optional list of metadata dicts, one per document.
                       Must be the same length as `documents` if provided.
            ids: Optional list of unique document IDs. If not provided,
                 UUIDs are generated automatically.

        Returns:
            The list of IDs assigned to the added documents.

        Raises:
            ValueError: If `documents` is empty, or if `metadatas`/`ids`
                        are provided with a length mismatch.
        """
        if not documents:
            raise ValueError("documents must not be empty.")

        if metadatas is not None and len(metadatas) != len(documents):
            raise ValueError("metadatas must be the same length as documents.")

        if ids is not None and len(ids) != len(documents):
            raise ValueError("ids must be the same length as documents.")

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
        Retrieve documents most semantically relevant to a query using
        vector similarity search.

        Args:
            query_text: The natural language query to search for.
            n_results: Maximum number of relevant documents to return.
            where: Optional metadata filter to narrow the search.

        Returns:
            A list of the most relevant document texts, ordered by
            relevance (most relevant first).
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
        )

        matched_documents = results.get("documents") or []
        if not matched_documents:
            return []

        # `documents` is a list of lists (one list per query text).
        # A single query was issued, so the first entry holds the results.
        return matched_documents[0]