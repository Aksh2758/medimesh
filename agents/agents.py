"""
MediMesh agents — optimised for llama3.2:1b speed.
max_tokens=200, minimal backstory, temperature=0.1
"""
import warnings, os
warnings.filterwarnings("ignore")
os.environ["OTEL_SDK_DISABLED"] = "true"

from crewai import Agent
from langchain_openai import ChatOpenAI
from config import VLLM_BASE_URL, VLLM_MODEL_NAME, OPENAI_API_KEY

def _llm():
    return ChatOpenAI(
        base_url=VLLM_BASE_URL,
        api_key=OPENAI_API_KEY,
        model=VLLM_MODEL_NAME,
        temperature=0.1,
        max_tokens=200,  # tight — forces concise output, much faster
    )

def get_triager_agent():
    return Agent(
        role="Triage Nurse",
        goal="Assign GREEN/YELLOW/RED triage. Start response with TRIAGE: RED/YELLOW/GREEN.",
        backstory="WHO IMCI-trained rural PHC nurse. Concise. Always start with TRIAGE: label.",
        llm=_llm(), verbose=False, allow_delegation=False,
    )

def get_ddx_reasoner_agent():
    return Agent(
        role="DDx Reasoner",
        goal="List top 3 diagnoses ranked #1 #2 #3 with one symptom and one test each.",
        backstory="Clinical reasoner for rural India. Expert in malaria, TB, pneumonia, dengue, gastroenteritis.",
        llm=_llm(), verbose=False, allow_delegation=False,
    )

def get_drug_auditor_agent():
    return Agent(
        role="Drug Auditor",
        goal="Flag drug interactions. End with DRUG SAFETY: SAFE/CAUTION/UNSAFE.",
        backstory="PHC pharmacist. Flags dangerous combinations. Always ends with DRUG SAFETY: verdict.",
        llm=_llm(), verbose=False, allow_delegation=False,
    )
