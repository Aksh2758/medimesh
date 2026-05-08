# 🏥 MediMesh
### Multi-Agent Health Triage for Rural Indian Clinics

> *"A nurse types symptoms. Three AI agents debate. A triage card appears in 60 seconds — no doctor required."*

Built for the **AMD Developer Hackathon** on lablab.ai · Track: AI Agents & Agentic Workflows

---

## The Problem

India has ~30,000 Primary Health Centres (PHCs) serving 800 million rural people — with a severe shortage of qualified doctors. A nurse alone must decide: **Is this child safe to go home, or do they need emergency referral?** A wrong call costs lives.

MediMesh gives that nurse a second opinion in 60 seconds.

---

## How It Works

Three specialised AI agents run sequentially over every patient case:

```
Patient Symptoms (free text)
        │
        ▼
┌─────────────────────┐
│  Agent 1: Triager   │  → GREEN / YELLOW / RED severity
└────────┬────────────┘
         │
         ▼
┌──────────────────────────┐
│  Agent 2: DDx Reasoner   │  → Top 3 differential diagnoses
└────────┬─────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Agent 3: Drug Safety Auditor│  → SAFE / CAUTION / UNSAFE
└─────────────────────────────┘
         │
         ▼
   📋 Triage Card → Nurse UI
```

Each agent is grounded in a **RAG layer** over:
- WHO IMCI Guidelines (25 indexed chunks)
- Indian drug interaction database (30 high-risk pairs)

---

## Tech Stack

| Layer | Tool |
|---|---|
| Agent Orchestration | CrewAI |
| LLM | Llama 3.1 8B Instruct |
| Inference Runtime | vLLM on AMD Developer Cloud (ROCm) |
| Vector Database | ChromaDB (local, persistent) |
| Knowledge Base | WHO IMCI Guidelines + Indian Pharmacopoeia |
| Frontend | Streamlit (Hindi + English) |
| Eval | 10 clinical vignettes with ground-truth labels |

---

## Evaluation Results

| Metric | Score |
|---|---|
| Triage Severity Accuracy | see `eval/eval_results.json` |
| Drug Safety Accuracy | see `eval/eval_results.json` |
| Avg Response Time | ~60 seconds |
| Vignettes Tested | 10 |

---

## Setup & Run

### 1. Clone and install
```bash
git clone https://github.com/YOUR_USERNAME/medimesh
cd medimesh
pip install -r requirements.txt
```

### 2. Configure AMD Cloud endpoint
```bash
cp .env.example .env
# Edit .env and set VLLM_BASE_URL to your AMD Developer Cloud instance IP
```

### 3. Ingest knowledge base
```bash
python rag/ingest.py
```

### 4. Run the app
```bash
streamlit run app.py
```

### 5. (Optional) Run evaluation
```bash
python eval/run_eval.py
```

---

## AMD Developer Cloud

MediMesh runs entirely on **AMD Developer Cloud** using:
- GPU instance with ROCm
- vLLM for OpenAI-compatible inference
- Llama 3.1 8B Instruct (open-source, no API key needed)

The RAG database is pre-indexed and local — meaning once set up, the system runs on **pre-cached knowledge** with no live internet dependency during inference. This makes it resilient for **low-bandwidth rural clinic environments**.

---

## Project Structure

```
medimesh/
├── app.py                    # Streamlit UI
├── crew.py                   # CrewAI orchestrator
├── config.py                 # Central config
├── requirements.txt
├── .env.example
├── agents/
│   ├── agents.py             # 3 agent definitions + system prompts
│   └── tasks.py              # Task definitions for each agent
├── rag/
│   ├── ingest.py             # One-time DB ingestion script
│   └── retriever.py          # Query functions used by agents
├── data/
│   ├── who_imci_guidelines.json   # 25 WHO IMCI chunks
│   └── drug_interactions.json     # 30 dangerous drug pairs
└── eval/
    ├── vignettes.py           # 10 clinical test cases
    ├── run_eval.py            # Evaluation runner
    └── eval_results.json      # Generated after running eval
```

---

## Limitations & Honest Notes

- MediMesh is a **decision support tool** — not a replacement for clinical judgment
- Drug interaction database covers 30 common pairs; not exhaustive
- LLM outputs should be validated by a qualified clinician before deployment
- Currently English-dominant; Hindi UI labels are provided for usability

---

## Built by

Solo submission for AMD Developer Hackathon | lablab.ai
*Track: AI Agents & Agentic Workflows*
