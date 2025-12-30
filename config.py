"""Configuration settings for the Chat with PDF application."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "ChatWithPDF")
OPENROUTER_APP_URL = os.getenv("OPENROUTER_APP_URL", "http://localhost:8501")

# Document Processing Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# LLM Configuration
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# OpenRouter API Base URL
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
