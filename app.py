import streamlit as st
import os
from dotenv import load_dotenv
from src.pdf_loader import load_pdf_documents
from src.vector_store import create_vector_store, load_vector_store
from src.rag_chain import get_rag_chain

# Load environment variables
load_dotenv()

st.set_page_config(page_title="DocuMind", page_icon="📄")

def main():
    st.title("DocuMind 📄")
    st.subheader("Private RAG Document Assistant")

    # Check for API Key
    if not os.environ.get("GOOGLE_API_KEY"):
        st.error("⚠️ GOOGLE_API_KEY is missing. Please add it to your .env file.")
        return

    # Sidebar: File Uploader
    with st.sidebar:
        st.header("Upload Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file:
            if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
                with st.spinner("Processing Document..."):
                    # Ingestion
                    chunks = load_pdf_documents(uploaded_file)
                    st.write(f"✅ Loaded {len(chunks)} chunks.")
                    
                    # Vector Store
                    vector_store = create_vector_store(chunks)
                    st.session_state.vector_store = vector_store
                    st.session_state.last_uploaded_file = uploaded_file.name
                    st.success("Analysis Complete!")
        
        # Reset Button
        if st.button("Clear Chat"):
            st.session_state.messages = []

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat Messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question about your document..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Response
        if "vector_store" in st.session_state:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    rag_chain = get_rag_chain(st.session_state.vector_store)
                    response = rag_chain.invoke({"input": prompt})
                    
                    answer = response["answer"]
                    sources = response.get("context", [])
                    
                    # Extract Page Numbers
                    page_numbers = set()
                    for doc in sources:
                        # PyPDFLoader usually stores page number in metadata 'page' (0-indexed)
                        page = doc.metadata.get("page", -1)
                        if page >= 0:
                            page_numbers.add(page + 1) # Convert to 1-indexed
                    
                    source_text = ""
                    if page_numbers:
                        source_list = sorted(list(page_numbers))
                        source_text = f"\n\n**Sources:** {', '.join([f'Page {p}' for p in source_list])}"
                    
                    final_response = answer + source_text
                    st.markdown(final_response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
        else:
             with st.chat_message("assistant"):
                st.warning("Please upload a PDF document first.")

if __name__ == "__main__":
    main()
