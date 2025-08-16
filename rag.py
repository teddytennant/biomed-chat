import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import redis
import pickle
import os
import config

# --- Globals ---
embedder = SentenceTransformer(config.RAG_MODEL)
dimension = embedder.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(dimension)
documents = []
redis_client = None

# --- Persistence ---

def initialize_persistence():
    """
    Initializes the persistence layer based on the configuration.
    """
    global redis_client
    if config.PERSISTENCE_TYPE == "redis":
        try:
            redis_client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD,
                db=0,
                socket_connect_timeout=5
            )
            redis_client.ping()
            print("Successfully connected to Redis.")
            load_rag_from_redis()
        except redis.exceptions.ConnectionError as e:
            print(f"Warning: Could not connect to Redis at {config.REDIS_HOST}:{config.REDIS_PORT}. Error: {e}")
            print("Falling back to in-memory RAG. No data will be persisted.")
            redis_client = None
    else:
        if os.path.exists(config.RAG_INDEX_PATH):
            print("Loading RAG index from file system.")
            load_rag_from_file()
        else:
            print("No RAG index file found. Starting with an empty index.")

def save_rag_index():
    """
    Saves the RAG index and documents to the configured persistence layer.
    """
    if redis_client:
        save_rag_to_redis()
    else:
        save_rag_to_file()

def load_rag_index():
    """
    Loads the RAG index and documents from the configured persistence layer.
    """
    if redis_client:
        load_rag_from_redis()
    else:
        load_rag_from_file()

# --- File-based Persistence ---

def save_rag_to_file():
    """Saves the FAISS index and documents to local files."""
    print(f"Saving RAG index to file: {config.RAG_INDEX_PATH}")
    faiss.write_index(index, config.RAG_INDEX_PATH)
    with open(config.RAG_DOCUMENTS_PATH, 'w', encoding='utf-8') as f:
        for doc in documents:
            f.write(doc + '\n')

def load_rag_from_file():
    """Loads the FAISS index and documents from local files."""
    global index, documents
    if os.path.exists(config.RAG_INDEX_PATH):
        index = faiss.read_index(config.RAG_INDEX_PATH)
        with open(config.RAG_DOCUMENTS_PATH, 'r', encoding='utf-8') as f:
            documents = [line.strip() for line in f.readlines()]
    else:
        print("No local RAG index found.")

# --- Redis-based Persistence ---

def save_rag_to_redis():
    """Saves the FAISS index and documents to Redis."""
    if not redis_client or index.ntotal == 0:
        return

    print("Saving RAG index to Redis...")
    try:
        # Serialize the FAISS index
        index_numpy = faiss.serialize_index(index)
        index_bytes = index_numpy.tobytes() # Convert numpy array to bytes
        
        pipe = redis_client.pipeline()
        pipe.set(config.REDIS_INDEX_KEY, index_bytes)
        pipe.delete(config.REDIS_DOCS_KEY)
        if documents:
            pipe.rpush(config.REDIS_DOCS_KEY, *documents)
        pipe.execute()
        print("Successfully saved RAG index to Redis.")
    except redis.exceptions.RedisError as e:
        print(f"Error saving RAG index to Redis: {e}")


def load_rag_from_redis():
    """Loads the FAISS index and documents from Redis."""
    global index, documents
    if not redis_client:
        return

    print("Loading RAG index from Redis...")
    try:
        index_bytes = redis_client.get(config.REDIS_INDEX_KEY)
        docs_list = redis_client.lrange(config.REDIS_DOCS_KEY, 0, -1)

        if index_bytes:
            # Convert bytes back to numpy array before deserializing
            index_numpy = np.frombuffer(index_bytes, dtype=np.uint8)
            index = faiss.deserialize_index(index_numpy)
            print(f"Loaded FAISS index with {index.ntotal} vectors from Redis.")
        else:
            index.reset()

        if docs_list:
            documents = [doc.decode('utf-8') for doc in docs_list]
            print(f"Loaded {len(documents)} documents from Redis.")
        else:
            documents = []

    except redis.exceptions.RedisError as e:
        print(f"Error loading RAG index from Redis: {e}")
        index.reset()
        documents = []

# --- Core RAG Functions ---

def add_to_rag(chunks):
    """
    Add text chunks to the RAG store.
    """
    if not chunks:
        return
    embeddings = embedder.encode(chunks)
    index.add(np.array(embeddings))
    documents.extend(chunks)

def retrieve_from_rag(query, top_k=None):
    """
    Retrieve top_k relevant chunks based on query similarity.
    """
    if top_k is None:
        top_k = config.RAG_TOP_K

    if index.ntotal == 0:
        return ""
        
    query_emb = embedder.encode([query])
    distances, indices = index.search(np.array(query_emb), top_k)
    
    relevant_chunks = [documents[i] for i in indices[0] if i < len(documents)]
    return "\n\n".join(relevant_chunks)
