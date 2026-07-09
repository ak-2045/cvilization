import json
import logging
from typing import Dict, Any
from services.llm_service import get_llm
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger("cvilization.agents.jd_analyzer")

def analyze_job_description(provider: str, api_key: str, model_name: str, jd_text: str) -> Dict[str, Any]:
    if not jd_text.strip():
        return {
            "title": "General Application",
            "required_tech": [],
            "preferred_tech": [],
            "responsibilities": [],
            "action_verbs": [],
            "ats_keywords": []
        }
        
    try:
        llm = get_llm(provider, api_key, model_name)
        prompt = ChatPromptTemplate.from_template("""
Extract structural details from the following Job Description (JD). Return the result strictly as a valid JSON object matching the template below. 

Do not include any markdown backticks (like ```json) or explanation, return ONLY the raw JSON text.

JSON template to output:
{{
  "title": "Exact job title",
  "required_tech": ["tech1", "tech2", ...],
  "preferred_tech": ["tech1", "tech2", ...],
  "responsibilities": ["core responsibility 1", "core responsibility 2", ...],
  "action_verbs": ["design", "optimize", "implement", ...],
  "ats_keywords": ["keyword1", "keyword2", ...]
}}

JOB DESCRIPTION:
{jd}
""")
        chain = prompt | llm
        response = chain.invoke({"jd": jd_text})
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
        logger.error(f"Error in JD Analyzer agent: {e}", exc_info=True)
        return {
            "title": "Parsed Position",
            "required_tech": [],
            "preferred_tech": [],
            "responsibilities": [],
            "action_verbs": [],
            "ats_keywords": ["Software", "Development"],
            "error": str(e)
        }
