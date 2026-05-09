import os
from dotenv import load_dotenv
load_dotenv()

VLLM_BASE_URL   = os.getenv("VLLM_BASE_URL", "http://localhost:11434/v1")
VLLM_MODEL_NAME = os.getenv("VLLM_MODEL_NAME", "llama3.2:1b")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "ollama")
CHROMA_DB_PATH  = os.getenv("CHROMA_DB_PATH", "./rag/chroma_db")
APP_TITLE       = os.getenv("APP_TITLE", "MediMesh")

# Groq support — set GROQ_API_KEY in .env to enable
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
USE_GROQ     = bool(GROQ_API_KEY)

SEVERITY = {
    "GREEN":  {"label": "Non-urgent",  "color": "#22c55e", "emoji": "🟢"},
    "YELLOW": {"label": "Urgent",      "color": "#eab308", "emoji": "🟡"},
    "RED":    {"label": "Emergency",   "color": "#ef4444", "emoji": "🔴"},
}
