
import streamlit as st
import json
import base64
import os
from pathlib import Path
from PIL import Image


if "theme_style" not in st.session_state:
    st.session_state.theme_style = "pop"


logo_img = "shield"
logo_base64 = ""
banner_base64 = ""
if os.path.exists("cvilization_logo.png"):
    try:
        logo_img = Image.open("cvilization_logo.png")
        with open("cvilization_logo.png", "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        pass

if os.path.exists("cvilization_hero_banner.png"):
    try:
        with open("cvilization_hero_banner.png", "rb") as f:
            banner_base64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        pass

st.set_page_config(
    page_title="cvilization",
    page_icon=logo_img,
    layout="wide",
    initial_sidebar_state="collapsed"
)

from database.connection import initialize_database, get_db_connection
from database.repository import (
    get_personal_info, update_personal_info,
    get_education, add_education, update_education, delete_education, toggle_education, reorder_education,
    get_experiences, add_experience, update_experience, delete_experience, toggle_experience, reorder_experiences,
    get_projects, add_project, update_project, delete_project, toggle_project, reorder_projects,
    get_skills, add_skill, update_skill, delete_skill, toggle_skill, reorder_skills,
    get_certifications, add_certification, update_certification, delete_certification, toggle_certification, reorder_certifications,
    get_achievements, add_achievement, update_achievement, delete_achievement, toggle_achievement, reorder_achievements,
    get_full_resume_state, restore_full_resume_state, save_to_history, get_history_states, clear_history,
    get_latest_job_description, add_job_description
)
from utils.latex_escaper import escape_latex
from utils.file_exporter import generate_markdown_summary, generate_zip_bundle
from services.ai_helper import (
    rewrite_bullet_point, generate_cover_letter, generate_recruiter_email,
    generate_linkedin_about, generate_github_summary, generate_portfolio_bio, generate_interview_intro
)
from agents.workflow import build_resume_workflow
from agents.latex_generator import generate_latex_resume

initialize_database()

def load_css():
    css_path = Path("styles/main.css")
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.components.v1.html("""
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault();
        const buttons = doc.querySelectorAll('button');
        for (const btn of buttons) {
            if (btn.innerText.includes('Undo')) {
                btn.click();
                break;
            }
        }
    }
    if ((e.ctrlKey || e.metaKey) && e.key === 'y') {
        const buttons = doc.querySelectorAll('button');
        for (const btn of buttons) {
            if (btn.innerText.includes('Redo')) {
                btn.click();
                break;
            }
        }
    }
});
</script>
""", height=0, width=0)

def get_icon(name: str, size: int = 18) -> str:
    icons = {
        "shield": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-shield"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.5 3.8 17 5 19 5a1 1 0 0 1 1 1z"/></svg>',
        "settings": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-settings"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.1a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
        "history": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-history"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><polyline points="3 3 3 8 8 8"/><line x1="12" y1="7" x2="12" y2="12"/><polyline points="12 12 16 14"/></svg>',
        "download": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-download"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
        "award": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-award"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>',
        "sparkles": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-sparkles"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275Z"/><path d="m5 3 1 2.5L8.5 6 6 7 5 9.5 4 7 1.5 6 4 5Z"/><path d="m19 17 1 2.5 2.5.5-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1Z"/></svg>',
        "briefcase": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-briefcase"><path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect width="20" height="14" x="2" y="6" rx="2"/></svg>',
        "graduation-cap": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-graduation-cap"><path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"/></svg>',
        "code": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-code"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
        "wrench": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-wrench"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
        "check-circle": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-check-circle"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        "alert-triangle": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-alert-triangle"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        "user": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-user"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
        "trash": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trash"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
        "copy": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>'
    }
    return icons.get(name, "")

if "history_index" not in st.session_state:
    clear_history()
    initial = get_full_resume_state()
    save_to_history(initial)
    st.session_state.history = get_history_states()
    st.session_state.history_index = 0

if "jd_analysis" not in st.session_state:
    latest_jd = get_latest_job_description()
    if latest_jd and latest_jd.get("analysis_json"):
        st.session_state.jd_analysis = json.loads(latest_jd["analysis_json"])
    else:
        st.session_state.jd_analysis = {}

if "ats_optimization" not in st.session_state:
    st.session_state.ats_optimization = {}

if "latex_cache" not in st.session_state:
    st.session_state.latex_cache = ""

if "pdf_cache" not in st.session_state:
    st.session_state.pdf_cache = None

def register_state_change():
    st.session_state.pdf_cache = None
    current = get_full_resume_state()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM history ORDER BY id ASC")
    ids = [r[0] for r in cursor.fetchall()]
    if st.session_state.history_index < len(ids) - 1:
        to_delete = ids[st.session_state.history_index + 1:]
        cursor.execute(f"DELETE FROM history WHERE id IN ({','.join(['?']*len(to_delete))})", to_delete)
        conn.commit()
    conn.close()

    save_to_history(current)
    st.session_state.history = get_history_states()
    st.session_state.history_index = len(st.session_state.history) - 1

def run_undo():
    if st.session_state.history_index > 0:
        st.session_state.history_index -= 1
        restore_full_resume_state(st.session_state.history[st.session_state.history_index])
        st.toast("Undo Applied")
        st.rerun()

def run_redo():
    if st.session_state.history_index < len(st.session_state.history) - 1:
        st.session_state.history_index += 1
        restore_full_resume_state(st.session_state.history[st.session_state.history_index])
        st.toast("Redo Applied")
        st.rerun()


col_brand, col_undo_redo, col_import, col_config, col_export = st.columns([2.5, 1.2, 1.5, 1.8, 1.8])

with col_brand:
    logo_html = f'<img class="brand-logo-interactive" src="data:image/png;base64,{logo_base64}" width="42" style="border-radius: 50%; vertical-align: middle;">' if logo_base64 else f'<div class="brand-logo-interactive" style="display:inline-block; vertical-align:middle;">{get_icon("shield", 32)}</div>'
    st.markdown(f"""
    <div style="display: flex; align-items: center; height: 100%; min-height: 42px;">
        {logo_html}
    </div>
    """, unsafe_allow_html=True)

with col_undo_redo:
    c_undo, c_redo = st.columns(2)
    with c_undo:
        is_undo_disabled = st.session_state.history_index == 0
        if st.button("", icon=":material/undo:", help=f"Undo (State {st.session_state.history_index + 1} of {len(st.session_state.history)})", key="nav_undo_btn", disabled=is_undo_disabled, use_container_width=True):
            run_undo()
    with c_redo:
        is_redo_disabled = st.session_state.history_index >= len(st.session_state.history) - 1
        if st.button("", icon=":material/redo:", help="Redo", key="nav_redo_btn", disabled=is_redo_disabled, use_container_width=True):
            run_redo()

with col_import:
    with st.popover("Import", icon=":material/upload:", use_container_width=True):
        st.markdown("### Import Resume State")
        import_file = st.file_uploader("Upload resume_data.json", type=["json"], key="nav_import_uploader")
        if import_file is not None:
            try:
                imported_data = json.load(import_file)
                restore_full_resume_state(imported_data)
                register_state_change()
                st.success("Resume data imported successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error parsing JSON: {e}")

with col_config:
    with st.popover("Configure AI", icon=":material/settings:", use_container_width=True):
        st.markdown("### Gemini API Settings")
        provider = "Gemini"
        api_key = st.text_input("Gemini API Key", type="password", key="nav_gemini_api_key", help="Leave blank to use the key from your local .env file.")
        model_options = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
        model_name = st.selectbox("LLM Model Name", model_options, index=0, key="nav_model_name")

with col_export:
    with st.popover("Export", icon=":material/download:", use_container_width=True):
        st.markdown("### Export Options")
        current_resume_data = get_full_resume_state()
        current_latex = generate_latex_resume(current_resume_data)
        pdf_bytes = st.session_state.pdf_cache

        st.download_button(
            label="Export LaTeX Source",
            data=current_latex,
            file_name="resume.tex",
            mime="application/x-latex",
            use_container_width=True,
            key="nav_export_latex"
        )

        if pdf_bytes:
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name="resume.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="nav_download_pdf"
            )
        else:
            st.button("Compiling PDF...", disabled=True, use_container_width=True, key="nav_pdf_compiling_disabled")

        md_summary = generate_markdown_summary(current_resume_data)
        st.download_button(
            label="Export Markdown Summary",
            data=md_summary,
            file_name="resume.md",
            mime="text/markdown",
            use_container_width=True,
            key="nav_export_md"
        )
        st.download_button(
            label="Export JSON Data",
            data=json.dumps(current_resume_data, indent=2),
            file_name="resume_data.json",
            mime="application/json",
            use_container_width=True,
            key="nav_export_json"
        )
        zip_bytes = generate_zip_bundle(current_resume_data, current_latex, pdf_bytes)
        st.download_button(
            label="Export ZIP Bundle",
            data=zip_bytes,
            file_name="cvilization_resume_bundle.zip",
            mime="application/zip",
            use_container_width=True,
            key="nav_export_zip"
        )


