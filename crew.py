"""
MediMesh orchestrator — smarter severity extraction + Groq-ready.
"""
import sys, os, concurrent.futures, warnings
warnings.filterwarnings("ignore")
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY"] = "false"

from crewai import Crew, Process
from agents.agents import get_triager_agent, get_ddx_reasoner_agent, get_drug_auditor_agent
from agents.tasks import make_triage_task, make_ddx_task, make_drug_audit_task
from rag.retriever import query_imci, query_drug_interactions
from config import SEVERITY

def _extract_severity(text):
    """
    Scans every line, last explicit TRIAGE: label wins.
    Also catches the model reasoning aloud ('warrants a GREEN triage').
    """
    t_upper = text.upper()
    last = None
    for line in t_upper.splitlines():
        line = line.strip()
        if "TRIAGE: RED"    in line: last = "RED"
        elif "TRIAGE: YELLOW" in line: last = "YELLOW"
        elif "TRIAGE: GREEN"  in line: last = "GREEN"
    if last:
        return last
    # Catch model reasoning aloud: "warrants a GREEN triage"
    if "WARRANTS A GREEN" in t_upper or "IS GREEN" in t_upper: return "GREEN"
    if "WARRANTS A YELLOW" in t_upper or "IS YELLOW" in t_upper: return "YELLOW"
    if "WARRANTS A RED" in t_upper or "IS RED" in t_upper: return "RED"
    # Last resort keyword scan
    if any(w in t_upper for w in ["EMERGENCY", "REFER IMMEDIATELY", "DANGER SIGN PRESENT"]): return "RED"
    if any(w in t_upper for w in ["URGENT", "FAST BREATHING", "CHEST INDRAWING"]): return "YELLOW"
    return "GREEN"

def _extract_drug_verdict(text):
    t = text.upper()
    last = None
    for line in t.splitlines():
        line = line.strip()
        if "DRUG SAFETY: UNSAFE"  in line: last = "UNSAFE"
        elif "DRUG SAFETY: CAUTION" in line: last = "CAUTION"
        elif "DRUG SAFETY: SAFE"    in line: last = "SAFE"
    return last or "SAFE"

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
    return str(Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False).kickoff())

def run_triage(patient_symptoms, current_medications="", proposed_treatment=""):
    all_drugs = f"{current_medications} {proposed_treatment}"
    extracted = _extract_drugs(all_drugs)

    print("[RAG] retrieval...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fi = ex.submit(query_imci, patient_symptoms, 2)
        fd = ex.submit(query_drug_interactions, extracted)
        imci_ctx = fi.result(timeout=30)
        drug_ctx = fd.result(timeout=30)

    print("[AGENT] Triager...")
    triager = get_triager_agent()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        triage_text = ex.submit(
            _run_agent, triager, make_triage_task(triager, patient_symptoms, imci_ctx)
        ).result(timeout=90)

    print("[AGENT] DDx + Drug (parallel)...")
    ddx     = get_ddx_reasoner_agent()
    auditor = get_drug_auditor_agent()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fd = ex.submit(_run_agent, ddx,
                       make_ddx_task(ddx, patient_symptoms, triage_text, imci_ctx))
        fa = ex.submit(_run_agent, auditor,
                       make_drug_audit_task(auditor, patient_symptoms,
                                            current_medications, proposed_treatment, drug_ctx))
        ddx_text  = fd.result(timeout=90)
        drug_text = fa.result(timeout=90)

    severity     = _extract_severity(triage_text)
    drug_verdict = _extract_drug_verdict(drug_text)
    print(f"DONE -- {severity} | Drug: {drug_verdict}")

    return {
        "severity":      severity,
        "severity_meta": SEVERITY[severity],
        "drug_verdict":  drug_verdict,
        "triage_text":   triage_text,
        "ddx_text":      ddx_text,
        "drug_text":     drug_text,
        "imci_context":  imci_ctx,
    }

if __name__ == "__main__":
    import time
    t0 = time.time()
    r = run_triage(
        "Female, 5yo. Mild fever 37.9C for 1 day. Runny nose, mild cough. Alert, eating well. RR 28/min. No danger signs.",
        "none", "paracetamol"
    )
    print(f"\nTime: {round(time.time()-t0,1)}s | Severity: {r['severity']} | Drug: {r['drug_verdict']}")
    print("\nTRIAGE OUTPUT:\n", r['triage_text'])
