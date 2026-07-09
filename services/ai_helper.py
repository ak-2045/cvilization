import json
from typing import Dict, Any
from services.llm_service import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_base_context(resume_data: Dict[str, Any]) -> str:
    p = resume_data.get("personal_info", {})
    context = f"Candidate Name: {p.get('name', '')}\n"
    context += f"Degree/Branch: {p.get('degree', '')} from {p.get('college', '')}\n"
    context += f"CGPA: {p.get('cgpa', '')}\n\n"
    
    context += "EDUCATION:\n"
    for edu in resume_data.get("education", []):
        if edu.get("is_selected", True):
            context += f"- {edu.get('degree')}, {edu.get('institute')} ({edu.get('year')}) - CGPA/Perc: {edu.get('cgpa_percentage')}\n"
            
    context += "\nEXPERIENCES:\n"
    for exp in resume_data.get("experiences", []):
        if exp.get("is_selected", True):
            bullets_str = "\n".join([f"  * {b}" for b in exp.get("bullets", [])])
            context += f"- Role: {exp.get('role')} at {exp.get('company')} ({exp.get('dates')})\n"
            context += f"  Technologies: {', '.join(exp.get('technologies', []))}\n"
            context += f"{bullets_str}\n"
            
    context += "\nPROJECTS:\n"
    for proj in resume_data.get("projects", []):
        if proj.get("is_selected", True):
            bullets_str = "\n".join([f"  * {b}" for b in proj.get("bullets", [])])
            context += f"- {proj.get('title')} ({proj.get('duration')})\n"
            context += f"  Tech Stack: {', '.join(proj.get('tech_stack', []))}\n"
            context += f"{bullets_str}\n"
            
    context += "\nTECHNICAL SKILLS:\n"
    for skill in resume_data.get("skills", []):
        if skill.get("is_selected", True):
            context += f"- {skill.get('category')}: {', '.join(skill.get('items', []))}\n"
            
    context += "\nCERTIFICATIONS:\n"
    for cert in resume_data.get("certifications", []):
        if cert.get("is_selected", True):
            context += f"- {cert.get('name')} by {cert.get('issuer')} ({cert.get('date')})\n"
            
    context += "\nACHIEVEMENTS / POSITIONS OF RESPONSIBILITY:\n"
    for ach in resume_data.get("achievements", []):
        if ach.get("is_selected", True):
            context += f"- {ach.get('category')}: {ach.get('description')}\n"
            
    return context

def generate_cover_letter(provider: str, api_key: str, model_name: str, resume_data: Dict[str, Any], jd_text: str) -> str:
    llm = get_llm(provider, api_key, model_name)
    context = get_base_context(resume_data)
    prompt = ChatPromptTemplate.from_template("""
You are an expert recruiter. Write a compelling, professional cover letter tailored for the job description below, using details from the candidate's profile context. Do NOT invent experiences or credentials. Keep it under 400 words.

CANDIDATE CONTEXT:
{context}

JOB DESCRIPTION:
{jd}

Write a cover letter linking the candidate's projects/experiences to the requirements:
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "jd": jd_text})

def generate_recruiter_email(provider: str, api_key: str, model_name: str, resume_data: Dict[str, Any], jd_text: str) -> str:
    llm = get_llm(provider, api_key, model_name)
    context = get_base_context(resume_data)
    prompt = ChatPromptTemplate.from_template("""
Write a cold email to a recruiter for the job description below. Highlight matching projects/experiences. Make it brief, structured, with a clear subject line.

CANDIDATE CONTEXT:
{context}

JOB DESCRIPTION:
{jd}

Write the email:
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "jd": jd_text})

def generate_linkedin_about(provider: str, api_key: str, model_name: str, resume_data: Dict[str, Any]) -> str:
    llm = get_llm(provider, api_key, model_name)
    context = get_base_context(resume_data)
    prompt = ChatPromptTemplate.from_template("""
Write a LinkedIn 'About' section for the candidate profile below. Do not fabricate details. Use a professional, modern tone.

CANDIDATE CONTEXT:
{context}

Write the LinkedIn About text:
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context})

def generate_github_summary(provider: str, api_key: str, model_name: str, resume_data: Dict[str, Any]) -> str:
    llm = get_llm(provider, api_key, model_name)
    context = get_base_context(resume_data)
    prompt = ChatPromptTemplate.from_template("""
Create a markdown formatted GitHub Profile README summary for the candidate profile below.

CANDIDATE CONTEXT:
{context}

Write the README:
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context})

def generate_portfolio_bio(provider: str, api_key: str, model_name: str, resume_data: Dict[str, Any]) -> str:
    llm = get_llm(provider, api_key, model_name)
    context = get_base_context(resume_data)
    prompt = ChatPromptTemplate.from_template("""
Write a personal biography for a portfolio website (a short summary and a detailed bio).

CANDIDATE CONTEXT:
{context}

Write the bios:
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context})

def generate_interview_intro(provider: str, api_key: str, model_name: str, resume_data: Dict[str, Any]) -> str:
    llm = get_llm(provider, api_key, model_name)
    context = get_base_context(resume_data)
    prompt = ChatPromptTemplate.from_template("""
Write a 90-second "Tell me about yourself" pitch for interviews based on the candidate profile. Do not invent details.

CANDIDATE CONTEXT:
{context}

Write the pitch:
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context})

def rewrite_bullet_point(
    provider: str,
    api_key: str,
    model_name: str,
    bullet: str,
    company: str,
    role: str,
    action: str,
    jd_text: str = ""
) -> str:
    llm = get_llm(provider, api_key, model_name)
    
    action_prompts = {
        "quantify": "Rewrite this bullet point to inject metrics, percentages, dollar amounts, or numbers. Make realistic, recruiter-friendly estimations based on context, but do NOT make up major falsehoods.",
        "star": "Structure this bullet using the STAR method (Situation, Task, Action, Result). Highlight what was done, how it was done, and what the positive outcome was.",
        "shorten": "Make this bullet point highly concise, removing fluff and keeping only the core technical impact. Keep it to one line.",
        "expand": "Expand this bullet point to add details about the engineering design decisions, tools, and technical difficulties faced.",
        "strong_verbs": "Replace weak or passive verbs (like 'helped', 'assisted', 'managed') with powerful technical action verbs (like 'spearheaded', 'orchestrated', 'implemented', 'engineered').",
        "recruiter_phrasing": "Adapt this bullet to read professionally for business executives and recruiters, highlighting business value and scalability.",
        "ats_tailor": f"Optimize this bullet point to directly align with the target job description: '{jd_text[:400]}' by using matching keywords and relevant metrics."
    }
    
    action_desc = action_prompts.get(action, "Rewrite this bullet point to make it more professional.")
    
    prompt = ChatPromptTemplate.from_template("""
Optimize this resume bullet point. Do NOT fabricate major lies. Maintain context.

Context:
Company/Project: {company}
Role: {role}
Original Bullet: {bullet}

Action:
{action_desc}

Write ONLY the optimized bullet point (no prefixes, quotes, bullet symbols, or comments):
""")
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({
        "company": company,
        "role": role,
        "bullet": bullet,
        "action_desc": action_desc
    })
    return result.strip().strip('"').strip("'")
