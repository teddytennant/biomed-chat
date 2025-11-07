"""Flexible Retrieval-Augmented Generation (RAG) pipeline utilities.

This module provides a higher-level abstraction around document ingestion,
chunking, embedding, vector indexing, retrieval, and persistence so the rest
of the application can work with a single, tested component.
"""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence
from uuid import uuid4

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """A single chunk of text captured in the vector store."""

    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class SearchResult:
    """A retrieval result returned to downstream consumers."""

    text: str
    metadata: Dict[str, Any]
    score: float
    chunk_id: str


class FlexibleRAGPipeline:
    """End-to-end RAG helper with chunking, vector storage, and retrieval."""

    def __init__(
        self,
        embedding_model: str,
        *,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        default_top_k: int = 3,
        normalize_embeddings: bool = True,
        index_factory: str = "flat_ip",
        index_path: Optional[str] = None,
        documents_path: Optional[str] = None,
        auto_load: bool = False,
        candidate_multiplier: int = 3,
        chunking_strategy: str = "auto",
    ) -> None:
        self.embedding_model = embedding_model
        self.chunk_size = max(chunk_size, 1)
        self.chunk_overlap = min(max(chunk_overlap, 0), self.chunk_size - 1)
        self.default_top_k = max(default_top_k, 1)
        self.normalize_embeddings = normalize_embeddings
        self.index_factory = index_factory.lower()
        self.index_path = index_path
        self.documents_path = documents_path
        self.candidate_multiplier = max(candidate_multiplier, 1)
        self.chunking_strategy = chunking_strategy

        self.embedder: Optional[SentenceTransformer] = None
        self.dimension: Optional[int] = None
        self.index: Optional[faiss.Index] = None
        self.documents: List[DocumentChunk] = []
        self._is_loaded = False
        self._auto_load = auto_load

        if auto_load:
            try:
                self.load()
            except FileNotFoundError:
                logger.debug("No existing RAG index found during auto-load.")
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Failed to auto-load RAG index: %s", exc)

    # ------------------------------------------------------------------
    # Model and index helpers
    # ------------------------------------------------------------------
    def _ensure_model(self) -> None:
        if self.embedder is None:
            self.embedder = SentenceTransformer(self.embedding_model)
            self.dimension = self.embedder.get_sentence_embedding_dimension()

    def _ensure_index(self) -> None:
        if self.index is not None:
            return
        if self.dimension is None:
            self._ensure_model()
        if self.dimension is None:
            raise RuntimeError("Embedding dimension is undefined; model failed to load.")

        if self.index_factory == "flat_ip":
            self.index = faiss.IndexFlatIP(self.dimension)
        elif self.index_factory == "flat_l2":
            self.index = faiss.IndexFlatL2(self.dimension)
        else:
            raise ValueError(f"Unsupported index factory: {self.index_factory}")

    def _ensure_loaded(self) -> None:
        if self._auto_load and not self._is_loaded:
            try:
                if self.index_path and os.path.exists(self.index_path):
                    self.load()
            except FileNotFoundError:
                pass
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Deferred load of RAG index failed: %s", exc)
            finally:
                self._is_loaded = True

    # ------------------------------------------------------------------
    # Chunking utilities
    # ------------------------------------------------------------------
    def _chunk_text(
        self,
        text: str,
        *,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        strategy: Optional[str] = None,
    ) -> List[str]:
        chunk_size = max(chunk_size or self.chunk_size, 1)
        effective_overlap = chunk_overlap
        if effective_overlap is None:
            effective_overlap = self.chunk_overlap
        max_overlap = chunk_size - 1
        if effective_overlap < 0:
            effective_overlap = 0
        if effective_overlap > max_overlap:
            effective_overlap = max_overlap

        chosen_strategy = (strategy or self.chunking_strategy or "auto").lower()
        cleaned = text.strip()
        if not cleaned:
            return []

        if chosen_strategy == "none":
            return [cleaned]

        if chosen_strategy == "paragraph":
            units = [para.strip() for para in cleaned.split("\n\n") if para.strip()]
            return self._chunk_units(units, chunk_size, effective_overlap)

        if chosen_strategy == "sentence":
            units = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
            return self._chunk_units(units, chunk_size, effective_overlap)

        if chosen_strategy == "auto":
            units = [para.strip() for para in cleaned.split("\n\n") if para.strip()]
            if units:
                return self._chunk_units(units, chunk_size, effective_overlap)
            units = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
            if units:
                return self._chunk_units(units, chunk_size, effective_overlap)

        # Fallback to raw character-based chunking
        return self._chunk_by_character(cleaned, chunk_size, effective_overlap)

    def _chunk_units(self, units: Sequence[str], chunk_size: int, chunk_overlap: int) -> List[str]:
        if not units:
            return []
        chunks: List[str] = []
        buffer: List[str] = []
        current_len = 0

        for unit in units:
            unit_len = len(unit)
            separator = 1 if buffer else 0  # Account for newline join
            if current_len + unit_len + separator <= chunk_size:
                buffer.append(unit)
                current_len += unit_len + separator
                continue

            if buffer:
                chunks.append("\n".join(buffer))
                if chunk_overlap > 0:
                    overlap_text = chunks[-1][-chunk_overlap:]
                    buffer = [overlap_text]
                    current_len = len(overlap_text)
                else:
                    buffer = []
                    current_len = 0

            if unit_len >= chunk_size:
                chunks.extend(self._chunk_by_character(unit, chunk_size, chunk_overlap))
                buffer = []
                current_len = 0
            else:
                buffer = [unit]
                current_len = len(unit)

        if buffer:
            chunks.append("\n".join(buffer))

        return chunks

    def _chunk_by_character(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        if not text:
            return []
        if chunk_overlap >= chunk_size:
            chunk_overlap = max(chunk_size - 1, 0)

        chunks: List[str] = []
        start = 0
        text_length = len(text)
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end == text_length:
                break
            if chunk_overlap > 0:
                start = max(end - chunk_overlap, start + 1)
            else:
                start = end
        return chunks

    # ------------------------------------------------------------------
    # Embedding utilities
    # ------------------------------------------------------------------
    def _embed_texts(self, texts: Sequence[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension or 0), dtype=np.float32)
        self._ensure_model()
        embeddings = self.embedder.encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=self.normalize_embeddings,
        )
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)
        return np.ascontiguousarray(embeddings)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def add_texts(
        self,
        texts: Iterable[str],
        *,
        metadata: Optional[Dict[str, Any]] = None,
        source_id: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        chunking_strategy: Optional[str] = None,
        auto_chunk: bool = True,
    ) -> List[DocumentChunk]:
        """Add one or more documents to the RAG store."""

        self._ensure_loaded()

        base_metadata = dict(metadata or {})
        if source_id and "source_id" not in base_metadata:
            base_metadata["source_id"] = source_id

        prepared_texts = []
        for text in texts:
            if text is None:
                continue
            cleaned = str(text).strip()
            if cleaned:
                prepared_texts.append(cleaned)

        if not prepared_texts:
            return []

        chunks: List[DocumentChunk] = []
        for doc_index, raw_text in enumerate(prepared_texts):
            current_meta = dict(base_metadata)
            current_meta["document_index"] = doc_index

            if auto_chunk:
                chunked_texts = self._chunk_text(
                    raw_text,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    strategy=chunking_strategy,
                )
            else:
                chunked_texts = [raw_text]

            for chunk_idx, chunk_text in enumerate(chunked_texts):
                chunk_meta = dict(current_meta)
                chunk_meta["chunk_index"] = chunk_idx
                chunk_meta["chunk_char_length"] = len(chunk_text)
                chunks.append(DocumentChunk(text=chunk_text, metadata=chunk_meta))

        if not chunks:
            return []

        self._ensure_index()
        embeddings = self._embed_texts([chunk.text for chunk in chunks])
        if embeddings.size == 0:
            return []

        self.index.add(embeddings)

        start_offset = len(self.documents)
        for offset, chunk in enumerate(chunks):
            if "chunk_id" in chunk.metadata:
                chunk_id = str(chunk.metadata["chunk_id"])
            else:
                source_hint = chunk.metadata.get("source_id", "chunk")
                chunk_id = f"{source_hint}-{start_offset + offset}"
            chunk.id = chunk_id
            chunk.metadata.setdefault("chunk_id", chunk_id)
            self.documents.append(chunk)

        return chunks

    def query(
        self,
        query_text: str,
        *,
        top_k: Optional[int] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        reranker: Optional[Callable[[str, List[SearchResult]], List[SearchResult]]] = None,
        max_candidates: Optional[int] = None,
    ) -> List[SearchResult]:
        """Retrieve relevant chunks for the supplied query."""

        self._ensure_loaded()

        if self.index is None or self.index.ntotal == 0:
            return []

        top_k = max(top_k or self.default_top_k, 1)
        if max_candidates is None:
            max_candidates = max(top_k * self.candidate_multiplier, top_k)
        else:
            max_candidates = max(max_candidates, top_k)

        query_embedding = self._embed_texts([query_text])
        if query_embedding.size == 0:
            return []

        scores, indices = self.index.search(query_embedding, max_candidates)
        candidates: List[SearchResult] = []
        seen_ids = set()
        for idx, score in zip(indices[0], scores[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
            chunk = self.documents[idx]
            if metadata_filters and not self._metadata_matches(chunk.metadata, metadata_filters):
                continue
            if chunk.id in seen_ids:
                continue
            candidates.append(
                SearchResult(
                    text=chunk.text,
                    metadata=dict(chunk.metadata),
                    score=float(score),
                    chunk_id=chunk.id,
                )
            )
            seen_ids.add(chunk.id)
            if len(candidates) >= max_candidates:
                break

        if not candidates:
            return []

        candidates.sort(key=lambda result: result.score, reverse=True)

        if reranker:
            reranked = reranker(query_text, candidates)
            if reranked:
                candidates = reranked

        return candidates[:top_k]

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def save(
        self,
        *,
        index_path: Optional[str] = None,
        documents_path: Optional[str] = None,
    ) -> None:
        """Persist the FAISS index and document metadata."""

        target_index_path = index_path or self.index_path
        target_documents_path = documents_path or self.documents_path

        if target_index_path is None or target_documents_path is None:
            raise ValueError("Both index_path and documents_path must be provided to save().")

        self._ensure_index()
        if self.index is None:
            raise RuntimeError("FAISS index failed to initialize before saving.")

        faiss.write_index(self.index, target_index_path)

        with open(target_documents_path, "w", encoding="utf-8") as handle:
            for chunk in self.documents:
                handle.write(
                    json.dumps(
                        {
                            "id": chunk.id,
                            "text": chunk.text,
                            "metadata": chunk.metadata,
                        }
                    )
                    + "\n"
                )

    def load(
        self,
        *,
        index_path: Optional[str] = None,
        documents_path: Optional[str] = None,
    ) -> None:
        """Load a previously saved FAISS index and document metadata."""

        target_index_path = index_path or self.index_path
        target_documents_path = documents_path or self.documents_path

        if target_index_path is None or target_documents_path is None:
            raise ValueError("Both index_path and documents_path must be provided to load().")

        if not os.path.exists(target_index_path):
            raise FileNotFoundError(target_index_path)

        self.index = faiss.read_index(target_index_path)
        self.dimension = self.index.d

        self.documents = []
        if os.path.exists(target_documents_path):
            with open(target_documents_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    cleaned = line.strip()
                    if not cleaned:
                        continue
                    if cleaned.startswith("{"):
                        payload = json.loads(cleaned)
                        text = payload.get("text", "").strip()
                        metadata = payload.get("metadata") or {}
                        chunk_id = payload.get("id") or payload.get("chunk_id")
                    else:
                        text = cleaned
                        metadata = {}
                        chunk_id = None
                    if not text:
                        continue
                    self.documents.append(
                        DocumentChunk(text=text, metadata=metadata, id=chunk_id or str(uuid4()))
                    )

        if len(self.documents) != self.index.ntotal:
            # Rebuild index to avoid mismatches
            texts = [chunk.text for chunk in self.documents]
            self._ensure_model()
            self._ensure_index()
            self.index.reset()
            if texts:
                embeddings = self._embed_texts(texts)
                self.index.add(embeddings)

        self._is_loaded = True

    def reset(self) -> None:
        """Completely clear the in-memory index and documents."""

        if self.index is not None:
            self.index.reset()
        self.documents = []

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------
    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.documents)

    def _metadata_matches(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        for key, expected in filters.items():
            value = metadata.get(key)
            if callable(expected):
                try:
                    if not expected(value):
                        return False
                except Exception:  # pragma: no cover - defensive guard
                    return False
            elif isinstance(expected, (list, tuple, set, frozenset)):
                if value not in expected:
                    return False
            else:
                if value != expected:
                    return False
        return True
