# Chat with PDF - REST API 📄🔌

A REST API application that allows you to upload PDF documents and ask questions about their content using LangChain and OpenRouter.

## 🌟 Features

- **PDF Processing**: Upload and process PDF documents of any size
- **Intelligent Q&A**: Ask questions and get accurate answers based on PDF content
- **Vector Search**: Uses FAISS for efficient semantic search with local embeddings
- **Multiple LLM Support**: Compatible with any OpenRouter-supported model
- **Session Management**: Track multiple chat sessions
- **REST API**: Full HTTP API for easy integration

## 🛠️ Technology Stack

- **FastAPI**: Modern Python web framework
- **LangChain**: Framework for LLM applications
- **OpenRouter**: Access to multiple LLM providers
- **FAISS**: Vector database for embeddings
- **Sentence Transformers**: Local embedding generation (free, no API calls)
- **PyPDF2**: PDF text extraction

## 📋 Prerequisites

- Python 3.10+
- Conda (Anaconda or Miniconda)
- OpenRouter API key ([Get one here](https://openrouter.ai/))

## 🚀 Setup Instructions

### 1. Create Conda Environment

```bash
conda create -n chat-with-pdf python=3.10 -y
conda activate chat-with-pdf
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-api.txt
```

### 3. Configure Environment Variables

Copy the example environment file and add your OpenRouter API key:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
OPENROUTER_API_KEY=your_actual_api_key_here
OPENROUTER_MODEL=openai/gpt-3.5-turbo  # or any other OpenRouter model
```

### 4. Run the API

```bash
python api.py
```

The API will be available at `http://localhost:8000`

**Interactive API Documentation:** `http://localhost:8000/docs`

## 📖 Usage Guide

### Quick Example

```python
import requests

# Upload PDF
with open('document.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/upload', 
                           files={'file': f})
    session_id = response.json()['session_id']

# Ask question
response = requests.post('http://localhost:8000/ask',
                        json={
                            'question': 'What is this document about?',
                            'session_id': session_id
                        })
print(response.json()['answer'])
```

### Test the API

```bash
# Quick test script
python test_pdf_context.py yourfile.pdf "What is this document about?"

# Or use the interactive example
python examples/api_example.py

# Or use bash/curl
./examples/test_api.sh
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API health |
| POST | `/upload` | Upload PDF file |
| POST | `/ask` | Ask question |
| GET | `/sessions` | List all sessions |
| GET | `/sessions/{id}` | Get session details |
| DELETE | `/sessions/{id}` | Delete session |

**Full API Documentation:** See [API_DOCUMENTATION.md](file:///home/agira/development/AI/lang-chai/API_DOCUMENTATION.md)

## ⚙️ Configuration

You can customize the application by modifying `config.py`:

- **CHUNK_SIZE**: Size of text chunks (default: 1000)
- **CHUNK_OVERLAP**: Overlap between chunks (default: 200)
- **TEMPERATURE**: LLM creativity (0-1, default: 0.7)
- **MAX_TOKENS**: Maximum response length (default: 1000)

## 🤖 Supported Models

You can use any model available on OpenRouter. Popular options include:

- `openai/gpt-3.5-turbo` (fast and cost-effective)
- `openai/gpt-4` (most capable)
- `anthropic/claude-2` (excellent for long documents)
- `meta-llama/llama-2-70b-chat` (open-source alternative)

Update the `OPENROUTER_MODEL` in your `.env` file to change models.

## 📁 Project Structure

```
lang-chai/
├── api.py                      # FastAPI REST API
├── config.py                   # Configuration settings
├── requirements.txt            # Core dependencies
├── requirements-api.txt        # API-specific dependencies
├── .env.example               # Environment variables template
├── .env                       # Your environment variables (create this)
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── API_DOCUMENTATION.md       # Full API reference
├── CONTEXT_FIX.md            # Context retrieval fix notes
├── TROUBLESHOOTING.md        # Troubleshooting guide
├── test_pdf_context.py       # Quick test script
├── utils/
│   ├── __init__.py           # Package initialization
│   ├── pdf_processor.py      # PDF processing (local embeddings)
│   └── chat_handler.py       # Chat and LLM logic (RetrievalQA)
└── examples/
    ├── api_example.py         # Python API example
    └── test_api.sh           # Bash/curl API example
```

## 🔍 How It Works

1. **PDF Upload**: User uploads a PDF via API
2. **Text Extraction**: PyPDF2 extracts text from all pages
3. **Text Chunking**: Text is split into manageable chunks
4. **Local Embeddings**: Sentence-transformers creates embeddings on your machine
5. **Vector Store**: Chunks are stored in FAISS for efficient retrieval
6. **Question Processing**: User asks a question via API
7. **Semantic Search**: Most relevant chunks are retrieved
8. **LLM Response**: OpenRouter LLM generates an answer based on context
9. **Session Tracking**: All interactions stored per session

## 🐛 Troubleshooting

### API Key Error
- Make sure you've created a `.env` file (not `.env.example`)
- Verify your OpenRouter API key is correct
- Check that the key has sufficient credits

### PDF Processing Error
- Ensure the PDF is not password-protected
- Try a different PDF to isolate the issue
- Check if the PDF contains extractable text (not just images)

### Context Not Working
- See [CONTEXT_FIX.md](file:///home/agira/development/AI/lang-chai/CONTEXT_FIX.md) for details
- Use the test script: `python test_pdf_context.py your.pdf`
- Check [TROUBLESHOOTING.md](file:///home/agira/development/AI/lang-chai/TROUBLESHOOTING.md) for common issues

### Port Already in Use
- Check if API is already running: `ps aux | grep api.py`
- Change port: `uvicorn api:app --port 8001`

## 💡 Tips for Best Results

- Ask specific, focused questions
- For long documents, break complex queries into smaller questions
- Use the session details endpoint to verify PDF extraction
- Try different phrasings if you don't get satisfactory answers

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

**Happy Chatting with your PDFs! 📄💬**
