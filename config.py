import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

WORKSPACE_DIR = Path(__file__).parent.resolve()
DB_PATH = WORKSPACE_DIR / "cvilization.db"
EXPORTS_DIR = WORKSPACE_DIR / "exports"
TEMP_DIR = WORKSPACE_DIR / "temp_build"
STYLES_DIR = WORKSPACE_DIR / "styles"

EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)
STYLES_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = "cvilization"
DEBUG = True

MARKDOWN_TEMPLATE_NAME = "resume_template.md"
PDF_LOG_FILE = TEMP_DIR / "latex_compile.log"
