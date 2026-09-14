#!/bin/bash
set -e

echo "===> Installing build dependencies on Vercel..."
if command -v uv &> /dev/null; then
    echo "Found uv: installing dependencies into system Python..."
    uv pip install --system -r requirements.txt || python3 -m pip install -r requirements.txt --break-system-packages || pip install -r requirements.txt --break-system-packages
elif command -v python3 &> /dev/null; then
    echo "Found python3: installing with --break-system-packages..."
    python3 -m pip install -r requirements.txt --break-system-packages || pip install -r requirements.txt --break-system-packages
else
    echo "Using default pip..."
    pip install -r requirements.txt --break-system-packages
fi

echo "===> Collecting static assets..."
if command -v python3 &> /dev/null; then
    python3 manage.py collectstatic --noinput --clear
else
    python manage.py collectstatic --noinput --clear
fi

echo "===> Structuring static files for Vercel CDN..."
mkdir -p staticfiles_build/static
cp -r abcg_project/staticfiles/* staticfiles_build/static/ 2>/dev/null || true

DB_CONN="${DATABASE_URL:-$POSTGRES_URL}"
if [ -n "$DB_CONN" ]; then
    echo "===> Remote database detected: applying database migrations..."
    python3 manage.py migrate --noinput || python manage.py migrate --noinput || true
    echo "===> Initializing groups, permissions, and accounts..."
    python3 manage.py setup_rbac_groups || python manage.py setup_rbac_groups || true
    python3 manage.py load_rbac_permissions || python manage.py load_rbac_permissions || true
    python3 manage.py setup_default_accounts || python manage.py setup_default_accounts || true
fi

echo "===> Static files build completed successfully!"
