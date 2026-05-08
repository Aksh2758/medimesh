"""
MediMesh evaluation set — 10 clinical vignettes with known correct triage severity.
Run with: python eval/run_eval.py
"""

VIGNETTES = [
    {
        "id": "eval_001",
        "name": "Severe Pneumonia - Child",
        "patient_input": """
Patient: Female, 18 months old.
Chief complaint: Cough and fast breathing for 2 days.
Vitals: Temp 38.9°C, RR 58 breaths/min, HR 148 bpm, SpO2 88%.
Signs: Severe chest indrawing, nasal flaring, grunting. Alert but irritable.
No neck stiffness. Feeding poorly.
Current medications: None.
Proposed treatment: Amoxicillin oral.
""",
        "expected_severity": "RED",
        "expected_drug_verdict": "SAFE",
        "notes": "Severe chest indrawing + SpO2 88% = severe pneumonia, RED triage, needs referral + O2"
    },
    {
        "id": "eval_002",
        "name": "Uncomplicated Pneumonia - Child",
        "patient_input": """
Patient: Male, 3 years old.
Chief complaint: Cough and fever for 3 days.
Vitals: Temp 38.4°C, RR 43 breaths/min, HR 120 bpm.
Signs: No chest indrawing. Alert, eating reduced but drinking well.
No danger signs.
Current medications: None.
Proposed treatment: Amoxicillin 250mg 3 times daily for 5 days.
""",
        "expected_severity": "YELLOW",
        "expected_drug_verdict": "SAFE",
        "notes": "Fast breathing (>40/min for age) without chest indrawing = pneumonia, YELLOW"
    },
    {
        "id": "eval_003",
        "name": "Severe Dehydration - Diarrhoea",
        "patient_input": """
Patient: Male, 8 months old.
Chief complaint: Watery diarrhoea for 2 days, 8 episodes today.
Vitals: Temp 37.8°C, HR 168 bpm, RR 40/min.
Signs: Lethargic, sunken eyes, dry lips, skin pinch returns very slowly (>2 seconds),
not able to drink, fontanelle sunken.
Current medications: None.
Proposed treatment: ORS.
""",
        "expected_severity": "RED",
        "expected_drug_verdict": "SAFE",
        "notes": "Lethargic + cannot drink + slow skin pinch = severe dehydration = RED, needs IV fluids"
    },
    {
        "id": "eval_004",
        "name": "Moderate Dehydration - Diarrhoea",
        "patient_input": """
Patient: Female, 2 years old.
Chief complaint: Diarrhoea for 1 day, 4 loose stools.
Vitals: Temp 37.5°C, HR 118 bpm.
Signs: Restless, sunken eyes, drinks eagerly when offered water, skin pinch
returns in 1 second. No lethargy.
Current medications: None.
Proposed treatment: ORS 75ml/kg over 4 hours, zinc 20mg daily for 10 days.
""",
        "expected_severity": "YELLOW",
        "expected_drug_verdict": "SAFE",
        "notes": "Restless + sunken eyes + drinks eagerly = some dehydration = YELLOW"
    },
    {
        "id": "eval_005",
        "name": "Dangerous Drug Interaction - TB + OCP",
        "patient_input": """
Patient: Female, 28 years old.
Chief complaint: Cough for 3 weeks, weight loss, night sweats.
Vitals: Temp 37.9°C, HR 88 bpm, RR 18/min.
Signs: Alert, no respiratory distress. Mildly pale conjunctiva.
Current medications: Oral contraceptive pill (Yasmin), rifampicin (TB treatment started 2 weeks ago).
Proposed treatment: Continue TB regimen.
""",
        "expected_severity": "YELLOW",
        "expected_drug_verdict": "UNSAFE",
        "notes": "Rifampicin drastically reduces OCP efficacy — UNSAFE drug interaction, needs barrier contraception"
    },
    {
        "id": "eval_006",
        "name": "Febrile Convulsion",
        "patient_input": """
Patient: Male, 2 years old.
Chief complaint: Seizure lasting 3 minutes, now stopped. Fever 39.8°C.
Vitals: Temp 39.8°C, HR 145 bpm, RR 30/min, SpO2 97%.
Signs: Now alert and crying. No neck stiffness. Fontanelle flat.
First seizure ever. No focal neurological signs. Parents very anxious.
Current medications: None.
Proposed treatment: Paracetamol, observe.
""",
        "expected_severity": "YELLOW",
        "expected_drug_verdict": "SAFE",
        "notes": "Single brief febrile seizure, now alert, no danger signs — YELLOW, refer for evaluation"
    },
    {
        "id": "eval_007",
        "name": "Neonatal Danger Signs",
        "patient_input": """
Patient: Female neonate, 5 days old.
Chief complaint: Not feeding for 12 hours, fast breathing since morning.
Vitals: Temp 36.1°C (low), RR 68 breaths/min, HR 178 bpm.
Signs: Grunting, nasal flaring, severe chest indrawing. Lethargic.
Umbilicus red with pus discharge extending to surrounding skin.
Current medications: None.
""",
        "expected_severity": "RED",
        "expected_drug_verdict": "SAFE",
        "notes": "Multiple neonatal danger signs — not feeding, fast breathing, lethargy, infected umbilicus = RED"
    },
    {
        "id": "eval_008",
        "name": "Simple Fever - Malaria Suspected",
        "patient_input": """
Patient: Male, 6 years old.
Chief complaint: Fever for 2 days, living in malaria endemic area (Odisha).
Vitals: Temp 38.6°C, HR 110 bpm, RR 28/min.
Signs: Alert, eating and drinking normally. No chest indrawing.
No neck stiffness. Mild pallor.
RDT: Positive for Plasmodium falciparum.
Current medications: None.
Proposed treatment: Artemether-Lumefantrine (AL) course.
""",
        "expected_severity": "YELLOW",
        "expected_drug_verdict": "SAFE",
        "notes": "Uncomplicated falciparum malaria, alert, no danger signs — YELLOW, treat with ACT"
    },
    {
        "id": "eval_009",
        "name": "Dangerous Combo - Digoxin + Amiodarone",
        "patient_input": """
Patient: Male, 68 years old.
Chief complaint: Palpitations and dizziness for 1 day.
Vitals: BP 100/70, HR 52 bpm (slow, irregular), RR 18/min, Temp 37.0°C.
Signs: Alert. No chest pain. Mild ankle oedema. No neck stiffness.
Current medications: Digoxin 0.25mg daily, Furosemide 40mg daily.
Proposed treatment: Add Amiodarone for arrhythmia.
""",
        "expected_severity": "YELLOW",
        "expected_drug_verdict": "UNSAFE",
        "notes": "Amiodarone + digoxin = digoxin toxicity risk (2x plasma levels) — UNSAFE"
    },
    {
        "id": "eval_010",
        "name": "Mild URTI - No Danger Signs",
        "patient_input": """
Patient: Female, 4 years old.
Chief complaint: Runny nose, mild cough, sore throat for 2 days.
Vitals: Temp 37.8°C, HR 100 bpm, RR 30/min.
Signs: Alert, playing, eating and drinking well. Throat mildly red, no pus.
No chest indrawing. No fast breathing. No danger signs.
Current medications: None.
Proposed treatment: Paracetamol for fever, honey for cough.
""",
        "expected_severity": "GREEN",
        "expected_drug_verdict": "SAFE",
        "notes": "Viral URTI, no danger signs, no fast breathing — GREEN, symptomatic treatment only"
    },
]
