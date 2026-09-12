# 📘 aBCG Study Investigator App - Codebase Navigation Guide

Welcome to the Developer Navigation Guide! This document is designed to help you quickly understand the layout of the project, what each file does, and where you need to go when you want to make specific changes.

---

## 📂 Project Directory Structure

Here is an overview of the workspace structure:

```text
abcg_project/                       # Workspace root directory
│
├── config/                         # Core Django project configuration
│   ├── settings.py                 # Project configurations (Apps, DB, middleware, static files)
│   ├── urls.py                     # Root URL router
│   └── wsgi.py                     # WSGI entrypoint for web server
│
├── questions/                      # Main study registration & dashboard app
│   ├── management/                 # Custom management CLI commands (e.g. data import tools)
│   ├── migrations/                 # DB migrations tracking model history
│   ├── static/questions/           # Static asset folders
│   │   ├── css/app.css             # Main stylesheet for dashboard & widgets
│   │   └── js/app.js               # Global Javascript triggers
│   ├── templates/                  # UI templates (HTML files)
│   │   ├── includes/               # Reusable UI fragments (navbar.html, footer.html)
│   │   ├── layouts/                # Base layouts (base.html template wrapper)
│   │   └── questions/              # Feature-specific templates (home, registration, search, etc.)
│   ├── admin.py                    # Django Admin registry for questions
│   ├── apps.py                     # App configuration metadata
│   ├── models.py                   # Main database model architectures (Participant, UserProfile, etc.)
│   ├── tests.py                    # Complete test suite for models, gates, and views
│   ├── urls.py                     # URL routes specifically mapped to questions app views
│   └── views.py                    # Core views & classification logic controllers
│
├── eptb/                           # Extra-Pulmonary Tuberculosis (EPTB) screening app
│   ├── migrations/                 # Database migrations for EPTB models
│   ├── templates/eptb/             # EPTB-specific templates (questions.html)
│   ├── admin.py                    # Admin registry for EPTB sites & sub-questions
│   ├── apps.py                     # App configuration metadata
│   ├── constants.py                # Defines raw list of EPTB categories
│   ├── forms.py                    # Django Form declaration for EPTB questions
│   ├── models.py                   # EPTB site and sub-question models
│   ├── tests.py                    # Basic tests for EPTB
│   ├── urls.py                     # Route mapping for eptb app
│   └── views.py                    # Simple controller rendering the form
│
├── bcg_records/                    # Media folder: User-uploaded BCG card images
├── bcg_scar_records/               # Media folder: User-uploaded BCG scar images
├── cxr_records/                    # Media folder: User-uploaded Chest X-Ray files
│
├── central_backend/                # Central sync backend server codebase
│   ├── central_project/            # Main Django configuration files
│   ├── api/                        # DRF Sync API application code
│   │   ├── eligibility.py          # Separated Study Rules Engine
│   │   ├── serializers.py          # Inbound payload serializer schemas
│   │   ├── models.py               # Aggregated database tables
│   │   └── views.py                # Sync endpoint controllers
│   └── manage.py                   # Administrative execution script
│
├── db.sqlite3                      # Local database file (SQLite)
├── manage.py                       # Django CLI execution tool
├── requirements.txt                # Python backend dependencies list
├── package.json                    # Frontend assets settings
└── README.md                       # High-level overview of project modules & instructions
```

---

## 📄 File-by-File Breakdown

### 1. Configuration (`config/`)
* [settings.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/config/settings.py): Contains all Django configurations. Update this to register new apps under `INSTALLED_APPS`, configure DB settings, adjust time zones (`TIME_ZONE = 'Asia/Kolkata'`), or edit security configurations.
* [urls.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/config/urls.py): Root URL dispatcher that points root path (`/`) requests to `questions.urls` and `/eptb/` to `eptb.urls`.

### 2. Main Clinical App (`questions/`)
* [models.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/models.py): Defines the database schema for the study:
  * `UserProfile`: Investigator profiles mapped to specific geographical jurisdictions (State, District, TB Unit).
  * `Participant`: The primary model storing clinical features, demographics, symptoms, and eligibility classifications.
  * `TptIndividual`: Tracks exploratory cohort participants who undergo TPT + BCG.
  * `IneligibleIndividual`: Tracks participants who fail eligibility gates.
  * `Symptom` and `RiskFactor`: Master catalogs for symptoms and HRGs.
  * `BcgVaccination`: Local registry list for lookup and verification.
* [views.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/views.py): The core controller logic:
  * `home()`: Loads operations dashboard stats (total cases, controls, synced) and handles inline authentication.
  * `registration()`: Evaluates the multi-step questionnaire inputs, processes eligibility checks via the Gate parameters, runs classification rules, and writes to corresponding DB tables.
  * `search()`: Handles participant lookups (exact match and text filters) and splits views for master-detail rendering.
  * `pending_sync()`: Handles data synchronization and processes silent device telemetry collection (`DeviceSyncLog`).
  * `reconcile()`: Compares local offline records side-by-side with Nikshay server registry values.

### 3. Central Sync Backend (`central_backend/`)
* [models.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/central_backend/api/models.py): Central database tables and the dynamic `GlobalSettings` configuration model.
* [views.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/central_backend/api/views.py): Auth logic, bulk data sync ingestor, and media upload controllers.
* [serializers.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/central_backend/api/serializers.py): DRF serializer schemas defining validation boundaries for sync payloads.
* [eligibility.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/central_backend/api/eligibility.py): Decoupled, on-premise study Rules Engine that matches participant criteria against dynamic DB-backed thresholds.
* [admin.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/central_backend/api/admin.py): Admin panel configurations with dynamic thresholds modification and export selected to CSV utility.

