import os
import pytest
import rag  # Import the module itself to avoid stale global variables

# A fixture to ensure the RAG index is reset for each test
@pytest.fixture(autouse=True)
def reset_rag_index():
    # Access and reset the global state via the module
    rag.index.reset()
    rag.documents.clear()
    yield
    # Teardown: clean up any created files
    if os.path.exists("test_rag_index.faiss"):
        os.remove("test_rag_index.faiss")
    if os.path.exists("documents.txt"):
        # The rag.py module hardcodes 'documents.txt', so we clean it up
        os.remove("documents.txt")

def test_add_and_retrieve():
    """Tests that basic adding and retrieving of documents works."""
    docs_to_add = [
        "CRISPR-Cas9 is a revolutionary gene-editing tool.",
        "The powerhouse of the cell is the mitochondria.",
    ]
    rag.add_to_rag(docs_to_add)

    # Use top_k=1 to get the most relevant document and make the test deterministic
    retrieved_context = rag.retrieve_from_rag(
        "Tell me about the gene-editing tool", top_k=1
    )
    assert "CRISPR-Cas9" in retrieved_context
    assert "mitochondria" not in retrieved_context

def test_retrieve_from_empty_rag():
    """Tests that retrieving from an empty RAG returns an empty string."""
    retrieved_context = rag.retrieve_from_rag("Any query")
    assert retrieved_context == ""

def test_persistence():
    """
    Tests that the RAG index and documents can be saved to and loaded from disk.
    """
    docs_to_add = ["This document tests the persistence feature."]
    rag.add_to_rag(docs_to_add)

    assert rag.index.ntotal == 1

    # Save the index to a test-specific file
    rag.save_rag_index(file_path='test_rag_index.faiss')

    # Reset the in-memory index to simulate an application restart
    rag.index.reset()
    rag.documents.clear()
    assert rag.index.ntotal == 0

    # Load the index from the test-specific file
    rag.load_rag_index(file_path='test_rag_index.faiss')

    # Check if the data was loaded correctly
    assert rag.index.ntotal == 1
    assert len(rag.documents) == 1
    assert "persistence feature" in rag.documents[0]

    # Verify that retrieval works after loading
    retrieved_context = rag.retrieve_from_rag("persistence")
    assert "persistence feature" in retrieved_context