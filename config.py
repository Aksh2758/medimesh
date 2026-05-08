import os
from dotenv import load_dotenv
load_dotenv()

# ── LLM endpoint ──────────────────────────────────────────────────────
# For LOCAL (Ollama): set VLLM_BASE_URL=http://localhost:11434/v1
#                          VLLM_MODEL_NAME=llama3.1 or phi3 or mistral
# For AMD Cloud (vLLM): set VLLM_BASE_URL=http://YOUR_IP:8000/v1
VLLM_BASE_URL   = os.getenv("VLLM_BASE_URL",   "http://localhost:11434/v1")
VLLM_MODEL_NAME = os.getenv("VLLM_MODEL_NAME", "llama3.1")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY",  "ollama")   # dummy for local

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./rag/chroma_db")
APP_TITLE      = "MediMesh"

SEVERITY = {
    "GREEN":  {"label": "Non-Urgent",  "color": "#22c55e", "emoji": "🟢"},
    "YELLOW": {"label": "Urgent",      "color": "#eab308", "emoji": "🟡"},
    "RED":    {"label": "EMERGENCY",   "color": "#ef4444", "emoji": "🔴"},
}
