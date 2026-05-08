"""
MediMesh — Streamlit UI. Run: streamlit run app.py
"""
import streamlit as st
import time, sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import APP_TITLE, SEVERITY
from crew import run_triage

st.set_page_config(page_title="MediMesh", page_icon="🏥", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }

.hero {
    background: linear-gradient(135deg, #1e3a5f 0%, #0f4c81 100%);
    border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;
    color: white;
}
.hero h1 { margin: 0; font-size: 2rem; font-weight: 700; }
.hero p  { margin: 0.25rem 0 0; opacity: 0.8; font-size: 0.9rem; }

.severity-banner {
    border-radius: 14px; padding: 1.25rem 1.75rem;
    margin: 0.75rem 0; display: flex; align-items: center; gap: 1rem;
}
.sev-red    { background: #fef2f2; border: 2px solid #ef4444; }
.sev-yellow { background: #fefce8; border: 2px solid #f59e0b; }
.sev-green  { background: #f0fdf4; border: 2px solid #22c55e; }

.sev-emoji  { font-size: 2.5rem; line-height: 1; }
.sev-label  { font-size: 1.4rem; font-weight: 700; }
.sev-sublabel { font-size: 0.85rem; opacity: 0.75; margin-top: 2px; }

.drug-badge {
    border-radius: 10px; padding: 0.65rem 1rem;
    margin: 0.5rem 0; font-weight: 600; font-size: 0.9rem;
    display: inline-block;
}
.drug-safe    { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
.drug-caution { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.drug-unsafe  { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }

.agent-box {
    border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 1rem 1.25rem; margin: 0.6rem 0;
    background: #fafafa;
}
.agent-header {
    font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.06em; color: #6b7280; margin-bottom: 0.5rem;
}
.action-banner {
    border-radius: 12px; padding: 1rem 1.25rem;
    font-weight: 600; font-size: 1rem; margin-top: 0.75rem;
}
.action-red    { background: #fef2f2; border: 2px solid #ef4444; color: #991b1b; }
.action-yellow { background: #fefce8; border: 2px solid #f59e0b; color: #92400e; }
.action-green  { background: #f0fdf4; border: 2px solid #22c55e; color: #166534; }

.stat-row { display: flex; gap: 1rem; margin: 0.5rem 0 1rem; }
.stat-chip {
    background: #f3f4f6; border-radius: 20px;
    padding: 0.3rem 0.75rem; font-size: 0.8rem; color: #374151;
}

.step-indicator {
    display: flex; gap: 0.5rem; align-items: center;
    font-size: 0.85rem; padding: 0.5rem 0;
}
.step-dot { width: 10px; height: 10px; border-radius: 50%; }
.step-active { background: #3b82f6; }
.step-done   { background: #22c55e; }
.step-wait   { background: #d1d5db; }
</style>
""", unsafe_allow_html=True)

# ── Hero header ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🏥 MediMesh</h1>
  <p>Multi-agent AI triage for rural PHC nurses &nbsp;·&nbsp; मेडिमेश — ग्रामीण स्वास्थ्य सहायक</p>
</div>
""", unsafe_allow_html=True)

# ── Demo scenario buttons ─────────────────────────────────────────────
st.markdown("**Quick demo scenarios / त्वरित परिदृश्य:**")
col1, col2, col3 = st.columns(3)

SCENARIOS = {
    "🟢 Mild Fever": {
        "symptoms": "Female, 5 years old. Mild fever 37.9°C for 1 day. Runny nose, mild cough. Alert, eating and drinking normally. RR 28/min, HR 98 bpm. No chest indrawing, no danger signs.",
        "meds": "none",
        "tx": "paracetamol"
    },
    "🟡 Pneumonia": {
        "symptoms": "Male, 3 years old. Fever 38.6°C for 3 days, cough, fast breathing. RR 44/min, HR 128 bpm, Temp 38.6°C. No chest indrawing. Alert, reduced appetite but drinking. No neck stiffness.",
        "meds": "none",
        "tx": "amoxicillin 250mg"
    },
    "🔴 Severe Dehydration": {
        "symptoms": "Male, 8 months old. Watery diarrhoea 2 days, 10 episodes today. Lethargic, sunken eyes, not able to drink, skin pinch returns very slowly. HR 172 bpm, RR 42/min, Temp 38.1°C. Fontanelle sunken.",
        "meds": "none",
        "tx": "ORS"
    },
}

chosen_scenario = None
with col1:
    if st.button("🟢 Mild Fever", use_container_width=True):
        chosen_scenario = "🟢 Mild Fever"
with col2:
    if st.button("🟡 Pneumonia", use_container_width=True):
        chosen_scenario = "🟡 Pneumonia"
with col3:
    if st.button("🔴 Severe Dehydration", use_container_width=True):
        chosen_scenario = "🔴 Severe Dehydration"

# Pre-fill from scenario
if chosen_scenario:
    s = SCENARIOS[chosen_scenario]
    st.session_state["prefill_symptoms"] = s["symptoms"]
    st.session_state["prefill_meds"]     = s["meds"]
    st.session_state["prefill_tx"]       = s["tx"]

st.divider()

# ── Input form ───────────────────────────────────────────────────────
st.subheader("Patient Presentation / रोगी की जानकारी")

with st.form("triage_form"):
    symptoms = st.text_area(
        "Symptoms & Vitals / लक्षण और वाइटल्स",
        value=st.session_state.get("prefill_symptoms", ""),
        placeholder="e.g. Male, 4 years. Fever 3 days, RR 46/min, Temp 39.2°C, chest indrawing present, alert, not eating.",
        height=130,
    )
    col_a, col_b = st.columns(2)
    with col_a:
        current_meds = st.text_input(
            "Current Medications / वर्तमान दवाएं",
            value=st.session_state.get("prefill_meds", ""),
            placeholder="e.g. metformin, rifampicin (or none)"
        )
    with col_b:
        proposed_tx = st.text_input(
            "Proposed Treatment / प्रस्तावित उपचार",
            value=st.session_state.get("prefill_tx", ""),
            placeholder="e.g. amoxicillin, ORS"
        )
    submitted = st.form_submit_button("🔍 Run Triage  /  जांच शुरू करें",
                                      use_container_width=True, type="primary")


# ── Run pipeline ─────────────────────────────────────────────────────
if submitted:
    if not symptoms.strip():
        st.error("Please enter patient symptoms first.")
        st.stop()

    start_time = time.time()

    # Live agent status panel
    status_box = st.empty()

    def show_status(step):
        steps = [
            ("RAG retrieval",          step > 0),
            ("Triager assessing",      step > 1),
            ("DDx + Drug (parallel)",  step > 2),
            ("Building triage card",   step > 3),
        ]
        html = '<div style="padding:1rem;background:#f9fafb;border-radius:10px;border:1px solid #e5e7eb">'
        html += '<div style="font-weight:600;font-size:0.85rem;color:#374151;margin-bottom:0.5rem">🤖 Agents working...</div>'
        for i, (label, done) in enumerate(steps):
            active = (i == step - 1) and not done
            if done:
                dot_class = "step-done"
                icon = "✅"
            elif i == step:
                dot_class = "step-active"
                icon = "⏳"
            else:
                dot_class = "step-wait"
                icon = "○"
            html += f'<div class="step-indicator"><span class="step-dot {dot_class}"></span>{icon} {label}</div>'
        html += '</div>'
        status_box.markdown(html, unsafe_allow_html=True)

    show_status(0)

    res_container = {"result": {}, "error": None}
    def _run():
        try:
            res_container["result"] = run_triage(symptoms, current_meds, proposed_tx)
        except Exception as e:
            res_container["error"] = e

    import threading
    t = threading.Thread(target=_run)
    t.start()

    # Animate steps while agents run
    step = 0
    while t.is_alive():
        show_status(step % 4)
        time.sleep(1.8)
        step += 1
    t.join()

    status_box.empty()

    if res_container["error"]:
        st.error(f"❌ Pipeline error: {res_container['error']}")
        st.info("Make sure Ollama is running: `ollama serve` and the model is pulled: `ollama pull llama3.1`")
        st.stop()

    elapsed = round(time.time() - start_time, 1)

    # ── Triage Card ───────────────────────────────────────────────────
    st.divider()

    sev          = res_container["result"]["severity"]
    sev_meta     = res_container["result"]["severity_meta"]
    drug_verdict = res_container["result"]["drug_verdict"]

    # Stats row
    model_name = "Llama 3.1 (local)" if "localhost" in str(os.getenv("VLLM_BASE_URL","localhost")) else "Llama 3.1 (AMD Cloud)"
    st.markdown(f"""
    <div class="stat-row">
      <span class="stat-chip">⏱ {elapsed}s</span>
      <span class="stat-chip">🤖 3 agents</span>
      <span class="stat-chip">📚 WHO IMCI + Drug DB</span>
      <span class="stat-chip">🖥 {model_name}</span>
    </div>
    """, unsafe_allow_html=True)

    # Severity banner
    sev_css = {"RED": "sev-red", "YELLOW": "sev-yellow", "GREEN": "sev-green"}[sev]
    sev_sub = {"RED": "Refer immediately to district hospital",
               "YELLOW": "Assess and treat within 1 hour",
               "GREEN":  "Manage at PHC — advise to return if worse"}[sev]
    st.markdown(f"""
    <div class="severity-banner {sev_css}">
      <div class="sev-emoji">{sev_meta['emoji']}</div>
      <div>
        <div class="sev-label" style="color:{sev_meta['color']}">{sev} — {sev_meta['label']}</div>
        <div class="sev-sublabel">{sev_sub}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Drug safety badge
    drug_css   = {"SAFE": "drug-safe", "CAUTION": "drug-caution", "UNSAFE": "drug-unsafe"}[drug_verdict]
    drug_icons = {"SAFE": "✅", "CAUTION": "⚠️", "UNSAFE": "🚨"}
    st.markdown(
        f'<div class="drug-badge {drug_css}">{drug_icons[drug_verdict]} Drug Safety: {drug_verdict}</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Agent output expanders
    with st.expander("🏥 Agent 1 — Triage Assessment", expanded=True):
        st.markdown(f'<div class="agent-header">Triager · WHO IMCI Protocol</div>', unsafe_allow_html=True)
        st.markdown(res_container["result"]["triage_text"])

    with st.expander("🔬 Agent 2 — Differential Diagnoses", expanded=True):
        st.markdown(f'<div class="agent-header">DDx Reasoner · Evidence-Grounded</div>', unsafe_allow_html=True)
        st.markdown(res_container["result"]["ddx_text"])

    with st.expander("💊 Agent 3 — Drug Safety Audit", expanded=True):
        st.markdown(f'<div class="agent-header">Drug Safety Auditor · Interaction Database</div>', unsafe_allow_html=True)
        st.markdown(res_container["result"]["drug_text"])

    with st.expander("📚 Evidence Retrieved (WHO IMCI)", expanded=False):
        st.caption("ChromaDB vector search · WHO IMCI Guidelines + Indian National Protocols")
        st.text(res_container["result"]["imci_context"])

    # Action banner
    action_msg = {
        "RED":    "🚨 REFER IMMEDIATELY — Give pre-referral treatment now. Write referral note.",
        "YELLOW": "⚡ URGENT — Treat and observe. Reassess in 30 minutes. Escalate if worse.",
        "GREEN":  "✅ NON-URGENT — Manage at PHC. Educate caregiver. Return if no improvement in 2 days.",
    }
    action_css = {"RED": "action-red", "YELLOW": "action-yellow", "GREEN": "action-green"}[sev]
    st.markdown(
        f'<div class="action-banner {action_css}">{action_msg[sev]}</div>',
        unsafe_allow_html=True
    )
    if drug_verdict == "UNSAFE":
        st.markdown(
            '<div class="action-banner action-red">🚨 STOP — Do NOT administer flagged drugs. See Drug Audit above.</div>',
            unsafe_allow_html=True
        )
