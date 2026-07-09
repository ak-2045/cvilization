from fpdf import FPDF
from typing import Dict, Any
import io

def sanitize(text: str) -> str:
    if not text:
        return ""
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u2022": "-",
        "\u00a0": " ",
        "\u200b": "",
        "\u2212": "-",
        "\ufeff": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", errors="replace").decode("latin-1")

class ResumePDF(FPDF):
    MARGIN = 15
    PAGE_W = 210 - 2 * 15
    ACCENT = (139, 29, 29)
    TEXT_DARK = (30, 30, 30)
    TEXT_MID = (80, 80, 80)

    def header(self):
        pass

    def footer(self):
        pass

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*self.ACCENT)
        self.cell(0, 7, sanitize(title.upper()), new_x="LMARGIN", new_y="NEXT")
        y = self.get_y()
        self.set_draw_color(*self.ACCENT)
        self.set_line_width(0.6)
        self.line(self.l_margin, y, self.l_margin + self.PAGE_W, y)
        self.ln(3)

    def add_text(self, text: str, style: str = "", size: int = 9, color=None):
        self.set_font("Helvetica", style, size)
        self.set_text_color(*(color or self.TEXT_DARK))
        self.multi_cell(0, 4.5, sanitize(text), new_x="LMARGIN", new_y="NEXT")

    def add_bullet(self, text: str):
        print(f"DEBUG add_bullet - X: {self.get_x()}, Y: {self.get_y()}, page width: {self.w}, l_margin: {self.l_margin}, r_margin: {self.r_margin}")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.TEXT_DARK)
        self.multi_cell(0, 4.5, sanitize(f"- {text}"), new_x="LMARGIN", new_y="NEXT")

