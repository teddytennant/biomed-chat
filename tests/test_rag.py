import os
from pathlib import Path

import pytest

import rag  # Import the module itself to avoid stale globals


TEST_INDEX_PATH = Path("test_rag_index.faiss")
TEST_DOCUMENTS_PATH = Path("test_rag_documents.jsonl")


@pytest.fixture(autouse=True)
def reset_rag_index():
    """Ensure each test starts with a clean pipeline state."""

    rag.reset_rag_index()
    yield
    rag.reset_rag_index()
    for path in (TEST_INDEX_PATH, TEST_DOCUMENTS_PATH):
        if path.exists():
            path.unlink()


def test_add_and_retrieve():
    """Tests that basic adding and retrieving of documents works."""

    rag.add_to_rag([
        "CRISPR-Cas9 is a revolutionary gene-editing tool.",
        "The powerhouse of the cell is the mitochondria.",
    ])

    retrieved_context = rag.retrieve_from_rag(
        "Tell me about the gene-editing tool", top_k=1
    )

    assert "CRISPR-Cas9" in retrieved_context
    assert "mitochondria" not in retrieved_context


def test_retrieve_from_empty_rag():
    """Tests that retrieving from an empty RAG returns an empty string."""

    retrieved_context = rag.retrieve_from_rag("Any query")
    assert retrieved_context == ""


def test_persistence_round_trip():
    """The index and documents should persist across save/load cycles."""

    rag.add_to_rag(["This document tests the persistence feature."])
    assert rag.pipeline.index is not None
    assert rag.pipeline.index.ntotal == 1

    rag.save_rag_index(
        index_path=str(TEST_INDEX_PATH),
        documents_path=str(TEST_DOCUMENTS_PATH),
    )

    rag.reset_rag_index()
    assert rag.pipeline.index is None or rag.pipeline.index.ntotal == 0
    assert len(rag.pipeline.documents) == 0

    rag.load_rag_index(
        index_path=str(TEST_INDEX_PATH),
        documents_path=str(TEST_DOCUMENTS_PATH),
    )

    assert rag.pipeline.index is not None
    assert rag.pipeline.index.ntotal == 1
    assert len(rag.pipeline.documents) == 1

    retrieved_context = rag.retrieve_from_rag("persistence", top_k=1)
    assert "persistence feature" in retrieved_context


def test_metadata_filtering():
    """Metadata filters should restrict retrieval results."""

    rag.add_to_rag(
        ["Guidelines recommend vaccination."],
        metadata={"category": "guideline"},
    )
    rag.add_to_rag(
        ["Clinical trial reports mixed outcomes."],
        metadata={"category": "trial"},
    )

    all_results = rag.retrieve_structured("outcomes", top_k=2)
    assert len(all_results) == 2

    filtered_results = rag.retrieve_structured(
        "outcomes",
        metadata_filters={"category": "guideline"},
    )

    assert len(filtered_results) == 1
    assert filtered_results[0].metadata.get("category") == "guideline"