provider = "Gemini"
api_key = st.session_state.get("nav_gemini_api_key", "")
if not api_key:
    api_key = os.environ.get("GEMINI_API_KEY", "")
model_name = st.session_state.get("nav_model_name", "gemini-1.5-flash")


if banner_base64:
    st.markdown(f"""
    <div style="width: 100%; overflow: hidden; border-radius: 16px; margin-bottom: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); border: 1px solid rgba(185, 28, 28, 0.25);">
        <img src="data:image/png;base64,{banner_base64}" style="width: 100%; display: block; filter: brightness(0.85) contrast(1.15);">
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("cvilization_hero_banner")

col_jd, col_score = st.columns([3, 1])

def extract_text_from_file(uploaded_file) -> str:
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        import pypdf
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif filename.endswith(".docx"):
        import docx
        doc = docx.Document(uploaded_file)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return "\n".join(text)
    elif filename.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    return ""

with col_jd:
    st.markdown('<div class="lego-header">TARGET JOB DESCRIPTION</div>', unsafe_allow_html=True)
    if "jd_text_val" not in st.session_state:
        st.session_state.jd_text_val = ""

    uploaded_file = st.file_uploader("Upload JD Document (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        extracted_text = extract_text_from_file(uploaded_file)
        if extracted_text and extracted_text != st.session_state.jd_text_val:
            st.session_state.jd_text_val = extracted_text
            st.success(f"Extracted text from {uploaded_file.name}")

    jd_input = st.text_area("Paste Job Description Text or URL", value=st.session_state.jd_text_val, height=120)

with col_score:
    st.markdown('<div class="lego-header">MATCH RATING</div>', unsafe_allow_html=True)
    match_val = st.session_state.ats_optimization.get("match_score", 0)
    ats_val = st.session_state.ats_optimization.get("ats_score", 0)


    st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card" style="padding: 20px; height: 207px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-sizing: border-box; margin-bottom: 0;">
        <div class="score-circle">
            <span class="score-num">{match_val}%</span>
            <span class="score-lbl">MATCH</span>
        </div>
        <p style="text-align:center; margin:20px 0 0 0; font-size:0.95rem; color:#fee2e2;">
            ATS Score: <strong>{ats_val}%</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

if st.button("RUN AI JOB DESCRIPTION OPTIMIZER", use_container_width=True):
    if not jd_input.strip():
        st.warning("Please paste a job description or upload a file first!")
    else:
        with st.spinner("Optimizing Resume via LangGraph..."):
            try:
                jd_id = add_job_description("Target Role", jd_input)
                full_state = get_full_resume_state()
                graph = build_resume_workflow()

                inputs = {
                    "provider": provider,
                    "api_key": api_key,
                    "model_name": model_name,
                    "jd_text": jd_input,
                    "resume_data": full_state,
                    "jd_analysis": {},
                    "ats_optimization": {},
                    "latex_code": "",
                    "pdf_compiled": False,
                    "pdf_log": "",
                    "pdf_bytes": b""
                }

                final_output = graph.invoke(inputs)
                st.session_state.jd_analysis = final_output.get("jd_analysis", {})
                st.session_state.ats_optimization = final_output.get("ats_optimization", {})
                st.session_state.latex_cache = final_output.get("latex_code", "")

                if final_output.get("pdf_compiled") and final_output.get("pdf_bytes"):
                    st.session_state.pdf_cache = final_output.get("pdf_bytes")
                else:
                    from utils.pdf_fallback import generate_fallback_pdf
                    st.session_state.pdf_cache = generate_fallback_pdf(get_full_resume_state())

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE job_descriptions SET analysis_json = ? WHERE id = ?",
                    (json.dumps(st.session_state.jd_analysis), jd_id)
                )
                conn.commit()
                conn.close()

                recs = st.session_state.ats_optimization.get("recommended_selections", {})
                if recs:
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    if "experience_ids" in recs:
                        cursor.execute("UPDATE experiences SET is_selected = 0")
                        for exp_id in recs["experience_ids"]:
                            cursor.execute("UPDATE experiences SET is_selected = 1 WHERE id = ?", (exp_id,))
                    if "project_ids" in recs:
                        cursor.execute("UPDATE projects SET is_selected = 0")
                        for proj_id in recs["project_ids"]:
                            cursor.execute("UPDATE projects SET is_selected = 1 WHERE id = ?", (proj_id,))
                    if "skill_categories" in recs:
                        cursor.execute("UPDATE skills SET is_selected = 0")
                        for cat in recs["skill_categories"]:
                            cursor.execute("UPDATE skills SET is_selected = 1 WHERE category = ?", (cat,))
                    if "certification_ids" in recs:
                        cursor.execute("UPDATE certifications SET is_selected = 0")
                        for cert_id in recs["certification_ids"]:
                            cursor.execute("UPDATE certifications SET is_selected = 1 WHERE id = ?", (cert_id,))
                    if "achievement_ids" in recs:
                        cursor.execute("UPDATE achievements SET is_selected = 0")
                        for ach_id in recs["achievement_ids"]:
                            cursor.execute("UPDATE achievements SET is_selected = 1 WHERE id = ?", (ach_id,))

                    conn.commit()
                    conn.close()
                    register_state_change()

                st.success("ATS optimization and analysis complete")
                st.rerun()

            except Exception as e:
                st.error(f"Error during AI optimization: {e}")

col_left_workspace, col_right_preview = st.columns([1, 1])

active_personal_info = get_personal_info()
active_education = get_education()
active_experiences = get_experiences()
active_projects = get_projects()
active_skills = get_skills()
active_certifications = get_certifications()
active_achievements = get_achievements()

with col_left_workspace:
    st.markdown('<div class="lego-header">RESUME COMPILER & EDITOR</div>', unsafe_allow_html=True)
    tabs = st.tabs(["Profile", "Education", "Experience", "Projects", "Skills", "Other Sections"])

    with tabs[0]:
        st.subheader("Edit Profile Information")
        with st.form("profile_form"):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                p_name = st.text_input("Full Name", value=active_personal_info.get("name", ""))
                p_degree = st.text_input("Degree Details", value=active_personal_info.get("degree", ""))
                p_college = st.text_input("College / Institute", value=active_personal_info.get("college", ""))
                p_roll = st.text_input("Roll Number", value=active_personal_info.get("roll_number", ""))
                p_email = st.text_input("Primary Email", value=active_personal_info.get("email", ""))
                p_cemail = st.text_input("College Email", value=active_personal_info.get("college_email", ""))
            with col_p2:
                p_phone = st.text_input("Phone Number", value=active_personal_info.get("phone", ""))
                p_loc = st.text_input("Location", value=active_personal_info.get("location", ""))
                p_git = st.text_input("GitHub Username", value=active_personal_info.get("github", ""))
                p_gitlink = st.text_input("GitHub Link", value=active_personal_info.get("github_link", ""))
                p_lnk = st.text_input("LinkedIn Username", value=active_personal_info.get("linkedin", ""))
                p_lnklink = st.text_input("LinkedIn Link", value=active_personal_info.get("linkedin_link", ""))

            p_port = st.text_input("Portfolio URL", value=active_personal_info.get("portfolio", ""))

            if st.form_submit_button("Save Profile Settings", use_container_width=True):
                update_personal_info({
                    "name": p_name, "degree": p_degree, "college": p_college, "roll_number": p_roll,
                    "email": p_email, "college_email": p_cemail, "phone": p_phone, "location": p_loc,
                    "github": p_git, "github_link": p_gitlink, "linkedin": p_lnk, "linkedin_link": p_lnklink,
                    "portfolio": p_port
                })
                register_state_change()
                st.success("Profile saved")
                st.rerun()

    with tabs[1]:
        st.subheader("Manage Academic History")

        with st.expander("Add New Educational Block"):
            with st.form("add_edu_form"):
                new_deg = st.text_input("Degree Name")
                new_inst = st.text_input("Institute / School")
                new_board = st.text_input("Board / University")
                new_cgpa = st.text_input("CGPA / Percentage")
                new_year = st.text_input("Year")

                if st.form_submit_button("Insert Block"):
                    add_education({
                        "degree": new_deg, "institute": new_inst, "board_university": new_board,
                        "cgpa_percentage": new_cgpa, "year": new_year
                    })
                    register_state_change()
                    st.success("Education block added")
                    st.rerun()

        for edu in active_education:
            with st.container():
                st.markdown(f'<div class="reorder-container"><span>{get_icon("graduation-cap")} <strong>{edu["degree"]}</strong> - {edu["institute"]}</span></div>', unsafe_allow_html=True)
                col_sel, col_up, col_down, col_dup, col_del = st.columns([2, 1, 1, 1, 1])

                with col_sel:
                    t_val = st.checkbox("Include in resume", value=bool(edu["is_selected"]), key=f"edu_sel_{edu['id']}")
                    if t_val != bool(edu["is_selected"]):
                        toggle_education(edu["id"], t_val)
                        register_state_change()
                        st.rerun()

                with col_up:
                    if st.button("", icon=":material/arrow_upward:", help="Move Up", key=f"edu_up_{edu['id']}", use_container_width=True):
                        idx = active_education.index(edu)
                        if idx > 0:
                            ordered = [e["id"] for e in active_education]
                            ordered[idx], ordered[idx-1] = ordered[idx-1], ordered[idx]
                            reorder_education(ordered)
                            register_state_change()
                            st.rerun()

                with col_down:
                    if st.button("", icon=":material/arrow_downward:", help="Move Down", key=f"edu_down_{edu['id']}", use_container_width=True):
                        idx = active_education.index(edu)
                        if idx < len(active_education) - 1:
                            ordered = [e["id"] for e in active_education]
                            ordered[idx], ordered[idx+1] = ordered[idx+1], ordered[idx]
                            reorder_education(ordered)
                            register_state_change()
                            st.rerun()

                with col_dup:
                    if st.button("", icon=":material/content_copy:", help="Duplicate", key=f"edu_dup_{edu['id']}", use_container_width=True):
                        add_education({
                            "degree": edu["degree"] + " (Copy)",
                            "institute": edu["institute"],
                            "board_university": edu["board_university"],
                            "cgpa_percentage": edu["cgpa_percentage"],
                            "year": edu["year"]
                        })
                        register_state_change()
                        st.rerun()

                with col_del:
                    if st.button("", icon=":material/delete:", help="Delete", key=f"edu_del_{edu['id']}", use_container_width=True):
                        delete_education(edu["id"])
                        register_state_change()
                        st.rerun()

                with st.expander("Details / Edit Block"):
                    with st.form(f"edu_edit_form_{edu['id']}"):
                        ed_deg = st.text_input("Degree Name", value=edu["degree"])
                        ed_inst = st.text_input("Institute / School", value=edu["institute"])
                        ed_board = st.text_input("Board / University", value=edu["board_university"])
                        ed_cgpa = st.text_input("CGPA / Percentage", value=edu["cgpa_percentage"])
                        ed_year = st.text_input("Year", value=edu["year"])

                        if st.form_submit_button("Save changes", key=f"edu_edit_sub_{edu['id']}"):
                            update_education(edu["id"], {
                                "degree": ed_deg, "institute": ed_inst, "board_university": ed_board,
                                "cgpa_percentage": ed_cgpa, "year": ed_year, "is_selected": edu["is_selected"]
                            })
                            register_state_change()
                            st.rerun()

    with tabs[2]:
        st.subheader("Manage Work Experience")

        exp_search = st.text_input("Search experiences...", value="", key="exp_search_bar")
        exp_filter = st.selectbox("Status Filter", ["All", "Selected Only", "Unselected Only"])

        with st.expander("Add New Experience Card"):
            with st.form("add_exp_form"):
                new_role = st.text_input("Role")
                new_comp = st.text_input("Company Name")
                new_loc = st.text_input("Location")
                new_dates = st.text_input("Dates")
                new_tech = st.text_input("Technologies (comma-separated)")
                new_bullets = st.text_area("Bullet points (one per line)")

                if st.form_submit_button("Insert Experience"):
                    tech_arr = [t.strip() for t in new_tech.split(",") if t.strip()]
                    bullet_arr = [b.strip() for b in new_bullets.split("\n") if b.strip()]
                    add_experience({
                        "role": new_role, "company": new_comp, "location": new_loc, "dates": new_dates,
                        "technologies": tech_arr, "bullets": bullet_arr
                    })
                    register_state_change()
                    st.success("Experience added")
                    st.rerun()

        for exp in active_experiences:
            if exp_search.lower() not in exp["role"].lower() and exp_search.lower() not in exp["company"].lower():
                continue
            if exp_filter == "Selected Only" and not exp["is_selected"]:
                continue
            if exp_filter == "Unselected Only" and exp["is_selected"]:
                continue

            box_class = "active-card" if exp["is_selected"] else ""
            st.markdown(f"""
            <div class="glass-card {box_class}" style="padding:15px; margin-bottom:10px; display:flex; align-items:center; gap:8px;">
                {get_icon("briefcase")} <div><strong>{exp['role']}</strong> at {exp['company']} ({exp['dates']})</div>
            </div>
            """, unsafe_allow_html=True)

            col_sel, col_up, col_down, col_dup, col_del = st.columns([2, 1, 1, 1, 1])

            with col_sel:
                t_val = st.checkbox("Include in resume", value=bool(exp["is_selected"]), key=f"exp_sel_{exp['id']}")
                if t_val != bool(exp["is_selected"]):
                    toggle_experience(exp["id"], t_val)
                    register_state_change()
                    st.rerun()

            with col_up:
                if st.button("", icon=":material/arrow_upward:", help="Move Up", key=f"exp_up_{exp['id']}", use_container_width=True):
                    idx = active_experiences.index(exp)
                    if idx > 0:
                        ordered = [e["id"] for e in active_experiences]
                        ordered[idx], ordered[idx-1] = ordered[idx-1], ordered[idx]
                        reorder_experiences(ordered)
                        register_state_change()
                        st.rerun()

            with col_down:
                if st.button("", icon=":material/arrow_downward:", help="Move Down", key=f"exp_down_{exp['id']}", use_container_width=True):
                    idx = active_experiences.index(exp)
                    if idx < len(active_experiences) - 1:
                        ordered = [e["id"] for e in active_experiences]
                        ordered[idx], ordered[idx+1] = ordered[idx+1], ordered[idx]
                        reorder_experiences(ordered)
                        register_state_change()
                        st.rerun()

            with col_dup:
                if st.button("", icon=":material/content_copy:", help="Duplicate", key=f"exp_dup_{exp['id']}", use_container_width=True):
                    add_experience({
                        "role": exp["role"] + " (Copy)", "company": exp["company"], "location": exp["location"],
                        "dates": exp["dates"], "technologies": exp["technologies"], "bullets": exp["bullets"]
                    })
                    register_state_change()
                    st.rerun()

            with col_del:
                if st.button("", icon=":material/delete:", help="Delete", key=f"exp_del_{exp['id']}", use_container_width=True):
                    delete_experience(exp["id"])
                    register_state_change()
                    st.rerun()

            with st.expander("Details / AI Rewriter"):
                with st.form(f"exp_edit_form_{exp['id']}"):
                    ex_role = st.text_input("Role", value=exp["role"])
                    ex_comp = st.text_input("Company", value=exp["company"])
                    ex_loc = st.text_input("Location", value=exp["location"])
                    ex_dates = st.text_input("Dates", value=exp["dates"])
                    ex_tech = st.text_input("Technologies (comma-separated)", value=", ".join(exp["technologies"]))

                    st.markdown("##### Bullet Points")
                    ex_bullets = []
                    for idx, bullet in enumerate(exp["bullets"]):
                        bullet_val = st.text_area(f"Bullet {idx+1}", value=bullet, key=f"exp_b_{exp['id']}_{idx}")
                        ex_bullets.append(bullet_val)

                    if st.form_submit_button("Save changes", key=f"exp_sub_edit_{exp['id']}"):
                        tech_arr = [t.strip() for t in ex_tech.split(",") if t.strip()]
                        update_experience(exp["id"], {
                            "role": ex_role, "company": ex_comp, "location": ex_loc, "dates": ex_dates,
                            "technologies": tech_arr, "bullets": ex_bullets, "is_selected": exp["is_selected"]
                        })
                        register_state_change()
                        st.rerun()

                st.markdown("##### AI Bullet Optimization Panel")
                bullet_to_rewrite_idx = st.selectbox(
                    "Choose Bullet Point to Optimize",
                    range(len(exp["bullets"])),
                    format_func=lambda i: f"Bullet {i+1}: {exp['bullets'][i][:50]}...",
                    key=f"exp_b_sel_opt_{exp['id']}"
                )

                rewrite_action = st.selectbox(
                    "Choose Optimization Goal",
                    ["Quantify (metrics)", "STAR Format", "Stronger Verbs", "Shorten", "Expand", "Recruiter Friendly Phrasing", "Tailor to Job Description"],
                    key=f"exp_act_{exp['id']}"
                )

                if st.button("Optimize Bullet with AI", key=f"exp_ai_btn_{exp['id']}"):
                    action_key = {
                        "Quantify (metrics)": "quantify", "STAR Format": "star", "Stronger Verbs": "strong_verbs",
                        "Shorten": "shorten", "Expand": "expand", "Recruiter Friendly Phrasing": "recruiter_phrasing",
                        "Tailor to Job Description": "ats_tailor"
                    }[rewrite_action]

                    with st.spinner("AI is rewriting bullet point..."):
                        try:
                            old_bullet = exp["bullets"][bullet_to_rewrite_idx]
                            new_bullet = rewrite_bullet_point(
                                provider=provider, api_key=api_key, model_name=model_name,
                                bullet=old_bullet, company=exp["company"], role=exp["role"],
                                action=action_key, jd_text=jd_input
                            )
                            updated_bullets = list(exp["bullets"])
                            updated_bullets[bullet_to_rewrite_idx] = new_bullet

                            update_experience(exp["id"], {
                                "role": exp["role"], "company": exp["company"], "location": exp["location"],
                                "dates": exp["dates"], "technologies": exp["technologies"], "bullets": updated_bullets,
                                "is_selected": exp["is_selected"]
                            })
                            register_state_change()
                            st.success("Bullet point optimized")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error during optimization: {e}")

    with tabs[3]:
        st.subheader("Manage Projects")
        proj_search = st.text_input("Search projects...", value="", key="proj_search_bar")

        with st.expander("Add New Project"):
            with st.form("add_proj_form"):
                new_p_title = st.text_input("Project Title")
                new_p_desc = st.text_input("Brief Subtitle / Tech Description")
                new_p_stack = st.text_input("Tech Stack (comma-separated)")
                new_p_git = st.text_input("GitHub Repo Link")
                new_p_live = st.text_input("Live Demo Link")
                new_p_dur = st.text_input("Duration")
                new_p_bullets = st.text_area("Bullet points (one per line)")

                if st.form_submit_button("Insert Project"):
                    stack_arr = [s.strip() for s in new_p_stack.split(",") if s.strip()]
                    bullet_arr = [b.strip() for b in new_p_bullets.split("\n") if b.strip()]
                    add_project({
                        "title": new_p_title, "description": new_p_desc, "tech_stack": stack_arr,
                        "github_link": new_p_git, "live_demo_link": new_p_live, "duration": new_p_dur,
                        "bullets": bullet_arr
                    })
                    register_state_change()
                    st.success("Project added")
                    st.rerun()

        for proj in active_projects:
            if proj_search.lower() not in proj["title"].lower() and proj_search.lower() not in ",".join(proj["tech_stack"]).lower():
                continue

            box_class = "active-card" if proj["is_selected"] else ""
            st.markdown(f"""
            <div class="glass-card {box_class}" style="padding:15px; margin-bottom:10px; display:flex; align-items:center; gap:8px;">
                {get_icon("code")} <div><strong>{proj['title']}</strong> ({proj['duration']})</div>
            </div>
            """, unsafe_allow_html=True)

            col_sel, col_up, col_down, col_dup, col_del = st.columns([2, 1, 1, 1, 1])

            with col_sel:
                t_val = st.checkbox("Include in resume", value=bool(proj["is_selected"]), key=f"proj_sel_{proj['id']}")
                if t_val != bool(proj["is_selected"]):
                    toggle_project(proj["id"], t_val)
                    register_state_change()
                    st.rerun()

            with col_up:
                if st.button("", icon=":material/arrow_upward:", help="Move Up", key=f"proj_up_{proj['id']}", use_container_width=True):
                    idx = active_projects.index(proj)
                    if idx > 0:
                        ordered = [p["id"] for p in active_projects]
                        ordered[idx], ordered[idx-1] = ordered[idx-1], ordered[idx]
                        reorder_projects(ordered)
                        register_state_change()
                        st.rerun()

            with col_down:
                if st.button("", icon=":material/arrow_downward:", help="Move Down", key=f"proj_down_{proj['id']}", use_container_width=True):
                    idx = active_projects.index(proj)
                    if idx < len(active_projects) - 1:
                        ordered = [p["id"] for p in active_projects]
                        ordered[idx], ordered[idx+1] = ordered[idx+1], ordered[idx]
                        reorder_projects(ordered)
                        register_state_change()
                        st.rerun()

            with col_dup:
                if st.button("", icon=":material/content_copy:", help="Duplicate", key=f"proj_dup_{proj['id']}", use_container_width=True):
                    add_project({
                        "title": proj["title"] + " (Copy)", "description": proj["description"],
                        "tech_stack": proj["tech_stack"], "github_link": proj["github_link"],
                        "live_demo_link": proj["live_demo_link"], "duration": proj["duration"],
                        "bullets": proj["bullets"]
                    })
                    register_state_change()
                    st.rerun()

            with col_del:
                if st.button("", icon=":material/delete:", help="Delete", key=f"proj_del_{proj['id']}", use_container_width=True):
                    delete_project(proj["id"])
                    register_state_change()
                    st.rerun()

            with st.expander("Details / AI Rewriter"):
                with st.form(f"proj_edit_form_{proj['id']}"):
                    pr_title = st.text_input("Title", value=proj["title"])
                    pr_desc = st.text_input("Subtitle / Tech Description", value=proj["description"])
                    pr_stack = st.text_input("Tech Stack (comma-separated)", value=", ".join(proj["tech_stack"]))
                    pr_git = st.text_input("GitHub Repo Link", value=proj["github_link"])
                    pr_live = st.text_input("Live Demo Link", value=proj["live_demo_link"])
                    pr_dur = st.text_input("Duration", value=proj["duration"])

                    st.markdown("##### Bullet Points")
                    pr_bullets = []
                    for idx, bullet in enumerate(proj["bullets"]):
                        bullet_val = st.text_area(f"Bullet {idx+1}", value=bullet, key=f"proj_b_{proj['id']}_{idx}")
                        pr_bullets.append(bullet_val)

                    if st.form_submit_button("Save changes", key=f"proj_sub_edit_{proj['id']}"):
                        stack_arr = [s.strip() for s in pr_stack.split(",") if s.strip()]
                        update_project(proj["id"], {
                            "title": pr_title, "description": pr_desc, "tech_stack": stack_arr,
                            "github_link": pr_git, "live_demo_link": pr_live, "duration": pr_dur,
                            "bullets": pr_bullets, "is_selected": proj["is_selected"]
                        })
                        register_state_change()
                        st.rerun()

                st.markdown("##### AI Bullet Optimization Panel")
                bullet_to_rewrite_idx = st.selectbox(
                    "Choose Bullet Point to Optimize",
                    range(len(proj["bullets"])),
                    format_func=lambda i: f"Bullet {i+1}: {proj['bullets'][i][:50]}...",
                    key=f"proj_b_sel_opt_{proj['id']}"
                )

                rewrite_action = st.selectbox(
                    "Choose Optimization Goal",
                    ["Quantify (metrics)", "STAR Format", "Stronger Verbs", "Shorten", "Expand", "Recruiter Friendly Phrasing", "Tailor to Job Description"],
                    key=f"proj_act_{proj['id']}"
                )

                if st.button("Optimize Bullet with AI", key=f"proj_ai_btn_{proj['id']}"):
                    action_key = {
                        "Quantify (metrics)": "quantify", "STAR Format": "star", "Stronger Verbs": "strong_verbs",
                        "Shorten": "shorten", "Expand": "expand", "Recruiter Friendly Phrasing": "recruiter_phrasing",
                        "Tailor to Job Description": "ats_tailor"
                    }[rewrite_action]

                    with st.spinner("AI is rewriting bullet point..."):
                        try:
                            old_bullet = proj["bullets"][bullet_to_rewrite_idx]
                            new_bullet = rewrite_bullet_point(
                                provider=provider, api_key=api_key, model_name=model_name,
                                bullet=old_bullet, company=proj["title"], role="Project Developer",
                                action=action_key, jd_text=jd_input
                            )
                            updated_bullets = list(proj["bullets"])
                            updated_bullets[bullet_to_rewrite_idx] = new_bullet

                            update_project(proj["id"], {
                                "title": proj["title"], "description": proj["description"], "tech_stack": proj["tech_stack"],
                                "github_link": proj["github_link"], "live_demo_link": proj["live_demo_link"],
                                "duration": proj["duration"], "bullets": updated_bullets, "is_selected": proj["is_selected"]
                            })
                            register_state_change()
                            st.success("Bullet point optimized")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error during optimization: {e}")

    with tabs[4]:
        st.subheader("Manage Technical Skills")

        with st.expander("Add New Skill Category"):
            with st.form("add_skill_form"):
                new_cat = st.text_input("Category Name")
                new_items = st.text_input("Skills (comma-separated)")
                if st.form_submit_button("Insert Category"):
                    item_arr = [i.strip() for i in new_items.split(",") if i.strip()]
                    add_skill({"category": new_cat, "items": item_arr})
                    register_state_change()
                    st.success("Category added")
                    st.rerun()

        for skill in active_skills:
            box_class = "active-card" if skill["is_selected"] else ""
            st.markdown(f"""
            <div class="glass-card {box_class}" style="padding:15px; margin-bottom:10px; display:flex; align-items:center; gap:8px;">
                {get_icon("wrench")} <div><strong>{skill['category']}</strong></div>
            </div>
            """, unsafe_allow_html=True)

            col_sel, col_up, col_down, col_del = st.columns([3, 1, 1, 1])

            with col_sel:
                t_val = st.checkbox("Include in resume", value=bool(skill["is_selected"]), key=f"skill_sel_{skill['id']}")
                if t_val != bool(skill["is_selected"]):
                    toggle_skill(skill["id"], t_val)
                    register_state_change()
                    st.rerun()

            with col_up:
                if st.button("", icon=":material/arrow_upward:", help="Move Up", key=f"skill_up_{skill['id']}", use_container_width=True):
                    idx = active_skills.index(skill)
                    if idx > 0:
                        ordered = [s["id"] for s in active_skills]
                        ordered[idx], ordered[idx-1] = ordered[idx-1], ordered[idx]
                        reorder_skills(ordered)
                        register_state_change()
                        st.rerun()

            with col_down:
                if st.button("", icon=":material/arrow_downward:", help="Move Down", key=f"skill_down_{skill['id']}", use_container_width=True):
                    idx = active_skills.index(skill)
                    if idx < len(active_skills) - 1:
                        ordered = [s["id"] for s in active_skills]
                        ordered[idx], ordered[idx+1] = ordered[idx+1], ordered[idx]
                        reorder_skills(ordered)
                        register_state_change()
                        st.rerun()

            with col_del:
                if st.button("", icon=":material/delete:", help="Delete", key=f"skill_del_{skill['id']}", use_container_width=True):
                    delete_skill(skill["id"])
                    register_state_change()
                    st.rerun()

            with st.expander("Edit Skills Category"):
                with st.form(f"skill_edit_form_{skill['id']}"):
                    s_cat = st.text_input("Category Name", value=skill["category"])
                    s_items = st.text_input("Skills (comma-separated)", value=", ".join(skill["items"]))

                    if st.form_submit_button("Save changes", key=f"skill_sub_edit_{skill['id']}"):
                        item_arr = [i.strip() for i in s_items.split(",") if i.strip()]
                        update_skill(skill["id"], {
                            "category": s_cat, "items": item_arr, "is_selected": skill["is_selected"]
                        })
                        register_state_change()
                        st.rerun()

    with tabs[5]:
        col_cert, col_ach = st.columns(2)

        with col_cert:
            st.markdown('<div class="lego-header">Certifications</div>', unsafe_allow_html=True)

            with st.expander("Add Certification"):
                with st.form("add_cert_form"):
                    nc_name = st.text_input("Certification Title")
                    nc_issuer = st.text_input("Issuer")
                    nc_date = st.text_input("Date")
                    nc_url = st.text_input("Credential URL")

                    if st.form_submit_button("Insert Certification"):
                        add_certification({
                            "name": nc_name, "issuer": nc_issuer, "date": nc_date, "credential_url": nc_url
                        })
                        register_state_change()
                        st.success("Certification added")
                        st.rerun()

            for cert in active_certifications:
                box_class = "active-card" if cert["is_selected"] else ""
                st.markdown(f"""
                <div class="glass-card {box_class}" style="padding:12px; margin-bottom:8px; font-size:0.9rem;">
                    <strong>{cert['name']}</strong> ({cert['date']})
                </div>
                """, unsafe_allow_html=True)

                col_c_sel, col_c_del = st.columns([3, 1])
                with col_c_sel:
                    t_val = st.checkbox("Include", value=bool(cert["is_selected"]), key=f"cert_sel_{cert['id']}")
                    if t_val != bool(cert["is_selected"]):
                        toggle_certification(cert["id"], t_val)
                        register_state_change()
                        st.rerun()
                with col_c_del:
                    if st.button("", icon=":material/delete:", help="Delete", key=f"cert_del_{cert['id']}", use_container_width=True):
                        delete_certification(cert["id"])
                        register_state_change()
                        st.rerun()

                with st.expander("Edit details"):
                    with st.form(f"cert_edit_{cert['id']}"):
                        c_name = st.text_input("Title", value=cert["name"])
                        c_issuer = st.text_input("Issuer", value=cert["issuer"])
                        c_date = st.text_input("Date", value=cert["date"])
                        c_url = st.text_input("Credential URL", value=cert["credential_url"])

                        if st.form_submit_button("Save changes", key=f"cert_edit_sub_{cert['id']}"):
                            update_certification(cert["id"], {
                                "name": c_name, "issuer": c_issuer, "date": c_date, "credential_url": c_url,
                                "is_selected": cert["is_selected"]
                            })
                            register_state_change()
                            st.rerun()

        with col_ach:
            st.markdown('<div class="lego-header">Achievements and Leadership</div>', unsafe_allow_html=True)

            with st.expander("Add Achievement"):
                with st.form("add_ach_form"):
                    na_cat = st.text_input("Category")
                    na_desc = st.text_area("Achievements / Points description")

                    if st.form_submit_button("Insert Achievement"):
                        add_achievement({
                            "category": na_cat, "description": na_desc
                        })
                        register_state_change()
                        st.success("Achievement added")
                        st.rerun()

            for ach in active_achievements:
                box_class = "active-card" if ach["is_selected"] else ""
                st.markdown(f"""
                <div class="glass-card {box_class}" style="padding:12px; margin-bottom:8px; font-size:0.9rem;">
                    <strong>{ach['category']}</strong>
                </div>
                """, unsafe_allow_html=True)

                col_a_sel, col_a_del = st.columns([3, 1])
                with col_a_sel:
                    t_val = st.checkbox("Include", value=bool(ach["is_selected"]), key=f"ach_sel_{ach['id']}")
                    if t_val != bool(ach["is_selected"]):
                        toggle_achievement(ach["id"], t_val)
                        register_state_change()
                        st.rerun()
                with col_a_del:
                    if st.button("", icon=":material/delete:", help="Delete", key=f"ach_del_{ach['id']}", use_container_width=True):
                        delete_achievement(ach["id"])
                        register_state_change()
                        st.rerun()

                with st.expander("Edit details"):
                    with st.form(f"ach_edit_{ach['id']}"):
                        a_cat = st.text_input("Category", value=ach["category"])
                        a_desc = st.text_area("Description", value=ach["description"])

                        if st.form_submit_button("Save changes", key=f"ach_edit_sub_{ach['id']}"):
                            update_achievement(ach["id"], {
                                "category": a_cat, "description": a_desc, "is_selected": ach["is_selected"]
                            })
                            register_state_change()
                            st.rerun()

with col_right_preview:
    st.markdown('<div class="lego-header">REAL-TIME PREVIEW & OPTIMIZATION</div>', unsafe_allow_html=True)

    current_resume_data = get_full_resume_state()
    fresh_latex = generate_latex_resume(current_resume_data)
    fresh_markdown = generate_markdown_summary(current_resume_data)


    col_gen, col_dl = st.columns(2)
    with col_gen:
        generate_clicked = st.button("Generate PDF", icon=":material/picture_as_pdf:", use_container_width=True, key="gen_pdf_btn")
    with col_dl:
        if st.session_state.pdf_cache:
            st.download_button(
                label="Download PDF",
                data=st.session_state.pdf_cache,
                file_name="resume.pdf",
                mime="application/pdf",
                icon=":material/download:",
                use_container_width=True,
                key="dl_pdf_btn"
            )
        else:
            st.button("Download PDF", icon=":material/download:", use_container_width=True, disabled=True, key="dl_pdf_disabled")

    if generate_clicked:
        with st.spinner("Generating PDF..."):
            try:
                from utils.pdf_generator import generate_resume_pdf
                pdf_bytes = generate_resume_pdf(current_resume_data)
                st.session_state.pdf_cache = pdf_bytes
                st.success("PDF generated successfully! Click Download PDF to save.")
                st.rerun()
            except Exception as e:
                st.error(f"PDF generation failed: {e}")


    preview_view = st.selectbox(
        "Choose Analysis/Preview View",
        [
            "LaTeX Source Code",
            "Markdown Summary",
            "AI Cover Letter Draft",
            "AI Recruiter Outreach Email",
            "Social Bios & Elevator Pitch",
            "Automated Quality Audit"
        ],
        index=0,
        key="preview_waterfall_select"
    )

    with st.container(height=500):
        if preview_view == "LaTeX Source Code":
            st.subheader("LaTeX Source Code")
            st.code(fresh_latex, language="latex")

        elif preview_view == "Markdown Summary":
            st.subheader("Markdown Render")
            st.markdown(fresh_markdown)

        elif preview_view == "AI Cover Letter Draft":
            st.subheader("AI Cover Letter Draft")
            if not jd_input.strip():
                st.info("Paste a Job Description in the top panel to generate a custom Cover Letter.")
            else:
                if st.button("Draft Cover Letter with AI", key="ai_cl_btn"):
                    with st.spinner("Writing cover letter..."):
                        try:
                            letter = generate_cover_letter(provider, api_key, model_name, current_resume_data, jd_input)
                            st.text_area("Cover Letter Outline", value=letter, height=450)
                        except Exception as e:
                            st.error(f"Error: {e}")

        elif preview_view == "AI Recruiter Outreach Email":
            st.subheader("AI Recruiter Outreach Email")
            if not jd_input.strip():
                st.info("Paste a Job Description in the top panel to generate a recruiter cold email.")
            else:
                if st.button("Draft Recruiter Email with AI", key="ai_em_btn"):
                    with st.spinner("Writing cold outreach email..."):
                        try:
                            email_out = generate_recruiter_email(provider, api_key, model_name, current_resume_data, jd_input)
                            st.text_area("Email Draft", value=email_out, height=350)
                        except Exception as e:
                            st.error(f"Error: {e}")

        elif preview_view == "Social Bios & Elevator Pitch":
            st.subheader("Personal Social Bios & Elevator Pitch")
            bio_action = st.radio("Choose Copy Generation", ["LinkedIn About", "GitHub README", "Portfolio Bio", "Interview Introduction"])

            if st.button("Generate Selected Copy with AI", key="ai_bio_btn"):
                with st.spinner("Generating copy..."):
                    try:
                        if bio_action == "LinkedIn About":
                            res_copy = generate_linkedin_about(provider, api_key, model_name, current_resume_data)
                        elif bio_action == "GitHub README":
                            res_copy = generate_github_summary(provider, api_key, model_name, current_resume_data)
                        elif bio_action == "Portfolio Bio":
                            res_copy = generate_portfolio_bio(provider, api_key, model_name, current_resume_data)
                        else:
                            res_copy = generate_interview_intro(provider, api_key, model_name, current_resume_data)

                        st.text_area("Generated Output", value=res_copy, height=400)
                    except Exception as e:
                        st.error(f"Error: {e}")

        elif preview_view == "Automated Quality Audit":
            st.subheader("Automated Quality Audit")
            warnings = []
            p_info = current_resume_data.get("personal_info", {})

            if not p_info.get("github_link") or not p_info.get("github"):
                warnings.append(f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; color:#f59e0b;">{get_icon("alert-triangle")} Missing GitHub Link or username in profile settings.</div>')
            if not p_info.get("linkedin_link") or not p_info.get("linkedin"):
                warnings.append(f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; color:#f59e0b;">{get_icon("alert-triangle")} Missing LinkedIn Link or username in profile settings.</div>')

            exps = [e for e in current_resume_data.get("experiences", []) if e.get("is_selected", True)]
            if not exps:
                warnings.append(f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; color:#f59e0b;">{get_icon("alert-triangle")} No work experiences are selected.</div>')
            else:
                for exp in exps:
                    bullets_joined = " ".join(exp.get("bullets", []))
                    has_digits = any(char.isdigit() for char in bullets_joined)
                    if not has_digits:
                        warnings.append(f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; color:#f59e0b;">{get_icon("alert-triangle")} <strong>{exp["role"]}</strong> at <strong>{exp["company"]}</strong> bullets contain no quantitative metrics.</div>')

                    weak_verbs = ["helped", "assisted", "managed", "worked", "did"]
                    for verb in weak_verbs:
                        if verb in bullets_joined.lower():
                            warnings.append(f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; color:#f59e0b;">{get_icon("alert-triangle")} <strong>{exp["role"]}</strong> bullets contain weak/passive action verb <strong>{verb}</strong>.</div>')

            projs = [pr for pr in current_resume_data.get("projects", []) if pr.get("is_selected", True)]
            if not projs:
                warnings.append(f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; color:#f59e0b;">{get_icon("alert-triangle")} No projects are selected.</div>')

            skls = [sk for sk in current_resume_data.get("skills", []) if sk.get("is_selected", True)]
            if not skls:
                warnings.append(f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; color:#f59e0b;">{get_icon("alert-triangle")} No technical skill categories are selected.</div>')

            missing = st.session_state.jd_analysis.get("required_tech", [])
            resume_full_text = fresh_markdown.lower()
            missing_skills_found = [m for m in missing if m.lower() not in resume_full_text]

            if missing_skills_found:
                warnings.append(f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; color:#ef4444;">{get_icon("alert-triangle")} <strong>Missing JD Tech Keywords:</strong> {", ".join(missing_skills_found)}</div>')

            if not warnings:
                st.markdown(f'<div style="display:flex; align-items:center; gap:8px; color:#10b981; font-weight:600;">{get_icon("check-circle")} All quality checks passed. Resume is fully optimized.</div>', unsafe_allow_html=True)
            else:
                for w in warnings:
                    st.markdown(w, unsafe_allow_html=True)

            ai_sugs = st.session_state.ats_optimization.get("suggestions", [])
            if ai_sugs:
                st.markdown("#### Actionable AI Improvements:")
                for sug in ai_sugs:
                    st.markdown(f"- {sug}")