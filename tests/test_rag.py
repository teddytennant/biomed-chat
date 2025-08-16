import os
import pytest
import rag
import config
from unittest.mock import patch
import fakeredis

# Fixture to reset the RAG state before each test
@pytest.fixture(autouse=True)
def reset_rag_state():
    rag.index.reset()
    rag.documents.clear()
    rag.redis_client = None
    # Clean up any potential leftover files
    if os.path.exists(config.RAG_INDEX_PATH):
        os.remove(config.RAG_INDEX_PATH)
    if os.path.exists(config.RAG_DOCUMENTS_PATH):
        os.remove(config.RAG_DOCUMENTS_PATH)
    yield
    # Teardown after test
    if os.path.exists(config.RAG_INDEX_PATH):
        os.remove(config.RAG_INDEX_PATH)
    if os.path.exists(config.RAG_DOCUMENTS_PATH):
        os.remove(config.RAG_DOCUMENTS_PATH)

def test_add_and_retrieve():
    """Tests that basic adding and retrieving of documents works."""
    docs_to_add = [
        "CRISPR-Cas9 is a revolutionary gene-editing tool.",
        "The powerhouse of the cell is the mitochondria.",
    ]
    rag.add_to_rag(docs_to_add)
    retrieved_context = rag.retrieve_from_rag("Tell me about the gene-editing tool", top_k=1)
    assert "CRISPR-Cas9" in retrieved_context
    assert "mitochondria" not in retrieved_context

def test_retrieve_from_empty_rag():
    """Tests that retrieving from an empty RAG returns an empty string."""
    retrieved_context = rag.retrieve_from_rag("Any query")
    assert retrieved_context == ""

def test_file_persistence():
    """
    Tests that the RAG index and documents can be saved to and loaded from the file system.
    """
    config.PERSISTENCE_TYPE = "file"
    docs_to_add = ["This document tests file persistence."]
    rag.add_to_rag(docs_to_add)
    assert rag.index.ntotal == 1

    # Save to file
    rag.save_rag_index()

    # Reset in-memory RAG
    rag.index.reset()
    rag.documents.clear()
    assert rag.index.ntotal == 0

    # Load from file
    rag.load_rag_index()

    assert rag.index.ntotal == 1
    assert len(rag.documents) == 1
    assert "file persistence" in rag.documents[0]

@patch('rag.redis.Redis', fakeredis.FakeRedis)
def test_redis_persistence():
    """
    Tests that the RAG index and documents can be saved to and loaded from Redis.
    """
    config.PERSISTENCE_TYPE = "redis"
    
    # Initialize with the fake redis client
    rag.initialize_persistence()
    assert rag.redis_client is not None

    docs_to_add = ["This document tests Redis persistence."]
    rag.add_to_rag(docs_to_add)
    assert rag.index.ntotal == 1

    # Save to Redis
    rag.save_rag_index()

    # Reset in-memory RAG
    rag.index.reset()
    rag.documents.clear()
    assert rag.index.ntotal == 0

    # Load from Redis
    rag.load_rag_from_redis()

    assert rag.index.ntotal == 1
    assert len(rag.documents) == 1
    assert "Redis persistence" in rag.documents[0]
