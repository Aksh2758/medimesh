"""
MediMesh orchestrator — 3-agent pipeline, optimised for speed.
"""
import sys, os, concurrent.futures, warnings
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY"] = "false"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crewai import Crew, Process
from agents.agents import get_triager_agent, get_ddx_reasoner_agent, get_drug_auditor_agent
from agents.tasks import make_triage_task, make_ddx_task, make_drug_audit_task
from rag.retriever import query_imci, query_drug_interactions
from config import SEVERITY

AGENT_TIMEOUT = 120  # seconds — increase if your machine is slow

def _extract_severity(text):
    t = text.upper()
    if "TRIAGE: RED"    in t: return "RED"
    if "TRIAGE: YELLOW" in t: return "YELLOW"
    return "GREEN"

def _extract_drug_verdict(text):
    t = text.upper()
    if "DRUG SAFETY: UNSAFE"  in t: return "UNSAFE"
    if "DRUG SAFETY: CAUTION" in t: return "CAUTION"
    return "SAFE"

def _extract_drugs(text):
    drugs = [
        "metformin","warfarin","aspirin","amoxicillin","ciprofloxacin",
        "rifampicin","isoniazid","phenytoin","digoxin","lithium",
        "tramadol","ibuprofen","paracetamol","omeprazole","atenolol",
        "verapamil","spironolactone","furosemide","gentamicin",
        "metronidazole","fluconazole","erythromycin","carbamazepine",
        "chloroquine","glibenclamide","theophylline","amiodarone",
        "clopidogrel","methotrexate","sildenafil","nitrate","ssri",
        "oral contraceptive","contraceptive pill","haloperidol",
        "iron","tetracycline","steroid","prednisolone","antacid",
    ]
    tl = text.lower()
    return [d for d in drugs if d in tl]

def _run_agent(agent, task):
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
    return str(crew.kickoff())

def run_triage(patient_symptoms, current_medications="", proposed_treatment=""):
    # Step 1: parallel RAG retrieval
    all_drugs = f"{current_medications} {proposed_treatment}"
    extracted = _extract_drugs(all_drugs)
    print("RAG retrieval (parallel)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fi = ex.submit(query_imci, patient_symptoms, 2)
        fd = ex.submit(query_drug_interactions, extracted)
        imci_ctx = fi.result(timeout=30)
        drug_ctx = fd.result(timeout=30)

    # Step 2: Triager (sequential — DDx depends on its output)
    print("Triager...")
    triager = get_triager_agent()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        f = ex.submit(_run_agent, triager, make_triage_task(triager, patient_symptoms, imci_ctx))
        triage_text = f.result(timeout=AGENT_TIMEOUT)

    # Step 3: DDx + Drug Auditor in parallel
    print("DDx + Drug Auditor (parallel)...")
    ddx     = get_ddx_reasoner_agent()
    auditor = get_drug_auditor_agent()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fd = ex.submit(_run_agent, ddx,
                       make_ddx_task(ddx, patient_symptoms, triage_text, imci_ctx))
        fa = ex.submit(_run_agent, auditor,
                       make_drug_audit_task(auditor, patient_symptoms,
                                            current_medications, proposed_treatment, drug_ctx))
        ddx_text  = fd.result(timeout=AGENT_TIMEOUT)
        drug_text = fa.result(timeout=AGENT_TIMEOUT)

    severity     = _extract_severity(triage_text)
    drug_verdict = _extract_drug_verdict(drug_text)
    print(f"Done - {severity} | Drug: {drug_verdict}")

    return {
        "severity":      severity,
        "severity_meta": SEVERITY[severity],
        "drug_verdict":  drug_verdict,
        "triage_text":   triage_text,
        "ddx_text":      ddx_text,
        "drug_text":     drug_text,
        "imci_context":  imci_ctx,
    }

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='replace').decode('ascii'))

if __name__ == "__main__":
    import time
    t0 = time.time()
    r = run_triage(
        "Male, 4yo. Fever 3 days, RR 46/min, Temp 39.2C, chest indrawing. Alert.",
        "none", "amoxicillin"
    )
    elapsed = round(time.time() - t0, 1)
    safe_print(f"\n{'='*50}")
    safe_print(f"Total time : {elapsed}s")
    safe_print(f"Severity   : {r['severity']}")
    safe_print(f"Drug safety: {r['drug_verdict']}")
    safe_print(f"\nTRIAGE:\n{r['triage_text']}")
    safe_print(f"\nDDx:\n{r['ddx_text']}")
    safe_print(f"\nDRUG:\n{r['drug_text']}")
