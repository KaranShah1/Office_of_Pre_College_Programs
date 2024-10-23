import streamlit as st
from openai import OpenAI
import os
from PyPDF2 import PdfReader

# Workaround for sqlite3 issue in Streamlit Cloud
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb

# Function to ensure the OpenAI client is initialized
def ensure_openai_client():
    if 'openai_client' not in st.session_state:
        api_key = st.secrets["openai"]
        st.session_state.openai_client = OpenAI(api_key=api_key)

# Function to create the ChromaDB collection (RAG-based)
def create_lab4_collection():
    if 'Lab4_vectorDB' not in st.session_state:
        persist_directory = os.path.join(os.getcwd(), "chroma_db")
        client = chromadb.PersistentClient(path=persist_directory)
        collection = client.get_or_create_collection("Lab4Collection")

        ensure_openai_client()

        # Directory containing the documents uploaded via RAGs
        pdf_dir = os.path.join(os.getcwd(), "Lab4_datafiles")
        if not os.path.exists(pdf_dir):
            st.error(f"Directory not found: {pdf_dir}")
            return None

        for filename in os.listdir(pdf_dir):
            if filename.endswith(".pdf"):
                filepath = os.path.join(pdf_dir, filename)
                try:
                    with open(filepath, "rb") as file:
                        pdf_reader = PdfReader(file)
                        text = ''.join([page.extract_text() or '' for page in pdf_reader.pages])

                    # Generate embeddings for extracted text
                    response = st.session_state.openai_client.embeddings.create(
                        input=text, model="text-embedding-ada-002"
                    )
                    embedding = response.data[0].embedding

                    # Add document to ChromaDB
                    collection.add(
                        documents=[text],
                        metadatas=[{"filename": filename}],
                        ids=[filename],
                        embeddings=[embedding]
                    )
                except Exception as e:
                    st.error(f"Error processing {filename}: {str(e)}")

        st.session_state.Lab4_vectorDB = collection

    return st.session_state.Lab4_vectorDB

# Function to summarize document based on user choice
def summarize_document(document, summary_option, language_option):
    ensure_openai_client()

    if summary_option == "Summarize in 5 bullet points":
        prompt = f"Summarize the following document in 5 bullet points: {document}"
    elif summary_option == "Summarize in 2 connecting paragraphs":
        prompt = f"Summarize the following document in 2 connecting paragraphs: {document}"

    prompt += f"\n\nOutput the summary in {language_option}."

    try:
        response = st.session_state.openai_client.completions.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=300
        )
        return response.choices[0].text.strip()
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

# Check if system is ready, if not, prepare it
if not st.session_state.get("system_ready", False):
    with st.spinner("Processing documents and preparing the system..."):
        st.session_state.collection = create_lab4_collection()
        if st.session_state.collection:
            st.session_state.system_ready = True
            st.success("System is ready!")
        else:
            st.error("Failed to load the document collection. Check file paths and try again.")

# Interface for document interaction
if st.session_state.get("system_ready", False):
    st.subheader("Training Document Summary Tool")

    # User option for summary type
    summary_option = st.selectbox(
        "How would you like the document summarized?",
        ["Summarize in 5 bullet points", "Summarize in 2 connecting paragraphs"]
    )

    # Dropdown for language option
    language_option = st.selectbox(
        "Choose output language:",
        ["English", "Chinese", "Spanish"]
    )

    # If a document has been uploaded in the backend via RAGs
    if st.session_state.collection:
        user_input = st.text_area("Ask a question or request a summary:")
        
        if user_input:
            relevant_texts, relevant_docs = query_vector_db(st.session_state.collection, user_input)
            context = "\n".join(relevant_texts)
            
            # Generate summary based on options
            summary = summarize_document(context, summary_option, language_option)
            
            if summary:
                st.subheader("Summary")
                st.write(summary)
                st.expander("Relevant documents", expanded=False).write(relevant_docs)

else:
    st.info("System is preparing. Please wait...")
