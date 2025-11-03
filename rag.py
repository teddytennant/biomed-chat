"""Compatibility layer around the flexible RAG pipeline implementation."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

import config
from rag_pipeline import FlexibleRAGPipeline, SearchResult


pipeline = FlexibleRAGPipeline(
    config.RAG_MODEL,
    chunk_size=config.RAG_CHUNK_SIZE,
    default_top_k=config.RAG_TOP_K,
    index_path=config.RAG_INDEX_PATH,
    documents_path=config.RAG_DOCUMENTS_PATH,
    auto_load=True,
)


def add_to_rag(
    chunks: Iterable[str],
    *,
    metadata: Optional[Dict[str, str]] = None,
    source_id: Optional[str] = None,
) -> List[SearchResult]:
    """Add pre-chunked strings directly to the vector store."""

    added_chunks = pipeline.add_texts(
        chunks,
        metadata=metadata,
        source_id=source_id,
        auto_chunk=False,
    )
    return [
        SearchResult(text=chunk.text, metadata=chunk.metadata, score=0.0, chunk_id=chunk.id)
        for chunk in added_chunks
    ]


def ingest_documents(
    documents: Iterable[str],
    *,
    metadata: Optional[Dict[str, str]] = None,
    source_id: Optional[str] = None,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    chunking_strategy: Optional[str] = None,
) -> List[SearchResult]:
    """Ingest raw documents with automatic chunking."""

    added_chunks = pipeline.add_texts(
        documents,
        metadata=metadata,
        source_id=source_id,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        chunking_strategy=chunking_strategy,
        auto_chunk=True,
    )
    return [
        SearchResult(text=chunk.text, metadata=chunk.metadata, score=0.0, chunk_id=chunk.id)
        for chunk in added_chunks
    ]


def retrieve_structured(
    query: str,
    *,
    top_k: Optional[int] = None,
    metadata_filters: Optional[Dict[str, object]] = None,
) -> List[SearchResult]:
    """Retrieve structured search results for advanced consumers."""

    return pipeline.query(
        query,
        top_k=top_k,
        metadata_filters=metadata_filters,
    )


def retrieve_from_rag(
    query: str,
    top_k: Optional[int] = None,
    *,
    metadata_filters: Optional[Dict[str, object]] = None,
    join_delimiter: str = "\n\n",
) -> str:
    """Backward-compatible helper that returns a newline-joined context string."""

    results = retrieve_structured(query, top_k=top_k, metadata_filters=metadata_filters)
    return join_delimiter.join(result.text for result in results)


def save_rag_index(
    *,
    index_path: Optional[str] = None,
    documents_path: Optional[str] = None,
) -> None:
    pipeline.save(index_path=index_path, documents_path=documents_path)


def load_rag_index(
    *,
    index_path: Optional[str] = None,
    documents_path: Optional[str] = None,
) -> None:
    pipeline.load(index_path=index_path, documents_path=documents_path)


def reset_rag_index() -> None:
    pipeline.reset()


__all__ = [
    "add_to_rag",
    "ingest_documents",
    "load_rag_index",
    "pipeline",
    "retrieve_from_rag",
    "retrieve_structured",
    "save_rag_index",
    "reset_rag_index",
    "SearchResult",
]