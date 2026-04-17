from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from medical_scribe.analyzer import analyze_visit
from medical_scribe.auth import authenticate_user, create_account, init_auth_db
from medical_scribe.emailer import send_email_report
from medical_scribe.records import get_visit_record, init_records_db, list_visit_records, save_visit_record
from medical_scribe.report import build_report_markdown, build_report_pdf, save_pdf_report, save_report
from medical_scribe.support import SupportEngine
from medical_scribe.transcriber import transcribe


AUTH_DB_PATH = ROOT / "data" / "users.db"
RECORDS_DB_PATH = ROOT / "data" / "clinical_records.db"


def _inject_styles(theme_mode: str) -> None:
    dark_vars = """
:root {
    --ink: #e8ecf3;
    --ink-muted: #b6c1d1;
    --paper: #141c2b;
    --paper-2: #1a2437;
    --paper-3: #22314b;
    --accent: #22c55e;
    --danger: #ef4444;
    --sidebar-bg: linear-gradient(180deg, #131d31, #121929);
    --sidebar-border: #2e3d58;
    --panel-bg: linear-gradient(180deg, #19263b, #172235);
    --panel-border: #334865;
    --button-bg: linear-gradient(90deg, #14532d, #166534);
    --button-text: #ecfdf5;
    --button-border: #22c55e;
    --ribbon-bg: linear-gradient(90deg, #14532d, #0f766e);
    --ribbon-text: #f0fdf4;
    --app-bg:
      radial-gradient(circle at 15% 20%, #203149 0%, rgba(32, 49, 73, 0) 36%),
      radial-gradient(circle at 85% 5%, #1e3a3b 0%, rgba(30, 58, 59, 0) 44%),
      linear-gradient(145deg, #0e1524, #121a2b 42%, #101b2a);
}
    """

    light_vars = """
:root {
    --ink: #162235;
    --ink-muted: #31445f;
    --paper: #f3f6fb;
    --paper-2: #e7edf6;
    --paper-3: #dce6f4;
    --accent: #0f766e;
    --danger: #b91c1c;
    --sidebar-bg: linear-gradient(180deg, #e9f0fb, #e3ecf9);
    --sidebar-border: #bac9de;
    --panel-bg: linear-gradient(180deg, #f6f9ff, #eff4fd);
    --panel-border: #c5d4eb;
    --button-bg: linear-gradient(90deg, #115e59, #0f766e);
    --button-text: #ecfeff;
    --button-border: #0f766e;
    --ribbon-bg: linear-gradient(90deg, #0f766e, #0369a1);
    --ribbon-text: #f0fdfa;
    --app-bg:
      radial-gradient(circle at 15% 20%, #dceaf8 0%, rgba(220, 234, 248, 0) 36%),
      radial-gradient(circle at 85% 5%, #dff2ed 0%, rgba(223, 242, 237, 0) 44%),
      linear-gradient(145deg, #f3f7ff, #eef4fb 42%, #eaf2fb);
}
    """

    root_vars = dark_vars if theme_mode == "Dark" else light_vars

    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Serif:wght@400;600&display=swap');

__ROOT_VARS__

.stApp {
    background: var(--app-bg);
    color: var(--ink);
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif;
    color: var(--ink);
    letter-spacing: 0.01em;
}

p, div, label, li, span {
    font-family: 'IBM Plex Serif', serif;
    color: var(--ink-muted);
}

[data-testid="stMetricValue"] {
    color: var(--accent);
}

[data-testid="stMetricLabel"],
[data-testid="stSidebar"] *,
.stRadio label,
.stTextInput label,
.stTextArea label,
.stFileUploader label,
.stSelectbox label {
    color: var(--ink) !important;
}

[data-testid="stSidebar"] {
    background: var(--sidebar-bg);
    border-right: 1px solid var(--sidebar-border);
}

.panel {
    background: var(--panel-bg);
    border: 1px solid var(--panel-border);
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 12px 28px rgba(2, 7, 14, 0.42);
}

.ribbon {
    background: var(--ribbon-bg);
    color: var(--ribbon-text);
    border-radius: 10px;
    padding: 8px 12px;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
}

.stTextInput > div > div > input,
.stTextArea textarea,
.stFileUploader > div,
.stSelectbox > div > div,
.stNumberInput input {
    background: var(--paper-2) !important;
    color: var(--ink) !important;
    border: 1px solid #3b4f6e !important;
}

.stButton > button,
.stDownloadButton > button {
    background: var(--button-bg) !important;
    color: var(--button-text) !important;
    border: 1px solid var(--button-border) !important;
    font-weight: 700;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    filter: brightness(1.08);
}

