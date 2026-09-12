# Adult BCG Vaccine Effectiveness Study Data Collection App

A secure, offline-first clinical data collection and eligibility screening system built for field investigators conducting the **Adult BCG Vaccine Effectiveness Study**. Enforces strict clinical, geographic campaign lock, and matching rules defined by epidemiological research protocols.

---

## Key Features & Clinical Workflows

### 1. Study Operations Dashboard
- **Dynamic Connection Auditor**: Real-time status indicator showing "Online Connection Active" vs. "Offline Staging Mode" using browser network event listeners (`navigator.onLine`).
- **Dynamic Last Sync Audit**: Tracks the last upload timestamp in browser `localStorage`. Clicking "Sync All Queue" on the outbound queue updates the timestamp across the dashboard in real-time.
- **Daily Performance Metrics**: Real-time counters showing the volume of participants registered today, total cases, and total matched controls.
- **Interactive Action Cards**: Custom `.workflow-card` structures with responsive hover transformations, glow highlights, and scaling micro-animations.

### 2. Redesigned Multi-Step Registration Wizard (4 Tabs)
- **Tab 1: Site Location Parameters**: Auto-populates State, District, and Tuberculosis Unit (TU) from the active investigator's profile session.
- **Tab 2: Personal Profile**: Captures First/Last Name, DOB, Age (auto-calculated in real-time when DOB is entered), Gender, Primary/Secondary phone numbers (with pre-attached country code `+91` input groups).
- **Tab 3: Socio-demographics & Address**: Captures door address, facility, village, pincode, marital status, socioeconomic status (APL/BPL), demographic area type, and a detailed 28-choice Occupation select.
- **Tab 4: Symptoms & Risk Profile**: Captures symptoms and key population check boxes.
  - **Symptom Exclusivity**: Checking "Asymptomatic" automatically clears and disables all other symptoms; checking any specific symptom clears "Asymptomatic".
  - **Risk Exclusivity**: Checking "Not Applicable" clears all other selected risk factors.

---

## Clinical Entry Gates & Eligibility Rules

When the investigator submits the wizard form, the system evaluates the candidate's eligibility:

1. **Symptomatic Gate**: Candidate must present **at least one clinical symptom** (any checkbox other than "Asymptomatic").
2. **High-Risk Group (HRG) Gate**: Candidate must match **at least one of the 6 core vulnerable groups**:
   - Malnourished (BMI < 18.5 kg/m2 check box)
   - Elderly (Age >= 60)
   - Tobacco / Smoker
   - Contact of Known TB Patients
   - Past history of TB
   - Diabetes
3. **TU Campaign Lock**: Dynamically displays the BCG Vaccination Campaign Period based on the pre-filled Tuberculosis Unit (TU) at the top of all steps (e.g. *Jan 2025 - Mar 2025*).

### Validation Verdicts:
- **Eligible**: Clears *both* Symptom and HRG gates. The system alerts the investigator via a success modal, generates a unique Study ID (`SCR-[YYMMDD]-[RAND]`), and saves the candidate in the database under `classification = "Pending"`.
- **Ineligible**: Fails either gate. The system warns the investigator via a blocker modal, generates a unique Study ID for reference, and logs the candidate under `classification = "Not Eligible"` for denominator analysis.

---

## Nikshay Registry Reconciliation Comparison
- Accessible via the **Search Participant** table for records with pending sync status.
- Compares local data side-by-side with official Nikshay database entries (Name, Age, Contact).
- Allows investigators to review spelling discrepancies, check agreement checkboxes to override/apply official values, enter the final Nikshay ID, and toggle the `synced = True` status.

---

## Technical Specifications
- **Backend Framework**: Django 4.2+ (Python 3.10+)
- **Database**: SQLite (local dev environment)
- **Frontend CSS**: Vanilla CSS variables, transitions, and Bootstrap 5 layout grids. No external CDNs or Tailwind dependencies required.

---

## Setup & Run Instructions

### 1. Database Migrations
Run the following commands to create/update database schemas:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 2. Testing Accounts
The application includes two pre-populated investigator accounts with predefined site coordinates:
- **User 1**:
  - Username: `staff`
  - Password: `password123`
- **User 2**:
  - Username: `admin`
  - Password: `adminpassword`

### 3. Running the Server
Launch the local development server:
```powershell
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your browser.

### 4. Running the Test Suite
The codebase includes 13 comprehensive unit tests verifying redirects, session configurations, form posts, and the joint eligibility checks:
```powershell
python manage.py test
```
