# REST API Documentation

## Overview

The Chat with PDF REST API allows you to upload PDF documents and ask questions about their content using AI. This is a FastAPI-based service that provides a programmatic interface without requiring the Streamlit UI.

## Base URL

```
http://localhost:8000
```

## Quick Start

### 1. Install Additional Dependencies

```bash
conda activate chat-with-pdf
pip install -r requirements-api.txt
```

### 2. Start the API Server

```bash
python api.py
```

Or using uvicorn directly:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access API Documentation

FastAPI provides interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

Check if the API is running and properly configured.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "api_configured": true
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Upload PDF

Upload a PDF file and create a new chat session.

**Endpoint:** `POST /upload`

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "PDF processed successfully",
  "pdf_name": "document.pdf",
  "num_chunks": 42
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@/path/to/document.pdf"
```

**Example with Python:**
```python
import requests

with open('document.pdf', 'rb') as f:
    files = {'file': ('document.pdf', f, 'application/pdf')}
    response = requests.post('http://localhost:8000/upload', files=files)
    data = response.json()
    session_id = data['session_id']
```

---

### 3. Ask Question

Ask a question about an uploaded PDF.

**Endpoint:** `POST /ask`

**Request:**
```json
{
  "question": "What is the main topic of this document?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "answer": "The main topic of this document is...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-12-30T16:12:24.123456"
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Example with Python:**
```python
import requests

payload = {
    "question": "What is this document about?",
    "session_id": session_id
}

response = requests.post(
    'http://localhost:8000/ask',
    json=payload
)
data = response.json()
print(data['answer'])
```

---

### 4. List Sessions

Get a list of all active sessions.

**Endpoint:** `GET /sessions`

**Response:**
```json
[
  {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-12-30T16:00:00.000000",
    "pdf_name": "document.pdf",
    "num_chunks": 42
  }
]
```

**Example:**
```bash
curl http://localhost:8000/sessions
```

---

### 5. Get Session Details

Get detailed information about a specific session, including chat history.

**Endpoint:** `GET /sessions/{session_id}`

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "pdf_name": "document.pdf",
  "num_chunks": 42,
  "created_at": "2025-12-30T16:00:00.000000",
  "chat_history": [
    {
      "question": "What is this about?",
      "answer": "This document is about...",
      "timestamp": "2025-12-30T16:01:00.000000"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/sessions/550e8400-e29b-41d4-a716-446655440000
```

---

### 6. Delete Session

Delete a session and free up resources.

**Endpoint:** `DELETE /sessions/{session_id}`

**Response:**
```json
{
  "message": "Session 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/sessions/550e8400-e29b-41d4-a716-446655440000
```

---

## Error Handling

The API uses standard HTTP status codes:

- **200**: Success
- **400**: Bad Request (e.g., invalid file type)
- **404**: Not Found (e.g., session doesn't exist)
- **500**: Internal Server Error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Examples

### Complete Workflow Example

```python
import requests

API_URL = "http://localhost:8000"

# 1. Check health
health = requests.get(f"{API_URL}/health").json()
print(f"API Status: {health['status']}")

# 2. Upload PDF
with open('document.pdf', 'rb') as f:
    files = {'file': ('document.pdf', f, 'application/pdf')}
    upload_response = requests.post(f"{API_URL}/upload", files=files)
    session_id = upload_response.json()['session_id']
    print(f"Session created: {session_id}")

# 3. Ask questions
questions = [
    "What is the main topic?",
    "Can you summarize the key points?",
    "What are the conclusions?"
]

for question in questions:
    response = requests.post(
        f"{API_URL}/ask",
        json={"question": question, "session_id": session_id}
    )
    answer = response.json()['answer']
    print(f"\nQ: {question}")
    print(f"A: {answer}")

# 4. Get session history
session_details = requests.get(f"{API_URL}/sessions/{session_id}").json()
print(f"\nTotal questions asked: {len(session_details['chat_history'])}")

# 5. Clean up
requests.delete(f"{API_URL}/sessions/{session_id}")
print("Session deleted")
```

### Using the Example Script

We've provided a ready-to-use example script:

```bash
python examples/api_example.py
```

Or using bash/curl:

```bash
./examples/test_api.sh
```

## Session Management

### Session Lifecycle

1. **Create**: Upload a PDF to create a new session
2. **Use**: Ask questions using the session ID
3. **Monitor**: Check session details and chat history
4. **Delete**: Remove session when done to free resources

### Important Notes

- Sessions are stored **in-memory** by default
- Sessions will be lost when the server restarts
- For production, consider using Redis or a database
- Implement session cleanup for long-running deployments

## Production Considerations

### 1. Session Storage

Replace in-memory storage with a persistent solution:

```python
# Use Redis
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Or use a database
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@localhost/dbname')
```

### 2. File Storage

Store uploaded PDFs if needed:

```python
import shutil
pdf_storage_path = "/app/uploads"
shutil.copy(temp_file_path, f"{pdf_storage_path}/{session_id}.pdf")
```

### 3. CORS Configuration

Update for your specific domain:

```python
allow_origins=["https://yourdomain.com"]
```

### 4. Rate Limiting

Add rate limiting middleware:

```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### 5. Authentication

Add API key authentication:

```python
from fastapi.security import APIKeyHeader
api_key_header = APIKeyHeader(name="X-API-Key")
```

## Testing

### Run the Example Script

```bash
# Make sure the API is running
python api.py

# In another terminal
conda activate chat-with-pdf
python examples/api_example.py
```

### Using Postman

1. Import the API into Postman
2. Create a new collection
3. Add requests for each endpoint
4. Test the workflow

### Using HTTPie

```bash
# Upload
http --form POST localhost:8000/upload file@document.pdf

# Ask
echo '{"question": "What is this?", "session_id": "YOUR_SESSION_ID"}' | \
  http POST localhost:8000/ask
```

## Troubleshooting

### API Key Not Configured

```json
{
  "detail": "OpenRouter API key not configured"
}
```

**Solution:** Add your API key to `.env` file

### Session Not Found

```json
{
  "detail": "Session not found. Please upload a PDF first."
}
```

**Solution:** Upload a PDF first to create a session

### Only PDF Files Supported

```json
{
  "detail": "Only PDF files are supported"
}
```

**Solution:** Ensure you're uploading a `.pdf` file

## Performance Tips

1. **Chunk Size**: Adjust `CHUNK_SIZE` in `config.py` for better results
2. **Concurrent Requests**: Use async clients for multiple requests
3. **Caching**: Consider caching frequently asked questions
4. **Vector Store**: For large PDFs, consider persistent vector stores

## Next Steps

- Add authentication and authorization
- Implement rate limiting
- Add support for multiple file formats
- Implement persistent session storage
- Add metrics and monitoring
- Deploy to production (Docker, Kubernetes, etc.)
