#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Sanitize CLOUDINARY_URL before Django or third-party packages load
raw_c_url = os.environ.get("CLOUDINARY_URL", "")
if raw_c_url:
    clean_c = raw_c_url.strip().strip("\"' ")
    if "cloudinary://" in clean_c:
        clean_c = "cloudinary://" + clean_c.split("cloudinary://", 1)[1].strip("\"' ")
    if clean_c.startswith("cloudinary://"):
        os.environ["CLOUDINARY_URL"] = clean_c
    else:
        # Invalid scheme: remove from os.environ to prevent fatal startup crash in cloudinary package
        os.environ.pop("CLOUDINARY_URL", None)
else:
    c_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
    c_key = os.environ.get("CLOUDINARY_API_KEY")
    c_secret = os.environ.get("CLOUDINARY_API_SECRET")
    if c_name and c_key and c_secret:
        os.environ["CLOUDINARY_URL"] = f"cloudinary://{c_key}:{c_secret}@{c_name}"

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
