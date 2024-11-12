import streamlit as st
from openai import OpenAI
import os
from PyPDF2 import PdfReader

# Workaround for sqlite3 issue in Streamlit Cloud
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb

# Add custom CSS to hide the GitHub icon
hide_github_icon = """
#GithubIcon {
  visibility: hidden;
}
"""

# Hide Streamlit style elements
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .st-emotion-cache-30do4w.e3g6aar1 {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Function to ensure the OpenAI client is initialized
def ensure_openai_client():
    if 'openai_client' not in st.session_state:
        # Get the API key from Streamlit secrets
        api_key = st.secrets["openai"]
        # Initialize the OpenAI client and store it in session state
        st.session_state.openai_client = OpenAI(api_key=api_key)

# Function to create the ChromaDB collection
def create_lab4_collection():
    if 'Lab4_vectorDB' not in st.session_state:
        # Set up the ChromaDB client
        persist_directory = os.path.join(os.getcwd(), "chroma_db")
        client = chromadb.PersistentClient(path=persist_directory)
        collection = client.get_or_create_collection("Lab4Collection")

        ensure_openai_client()

        # Define the directory containing the PDF files
        pdf_dir = os.path.join(os.getcwd(), "Lab4_datafiles")
        if not os.path.exists(pdf_dir):
            st.error(f"Directory not found: {pdf_dir}")
            return None

        # Process each PDF file in the directory
        for filename in os.listdir(pdf_dir):
            if filename.endswith(".pdf"):
                filepath = os.path.join(pdf_dir, filename)
                try:
                    # Extract text from the PDF
                    with open(filepath, "rb") as file:
                        pdf_reader = PdfReader(file)
                        text = ''.join([page.extract_text() or '' for page in pdf_reader.pages])

                    # Generate embeddings for the extracted text
                    response = st.session_state.openai_client.embeddings.create(
                        input=text, model="text-embedding-3-small"
                    )
                    embedding = response.data[0].embedding

                    # Add the document to ChromaDB
                    collection.add(
                        documents=[text],
                        metadatas=[{"filename": filename}],
                        ids=[filename],
                        embeddings=[embedding]
                    )
                except Exception as e:
                    st.error(f"Error processing {filename}: {str(e)}")

        # Store the collection in session state
        st.session_state.Lab4_vectorDB = collection

    return st.session_state.Lab4_vectorDB

# Function to query the vector database
def query_vector_db(collection, query):
    ensure_openai_client()
    try:
        # Generate embedding for the query
        response = st.session_state.openai_client.embeddings.create(
            input=query, model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding

        # Query the ChromaDB collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        return results['documents'][0], [result['filename'] for result in results['metadatas'][0]]
    except Exception as e:
        st.error(f"Error querying the database: {str(e)}")
        return [], []

# Function to get chatbot response using OpenAI's GPT model
def get_chatbot_response(query, context, language_option, answer_option):
    ensure_openai_client()
    
    # Adjust the prompt based on summary and language options
    if answer_option == "Summarize in 100 words":
        prompt = f"Summarize the following document in 100 words in {language_option}: {context}"
    elif answer_option == "Summarize in 2 connecting paragraphs":
        prompt = f"Summarize the following document in 2 connecting paragraphs in {language_option}: {context}"
    elif answer_option == "Summarize in 5 bullet points":
        prompt = f"Summarize the following document in 5 bullet points in {language_option}: {context}"

    # Construct the prompt for the GPT model
    prompt += f"\n\nUser Question: {query}\nAnswer:"
    
    try:
        # Generate streaming response using OpenAI's chat completion
        response_stream = st.session_state.openai_client.chat.completions.create(
            model="gpt-4o",  # Using the latest GPT-4 model
            messages=[
                {"role": "system", "content": "You are a supportive assistant who will be assisting Summer Residential Counselors with their training materials. Please ensure that you provide them with helpful guidance."},
                {"role": "user", "content": prompt}
            ],
            stream=True  # Enable streaming
        )
        return response_stream
    except Exception as e:
        st.error(f"Error getting chatbot response: {str(e)}")
        return None

# Initialize session state for chat history, system readiness, and collection
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False
if 'collection' not in st.session_state:
    st.session_state.collection = None

# Page content

# Check if the system is ready, if not, prepare it
if not st.session_state.system_ready:
    with st.spinner("Processing documents and preparing the system..."):
        st.session_state.collection = create_lab4_collection()
        if st.session_state.collection:
            st.session_state.system_ready = True
            st.success("AI ChatBot is Ready!!!")
        else:
            st.error("Failed to create or load the document collection. Please check the file path and try again.")

# Only show the chat interface if the system is ready
if st.session_state.system_ready and st.session_state.collection:
    st.subheader("Chat with the AI Assistant")

    # Display chat history
    for message in st.session_state.chat_history:
        if isinstance(message, dict):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        elif isinstance(message, tuple):
            role, content = message
            with st.chat_message("user" if role == "You" else "assistant"):
                st.markdown(content)

    # Choose summary option
    answer_option = st.sidebar.selectbox(
        "Choose an Answer type:",
        ["Summarize in 100 words", "Summarize in 2 connecting paragraphs", "Summarize in 5 bullet points"]
    )
    
    # Dropdown menu for language selection
    language_option = st.selectbox(
        "Choose output language:",
        ["English", "French", "Spanish"]
    )

    # User input
    user_input = st.chat_input("Ask a question about the documents:")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        # Query the vector database
        relevant_texts, relevant_docs = query_vector_db(st.session_state.collection, user_input)
        context = "\n".join(relevant_texts)

        # Get streaming chatbot response with selected language
        response_stream = get_chatbot_response(user_input, context, language_option, answer_option)

        # Display AI response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            for chunk in response_stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)

        # Add to chat history (new format)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

        # Display relevant documents
        with st.expander("Relevant documents used"):
            for doc in relevant_docs:
                st.write(f"- {doc}")

