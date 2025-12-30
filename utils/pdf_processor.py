"""PDF processing utilities for extracting and chunking text from PDF documents."""

from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import config


def load_pdf(pdf_file):
    """
    Load and extract text from a PDF file.
    
    Args:
        pdf_file: Uploaded PDF file object
        
    Returns:
        str: Extracted text from the PDF
    """
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def get_text_chunks(text):
    """
    Split text into chunks for processing.
    
    Args:
        text (str): Input text to split
        
    Returns:
        list: List of text chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def create_vector_store(text_chunks):
    """
    Create a FAISS vector store from text chunks.
    
    Args:
        text_chunks (list): List of text chunks
        
    Returns:
        FAISS: Vector store with embeddings
    """
    # Use HuggingFace embeddings instead of OpenAI
    # OpenRouter doesn't support the embeddings API endpoint
    from langchain_community.embeddings import HuggingFaceEmbeddings
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vector_store = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vector_store
