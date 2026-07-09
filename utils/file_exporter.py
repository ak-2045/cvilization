import json
import io
import zipfile
from typing import Dict, Any, Optional

def generate_markdown_summary(resume_data: Dict[str, Any]) -> str:
    p = resume_data.get("personal_info", {})
    md = f"# {p.get('name', 'Resume')}\n\n"
    
    contact = []
    if p.get("phone"): contact.append(p.get("phone"))
    if p.get("email"): contact.append(p.get("email"))
    if p.get("location"): contact.append(p.get("location"))
    md += " | ".join(contact) + "\n\n"
    
    socials = []
    if p.get("github_link"): socials.append(f"[GitHub]({p.get('github_link')})")
    if p.get("linkedin_link"): socials.append(f"[LinkedIn]({p.get('linkedin_link')})")
    if p.get("portfolio"): socials.append(f"[Portfolio]({p.get('portfolio')})")
    if socials:
        md += " | ".join(socials) + "\n\n"
        
    md += "---\n\n"
    
    edu_list = [e for e in resume_data.get("education", []) if e.get("is_selected", True)]
    if edu_list:
        md += "## Education\n\n"
        for edu in edu_list:
            md += f"**{edu.get('degree')}** — *{edu.get('institute')}* ({edu.get('year')})\n"
            md += f"- CGPA/Percentage: {edu.get('cgpa_percentage')} | Board/University: {edu.get('board_university')}\n\n"
            
    exp_list = [e for e in resume_data.get("experiences", []) if e.get("is_selected", True)]
    if exp_list:
        md += "## Experience\n\n"
        for exp in exp_list:
            md += f"**{exp.get('role')}** | *{exp.get('company')}* — {exp.get('location')} ({exp.get('dates')})\n"
            if exp.get("technologies"):
                md += f"*Technologies: {', '.join(exp.get('technologies'))}*\n"
            for bullet in exp.get("bullets", []):
                md += f"- {bullet}\n"
            md += "\n"
            
    proj_list = [pr for pr in resume_data.get("projects", []) if pr.get("is_selected", True)]
    if proj_list:
        md += "## Projects\n\n"
        for proj in proj_list:
            md += f"**{proj.get('title')}** ({proj.get('duration')})\n"
            if proj.get("tech_stack"):
                md += f"*Tech Stack: {', '.join(proj.get('tech_stack'))}*\n"
            
            links = []
            if proj.get("github_link"):
                links.append(f"[GitHub]({proj.get('github_link')})")
            if proj.get("live_demo_link"):
                links.append(f"[Live Demo]({proj.get('live_demo_link')})")
            if links:
                md += f"*Links: {' | '.join(links)}*\n"
                
            for bullet in proj.get("bullets", []):
                md += f"- {bullet}\n"
            md += "\n"
            
    skills_list = [s for s in resume_data.get("skills", []) if s.get("is_selected", True)]
    if skills_list:
        md += "## Technical Skills\n\n"
        for skill in skills_list:
            md += f"- **{skill.get('category')}**: {', '.join(skill.get('items', []))}\n"
        md += "\n"
        
    cert_list = [c for c in resume_data.get("certifications", []) if c.get("is_selected", True)]
    if cert_list:
        md += "## Certifications\n\n"
        for cert in cert_list:
            url_str = f" ([Credential]({cert.get('credential_url')}))" if cert.get("credential_url") else ""
            md += f"- **{cert.get('name')}** — {cert.get('issuer')} ({cert.get('date')}){url_str}\n"
        md += "\n"
        
    ach_list = [a for a in resume_data.get("achievements", []) if a.get("is_selected", True)]
    if ach_list:
        md += "## Achievements / Leadership\n\n"
        for ach in ach_list:
            md += f"### {ach.get('category')}\n"
            md += f"{ach.get('description')}\n\n"
            
    return md.strip()

def generate_zip_bundle(
    resume_data: Dict[str, Any], 
    latex_code: str, 
    pdf_bytes: Optional[bytes] = None
) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("resume.tex", latex_code)
        if pdf_bytes:
            zip_file.writestr("resume.pdf", pdf_bytes)
        md_text = generate_markdown_summary(resume_data)
        zip_file.writestr("resume.md", md_text)
        json_data = json.dumps(resume_data, indent=2)
        zip_file.writestr("resume.json", json_data)
        
        readme = (
            "====================================================\n"
            "   cvilization - AI Generated Resume Bundle\n"
            "====================================================\n\n"
            "Your bundle contains:\n"
            "1. resume.tex : The raw LaTeX source file.\n"
            "2. resume.pdf : Compiled high-quality PDF.\n"
            "3. resume.md  : Markdown format.\n"
            "4. resume.json: Structured JSON.\n"
        )
        zip_file.writestr("README.txt", readme)
        
    return zip_buffer.getvalue()
