# cvilization
**Build your career empire!**

![cvilization Hero Banner](cvilization_hero_banner.png)

**[Project Demo](https://your-cvilization-link.com)**

Welcome to **cvilization**, the automated resume forge and career-empire architect. Because in the modern corporate colosseum, your resume shouldn't just list your achievements; it should aggressively conquer the Applicant Tracking System (ATS) and leave recruiters weeping tears of joy.

---

## The Problem Statement

In an alternate timeline (last Tuesday), job hunters spent hours copy-pasting bullet points, manual-aligning tables in MS Word, and crying over broken LaTeX dependencies, all to receive a generic automated rejection email 45 seconds after applying. 

The core issues:
1. **The ATS Black Box**: Resumes optimized for humans get vaporized by automated screening algorithms.
2. **The LaTeX Tax**: High-quality resume designs require LaTeX, but installing a local compiler can make grown developers question their life choices.
3. **The Multiverse of Tailoring**: Adjusting your resume for 50 different jobs is a recipe for repetitive strain injury.

**cvilization** solves this by wrapping a high-octane **AI Agent Workflow** (powered by Gemini) and a robust **local SQL database** inside a sleek **Streamlit interface**. 

It analyzes the Job Description, matches your profile, toggles irrelevant sections off, injects necessary keywords, automatically updates your resume state, compiles a pristine LaTeX document, and hands you a print-ready PDF—all with a single button click. Undo/Redo is supported (via Ctrl+Z/Ctrl+Y) so you can reverse your mistakes faster than you can make them.

---

## Folder Structure

The repository is modularly structured, keeping the brain, the muscles, and the beauty beautifully separated.

```
cvilization/
├── app.py                     # The grand Streamlit arena (UI, event loops, real-time previews)
├── config.py                  # Global configurations & file-path resolutions
├── agents/                    # The AI Brain Trust (Agent nodes & workflow graphs)
│   ├── workflow.py            # LangGraph pipeline orchestration
│   ├── jd_analyzer.py         # Node to extract skills, keywords, and role info from JDs
│   ├── ats_optimizer.py        # Node to score profile and recommend toggling sections
│   ├── latex_generator.py     # Converts database records to clean, beautiful LaTeX code
│   └── pdf_compiler.py        # Local LaTeX engine coordinator (finds and executes pdflatex)
├── database/                  # Persistence Layer (SQLite + SQLAlchemy schemas)
│   ├── connection.py          # Schema initialization & preloaded data loading
│   ├── models.py              # Pydantic schemas for data validation
│   └── repository.py          # Data access patterns (CRUD operations & history state tracking)
├── services/                  # Core LLM Integrations
│   ├── llm_service.py         # Multi-provider factory (Gemini / OpenAI API configurations)
│   └── ai_helper.py           # Individual prompt helpers (Cover letters, cold emails, bios)
├── utils/                     # Utility Belts & Fallback Generators
│   ├── pdf_generator.py       # Local PDF compiler utilizing python FPDF2
│   ├── pdf_fallback.py        # Pure-python raw PDF writer (runs without dependencies!)
│   ├── file_exporter.py       # ZIP bundling and markdown summary exports
│   └── latex_escaper.py       # Prevents LaTeX syntax errors from special character injections
└── styles/                    # Visual Styling
    └── main.css               # The gorgeous dark-glassmorphism theme
```

---

## System Architecture

The following diagram illustrates how your career empire is forged. When you click **Run AI Job Description Optimizer**, a state-managed pipeline executes sequentially:

```mermaid
graph TD
    %% Define Styles
    classDef ui fill:#8B1D1D,stroke:#fee2e2,stroke-width:2px,color:#fff;
    classDef graph fill:#1E1E1E,stroke:#8B1D1D,stroke-width:2px,color:#eee;
    classDef db fill:#2A2A2A,stroke:#fee2e2,stroke-width:1px,color:#ddd;
    classDef service fill:#0f172a,stroke:#38bdf8,stroke-width:1px,color:#fff;

    %% Components
    UI[Streamlit UI app.py]:::ui
    DB[(SQLite cvilization.db)]:::db
    
    subgraph LangGraph Pipeline [agents/workflow.py]
        direction TB
        NodeA[Analyze JD Node<br>agents/jd_analyzer.py]:::graph
        NodeB[Optimize ATS Node<br>agents/ats_optimizer.py]:::graph
        NodeC[Generate LaTeX Node<br>agents/latex_generator.py]:::graph
        NodeD[Compile PDF Node<br>agents/pdf_compiler.py]:::graph
        
        NodeA -->|Extracts requirements| NodeB
        NodeB -->|Toggles elements, matches profile| NodeC
        NodeC -->|Translates to TeX source| NodeD
    end
    
    Gemini[Gemini API / LLM Service]:::service
    PDF_Engine[pdflatex compiler / FPDF Fallback]:::service

    %% Interactions
    UI -->|1. Submit JD & Profile| NodeA
    NodeA <-->|Query base profile| DB
    NodeA -->|2. Send JD text| Gemini
    NodeB -->|3. Compare Profile vs JD| Gemini
    NodeB -->|4. Persist selections & update history| DB
    NodeD -->|5. Render PDF| PDF_Engine
    NodeD -->|6. Cache binary results| UI
```

---

## Tech Stack & Key Libraries

Here are the libraries that make this engine roar, complete with their purpose and code snippets demonstrating their role in the project:

### 1. LangGraph (`langgraph`)
* **Purpose**: Orchestrates the execution flow. It structures the multi-agent optimization process as a stateful, directional graph where each node represents a processing task and the output of each node updates the state of the workflow.
* **Code Example ([workflow.py](file:///d:/Placement%20Prep/GEN%20AI/projects/cvilization/agents/workflow.py))**:
```python
from langgraph.graph import StateGraph, START, END

# Define our workflow state schema
class ResumeState(TypedDict):
    provider: str
    api_key: str
    model_name: str
    jd_text: str
    resume_data: Dict[str, Any]
    jd_analysis: Dict[str, Any]
    ats_optimization: Dict[str, Any]
    latex_code: str
    pdf_compiled: bool

# Initialize graph and append execution nodes
workflow = StateGraph(ResumeState)
workflow.add_node("analyze_jd", analyze_jd_node)
workflow.add_node("optimize_ats", optimize_ats_node)
workflow.add_node("generate_latex", generate_latex_node)
workflow.add_node("compile_pdf", compile_pdf_node)

# Chain them up sequentially
workflow.add_edge(START, "analyze_jd")
workflow.add_edge("analyze_jd", "optimize_ats")
workflow.add_edge("optimize_ats", "generate_latex")
workflow.add_edge("generate_latex", "compile_pdf")
workflow.add_edge("compile_pdf", END)

# Compile into a runnable system
compiled_graph = workflow.compile()
```

### 2. LangChain Google GenAI (`langchain-google-genai`)
* **Purpose**: Provides clean abstractions to call the Gemini API, ensuring structured inputs and parsing outputs while maintaining prompt guidelines and JSON formatting constraints.
* **Code Example ([ats_optimizer.py](file:///d:/Placement%20Prep/GEN%20AI/projects/cvilization/agents/ats_optimizer.py))**:
```python
from services.llm_service import get_llm
from langchain_core.prompts import ChatPromptTemplate

llm = get_llm(provider, api_key, model_name)
prompt = ChatPromptTemplate.from_template("""
Compare the candidate's profile context against the target job requirements.
JSON template to output:
{{
  "match_score": 85,
  "ats_score": 78,
  "missing_skills": ["AWS", "Docker"],
  "recommended_selections": {{
      "education_ids": [1],
      "experience_ids": [1, 2]
  }}
}}
CANDIDATE CONTEXT: {context}
JOB REQUIREMENTS: {jd_summary}
""")

chain = prompt | llm
response = chain.invoke({"context": context, "jd_summary": jd_summary})
```

### 3. Streamlit (`streamlit`)
* **Purpose**: Serves as our beautiful frontend framework. Enables quick layout definition, custom styling injections, reactive states, re-ordering actions, download button handles, and undo/redo keyboard listener binding.
* **Code Example ([app.py](file:///d:/Placement%20Prep/GEN%20AI/projects/cvilization/app.py))**:
```python
import streamlit as st

# Custom CSS injector
def load_css():
    css_path = Path("styles/main.css")
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Tabs navigation
tabs = st.tabs(["Profile", "Education", "Experience", "Projects", "Skills"])
with tabs[0]:
    st.subheader("Edit Profile Information")
    with st.form("profile_form"):
        p_name = st.text_input("Full Name", value="Akmal Hossain")
        if st.form_submit_button("Save Profile Settings"):
            update_personal_info({"name": p_name})
            st.rerun()
```

### 4. Pure Python PDF Writer (`utils.pdf_fallback.py`)
* **Purpose**: When local system LaTeX compilers aren't found, this fallback engine directly writes binary PDF structural blocks from scratch using basic PDF specifications, escaping Parentheses and backslashes, tracking positions, and outputting pristine streams without any third-party rendering wrappers.
* **Code Example ([pdf_fallback.py](file:///d:/Placement%20Prep/GEN%20AI/projects/cvilization/utils/pdf_fallback.py))**:
```python
def generate_fallback_pdf(resume_data: dict) -> bytes:
    stream_cmds = []
    stream_cmds.append("BT")  # Begin Text block
    stream_cmds.append("/F2 20 Tf")  # Font F2 (Helvetica-Bold), size 20
    stream_cmds.append("54 730 Td")  # Position
    stream_cmds.append(f"({escape_pdf_text(name)}) Tj")  # Print name
    
    # ... builds the layout stream details ...
    
    stream_bytes = "\n".join(stream_cmds).encode("latin-1")
    # Wrap in structural PDF objects, catalogs, cross-reference tables, and return raw bytes
```

### 5. SQLite Database Repository (`database.repository.py`)
* **Purpose**: Keeps trace of all elements in the resume database and records historical snapshots to allow real-time State Undo & Redo.
* **Code Example ([repository.py](file:///d:/Placement%20Prep/GEN%20AI/projects/cvilization/database/repository.py))**:
```python
def save_to_history(state_dict: dict) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    # Serialize the complete FullResumeModel into a single historical record
    cursor.execute("INSERT INTO history (state_json) VALUES (?)", (json.dumps(state_dict),))
    conn.commit()
    conn.close()
```

---

## Conclusion

Congratulations! Your resume is no longer just another document in a sea of applications. With **cvilization**, you have an AI-powered career companion that helps you craft tailored, ATS-friendly resumes for every opportunity. Focus on building your skills and telling your story. Let the AI handle the formatting, optimization, and keyword matching while you focus on building your career empire.

Good luck, and may your inbox be filled with interview invitations rather than automated rejections.


