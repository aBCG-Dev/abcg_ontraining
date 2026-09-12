# 📐 Central Backend Design Blueprint (Stakeholder-Resilient Architecture)

In clinical research studies, stakeholders frequently request changes to questionnaires, age thresholds, eligibility criteria, and risk factors. Making direct database schema migrations and code updates for every stakeholder request leads to brittle code, potential data loss, and slow turnaround times.

This blueprint details how the central backend is designed to be **resilient to frequent changes** by utilizing dynamic metadata schemas, JSON storage fields, and a decoupled Rules Engine.

---

## 🛠️ Key Design Principles for Frequent Changes

### 1. Dynamic Metadata Models (Zero-Code Question Changes)
Instead of adding a new database column every time a stakeholder adds a survey question, we use a catalog table model.
* We define `Question` and `Option` tables.
* A participant's questionnaire answers are saved as a single JSON map (`questionnaire_answers`) in the database.
* **To add/edit/remove a question:** You simply log into the Django Admin panel and create a new `Question` record. The field app and central server load these dynamically. No database migrations are required!

### 2. Decoupled Rules Engine (Zero-Code Eligibility Changes)
Instead of embedding eligibility logic directly inside the API view endpoints, all eligibility gates are separated into a dedicated `RulesEngine` class.
* Thresholds (such as the BMI threshold of `< 18` or age cutoff of `>= 60`) are stored in a database-backed `GlobalSettings` model.
* **To change eligibility cutoffs:** You change the values in the `GlobalSettings` table via Django Admin. The Rules Engine dynamically fetches these parameters. No code changes are required!

### 3. Decoupled API Serialization (Django REST Framework)
We utilize **Django REST Framework (DRF)**. Serializers handle all inbound payload validation automatically.
* Using DRF ensures that payload schema mismatches return clear validation errors (`HTTP 400 Bad Request`) to the client, preventing dirty or incomplete data from corrupting the central database.

---

## 📂 central_backend/ Directory Layout

We will create a boilerplate Django project structured as follows:

```text
central_backend/
│
├── central_project/                # Core Django project settings
│   ├── settings.py                 # DB connections, CORS settings, local media folders
│   ├── urls.py                     # Main router routing /api/v1/ to api app
│   └── wsgi.py                     # WSGI deployment entry point
│
├── api/                            # Central sync API application
│   ├── models.py                   # Configurable settings, Participant, and Telemetry models
│   ├── serializers.py              # Inbound bulk records serializers
│   ├── views.py                    # Auth, Sync, and Media endpoints
│   ├── urls.py                     # API route endpoints
│   ├── admin.py                    # Full Django Admin interface (with CSV export capability)
│   └── eligibility.py              # The decoupled Rules Engine
│
└── manage.py                       # CLI manage script
```

---

## 🛠️ Step-by-Step Backend Codebase Implementation

The next steps will create the actual central backend directory and files in your workspace so you can run it immediately on your organization's server!
