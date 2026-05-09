# 🏥 MediMesh
### Multi-Agent AI Health Triage for Rural Indian Clinics

> *"A nurse types symptoms. Three AI agents reason. A triage card appears in 60 seconds — no doctor required."*

Built for the **AMD Developer Hackathon** on lablab.ai · Track: **AI Agents & Agentic Workflows**

---

## The Problem

India has ~30,000 Primary Health Centres (PHCs) serving 800 million rural people — with a severe shortage of qualified doctors. A nurse alone must decide: **Is this patient safe to go home, or do they need emergency referral?** A wrong call costs lives.

MediMesh gives that nurse an AI second opinion in under 60 seconds.

---

## How It Works

Three specialised AI agents run in an optimised pipeline — Triager first, then DDx Reasoner and Drug Auditor **in parallel** to cut latency:

```
Patient Symptoms + Vitals + Medications (free text)
        │
        ▼ RAG retrieval (ChromaDB — WHO IMCI + Drug DB)
        │
        ▼
┌─────────────────────┐
│  Agent 1: Triager   │  → 🟢 GREEN / 🟡 YELLOW / 🔴 RED severity
└────────┬────────────┘
         │
    ┌────┴────┐  (parallel)
    ▼         ▼
┌──────────┐  ┌──────────────────────┐
│ Agent 2  │  │      Agent 3         │
│  DDx     │  │  Drug Safety Auditor │
│ Reasoner │  │                      │
└──────────┘  └──────────────────────┘
    │               │
    └───────┬────────┘
            ▼
   📋 Triage Card → Nurse UI
   Severity · Top 3 Diagnoses · Drug Safety · Action
```

Each agent is grounded in a **local RAG layer** over:
- WHO IMCI Guidelines (25 indexed chunks in ChromaDB)
- Indian PHC drug interaction database (30 high-risk pairs)

---

## Tech Stack

| Layer | Tool |
|---|---|
| Agent Orchestration | CrewAI |
| LLM (production) | Llama 3.2 1b Instruct via AMD Developer Cloud + vLLM |
| LLM (demo / fast) | Llama 3 1b via Groq API (free tier) |
| Inference Runtime | vLLM on AMD ROCm |
| Vector Database | ChromaDB (local, persistent, no internet at inference) |
| Knowledge Base | WHO IMCI Guidelines + Indian Pharmacopoeia |
| Frontend | Streamlit (Hindi + English bilingual UI) |
| Eval | 10 clinical vignettes with ground-truth severity labels |

---

## Demo Scenarios

Three one-click scenarios pre-loaded in the sidebar:

| Scenario | Expected Output |
|---|---|
| 🟢 Female, 5yo — Mild fever, runny nose, alert | GREEN — Non-urgent, manage at PHC |
| 🟡 Male, 3yo — Fever, RR 44/min, no chest indrawing | YELLOW — Pneumonia, amoxicillin |
| 🔴 Male, 8mo — Lethargic, sunken eyes, cannot drink | RED — Severe dehydration, refer immediately |

---

## Evaluation Results

| Metric | Result |
|---|---|
| Triage Severity Accuracy | see `eval/eval_results.json` |
| Drug Safety Accuracy | see `eval/eval_results.json` |
| Avg Response Time (Groq) | ~15 seconds |
| Avg Response Time (local CPU) | ~60 seconds |
| Clinical Vignettes Tested | 10 |

---

## Setup & Run

### 1. Clone and install
```bash
git clone https://github.com/YOUR_USERNAME/medimesh
cd medimesh
pip install -r requirements.txt
```

### 2. Configure your LLM backend

Copy the example env file:
```bash
cp .env.example .env
```

**Option A — Groq (recommended for demo, free):**
Get a free API key at [console.groq.com](https://console.groq.com), then add to `.env`:
```
GROQ_API_KEY=gsk_your_key_here
```
The app auto-detects Groq when this key is present.

**Option B — Local Ollama:**
```bash
ollama pull llama3.2:1b
```
Set in `.env`:
```
VLLM_BASE_URL=http://localhost:11434/v1
VLLM_MODEL_NAME=llama3.2:1b
OPENAI_API_KEY=ollama
```

**Option C — AMD Developer Cloud (production):**
```
VLLM_BASE_URL=http://YOUR_AMD_INSTANCE_IP:8000/v1
VLLM_MODEL_NAME=meta-llama/Meta-Llama-3.2-1b-Instruct
OPENAI_API_KEY=not-needed
```

### 3. Ingest knowledge base (run once)
```bash
python rag/ingest.py
```
This populates ChromaDB with WHO IMCI guidelines and drug interaction data locally.

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

MediMesh is architected for **AMD Developer Cloud** using:
- GPU instance with ROCm
- vLLM for OpenAI-compatible inference endpoint
- Llama 3.2 1b Instruct (open-source, no per-query API cost)

The RAG database is pre-indexed at setup time — inference requires **zero live internet**. This makes MediMesh resilient for low-bandwidth rural clinic environments and scalable across India's 30,000 PHCs at minimal cost.

---

## Project Structure

```
medimesh/
├── app.py                         # Streamlit UI (bilingual, dark theme)
├── crew.py                        # CrewAI orchestrator (parallel pipeline)
├── config.py                      # Central config + Groq/Ollama/AMD switch
├── requirements.txt
├── .env.example
├── agents/
│   ├── agents.py                  # 3 agent definitions + system prompts
│   └── tasks.py                   # Task prompts for each agent
├── rag/
│   ├── ingest.py                  # One-time ChromaDB ingestion script
│   └── retriever.py               # RAG query functions used by agents
├── data/
│   ├── who_imci_guidelines.json   # 25 WHO IMCI guideline chunks
│   └── drug_interactions.json     # 30 dangerous drug pairs (Indian PHC context)
└── eval/
    ├── vignettes.py               # 10 clinical test cases with ground truth
    ├── run_eval.py                # Evaluation runner + accuracy report
    └── eval_results.json          # Generated output — include in submission
```

---

## Limitations & Honest Notes

- MediMesh is a **clinical decision support tool** — not a replacement for qualified medical judgment
- Drug interaction database covers 30 common pairs relevant to Indian PHCs; not exhaustive
- LLM outputs must be validated by a clinician before real-world deployment
- Hindi labels in UI improve usability; full Hindi output requires a fine-tuned model
- Severity classification accuracy depends on model size — larger models (1b+) perform significantly better than 1B models

---

## Built by

Solo submission · AMD Developer Hackathon | lablab.ai
**Track: AI Agents & Agentic Workflows**
