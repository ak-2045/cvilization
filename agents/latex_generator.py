import os
import logging
from typing import Dict, Any
from utils.latex_escaper import escape_latex_recursive

logger = logging.getLogger("cvilization.agents.latex_generator")

def generate_latex_resume(resume_data: Dict[str, Any]) -> str:
    data = escape_latex_recursive(resume_data)
    p = data.get("personal_info", {})
    
    name = p.get("name", "Akmal Hossain")
    course = p.get("course", "B.Tech in Electronics and Communication Engineering")
    roll = p.get("roll_number", "23UEC116")
    phone = p.get("phone", "+91 93726 65103")
    emaila = p.get("email", "akmal.hossain.ece.27@gmail.com")
    emailb = p.get("college_email", "AKMAL_23UEC116@ug.nita.ac.in")
    github = p.get("github", "ak-2045")
    githublink = p.get("github_link", "https://github.com/ak-2045")
    linkedin = p.get("linkedin", "akmal-hossain-72a7b5277")
    linkedinlink = p.get("linkedin_link", "https://www.linkedin.com/in/akmal-hossain-72a7b5277")
    location = p.get("location", "National Institute of Technology, Agartala")

    header_tex = f"""\\newcommand{{\\name}}{{{name}}}
\\newcommand{{\\course}}{{{course}}}
\\newcommand{{\\roll}}{{{roll}}} 
\\newcommand{{\\phone}}{{{phone}}}

\\newcommand{{\\emaila}}{{{emaila}}}
\\newcommand{{\\emailb}}{{{emailb}}}

\\newcommand{{\\github}}{{{github}}}
\\newcommand{{\\githublink}}{{{githublink}}}

\\newcommand{{\\linkedin}}{{{linkedin}}}
\\newcommand{{\\linkedinlink}}{{{linkedinlink}}}"""

    edu_list = [e for e in data.get("education", []) if e.get("is_selected", True)]
    edu_rows = []
    for edu in edu_list:
        degree = edu.get("degree", "")
        institute = edu.get("institute", "")
        board_univ = edu.get("board_university", "")
        cgpa_perc = edu.get("cgpa_percentage", "")
        year = edu.get("year", "")
        row = f"  {degree} & {institute} & {board_univ} & {cgpa_perc} & {year}\\\\"
        edu_rows.append(row)
    
    edu_rows_tex = "\n  \\hline\n".join(edu_rows)
    education_tex = ""
    if edu_list:
        education_tex = f"""\\section{{\\textbf{{Education}}}}
\\setlength{{\\tabcolsep}}{{5pt}}
\\small{{\\begin{{tabularx}}
{{\\dimexpr\\textwidth-2mm\\relax}}{{|c|C|c|c|c|}}
  \\hline
  \\textbf{{Degree }} & \\textbf{{Institute}} & \\textbf{{Board / University}} & \\textbf{{CGPA/Percentage}} & \\textbf{{Year}}\\\\
  \\hline
{edu_rows_tex}
  \\hline
\\end{{tabularx}}}}
\\vspace{{-1.5mm}}"""

    exp_list = [e for e in data.get("experiences", []) if e.get("is_selected", True)]
    exp_items_tex = []
    for exp in exp_list:
        role = exp.get("role", "")
        company = exp.get("company", "")
        loc = exp.get("location", "")
        dates = exp.get("dates", "")
        bullets = exp.get("bullets", [])
        bullets_tex = "\n".join([f"    \\item {{{b}}}" for b in bullets])
        exp_item = f"""\\resumeSubheading
  {{{role}}}{{{loc}}}
  {{{company}}}{{{dates}}}
  \\resumeItemListStart
{bullets_tex}
  \\resumeItemListEnd"""
        exp_items_tex.append(exp_item)
        
    experiences_tex = ""
    if exp_list:
        experiences_tex = "\\section{\\textbf{Experience}}\n\\resumeSubHeadingListStart\n" + "\n\n".join(exp_items_tex) + "\n\\resumeSubHeadingListEnd\n\\vspace{-6.5mm}"

    proj_list = [pr for pr in data.get("projects", []) if pr.get("is_selected", True)]
    proj_items_tex = []
    for proj in proj_list:
        title = proj.get("title", "")
        tech = ", ".join(proj.get("tech_stack", []))
        dur = proj.get("duration", "")
        g_link = proj.get("github_link", "")
        l_link = proj.get("live_demo_link", "")
        bullets = proj.get("bullets", [])
        
        links_parts = []
        if l_link:
            links_parts.append(f"\\href{{{l_link}}}{{\\textbf{{Live}}}}")
        if g_link:
            links_parts.append(f"\\href{{{g_link}}}{{\\textbf{{GitHub}}}}")
            
        links_tex = " \\;|\\; ".join(links_parts)
        bullets_tex = "\n".join([f"    \\item {{{b}}}" for b in bullets])
        
        proj_item = f"""\\resumeProject
  {{{title}}}
  {{{tech}}}
  {{{dur}}}
  {{{links_tex}}}
  \\resumeItemListStart
{bullets_tex}
  \\resumeItemListEnd"""
        proj_items_tex.append(proj_item)
        
    projects_tex = ""
    if proj_list:
        projects_tex = "\\section{\\textbf{Projects}}\n\\resumeSubHeadingListStart\n" + "\n\\vspace{-1mm}\n\n".join(proj_items_tex) + "\n\\resumeSubHeadingListEnd\n\\vspace{-7.5mm}"

    skills_list = [s for s in data.get("skills", []) if s.get("is_selected", True)]
    skill_items_tex = []
    for skill in skills_list:
        cat = skill.get("category", "")
        items_str = ", ".join(skill.get("items", []))
        skill_items_tex.append(f"\\resumeSubItem{{{cat}}}\n  {{{items_str}}}")
        
    skills_tex = ""
    if skills_list:
        skills_tex = "\\section{\\textbf{Technical Skills}}\n\\resumeHeadingSkillStart\n" + "\n\n".join(skill_items_tex) + "\n\\resumeHeadingSkillEnd\n\\vspace{-1mm}"

    cert_list = [c for c in data.get("certifications", []) if c.get("is_selected", True)]
    cert_items_tex = []
    for cert in cert_list:
        name_c = cert.get("name", "")
        issuer = cert.get("issuer", "")
        date = cert.get("date", "")
        url = cert.get("credential_url", "")
        url_tex = f"\\href{{{url}}}{{\\textbf{{View}}}}" if url else ""
        
        cert_item = f"""\\resumeSubheading
  {{{name_c}}}{{{date}}}
  {{{issuer}}}
  {{{url_tex}}}"""
        cert_items_tex.append(cert_item)
        
    certifications_tex = ""
    if cert_list:
        certifications_tex = "\\section{\\textbf{Certifications}}\n\\resumeSubHeadingListStart\n" + "\n\n".join(cert_items_tex) + "\n\\resumeSubHeadingListEnd\n\\vspace{-5mm}"

    ach_list = [a for a in data.get("achievements", []) if a.get("is_selected", True)]
    ach_items_tex = []
    for ach in ach_list:
        cat = ach.get("category", "")
        desc = ach.get("description", "")
        ach_item = f"\\item{{\n\\textbf{{{cat}:}} {desc}}}"
        ach_items_tex.append(ach_item)
        
    achievements_tex = ""
    if ach_list:
        ach_items_tex_joined = "\n\n\\vspace{-1mm}\n\n".join(ach_items_tex)
        achievements_tex = f"""\\section{{\\textbf{{Achievements}}}}
\\vspace{{0.2mm}}

\\begin{{itemize}}[leftmargin=0.05in, label={{}}]
\\small{{

{ach_items_tex_joined}

}}
\\end{{itemize}}
\\vspace{{-4mm}}"""

    full_latex = f"""\\documentclass[a4paper,11pt]{{article}}
\\usepackage{{latexsym}}
\\usepackage{{xcolor}}
\\usepackage{{float}}
\\usepackage{{ragged2e}}
\\usepackage[empty]{{fullpage}}
\\usepackage{{wrapfig}}
\\usepackage{{lipsum}}
\\usepackage{{tabularx}}
\\usepackage{{titlesec}}
\\usepackage{{geometry}}
\\usepackage{{fontawesome}}
\\usepackage{{marvosym}}
\\usepackage{{verbatim}}
\\usepackage{{enumitem}}
\\usepackage[hidelinks]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage{{multicol}}
\\usepackage{{graphicx}}
\\usepackage{{cfr-lm}}
\\usepackage[T1]{{fontenc}}
\\setlength{{\\multicolsep}}{{0pt}} 
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyfoot{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}
\\geometry{{left=0.6cm, top=0.8cm, right=0.6cm, bottom=0.5cm}}

\\usepackage[most]{{tcolorbox}}
\\tcbset{{
	frame code={{}}
	center title,
	left=0pt,
	right=0pt,
	top=0pt,
	bottom=0pt,
	colback=gray!20,
	colframe=white,
	width=\\dimexpr\\textwidth\\relax,
	enlarge left by=-2mm,
	boxsep=4pt,
	arc=0pt,outer arc=0pt,
}}

\\urlstyle{{same}}

\\raggedright
\\setlength{{\\tabcolsep}}{{0in}}

\\titleformat{{\\section}}{{
  \\vspace{{-4pt}}\\scshape\\raggedright\\large
}}{{}}{{0em}}{{}}[\\color{{black}}\\titlerule \\vspace{{-7pt}}]


\\newcommand{{\\resumeItem}}[2]{{
  \\item{{
    \\textbf{{#1}}{{:\\hspace{{0.5mm}}#2 \\vspace{{-0.5mm}}}}
  }}
}}

\\newcommand{{\\resumePOR}}[3]{{
\\vspace{{0.5mm}}\\item
    \\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
        \\textbf{{#1}},\\hspace{{0.3mm}}#2 & \\textit{{\\small{{#3}}}} 
    \\end{{tabular*}}
    \\vspace{{-2mm}}
}}

\\newcommand{{\\resumeSubheading}}[4]{{
\\vspace{{0.5mm}}\\item
    \\begin{{tabular*}}{{0.98\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
        \\textbf{{#1}} & \\textit{{\\footnotesize{{#4}}}} \\\\
        \\textit{{\\footnotesize{{#3}}}} &  \\footnotesize{{#2}}\\\\
    \\end{{tabular*}}
    \\vspace{{-2.4mm}}
}}

\\newcommand{{\\resumeProject}}[4]{{
\\vspace{{0.5mm}}\\item
    \\begin{{tabular*}}{{0.98\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
        \\textbf{{#1}} & \\textit{{\\footnotesize{{#3}}}} \\\\
        \\footnotesize{{\\textit{{#2}}}} & \\footnotesize{{#4}}
    \\end{{tabular*}}
    \\vspace{{-2.4mm}}
}}

\\newcommand{{\\resumeSubItem}}[2]{{\\resumeItem{{#1}}{{#2}}\\vspace{{-4pt}}}}

\\renewcommand{{\\labelitemi}}{{$\\vcenter{{\\hbox{{\\tiny$\\bullet$}}}}$}}

\\newcommand{{\\resumeSubHeadingListStart}}{{\\begin{{itemize}}[leftmargin=*,labelsep=0mm]}}
\\newcommand{{\\resumeHeadingSkillStart}}{{\\begin{{itemize}}[leftmargin=*,itemsep=1.7mm, rightmargin=2ex]}}
\\newcommand{{\\resumeItemListStart}}{{\\begin{{justify}}\\begin{{itemize}}[leftmargin=3ex, rightmargin=2ex, noitemsep,labelsep=1.2mm,itemsep=0mm]\\small}}

\\newcommand{{\\resumeSubHeadingListEnd}}{{\\end{{itemize}}\\vspace{{2mm}}}}
\\newcommand{{\\resumeHeadingSkillEnd}}{{\\end{{itemize}}\\vspace{{-2mm}}}}
\\newcommand{{\\resumeItemListEnd}}{{\\end{{itemize}}\\end{{justify}}\\vspace{{-2mm}}}}
\\newcommand{{\\cvsection}}[1]{{%
\\vspace{{2mm}}
\\begin{{tcolorbox}}
    \\textbf{{\\large #1}}
\\end{{tcolorbox}}
    \\vspace{{-4mm}}
}}

\\newcolumntype{{L}}{{>{{\\raggedright\\arraybackslash}}X}}%
\\newcolumntype{{R}}{{>{{\\raggedleft\\arraybackslash}}X}}%
\\newcolumntype{{C}}{{>{{\\centering\\arraybackslash}}X}}%

{header_tex}

\\begin{{document}}
\\fontfamily{{cmr}}\\selectfont

\\parbox{{2.5cm}}{{
    \\includegraphics[width=2.2cm]{{logo-29.png}}
}}
\\hfill
\\parbox{{\\dimexpr\\linewidth-2.8cm\\relax}}{{

\\begin{{tabularx}}{{\\linewidth}}{{L r}}

\\textbf{{\\LARGE \\name}} 
& \\faPhone\\ \\phone \\\\

\\course 
& \\faEnvelope\\ \\href{{mailto:\\emaila}}{{\\emaila}} \\\\

Roll No.: \\roll 
& 

\\\\

{location}
&
\\href{{mailto:\\emailb}}{{\\textcolor{{blue}}
{{\\faEnvelope\\ College Mail}}}}
\\ $|$\\ 
\\href{{\\githublink}}{{\\textcolor{{blue}}{{\\faGithub\\
GitHub}}}}
\\ $|$\\ 
\\href{{\\linkedinlink}}{{\\textcolor{{blue}}{{\\faLinkedin\\
LinkedIn}}}}
\\\\

\\end{{tabularx}}
}}

\\vspace{{-2mm}}

{education_tex}

{experiences_tex}

{projects_tex}

{skills_tex}

{certifications_tex}

{achievements_tex}

\\vfill
\\center{{\\footnotesize Last updated: \\today}}

\\end{{document}}
"""
    return full_latex
