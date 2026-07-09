import json
import logging
from typing import Dict, Any
from services.llm_service import get_llm
from services.ai_helper import get_base_context
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger("cvilization.agents.ats_optimizer")

def optimize_for_ats(
    provider: str, 
    api_key: str, 
    model_name: str, 
    resume_data: Dict[str, Any], 
    jd_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    context = get_base_context(resume_data)
    jd_summary = f"Title: {jd_analysis.get('title', 'Unknown')}\n"
    jd_summary += f"Required Tech: {', '.join(jd_analysis.get('required_tech', []))}\n"
    jd_summary += f"Preferred Tech: {', '.join(jd_analysis.get('preferred_tech', []))}\n"
    jd_summary += f"ATS Keywords: {', '.join(jd_analysis.get('ats_keywords', []))}\n"
    
    try:
        llm = get_llm(provider, api_key, model_name)
        prompt = ChatPromptTemplate.from_template("""
Compare the candidate's profile context against the target job requirements. Output a JSON object containing scores and suggestions.

Do not write markdown backticks (like ```json) or explanation, output ONLY raw JSON text.

JSON template to output:
{{
  "match_score": 85,
  "ats_score": 78,
  "missing_skills": ["AWS", "Docker", ...],
  "recommended_selections": {{
      "education_ids": [1, 2],
      "experience_ids": [1, 2, 4],
      "project_ids": [1, 2],
      "skill_categories": ["Programming Languages", "GenAI & Backend Development"],
      "certification_ids": [1, 3],
      "achievement_ids": [1, 2]
  }},
  "suggestions": [
      "Actionable optimization step 1",
      "Actionable optimization step 2"
  ]
}}

CANDIDATE CONTEXT:
{context}

JOB REQUIREMENTS:
{jd_summary}
""")
        chain = prompt | llm
        response = chain.invoke({
            "context": context,
            "jd_summary": jd_summary
        })
        
        content = response.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            if lines[0].startswith("```json") or lines[0] == "```":
                lines = lines[1:]
            if lines[-1] == "```":
                lines = lines[:-1]
            content = "\n".join(lines).strip()
            
        return json.loads(content)
        
    except Exception as e:
        logger.error(f"Error in ATS Optimizer: {e}", exc_info=True)
        resume_text = context.lower()
        required_tech = [t.lower() for t in jd_analysis.get("required_tech", [])]
        matched = [t for t in required_tech if t in resume_text]
        score = int((len(matched) / len(required_tech)) * 100) if required_tech else 70
        
        return {
            "match_score": score,
            "ats_score": score,
            "missing_skills": [t for t in jd_analysis.get("required_tech", []) if t.lower() not in resume_text],
            "recommended_selections": {
                "education_ids": [e.get("id") for e in resume_data.get("education", [])],
                "experience_ids": [e.get("id") for e in resume_data.get("experiences", [])],
                "project_ids": [p.get("id") for p in resume_data.get("projects", [])],
                "skill_categories": [s.get("category") for s in resume_data.get("skills", [])],
                "certification_ids": [c.get("id") for c in resume_data.get("certifications", [])],
                "achievement_ids": [a.get("id") for a in resume_data.get("achievements", [])]
            },
            "suggestions": ["Add missing skills from job description.", "Quantify achievements using metrics."]
        }
