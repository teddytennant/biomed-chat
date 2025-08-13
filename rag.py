# rag.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embedding model (lightweight and effective for biomedical text)
embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Or 'biobert-v1.1-pubmed' for more domain-specific

# Initialize FAISS index (vector store)
dimension = 384  # Matches the embedder's output size
index = faiss.IndexFlatL2(dimension)  # Simple L2 distance index
documents = []  # List to store original text chunks (parallel to vectors)

def add_to_rag(chunks):
    """
    Add text chunks (e.g., tool outputs) to the RAG store.
    :param chunks: List of strings (e.g., ['Abstract: ...', 'Simulation result: ...'])
    """
    global documents
    embeddings = embedder.encode(chunks)
    index.add(np.array(embeddings))
    documents.extend(chunks)  # Keep original texts

def retrieve_from_rag(query, top_k=3):
    """
    Retrieve top_k relevant chunks based on query similarity.
    :return: String of concatenated relevant chunks (for prompt injection)
    """
    if index.ntotal == 0:
        return ""  # No data yet
    query_emb = embedder.encode([query])
    distances, indices = index.search(np.array(query_emb), top_k)
    relevant_chunks = [documents[i] for i in indices[0] if i < len(documents)]
    return "\n\n".join(relevant_chunks)  # Format for easy prompt appending

# Optional: Persistence (save/load index for sessions)
def save_rag_index(file_path='rag_index.faiss'):
    faiss.write_index(index, file_path)
    with open('documents.txt', 'w') as f:
        f.write('\n'.join(documents))

def load_rag_index(file_path='rag_index.faiss'):
    global index, documents
    index = faiss.read_index(file_path)
    with open('documents.txt', 'r') as f:
        documents = f.read().splitlines()
