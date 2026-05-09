"""
MediMesh agents — supports both Groq and Ollama via .env switch.
Switch to Groq for demo: set GROQ_API_KEY in .env
"""
import warnings, os
warnings.filterwarnings("ignore")
os.environ["OTEL_SDK_DISABLED"] = "true"

from crewai import Agent
from langchain_openai import ChatOpenAI
from config import VLLM_BASE_URL, VLLM_MODEL_NAME, OPENAI_API_KEY, GROQ_API_KEY, USE_GROQ

def _llm():
    if USE_GROQ:
        # Groq: ~3-5s per agent, free tier, great quality
        return ChatOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY,
            model="llama-3.1-8b-instant",   # Llama 3.1 8B on Groq — fast + accurate
            temperature=0.1,
            max_tokens=300,
        )
    else:
        # Local Ollama fallback
        return ChatOpenAI(
            base_url=VLLM_BASE_URL,
            api_key=OPENAI_API_KEY,
            model=VLLM_MODEL_NAME,
            temperature=0.1,
            max_tokens=300,
        )

def get_triager_agent():
    return Agent(
        role="Triage Nurse",
        goal="Assign triage severity. First line of response MUST be: TRIAGE: RED or TRIAGE: YELLOW or TRIAGE: GREEN",
        backstory=(
            "WHO IMCI-trained rural PHC nurse. Expert at spotting danger signs. "
            "You ALWAYS start your response with TRIAGE: RED, TRIAGE: YELLOW, or TRIAGE: GREEN on its own line. "
            "RED = danger signs present. YELLOW = urgent but stable. GREEN = non-urgent."
        ),
        llm=_llm(), verbose=False, allow_delegation=False,
    )

def get_ddx_reasoner_agent():
    return Agent(
        role="DDx Reasoner",
        goal="Provide exactly 3 differential diagnoses ranked #1 #2 #3.",
        backstory=(
            "Clinical reasoning expert for rural India. "
            "Specialist in malaria, TB, pneumonia, dengue, gastroenteritis, SAM. "
            "Always give exactly 3 diagnoses with: name, key symptom, confirmatory test."
        ),
        llm=_llm(), verbose=False, allow_delegation=False,
    )

def get_drug_auditor_agent():
    return Agent(
        role="Drug Safety Auditor",
        goal="Check drug interactions. Last line MUST be: DRUG SAFETY: SAFE or DRUG SAFETY: CAUTION or DRUG SAFETY: UNSAFE",
        backstory=(
            "PHC clinical pharmacist. Flags dangerous drug combinations. "
            "You ALWAYS end your response with DRUG SAFETY: SAFE, DRUG SAFETY: CAUTION, or DRUG SAFETY: UNSAFE on its own line."
        ),
        llm=_llm(), verbose=False, allow_delegation=False,
    )
