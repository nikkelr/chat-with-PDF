"""REST API for Chat with PDF using FastAPI.

This API provides endpoints to upload PDFs and ask questions about them.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import uuid
import os
import tempfile
from datetime import datetime

from utils.pdf_processor import load_pdf, get_text_chunks, create_vector_store
from utils.chat_handler import create_conversation_chain, get_response
import config

# Initialize FastAPI app
app = FastAPI(
    title="Chat with PDF API",
    description="Upload PDFs and ask questions about their content using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (use Redis or database in production)
sessions: Dict[str, dict] = {}


# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    session_id: str


class QuestionResponse(BaseModel):
    answer: str
    session_id: str
    timestamp: str


class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    pdf_name: str
    num_chunks: int


class UploadResponse(BaseModel):
    session_id: str
    message: str
    pdf_name: str
    num_chunks: int


class HealthResponse(BaseModel):
    status: str
    api_configured: bool


# Background task to clean up old sessions
def cleanup_old_sessions():
    """Remove sessions older than 1 hour (customize as needed)."""
    # This is a placeholder - implement based on your requirements
    pass


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Chat with PDF API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload",
            "ask": "/ask",
            "sessions": "/sessions",
            "session_detail": "/sessions/{session_id}"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and configuration status."""
    api_configured = bool(
        config.OPENROUTER_API_KEY and 
        config.OPENROUTER_API_KEY != "your_openrouter_api_key_here"
    )
    
    return HealthResponse(
        status="healthy" if api_configured else "not_configured",
        api_configured=api_configured
    )


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a PDF file and create a new chat session.
    
    Args:
        file: PDF file to upload
        
    Returns:
        Session ID and processing information
    """
    # Validate API configuration
    if not config.OPENROUTER_API_KEY or config.OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        raise HTTPException(
            status_code=500,
            detail="OpenRouter API key not configured. Please set OPENROUTER_API_KEY in .env file"
        )
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Create temporary file to save uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process PDF
        try:
            # Open the temporary file for reading
            with open(temp_file_path, 'rb') as pdf_file:
                raw_text = load_pdf(pdf_file)
            
            text_chunks = get_text_chunks(raw_text)
            vector_store = create_vector_store(text_chunks)
            conversation_chain = create_conversation_chain(vector_store)
            
            # Create session
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                "conversation_chain": conversation_chain,
                "pdf_name": file.filename,
                "num_chunks": len(text_chunks),
                "created_at": datetime.now().isoformat(),
                "chat_history": [],
                "raw_text": raw_text  # Store for debugging
            }
            
            return UploadResponse(
                session_id=session_id,
                message="PDF processed successfully",
                pdf_name=file.filename,
                num_chunks=len(text_chunks)
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about an uploaded PDF.
    
    Args:
        request: Question and session ID
        
    Returns:
        AI-generated answer based on PDF content
    """
    # Validate session
    if request.session_id not in sessions:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please upload a PDF first."
        )
    
    try:
        session = sessions[request.session_id]
        conversation_chain = session["conversation_chain"]
        
        # Get response
        response = get_response(conversation_chain, request.question)
        
        # Store in chat history
        chat_entry = {
            "question": request.question,
            "answer": response["answer"],
            "timestamp": datetime.now().isoformat()
        }
        session["chat_history"].append(chat_entry)
        
        return QuestionResponse(
            answer=response["answer"],
            session_id=request.session_id,
            timestamp=chat_entry["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """
    List all active sessions.
    
    Returns:
        List of session information
    """
    return [
        SessionInfo(
            session_id=session_id,
            created_at=session_data["created_at"],
            pdf_name=session_data["pdf_name"],
            num_chunks=session_data["num_chunks"]
        )
        for session_id, session_data in sessions.items()
    ]


@app.get("/sessions/{session_id}", response_model=dict)
async def get_session(session_id: str):
    """
    Get detailed information about a specific session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session details including chat history
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Get sample text from first few chunks for debugging
    sample_text = ""
    if "raw_text" in session:
        sample_text = session["raw_text"][:500] + "..." if len(session.get("raw_text", "")) > 500 else session.get("raw_text", "")
    
    return {
        "session_id": session_id,
        "pdf_name": session["pdf_name"],
        "num_chunks": session["num_chunks"],
        "created_at": session["created_at"],
        "chat_history": session["chat_history"],
        "sample_text": sample_text  # For debugging - first 500 chars
    }


@app.delete("/sessions/{session_id}", response_model=dict)
async def delete_session(session_id: str):
    """
    Delete a session and free up resources.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Confirmation message
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    
    return {
        "message": f"Session {session_id} deleted successfully"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
