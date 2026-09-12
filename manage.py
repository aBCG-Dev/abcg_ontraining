#!/usr/bin/env python
import os
import sys
from pathlib import Path

def main():
    # Ensure abcg_project directory is on sys.path
    project_dir = Path(__file__).resolve().parent / "abcg_project"
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))
    
    # Change working directory to abcg_project so relative paths resolve cleanly
    os.chdir(project_dir)
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Is it installed and available on your PYTHONPATH?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
