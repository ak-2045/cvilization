import logging
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, START, END

from agents.jd_analyzer import analyze_job_description
from agents.ats_optimizer import optimize_for_ats
from agents.latex_generator import generate_latex_resume
from agents.pdf_compiler import compile_pdf

logger = logging.getLogger("cvilization.agents.workflow")

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
    pdf_log: str
    pdf_bytes: bytes

def analyze_jd_node(state: ResumeState) -> Dict[str, Any]:
    analysis = analyze_job_description(
        provider=state["provider"],
        api_key=state["api_key"],
        model_name=state["model_name"],
        jd_text=state["jd_text"]
    )
    return {"jd_analysis": analysis}

def optimize_ats_node(state: ResumeState) -> Dict[str, Any]:
    optimization = optimize_for_ats(
        provider=state["provider"],
        api_key=state["api_key"],
        model_name=state["model_name"],
        resume_data=state["resume_data"],
        jd_analysis=state["jd_analysis"]
    )
    return {"ats_optimization": optimization}

def generate_latex_node(state: ResumeState) -> Dict[str, Any]:
    latex_code = generate_latex_resume(state["resume_data"])
    return {"latex_code": latex_code}

def compile_pdf_node(state: ResumeState) -> Dict[str, Any]:
    success, result = compile_pdf(state["latex_code"])
    if success:
        return {
            "pdf_compiled": True,
            "pdf_bytes": result,
            "pdf_log": "Compilation Successful."
        }
    else:
        return {
            "pdf_compiled": False,
            "pdf_bytes": b"",
            "pdf_log": str(result)
        }

def build_resume_workflow():
    workflow = StateGraph(ResumeState)
    
    workflow.add_node("analyze_jd", analyze_jd_node)
    workflow.add_node("optimize_ats", optimize_ats_node)
    workflow.add_node("generate_latex", generate_latex_node)
    workflow.add_node("compile_pdf", compile_pdf_node)
    
    workflow.add_edge(START, "analyze_jd")
    workflow.add_edge("analyze_jd", "optimize_ats")
    workflow.add_edge("optimize_ats", "generate_latex")
    workflow.add_edge("generate_latex", "compile_pdf")
    workflow.add_edge("compile_pdf", END)
    
    return workflow.compile()
