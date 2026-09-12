# Adult BCG Vaccine Effectiveness Study &mdash; Training & Simulation Portal (`abcg_ontraining`)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.x](https://img.shields.io/badge/django-5.x-green.svg)](https://www.djangoproject.com/)
[![Tests Passing](https://img.shields.io/badge/tests-52%20passed-brightgreen.svg)]()
[![Status](https://img.shields.io/badge/build-training--ready-success.svg)]()

A secure, offline-first clinical data capture, eligibility screening, and operational surveillance system designed for field investigators, project nurses, and nodal officers conducting the **Adult BCG Vaccine Effectiveness Study (aBCG)**.

This repository (`abcg_ontraining`) serves as the dedicated training and simulation environment, enabling field staff to practice clinical intake workflows, multi-step symptom screening, laboratory and radiological diagnostic tracking, Nikshay registry reconciliation, and real-time monitoring.

---

## Table of Contents
- [Key Features & Capabilities](#key-features--capabilities)
- [8-Step Clinical Registration Wizard](#8-step-clinical-registration-wizard)
- [Operational Dashboards & Surveillance](#operational-dashboards--surveillance)
- [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
- [System Architecture & Directory Structure](#system-architecture--directory-structure)
- [Installation & Quick Start](#installation--quick-start)
- [Preconfigured Training Accounts](#preconfigured-training-accounts)
- [Running Automated Tests](#running-automated-tests)
- [License & Study Attribution](#license--study-attribution)

---

## Key Features & Capabilities

- **Offline-First Resilience**: Local caching and responsive state preservation ensure uninterrupted clinical data entry even during intermittent mobile network availability.
- **Intelligent Clinical Gates**: Automated verification of TB symptoms and High-Risk Groups (HRGs) with immediate classification into Case, Control, TPT+BCG, or Ineligible categories.
- **Dynamic Geographic Hierarchy**: Real-time cascading filters across States, Districts, and Tuberculosis Units (TBUs) with automatic campaign period locks.
- **Integrated Camera & Diagnostics**: Capture Chest X-Ray images, BCG scars, and vaccination certificates directly using tablet/phone camera feeds or file upload.
- **Nikshay Reconciliation**: Side-by-side comparative reconciliation engine aligning field records with official Nikshay surveillance entries.
- **Real-Time Analytics & Telemetry**: Dynamic KPI aggregation, diagnostic confirmation splits, fleet telemetry tracking, and exportable datasets.

---

## 8-Step Clinical Registration Wizard

The core registration flow (`/registration/`) guides field nurses through an 8-stage clinical intake protocol with real-time validation:

```
[1. Participant Info] ➔ [2. Socio-Demographics] ➔ [3. Vitals & Nutritional] ➔ [4. Risk Screening]
        ➔ [5. TPT Eligibility] ➔ [6. Symptoms Checklist] ➔ [7. Diagnosis] ➔ [8. BCG Verification]
```

1. **Step 1: Participant Information**: Full legal name, gender, date of birth, automatic age calculation, primary and secondary contact numbers, residence details, and assigned TB Unit.
2. **Step 2: Socio-Demographic Details**: Marital status, socioeconomic classification (APL/BPL), demographic area type, and occupation classification.
3. **Step 3: Vitals & Nutritional Status**: Standing height (cm) and weight (kg) with real-time Body Mass Index (BMI) computation and clinical nutritional assessment.
4. **Step 4: Risk Factor Screening**: Identifies 6 core High-Risk Groups (HRGs) defined by the protocol:
   - Malnutrition (BMI < 18.5 kg/m²)
   - Elderly (Age &ge; 60 years)
   - Contact of known active TB patients
   - Diabetes mellitus
   - Past history of tuberculosis
   - Tobacco smoking / consumption
   - *Clinical Decision Gate*: Triggers automated evaluation and alerts before proceeding to clinical evaluation.
5. **Step 5: TPT (Tuberculosis Preventive Treatment) Eligibility**: Assesses past preventive therapy regimens, start/end dates, and duration.
6. **Step 6: Symptoms Screening (PTB & EPTB)**:
   - *Pulmonary TB Checklist*: Cough (&ge; 2 weeks), fever, hemoptysis, night sweats, unexplained weight loss, or asymptomatic.
   - *Extra-Pulmonary TB (EPTB) Module*: Site-specific screening across 11 anatomical locations (Lymph node, Pleura, CNS/Meninges, Abdomen, Bone & Joint, Genitourinary, Pericardial, Cutaneous, Ocular, etc.).
7. **Step 7: Diagnosis (CXR, PTB, EPTB)**:
   - *Chest X-Ray (CXR)*: CXR taken status (Yes/No), date, facility, radiological findings (Normal, Suggestive of TB, Abnormal Non-TB), live camera capture, and image upload.
   - *Pulmonary TB (PTB) Investigations*: Sputum microscopy (ZN/Fluorescent), NAAT / Truenat / CBNAAT, Culture, DST results, and sample tracking.
   - *Extra-Pulmonary TB (EPTB) Investigations*: Site-specific biopsy, cytology, fluid analysis, and histopathology.
   - *Training Flexibility*: Visible-only constraint validation prevents blocking trainees on optional laboratory serials while collecting all available data.
8. **Step 8: BCG Vaccine Verification**:
   - Campaign period verification locked to the assigned jurisdiction.
   - Scar inspection with live photo capture and record upload.
   - Flexible verification designed for both training simulations and live field intake.

---

## Operational Dashboards & Surveillance

Accessible to Nodal Officers, Investigators, and Administrators via `/dashboard/`:

- **Real-Time Analytics (`/dashboard/analytics/`)**: Real-time screening counts, TB case positivity rates, microbial vs. clinical diagnosis proportions, and geographic site volume comparisons.
- **Data Quality Studio (`/dashboard/data-quality/`)**: Automated surveillance engine flagging protocol violations, unreconciled Nikshay links, physiological BMI outliers, and pending diagnostic tests.
- **Study Site Monitoring (`/dashboard/study-site/`)**: Geographic location hierarchy management and dynamic clinical tablet fleet monitoring.
- **Sync & Telemetry Center (`/dashboard/telemetry/`)**: Real-time 24-hour transmission throughput, background sync pipelines, and operational audit streams.
- **Data Export (`/dashboard/data-export/`)**: Streamlined export interface offering multi-sheet Excel Analytics workbooks and raw CSV matrices.
- **BCG Campaign Date Settings (`/dashboard/settings/`)**: Dynamic cascading location filters (State &rarr; District &rarr; TB Unit) with real-time campaign period configuration.

---

## Role-Based Access Control (RBAC)

The system enforces modular access permissions managed under `/rbac/`:

| Role | Permissions & Scope |
| :--- | :--- |
| **Project Nurse** | Participant intake, 8-step screening, CXR/sample recording, search, and local draft synchronization. |
| **Doctor** | Clinical queue review, diagnostic adjudication, classification confirmation, and referral management. |
| **Nodal Officer** | Study site performance monitoring, data quality review, Nikshay reconciliation, and district reporting. |
| **Super Administrator** | Full system control, RBAC permission matrix configuration, campaign period locks, and audit trails. |

---

## System Architecture & Directory Structure

```
abcg_project-training/
├── manage.py                     # Root environment launcher & runner
├── requirements.txt              # Production and development dependencies
├── .gitignore                    # Git exclusions (virtualenvs, pycache, temporary files)
├── README.md                     # Repository documentation
└── abcg_project/                 # Primary Django application core
    ├── manage.py                 # Core application manage script
    ├── config/                   # Django settings, WSGI, ASGI, and root URL routing
    │   ├── settings.py           # Application settings, installed apps, and auth config
    │   ├── urls.py               # Root URL configuration
    │   └── wsgi.py               # WSGI server entry point
    ├── questions/                # Clinical intake, screening logic, and dashboard views
    │   ├── models.py             # Participant, UserProfile, AuditLog, and EPTB models
    │   ├── views.py              # Clinical workflow, registration, and dashboard controllers
    │   ├── urls.py               # Application endpoints and routing
    │   ├── rbac_config.py        # Centralized RBAC definition and permissions matrix
    │   ├── templates/            # HTML5 responsive templates (Bootstrap 5 + Custom CSS)
    │   │   ├── dashboard/        # Analytics, study site, settings, and telemetry templates
    │   │   ├── questions/        # Registration wizard, participant detail, and search
    │   │   └── rbac/             # User, role, and group management interfaces
    │   └── tests.py              # Comprehensive automated unit and integration tests
    ├── eptb/                     # Dedicated Extra-Pulmonary Tuberculosis subsystem
    ├── central_backend/          # Simulated central synchronization API backend
    └── db.sqlite3                # Pre-seeded training database
```

---

## Installation & Quick Start

### Prerequisites
- **Python**: Version 3.10, 3.11, or 3.12
- **Git**: Installed and configured
- **Web Browser**: Modern browser (Chrome, Edge, Firefox, Safari)

### 1. Clone the Repository
```bash
git clone https://github.com/aBCG-Dev/abcg_ontraining.git
cd abcg_ontraining
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Launch the Development Server
```bash
# Default port 8000
python manage.py runserver

# Or specify a custom port (e.g., 3000)
python manage.py runserver 3000
```
Open your browser and navigate to: `http://127.0.0.1:3000/` (or `http://127.0.0.1:8000/`).

---

## Preconfigured Training Accounts

The pre-seeded training database includes ready-to-use user accounts representing each operational role:

| Username | Password | Role | Assigned Site |
| :--- | :--- | :--- | :--- |
| `staff` | `staff123` | **Project Nurse** | Dharwad TU, Karnataka |
| `nodal` | `staff123` | **Nodal Officer** | Dharwad District, Karnataka |
| `doctor_user` | `staff123` | **Doctor** | District Hospital |
| `admin` | `admin123` | **Super Admin** | State Operations Center |

---

## Running Automated Tests

The application includes a comprehensive test suite covering clinical classification rules, validation constraints, RBAC permissions, and API endpoints:

```bash
# Run all tests
python manage.py test

# Run tests with detailed output
python manage.py test -v 2
```

**Test Coverage Summary**:
- **52 Passing Tests (100% OK)**
- Tests clinical eligibility gates (Symptomatic, High-Risk Group matching, TPT criteria)
- Validates offline synchronization and Nikshay reconciliation routines
- Verifies Role-Based Access Control route guards and permission checks

---

## License & Study Attribution

This software is developed and maintained for the **Adult BCG Vaccine Effectiveness Study (aBCG)** research initiative. All clinical protocols, questionnaire instruments, and diagnostic algorithms conform to study steering committee specifications.
