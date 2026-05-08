"""
MediMesh tasks — tight prompts optimised for small/fast models (1B-8B).
"""
from crewai import Task

def make_triage_task(agent, patient_symptoms, imci_context):
    return Task(
        description=f"""Patient case:
{patient_symptoms}

WHO IMCI reference:
{imci_context}

Instructions:
- Line 1 must be exactly: TRIAGE: RED or TRIAGE: YELLOW or TRIAGE: GREEN
- Line 2: list any danger signs found (or "None")
- Line 3-4: one sentence clinical reason for your choice
- Maximum 80 words total. Be direct.""",
        expected_output="TRIAGE: [RED/YELLOW/GREEN] followed by danger signs and brief rationale. Under 80 words.",
        agent=agent,
    )

def make_ddx_task(agent, patient_symptoms, triage_output, imci_context):
    return Task(
        description=f"""Patient: {patient_symptoms}
Triage: {triage_output}

Give exactly 3 differential diagnoses, ranked #1 most likely to #3 least likely.
Format each as:
#1 [NAME] — [one supporting symptom] — confirm with: [one test]
#2 [NAME] — [one supporting symptom] — confirm with: [one test]
#3 [NAME] — [one supporting symptom] — confirm with: [one test]

Maximum 90 words. No preamble.""",
        expected_output="Three ranked diagnoses in the exact format shown. Under 90 words.",
        agent=agent,
    )

def make_drug_audit_task(agent, patient_symptoms, current_meds, proposed_treatment, drug_context):
    return Task(
        description=f"""Current medications: {current_meds or 'None'}
Proposed treatment: {proposed_treatment or 'None'}

Drug interaction database findings:
{drug_context}

Instructions:
- Flag any dangerous combinations with ⚠️
- For each flag: one sentence on the risk + one safe alternative
- Last line must be exactly: DRUG SAFETY: SAFE or DRUG SAFETY: CAUTION or DRUG SAFETY: UNSAFE
- If no medications given, write: No medications to audit. DRUG SAFETY: SAFE
- Maximum 80 words total.""",
        expected_output="Drug safety review ending with DRUG SAFETY: [SAFE/CAUTION/UNSAFE]. Under 80 words.",
        agent=agent,
    )
