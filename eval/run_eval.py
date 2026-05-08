"""
MediMesh evaluation runner.
Usage: python eval/run_eval.py

Runs all 10 clinical vignettes through the full agent pipeline
and prints an accuracy report you can include in your submission.
"""
import sys
import os
import time
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval.vignettes import VIGNETTES
from crew import run_triage

def run_eval():
    print("=" * 65)
    print("  MediMesh Evaluation Suite — 10 Clinical Vignettes")
    print("=" * 65)

    results = []
    severity_correct = 0
    drug_correct = 0
    total = len(VIGNETTES)

    for i, v in enumerate(VIGNETTES, 1):
        print(f"\n[{i}/{total}] Running: {v['name']}...")
        start = time.time()

        try:
            output = run_triage(
                patient_symptoms=v["patient_input"],
                current_medications="",
                proposed_treatment="",
            )

            sev_match  = output["severity"] == v["expected_severity"]
            drug_match = output["drug_verdict"] == v["expected_drug_verdict"]

            if sev_match:
                severity_correct += 1
            if drug_match:
                drug_correct += 1

            elapsed = round(time.time() - start, 1)

            status_sev  = "✅" if sev_match  else "❌"
            status_drug = "✅" if drug_match else "❌"

            print(f"   Severity : {status_sev} got={output['severity']:6s} expected={v['expected_severity']}")
            print(f"   Drug     : {status_drug} got={output['drug_verdict']:6s} expected={v['expected_drug_verdict']}")
            print(f"   Time     : {elapsed}s")

            results.append({
                "id":               v["id"],
                "name":             v["name"],
                "severity_correct": sev_match,
                "drug_correct":     drug_match,
                "got_severity":     output["severity"],
                "got_drug":         output["drug_verdict"],
                "expected_severity":v["expected_severity"],
                "expected_drug":    v["expected_drug_verdict"],
                "time_s":           elapsed,
            })

        except Exception as e:
            print(f"   ⚠️  ERROR: {str(e)}")
            results.append({
                "id": v["id"],
                "name": v["name"],
                "severity_correct": False,
                "drug_correct": False,
                "error": str(e),
            })

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  EVALUATION RESULTS")
    print("=" * 65)
    sev_acc  = round(severity_correct / total * 100, 1)
    drug_acc = round(drug_correct     / total * 100, 1)
    combined = round((severity_correct + drug_correct) / (total * 2) * 100, 1)

    print(f"  Triage Severity Accuracy : {severity_correct}/{total} = {sev_acc}%")
    print(f"  Drug Safety Accuracy     : {drug_correct}/{total}   = {drug_acc}%")
    print(f"  Combined Score           : {combined}%")
    print("=" * 65)

    # Save results JSON for submission
    output_path = "eval/eval_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "summary": {
                "severity_accuracy": sev_acc,
                "drug_accuracy": drug_acc,
                "combined": combined,
                "total_vignettes": total,
            },
            "results": results,
        }, f, indent=2)

    print(f"\n📄 Full results saved to: {output_path}")
    print("   Include this file in your hackathon submission.\n")

if __name__ == "__main__":
    run_eval()