pre {
    color: var(--ink);
    white-space: pre-wrap;
}
</style>
    """
    st.markdown(css.replace("__ROOT_VARS__", root_vars), unsafe_allow_html=True)


def _save_uploaded_file(uploaded_file) -> str:
    outputs = ROOT / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    path = outputs / f"uploaded_{uploaded_file.name}"
    path.write_bytes(uploaded_file.read())
    return str(path)


def _run_pipeline(patient_id: str, transcript_text: str, kb_path: str):
    analysis = analyze_visit(transcript_text)
    support_engine = SupportEngine.from_file(kb_path)
    support = support_engine.generate(analysis.chief_complaint, transcript_text)
    report_content = build_report_markdown(patient_id, analysis, support)
    report_pdf = build_report_pdf(report_content)
    report_path = save_report(report_content, output_dir=str(ROOT / "outputs"))
    report_pdf_path = save_pdf_report(report_pdf, output_dir=str(ROOT / "outputs"))
    return analysis, support, report_content, report_pdf, report_path, report_pdf_path


def _init_session_state() -> None:
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "current_user_email" not in st.session_state:
        st.session_state.current_user_email = ""


def _render_auth_screen() -> None:
    st.markdown("<div class='ribbon'>AI MEDICAL SCRIBE CLONE</div>", unsafe_allow_html=True)
    st.title("Account Access")
    st.caption("Create an account or log in with your email and password.")

    login_tab, signup_tab = st.tabs(["Login", "Create Account"])

    with login_tab:
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In", type="primary", use_container_width=True):
            if authenticate_user(login_email, login_password, str(AUTH_DB_PATH)):
                st.session_state.is_authenticated = True
                st.session_state.current_user_email = login_email.strip().lower()
                st.success("Logged in successfully.")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with signup_tab:
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
        if st.button("Create Account", use_container_width=True):
            if signup_password != signup_confirm:
                st.error("Passwords do not match.")
            else:
                created, message = create_account(signup_email, signup_password, str(AUTH_DB_PATH))
                if created:
                    st.success(message)
                else:
                    st.error(message)


def _render_records_viewer(current_user_email: str) -> None:
    st.markdown("<div class='ribbon'>PATIENT DATABASE VIEWER</div>", unsafe_allow_html=True)
    st.title("Saved Patient Reports")
    st.caption("Review patient reports generated in this account.")

    rows = list_visit_records(str(RECORDS_DB_PATH), created_by=current_user_email)
    if not rows:
        st.info("No patient reports saved yet. Generate one from the Scribe Workspace page.")
        return

    st.dataframe(rows, use_container_width=True)
    selected_id = st.selectbox(
        "Select record ID",
        options=[int(r["id"]) for r in rows],
    )
    selected = get_visit_record(str(RECORDS_DB_PATH), selected_id, created_by=current_user_email)
    if not selected:
        st.warning("Selected record was not found.")
        return

    st.subheader(f"Patient {selected['patient_id']} | Record #{selected['id']}")
    st.write(f"Created at: {selected['created_at']}")
    st.write(f"Source mode: {selected['source_mode']}")
    st.write(f"Chief complaint: {selected['chief_complaint']}")

    st.markdown("### Transcript")
    st.text_area("Transcript", value=selected["transcript"], height=180, disabled=True)

    st.markdown("### SOAP Note")
    st.text_area("SOAP", value=selected["soap_note"], height=180, disabled=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### Area 1")
        for item in selected["area1_real_world_evidence"]:
            st.write(f"- {item}")
    with c2:
        st.markdown("#### Area 2")
        for item in selected["area2_medical_issues"]:
            st.write(f"- {item}")
    with c3:
        st.markdown("#### Area 3")
        for item in selected["area3_guidelines"]:
            st.write(f"- {item}")

    st.markdown("### References")
    for item in selected["references"]:
        st.write(f"- {item}")

    st.download_button(
        label="Download Saved Report (.md)",
        data=selected["report_markdown"],
        file_name=f"medical_scribe_{selected['patient_id']}_record_{selected['id']}.md",
        mime="text/markdown",
        use_container_width=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="AI Medical Scribe",
        page_icon="🩺",
        layout="wide",
    )
    AUTH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    init_auth_db(str(AUTH_DB_PATH))
    init_records_db(str(RECORDS_DB_PATH))
    _init_session_state()

    with st.sidebar:
        theme_mode = st.radio("Theme", ["Dark", "Light"], horizontal=True, index=0)
        if st.session_state.is_authenticated:
            st.success(f"Logged in as {st.session_state.current_user_email}")
            page = st.radio("Page", ["Scribe Workspace", "Database Viewer"], index=0)
            if st.button("Log Out", use_container_width=True):
                st.session_state.is_authenticated = False
                st.session_state.current_user_email = ""
                st.rerun()

            st.header("Run Settings")
            patient_id = st.text_input("Patient ID", value="UNKNOWN")
            kb_path = st.text_input(
                "Knowledge Base Path",
                value=str(ROOT / "data" / "knowledge_base.json"),
            )
            send_email = st.checkbox("Send report by email")
            recipient_email = st.text_input("Recipient Email", value="")
            st.markdown("SMTP credentials are read from environment variables.")

    _inject_styles(theme_mode)

    if not st.session_state.is_authenticated:
        _render_auth_screen()
        return

    if page == "Database Viewer":
        _render_records_viewer(st.session_state.current_user_email)
        return

    st.markdown("<div class='ribbon'>AI MEDICAL SCRIBE CLONE</div>", unsafe_allow_html=True)
    st.title("Clinical Scribe Dashboard")
    st.caption("Voice/Text to Transcript, SOAP Note, Decision Support, References, and Report")

    st.subheader("Input")
    mode = st.radio(
        "Choose input mode",
        ["Typed Text", "Upload Audio/Text File", "Record in Browser"],
        horizontal=True,
    )

    transcript_text = ""
    if mode == "Typed Text":
        transcript_text = st.text_area(
            "Clinical conversation/transcript",
            placeholder="Patient reports headache and fever for two days...",
            height=180,
        )
    elif mode == "Upload Audio/Text File":
        uploaded = st.file_uploader(
            "Upload .wav, .aiff, .flac, or .txt",
            type=["wav", "aiff", "flac", "txt"],
        )
        if uploaded is not None:
            saved_path = _save_uploaded_file(uploaded)
            try:
                transcript_text = transcribe(audio_file=saved_path)
                st.success("Transcription complete from uploaded file.")
            except Exception as exc:
                st.error(f"Transcription failed: {exc}")
                st.info(
                    "Try clearer speech, less background noise, a longer sample, or upload a .txt transcript."
                )
    else:
        if hasattr(st, "audio_input"):
            audio = st.audio_input("Record doctor-controlled audio")
            if audio is not None:
                saved_path = _save_uploaded_file(audio)
                try:
                    transcript_text = transcribe(audio_file=saved_path)
                    st.success("Transcription complete from browser recording.")
                except Exception as exc:
                    st.error(f"Transcription failed: {exc}")
                    st.info(
                        "Try speaking closer to the microphone, reducing noise, or upload a .txt transcript."
                    )
        else:
            st.warning("This Streamlit version does not support browser recording. Use Upload mode.")

    generate = st.button("Generate Clinical Output", type="primary", use_container_width=True)
    if not generate:
        return

    if not transcript_text.strip():
        st.error("No transcript detected. Enter text or provide an audio/text file.")
        return

    try:
        analysis, support, report_md, report_pdf, report_path, report_pdf_path = _run_pipeline(
            patient_id,
            transcript_text,
            kb_path,
        )
        record_id = save_visit_record(
            db_path=str(RECORDS_DB_PATH),
            patient_id=patient_id,
            source_mode=mode,
            analysis=analysis,
            support=support,
            report_markdown=report_md,
            created_by=st.session_state.current_user_email,
        )
    except Exception as exc:  # pragma: no cover - UI exception display
        st.error(f"Processing failed: {exc}")
        return

    st.subheader("Results")
    top_a, top_b = st.columns([1, 3])
    with top_a:
        st.metric("Chief Complaint", analysis.chief_complaint.title())
    with top_b:
        st.markdown("<div class='panel'><b>SOAP Note</b><pre>" + analysis.soap_note + "</pre></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='panel'><h4>Area 1: Real-World Evidence</h4></div>", unsafe_allow_html=True)
        for item in support.area1_real_world_evidence:
            st.write(f"- {item}")
    with c2:
        st.markdown("<div class='panel'><h4>Area 2: Med Issues</h4></div>", unsafe_allow_html=True)
        for item in support.area2_medical_issues:
            st.write(f"- {item}")
    with c3:
        st.markdown("<div class='panel'><h4>Area 3: Guidelines</h4></div>", unsafe_allow_html=True)
        for item in support.area3_guidelines:
            st.write(f"- {item}")

    st.markdown("### References")
    for item in support.references:
        st.write(f"- {item}")

    st.download_button(
        label="Download Report (.md)",
        data=report_md,
        file_name=f"medical_scribe_{patient_id}.md",
        mime="text/markdown",
        use_container_width=True,
    )
    st.download_button(
        label="Download Report (.pdf)",
        data=report_pdf,
        file_name=f"medical_scribe_{patient_id}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    st.info(f"Reports saved to: {report_path} and {report_pdf_path}")
    st.success(f"Database record saved with ID: {record_id}")

    if send_email:
        if not recipient_email:
            st.warning("Recipient email is required to send email.")
        else:
            try:
                send_email_report(
                    recipient=recipient_email,
                    subject=f"Medical Scribe Report - {patient_id}",
                    body=report_md,
                )
                st.success(f"Report emailed to {recipient_email}")
            except Exception as exc:  # pragma: no cover - UI exception display
                st.error(f"Email send failed: {exc}")


if __name__ == "__main__":
    main()
