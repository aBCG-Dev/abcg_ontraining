# Adult BCG Vaccine Effectiveness Study &mdash; Training & Simulation Portal (`abcg_ontraining`)

A secure, offline-first clinical data capture, eligibility screening, and operational surveillance system designed for field investigators, project nurses, and nodal officers conducting the **Adult BCG Vaccine Effectiveness Study (aBCG)**.

For complete setup guides, role descriptions, architectural diagrams, and clinical protocols, refer to the [Root README](../README.md).

### Quick Commands
```bash
# Apply database migrations
python manage.py migrate

# Run development server
python manage.py runserver 3000

# Execute automated test suite (52 tests)
python manage.py test
```

### Preconfigured Training Accounts
- **Project Nurse**: `staff` / `staff123`
- **Nodal Officer**: `nodal` / `staff123`
- **Doctor**: `doctor_user` / `staff123`
- **Super Administrator**: `admin` / `admin123`