def generate_resume_pdf(resume_data: Dict[str, Any]) -> bytes:
    pdf = ResumePDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(ResumePDF.MARGIN, 12, ResumePDF.MARGIN)

    personal = resume_data.get("personal_info", {}) or {}
    name = personal.get("name", "Resume")

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*ResumePDF.ACCENT)
    pdf.cell(0, 10, sanitize(name), align="C", new_x="LMARGIN", new_y="NEXT")

    contact_parts = []
    if personal.get("phone"):
        contact_parts.append(personal["phone"])
    if personal.get("email"):
        contact_parts.append(personal["email"])
    if personal.get("location"):
        contact_parts.append(personal["location"])
    if contact_parts:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*ResumePDF.TEXT_MID)
        pdf.cell(0, 5, sanitize("  |  ".join(contact_parts)), align="C", new_x="LMARGIN", new_y="NEXT")

    links = []
    if personal.get("portfolio"):
        links.append(personal["portfolio"])
    if personal.get("github_link"):
        links.append(personal["github_link"])
    if personal.get("linkedin_link"):
        links.append(personal["linkedin_link"])
    if links:
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(70, 70, 170)
        pdf.cell(0, 5, sanitize("  |  ".join(links)), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)

    edu_list = [e for e in resume_data.get("education", []) if e.get("is_selected", True)]
    if edu_list:
        pdf.section_title("Education")
        for edu in edu_list:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*ResumePDF.TEXT_DARK)
            degree = edu.get("degree", "")
            institute = edu.get("institute", "")
            pdf.cell(0, 5, sanitize(f"{degree} - {institute}"), new_x="LMARGIN", new_y="NEXT")
            detail_parts = []
            if edu.get("year"):
                detail_parts.append(f"Year: {edu['year']}")
            if edu.get("cgpa_percentage"):
                detail_parts.append(f"CGPA/Score: {edu['cgpa_percentage']}")
            if edu.get("board_university"):
                detail_parts.append(f"Board: {edu['board_university']}")
            if detail_parts:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(*ResumePDF.TEXT_MID)
                pdf.cell(0, 4.5, sanitize("  |  ".join(detail_parts)), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

    exp_list = [e for e in resume_data.get("experiences", []) if e.get("is_selected", True)]
    if exp_list:
        pdf.section_title("Experience")
        for exp in exp_list:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*ResumePDF.TEXT_DARK)
            role = exp.get("role", "")
            company = exp.get("company", "")
            print(f"DEBUG EXP - Before Title - X: {pdf.get_x()}, Y: {pdf.get_y()}")
            pdf.cell(0, 5, sanitize(f"{role} - {company}"), new_x="LMARGIN", new_y="NEXT")
            print(f"DEBUG EXP - After Title - X: {pdf.get_x()}, Y: {pdf.get_y()}")
            meta = []
            if exp.get("location"):
                meta.append(exp["location"])
            if exp.get("dates"):
                meta.append(exp["dates"])
            if meta:
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(*ResumePDF.TEXT_MID)
                print(f"DEBUG EXP - Before Meta - X: {pdf.get_x()}, Y: {pdf.get_y()}")
                pdf.cell(0, 4.5, sanitize("  |  ".join(meta)), new_x="LMARGIN", new_y="NEXT")
                print(f"DEBUG EXP - After Meta - X: {pdf.get_x()}, Y: {pdf.get_y()}")
            if exp.get("technologies"):
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(100, 100, 100)
                print(f"DEBUG EXP - Before Tech - X: {pdf.get_x()}, Y: {pdf.get_y()}")
                pdf.cell(0, 4, sanitize(f"Technologies: {', '.join(exp['technologies'])}"), new_x="LMARGIN", new_y="NEXT")
                print(f"DEBUG EXP - After Tech - X: {pdf.get_x()}, Y: {pdf.get_y()}")
            for bullet in exp.get("bullets", []):
                pdf.add_bullet(bullet)
            pdf.ln(2)

    proj_list = [p for p in resume_data.get("projects", []) if p.get("is_selected", True)]
    if proj_list:
        pdf.section_title("Projects")
        for proj in proj_list:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*ResumePDF.TEXT_DARK)
            title = proj.get("title", "")
            dur = proj.get("duration", "")
            header = title
            if dur:
                header += f"  ({dur})"
            pdf.cell(0, 5, sanitize(header), new_x="LMARGIN", new_y="NEXT")
            if proj.get("tech_stack"):
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 4, sanitize(f"Tech: {', '.join(proj['tech_stack'])}"), new_x="LMARGIN", new_y="NEXT")
            for bullet in proj.get("bullets", []):
                pdf.add_bullet(bullet)
            pdf.ln(2)

    skills_list = [s for s in resume_data.get("skills", []) if s.get("is_selected", True)]
    if skills_list:
        pdf.section_title("Technical Skills")
        for skill in skills_list:
            cat = skill.get("category", "")
            items = ", ".join(skill.get("items", []))
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*ResumePDF.TEXT_DARK)
            pdf.cell(40, 4.5, sanitize(f"{cat}: "), new_x="END")
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(0, 4.5, sanitize(items), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    cert_list = [c for c in resume_data.get("certifications", []) if c.get("is_selected", True)]
    if cert_list:
        pdf.section_title("Certifications")
        for cert in cert_list:
            cert_name = cert.get("name", "")
            issuer = cert.get("issuer", "")
            date = cert.get("date", "")
            line = f"{cert_name} - {issuer}"
            if date:
                line += f" ({date})"
            pdf.add_bullet(line)
        pdf.ln(2)

    ach_list = [a for a in resume_data.get("achievements", []) if a.get("is_selected", True)]
    if ach_list:
        pdf.section_title("Achievements & Leadership")
        for ach in ach_list:
            cat = ach.get("category", "")
            desc = ach.get("description", "")
            if cat:
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(*ResumePDF.TEXT_DARK)
                pdf.cell(0, 4.5, sanitize(cat), new_x="LMARGIN", new_y="NEXT")
            if desc:
                pdf.add_text(desc, size=9, color=ResumePDF.TEXT_MID)
            pdf.ln(1)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
