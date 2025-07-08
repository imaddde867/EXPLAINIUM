"""
Vector embedding and semantic search utilities for EXPLAINIUM Phase 2
"""
from sentence_transformers import SentenceTransformer
import chromadb

# Load embedding model (can be replaced with a more advanced one)
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB client
chroma_client = chromadb.Client()

# Example: Embed a document

def embed_text(text: str):
    return EMBEDDING_MODEL.encode([text])[0]

# Example: Add document to ChromaDB

def add_document_to_chroma(doc_id: str, text: str):
    embedding = embed_text(text)
    chroma_client.insert(collection_name="documents", ids=[doc_id], embeddings=[embedding], metadatas=[{"text": text}])

# Example: Semantic search

def semantic_search(query: str, top_k: int = 5):
    query_vec = embed_text(query)
    results = chroma_client.query(collection_name="documents", query_embeddings=[query_vec], n_results=top_k)
    return results
