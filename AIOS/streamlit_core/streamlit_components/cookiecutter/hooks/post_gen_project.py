#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import shutil
from pathlib import Path

project_dir = Path("{{ cookiecutter.import_name }}").absolute()

framework = "{{ cookiecutter.framework }}"
if framework == "React + Typescript":
    shutil.move(str(project_dir / "frontend-react"), str(project_dir / "frontend"))
    shutil.rmtree(str(project_dir / "frontend-reactless"))
elif framework == "Pure Typescript":
    shutil.move(str(project_dir / "frontend-reactless"), str(project_dir / "frontend"))
    shutil.rmtree(str(project_dir / "frontend-react"))
else:
    raise Exception(f"Unsupported option: {framework!r}")
