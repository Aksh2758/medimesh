# MediMesh — Local Setup (Ollama)

## Why local? AMD Cloud credits delayed? No problem.
This setup runs the exact same stack locally using Ollama.
For the hackathon judges: the AMD Cloud version uses identical code —
just swap the endpoint URL.

---

## Step 1 — Install Ollama
```bash
# Mac / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: download from https://ollama.com
```

## Step 2 — Pull the model
```bash
ollama pull llama3.1       # 4.7GB — best quality
# OR if low RAM:
ollama pull phi3           # 2.3GB — faster, smaller
ollama pull mistral        # 4.1GB — good alternative
```

## Step 3 — Start Ollama server
```bash
ollama serve
# Runs on http://localhost:11434 — leave this terminal open
```

## Step 4 — Project setup
```bash
git clone https://github.com/YOUR_USERNAME/medimesh
cd medimesh
pip install -r requirements.txt

# config.py already defaults to localhost:11434 — no .env changes needed!
```

## Step 5 — Ingest knowledge base (one time)
```bash
python rag/ingest.py
```

## Step 6 — Run
```bash
streamlit run app.py
# Open http://localhost:8501
```

---

## Switching to AMD Cloud later
Just set these in your .env:
```
VLLM_BASE_URL=http://YOUR_AMD_INSTANCE_IP:8000/v1
VLLM_MODEL_NAME=meta-llama/Meta-Llama-3.1-8B-Instruct
OPENAI_API_KEY=not-needed
```
Zero code changes. Same app.

---

## Expected performance
| Hardware       | Approx response time |
|----------------|---------------------|
| Mac M1/M2      | 12–18 seconds       |
| GPU (NVIDIA)   | 8–12 seconds        |
| AMD Ryzen AI   | 10–15 seconds       |
| AMD Cloud vLLM | 8–12 seconds        |
| CPU only       | 45–90 seconds       |

