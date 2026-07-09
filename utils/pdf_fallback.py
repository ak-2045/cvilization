def generate_fallback_pdf(resume_data: dict) -> bytes:
    """
    Generates a standard Helvetica PDF from the resume data.
    This runs completely in pure Python without needing pdflatex or any third-party libraries.
    """
    # Extract info
    personal = resume_data.get("personal_info", {}) or {}
    name = personal.get("name", "Resume")
    email = personal.get("email", "")
    phone = personal.get("phone", "")
    website = personal.get("website", "")
    location = personal.get("location", "")
    summary = personal.get("summary", "")
    
    education = resume_data.get("education", []) or []
    experience = resume_data.get("experience", []) or []
    projects = resume_data.get("projects", []) or []
    skills = resume_data.get("skills", []) or []
    
    # Build stream commands
    stream_cmds = []
    stream_cmds.append("BT")
    
    def escape_pdf_text(text: str) -> str:
        if not text:
            return ""
        # Escape backslashes and parentheses which are special characters in PDF string syntax
        return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    
    # Write Name (Bold, large)
    stream_cmds.append("/F2 20 Tf")
    stream_cmds.append("54 730 Td")
    stream_cmds.append(f"({escape_pdf_text(name)}) Tj")
    
    # Contact Info
    stream_cmds.append("/F1 9 Tf")
    contact_parts = []
    if email: contact_parts.append(email)
    if phone: contact_parts.append(phone)
    if location: contact_parts.append(location)
    if website: contact_parts.append(website)
    contact_str = "  |  ".join(contact_parts)
    stream_cmds.append("0 -18 Td")
    stream_cmds.append(f"({escape_pdf_text(contact_str)}) Tj")
    
    # Divider line
    stream_cmds.append("0 -12 Td")
    stream_cmds.append("() Tj")
    
    # Track vertical offset (page height is 792, margins are 54pt top/bottom)
    # We started at 730 and moved down by 18, then 12. Current y is 700.
    
    # Summary
    if summary:
        stream_cmds.append("/F2 11 Tf")
        stream_cmds.append("0 -15 Td")
        stream_cmds.append("(PROFESSIONAL SUMMARY) Tj")
        stream_cmds.append("/F1 9 Tf")
        
        # Word wrapping helper
        words = summary.split()
        line = []
        for word in words:
            if len(" ".join(line + [word])) > 90:
                stream_cmds.append("0 -11 Td")
                stream_cmds.append(f"({escape_pdf_text(' '.join(line))}) Tj")
                line = [word]
            else:
                line.append(word)
        if line:
            stream_cmds.append("0 -11 Td")
            stream_cmds.append(f"({escape_pdf_text(' '.join(line))}) Tj")
            
    # Experience
    if experience:
        stream_cmds.append("0 -10 Td")
        stream_cmds.append("() Tj")
        stream_cmds.append("/F2 11 Tf")
        stream_cmds.append("0 -14 Td")
        stream_cmds.append("(WORK EXPERIENCE) Tj")
        
        for exp in experience:
            # Skip if experience is toggled off (active=0 or similar)
            if not exp.get("is_active", 1) and str(exp.get("is_active")) == "0":
                continue
            role = exp.get("role", "")
            company = exp.get("company", "")
            duration = exp.get("duration", "")
            desc = exp.get("description", "")
            
            stream_cmds.append("/F2 9.5 Tf")
            stream_cmds.append("0 -14 Td")
            stream_cmds.append(f"({escape_pdf_text(role)} - {escape_pdf_text(company)} \\({escape_pdf_text(duration)}\\)) Tj")
            
            if desc:
                stream_cmds.append("/F1 9 Tf")
                for bullet in desc.split("\n"):
                    bullet = bullet.strip().lstrip("- ")
                    if not bullet: continue
                    words = bullet.split()
                    line = ["-"]
                    for word in words:
                        if len(" ".join(line + [word])) > 90:
                            stream_cmds.append("0 -11 Td")
                            stream_cmds.append(f"({escape_pdf_text(' '.join(line))}) Tj")
                            line = ["  " + word]
                        else:
                            line.append(word)
                    if line:
                        stream_cmds.append("0 -11 Td")
                        stream_cmds.append(f"({escape_pdf_text(' '.join(line))}) Tj")
                        
    # Education
    if education:
        stream_cmds.append("0 -10 Td")
        stream_cmds.append("() Tj")
        stream_cmds.append("/F2 11 Tf")
        stream_cmds.append("0 -14 Td")
        stream_cmds.append("(EDUCATION) Tj")
        
        for edu in education:
            if not edu.get("is_active", 1) and str(edu.get("is_active")) == "0":
                continue
            deg = edu.get("degree", "")
            school = edu.get("school", "")
            year = edu.get("year", "")
            stream_cmds.append("/F1 9 Tf")
            stream_cmds.append("0 -12 Td")
            stream_cmds.append(f"({escape_pdf_text(deg)} - {escape_pdf_text(school)} \\({escape_pdf_text(year)}\\)) Tj")
            
    # Projects
    if projects:
        stream_cmds.append("0 -10 Td")
        stream_cmds.append("() Tj")
        stream_cmds.append("/F2 11 Tf")
        stream_cmds.append("0 -14 Td")
        stream_cmds.append("(PROJECTS) Tj")
        
        for proj in projects:
            if not proj.get("is_active", 1) and str(proj.get("is_active")) == "0":
                continue
            title = proj.get("title", "")
            tech = proj.get("technologies", "")
            desc = proj.get("description", "")
            stream_cmds.append("/F2 9.5 Tf")
            stream_cmds.append("0 -12 Td")
            proj_header = title
            if tech: proj_header += f" [{tech}]"
            stream_cmds.append(f"({escape_pdf_text(proj_header)}) Tj")
            
            if desc:
                stream_cmds.append("/F1 9 Tf")
                for bullet in desc.split("\n"):
                    bullet = bullet.strip().lstrip("- ")
                    if not bullet: continue
                    words = bullet.split()
                    line = ["-"]
                    for word in words:
                        if len(" ".join(line + [word])) > 90:
                            stream_cmds.append("0 -11 Td")
                            stream_cmds.append(f"({escape_pdf_text(' '.join(line))}) Tj")
                            line = ["  " + word]
                        else:
                            line.append(word)
                    if line:
                        stream_cmds.append("0 -11 Td")
                        stream_cmds.append(f"({escape_pdf_text(' '.join(line))}) Tj")
                        
    # Skills
    if skills:
        stream_cmds.append("0 -10 Td")
        stream_cmds.append("() Tj")
        stream_cmds.append("/F2 11 Tf")
        stream_cmds.append("0 -14 Td")
        stream_cmds.append("(SKILLS) Tj")
        
        skills_list = []
        for sk in skills:
            if not sk.get("is_active", 1) and str(sk.get("is_active")) == "0":
                continue
            name_sk = sk.get("name", "")
            lvl = sk.get("level", "")
            if lvl:
                skills_list.append(f"{name_sk} ({lvl})")
            else:
                skills_list.append(name_sk)
        skills_str = ", ".join(skills_list)
        stream_cmds.append("/F1 9 Tf")
        words = skills_str.split()
        line = []
        for word in words:
            if len(" ".join(line + [word])) > 90:
                stream_cmds.append("0 -11 Td")
                stream_cmds.append(f"({escape_pdf_text(' '.join(line))}) Tj")
                line = [word]
            else:
                line.append(word)
        if line:
            stream_cmds.append("0 -11 Td")
            stream_cmds.append(f"({escape_pdf_text(' '.join(line))}) Tj")
            
    stream_cmds.append("ET")
    
    # Convert stream commands to bytes
    stream_bytes = "\n".join(stream_cmds).encode("utf-8")
    
    # Build PDF Objects
    objects = []
    # Obj 1: Catalog
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    # Obj 2: Pages list
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    # Obj 3: Page resource definitions
    objects.append(b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /MediaBox [0 0 612 792] /Contents 6 0 R >>")
    # Obj 4: Font F1 (Helvetica)
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    # Obj 5: Font F2 (Helvetica-Bold)
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    # Obj 6: Stream container object
    obj6_content = f"<< /Length {len(stream_bytes)} >>\nstream\n".encode("utf-8") + stream_bytes + b"\nendstream"
    objects.append(obj6_content)
    
    # Construct total byte buffer and calculate byte offsets for xref
    offsets = []
    current_offset = 9 # length of b"%PDF-1.4\n"
    
    output = [b"%PDF-1.4\n"]
    for i, obj in enumerate(objects):
        obj_id = i + 1
        obj_bytes = f"{obj_id} 0 obj\n".encode("utf-8") + obj + b"\nendobj\n"
        offsets.append(current_offset)
        current_offset += len(obj_bytes)
        output.append(obj_bytes)
        
    xref_pos = current_offset
    output.append(b"xref\n")
    output.append(f"0 {len(objects) + 1}\n".encode("utf-8"))
    output.append(b"0000000000 65535 f \n")
    for offset in offsets:
        output.append(f"{offset:010d} 00000 n \n".encode("utf-8"))
        
    output.append(b"trailer\n")
    output.append(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("utf-8"))
    output.append(b"startxref\n")
    output.append(f"{xref_pos}\n".encode("utf-8"))
    output.append(b"%%EOF\n")
    
    return b"".join(output)
