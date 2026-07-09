import os
import subprocess
import shutil
import logging
from pathlib import Path
from PIL import Image
from config import TEMP_DIR, PDF_LOG_FILE

logger = logging.getLogger("cvilization.agents.pdf_compiler")

def ensure_logo_image(target_dir: Path) -> None:
    logo_path = target_dir / "logo-29.png"
    if not logo_path.exists():
        try:
            img = Image.new("RGBA", (200, 200), (255, 255, 255, 0))
            img.save(logo_path, "PNG")
        except Exception as e:
            logger.error(f"Failed to create placeholder logo image: {e}")

def find_pdflatex_path() -> str:
    which_path = shutil.which("pdflatex")
    if which_path:
        return which_path
        
    user_home = os.path.expanduser("~")
    common_paths = [
        Path(user_home) / "AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe",
        Path("C:/Program Files/MiKTeX/miktex/bin/x64/pdflatex.exe"),
        Path("C:/Program Files (x86)/MiKTeX/miktex/bin/x64/pdflatex.exe"),
        Path("C:/texlive/2025/bin/windows/pdflatex.exe"),
        Path("C:/texlive/2026/bin/windows/pdflatex.exe"),
        Path("C:/texlive/2024/bin/windows/pdflatex.exe"),
    ]
    
    for p in common_paths:
        if p.exists():
            return str(p)
            
    return ""

def compile_pdf(latex_code: str) -> tuple[bool, bytes | str]:
    tex_path = TEMP_DIR / "resume.tex"
    pdf_path = TEMP_DIR / "resume.pdf"
    
    try:
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)
            
        ensure_logo_image(TEMP_DIR)
        compiler = find_pdflatex_path()
        if not compiler:
            msg = ("pdflatex executable not found in PATH or standard installation folders.\n"
                   "Please install MiKTeX (https://miktex.org/) or TeX Live, or download the LaTeX source (.tex) "
                   "and upload it to Overleaf.")
            return False, msg
            
        for i in range(2):
            cmd = [
                compiler,
                "-interaction=nonstopmode",
                "-halt-on-error",
                "resume.tex"
            ]
            process = subprocess.run(
                cmd,
                cwd=TEMP_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            with open(PDF_LOG_FILE, "w", encoding="utf-8") as lf:
                lf.write(process.stdout)
                lf.write(process.stderr)
                
            if process.returncode != 0:
                errors = []
                for line in process.stdout.splitlines():
                    if line.startswith("!") or "Error" in line:
                        errors.append(line)
                error_msg = "\n".join(errors[:10]) if errors else process.stdout[-2000:]
                return False, f"pdflatex compilation error:\n{error_msg}"
                
        if pdf_path.exists():
            with open(pdf_path, "rb") as pf:
                pdf_bytes = pf.read()
            return True, pdf_bytes
        else:
            return False, "PDF file was not created by the compiler."
            
    except Exception as e:
        return False, f"Exception: {str(e)}"
