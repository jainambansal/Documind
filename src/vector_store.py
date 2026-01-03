import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize embeddings globally to be reused
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def create_vector_store(text_chunks, index_path="faiss_index"):
    """
    Creates a FAISS vector store from text chunks and saves it locally.
    
    Args:
        text_chunks (list): List of Document chunks.
        index_path (str): Path to save the FAISS index.
        
    Returns:
        FAISS: The vector store object.
    """
    vector_store = FAISS.from_documents(text_chunks, embedding=embeddings)
    vector_store.save_local(index_path)
    return vector_store

def load_vector_store(index_path="faiss_index"):
    """
    Loads a FAISS vector store from a local folder.
    
    Args:
        index_path (str): Path to the saved FAISS index.
        
    Returns:
        FAISS: The vector store object, or None if not found.
    """
    if os.path.exists(index_path):
        return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    return None
