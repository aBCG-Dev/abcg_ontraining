import os
import sys
from pathlib import Path

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
