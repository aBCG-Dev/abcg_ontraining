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
        os.environ.pop("CLOUDINARY_URL", None)
else:
    c_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
    c_key = os.environ.get("CLOUDINARY_API_KEY")
    c_secret = os.environ.get("CLOUDINARY_API_SECRET")
    if c_name and c_key and c_secret:
        os.environ["CLOUDINARY_URL"] = f"cloudinary://{c_key}:{c_secret}@{c_name}"

# Resolve paths
root_dir = Path(__file__).resolve().parent.parent
project_dir = root_dir / "abcg_project"
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

# Switch working directory to abcg_project
try:
    os.chdir(project_dir)
except Exception:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
