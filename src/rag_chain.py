import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

def get_rag_chain(vector_store):
    """
    Creates a RAG chain linked to the provided vector store.
    
    Args:
        vector_store (FAISS): The vector store to retrieve from.
        
    Returns:
        Chain: A LangChain retrieval chain.
    """
    # Initialize Gemini
    # Ensure GOOGLE_API_KEY is in os.environ
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        google_api_key=os.environ.get("GOOGLE_API_KEY")
    )

    # Retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Prompt
    system_prompt = (
        "You are a helpful assistant. Answer the user's question based ONLY on the provided context. "
        "If the answer is not in the context, say 'I don't know'. "
        "\n\n"
        "Context: {context}"
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    # Create Chains
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain
