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

# Automatically apply database migrations and ensure columns/locations on remote database (Neon / PostgreSQL)
try:
    from django.db import connection
    if connection.vendor == "postgresql":
        with connection.cursor() as cursor:
            cursor.execute('ALTER TABLE "questions_ineligibleindividual" ADD COLUMN IF NOT EXISTS "consent" varchar(10) NULL;')
            cursor.execute('ALTER TABLE "questions_participant" ADD COLUMN IF NOT EXISTS "consent" varchar(10) NULL;')
            cursor.execute('ALTER TABLE "questions_tptindividual" ADD COLUMN IF NOT EXISTS "consent" varchar(10) NULL;')

            # Auto-heal any legacy records corrupted with generic locations
            for tbl in ["questions_participant", "questions_tptindividual", "questions_ineligibleindividual"]:
                cursor.execute(f"""
                    UPDATE {tbl} SET state = 'Andhra Pradesh', district = 'Sri Potti Sriramulu Nellore', tb_unit = 'NELLORE-1'
                    WHERE (study_id LIKE 'ABCG-AN-NEL-%' OR facility = 'ACSR Medical college')
                      AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));
                """)
                cursor.execute(f"""
                    UPDATE {tbl} SET state = 'Andhra Pradesh', district = 'Guntur', tb_unit = 'Guntur DTC'
                    WHERE (study_id LIKE 'ABCG-AN-GUN-%' OR facility = 'Guntur DTC')
                      AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));
                """)
                cursor.execute(f"""
                    UPDATE {tbl} SET state = 'Odisha', district = 'Mayurbhanj', tb_unit = 'Baripada_DTC'
                    WHERE (study_id LIKE 'ABCG-OD-BAR-%' OR facility ILIKE '%Mayurbhanj%')
                      AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));
                """)
                cursor.execute(f"""
                    UPDATE {tbl} SET state = 'Odisha', district = 'Cuttack', tb_unit = 'Urban_TU'
                    WHERE (study_id LIKE 'ABCG-OD-URB-%' OR facility ILIKE '%SCB%')
                      AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));
                """)
                cursor.execute(f"""
                    UPDATE {tbl} SET state = 'Tamil Nadu', district = 'Tiruvallur', tb_unit = 'Tiruvallur TU'
                    WHERE (study_id LIKE 'ABCG-TN-TIR-%' OR facility ILIKE '%Avadi%' OR facility ILIKE '%Tiruvallur%')
                      AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));
                """)
                cursor.execute(f"""
                    UPDATE {tbl} SET state = 'Karnataka', district = 'Bengaluru', tb_unit = 'Bengaluru TU'
                    WHERE (study_id LIKE 'ABCG-KA-BEN-%' OR facility ILIKE '%Bengaluru%')
                      AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));
                """)

    from django.core.management import call_command
    call_command("migrate", interactive=False, verbosity=0)
except Exception as _e:
    pass