* [urls.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/urls.py): Maps URL endpoints (e.g., `/registration/`, `/search/`, `/pending-sync/`) to views.
* [tests.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/tests.py): The suite of tests verifying client redirects, campaign locks, symptom exclusivity, and joint eligibility criteria.

### 3. Extra-Pulmonary TB App (`eptb/`)
* [models.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/eptb/models.py): Defines `EptbSite` and `EptbSubQuestion` representing specific anatomical sites for EPTB.
* [forms.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/eptb/forms.py): Form definition dynamically generating yes/no radio selectors and detail textareas.
* [constants.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/eptb/constants.py): Holds static list of EPTB categories (e.g., Lymph Node, Pleural, Abdominal TB).

---

## 🗺️ Change Navigation Map (Where do I go to change...?)

If you want to perform a development task, use this cheat sheet to find the files you need to modify:

| Feature / Goal | Where to go / File to open | What to do |
| :--- | :--- | :--- |
| **Add or remove database fields** for a participant | 📝 [questions/models.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/models.py) | Edit the fields in `Participant`, `TptIndividual`, or `UserProfile`. Then run database migrations commands. |
| **Change the rules of who is "Eligible"** (e.g. modify symptom gates or high-risk rules) | 📝 [questions/views.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/views.py) | Modify the gating criteria within the POST logic of the `registration()` view function. |
| **Modify the Registration wizard layout, inputs, or tabs** | 📝 [questions/templates/questions/registration.html](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/templates/questions/registration.html) | Update the wizard steps, edit Javascript client-side validation rules, or modify step indicators. |
| **Customize CSS styling, colors, or page layouts** | 📝 [questions/static/questions/css/app.css](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/static/questions/css/app.css) | Modify CSS variables (`--brand`, `--radius`, etc.) and visual class definitions. |
| **Edit the Dashboard home page stats, counters, or actions** | 📝 [questions/views.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/views.py)<br>📝 [questions/templates/questions/home.html](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/templates/questions/home.html) | Update the queries inside `home()` view, and edit layout HTML cards in the dashboard template. |
| **Modify site navigation or the top header bar** | 📝 [questions/templates/includes/navbar.html](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/templates/includes/navbar.html) | Add menu items or change the connection status indicator UI markup. |
| **Add a new view or endpoint (e.g., custom report page)** | 📝 [questions/urls.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/urls.py)<br>📝 [questions/views.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/views.py)<br>📝 [questions/templates/questions/](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/templates/questions/) | 1. Add URL path map in `urls.py`. <br>2. Define a view function inside `views.py`. <br>3. Create a corresponding HTML template. |
| **Modify EPTB screening questions** | 📝 [eptb/constants.py](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/eptb/constants.py) | Add or edit the categories in the `EPTB_QUESTIONS` list. |
| **Run unit tests to verify changes** | 💻 Console | Run: `python manage.py test` to verify your changes haven't broken current rules. |

---

## 🎨 Frontend Architecture & Design System

The client-side interface is engineered to offer a fast, premium, and highly responsive clinical data entry experience for field investigators working on various devices (tablets, mobiles, laptops).

### 1. Style Guide & Design Tokens
All layout colors and styles are governed by CSS custom properties (variables) defined in 📝 [app.css](file:///c:/Users/BCG%20Vaccine/abcg_project/abcg_project/questions/static/questions/css/app.css):
* **Colors:**
  * `--brand` (`#0f4c81`): Deep clinical blue used for navbar, primary search indicators, and actions.
  * `--accent` (`#1b8a6b`): Emerald green used for success statuses, registration action cards, and positive verdicts.
  * `--ink` (`#172033`): High-contrast dark charcoal color for optimal reading under direct sunlight.
  * `--muted` (`#667085`): Cool grey used for section tags and clinical instructions.
  * `--surface-soft` (`#f6f8fb`): Off-white background canvas that minimizes eye fatigue.
* **Typography:** Enforces the geometric **Inter** font family (Google Fonts) with weights ranging from Regular (400) to ExtraBold (800).

### 2. Core Interactive Modules
* **Dashboard Portal:** Grid system holding responsive action cards (`.workflow-card`). Uses a custom cubic-bezier transformation to elevate cards on hover with soft drop shadows and glow effects.
* **Progressive Multi-Step Wizard (`registration.html`):** Renders a structured 8-step questionnaire. Uses client-side JS state management to handle step navigation, real-time BMI estimation, and exclusion validation (like clearing and disabling other check boxes when "Asymptomatic" is checked).
* **Master-Detail Search Panel (`search.html`):** Renders a split-pane layout. On mobile screens, JavaScript dynamically collapses the split view into a sliding drawer overlay to preserve horizontal space.
* **Client-Side Telemetry Hook (`pending_sync.html`):** Integrates Web APIs (`navigator.onLine`, Geolocation API, and Battery Status API) to monitor investigator device state before launching outbound sync requests.

---

## 🛠️ CLI Cheat Sheet

Run these command-line actions inside the terminal in the workspace root directory:

* **Start the development server:**
  ```powershell
  python manage.py runserver
  ```
* **Run automated unit tests:**
  ```powershell
  python manage.py test
  ```
* **Generate new database migrations after models change:**
  ```powershell
  python manage.py makemigrations
  ```
* **Apply database migrations to database file:**
  ```powershell
  python manage.py migrate
  ```
* **Create a new administrator user:**
  ```powershell
  python manage.py createsuperuser
  ```
