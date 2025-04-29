import streamlit as st
from PyPDF2 import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Google API key not found. Please set GOOGLE_API_KEY in your .env file")
    st.stop()

# Step 1: Process the uploaded PDF
def process_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Step 2: Split text into chunks and create embeddings
def preprocess_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_text(text)
    
    # Initialize embeddings with API key
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY
    )
    
    # Create vector store in our case FAISS
    # Note: FAISS is a library for efficient similarity search and clustering of dense vectors
    vector_store = FAISS.from_texts(chunks, embeddings)
    return chunks, vector_store

# Step 3: Retrieve relevant chunks and generate answers
def retrieve_and_generate(query, vector_store):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        temperature=0.7,
        google_api_key=GOOGLE_API_KEY
    )
    
    # Create retrieval 
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )
    
    result = qa_chain({"query": query})
    answer = result["result"]
    source_chunks = [doc.page_content for doc in result["source_documents"]]
    
    return source_chunks, answer

# # Step 4: Define the Streamlit UI and some css styling

st.markdown("""
<style>
h1 {
    color: #811331 !important;
    text-align: center !important;
}

.stFileUploader > section > button {
    background-color:#811331 !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)


st.title("PDF-Based Q&A with RAG using Gemini🤗")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Process the uploaded PDF
    with st.spinner("Processing PDF..."):
        pdf_text = process_pdf(uploaded_file)
        chunks, vector_store = preprocess_text(pdf_text)
    st.success("PDF processed successfully!")
   
    query = st.text_input("Ask a question about the PDF:")
    
    if query:
        with st.spinner("Generating answer..."):
            try:
                retrieved_chunks, answer = retrieve_and_generate(query, vector_store)
                
                # Display retrieved chunks
                # st.subheader("Retrieved Context:")
                # for i, chunk in enumerate(retrieved_chunks, 1):
                #     st.write(f"Chunk {i}: {chunk}")
                #     st.write("---")
                
                # Display the generated answer
                st.subheader("Generated Answer:")
                st.write(answer)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
