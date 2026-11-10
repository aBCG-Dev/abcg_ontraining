# Participant Classification & Eligibility Rules Engine

**Document Version:** 1.4 (Updated: Formal Protocol Excluded Definitions & Safeguards)  
**Target Codebase Location:** [`abcg_project/questions/views.py`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/views.py#L995-L1170) and [`abcg_project/central_backend/api/eligibility.py`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/central_backend/api/eligibility.py#L40-L160)  
**Database Models:** [`Participant`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L180), [`TptIndividual`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L460), [`IneligibleIndividual`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L640)  

---

## 1. Overview & Purpose

The **Eligibility & Clinical Classification Engine** automatically evaluates each screened individual during registration (and upon clinical record updates) to categorize them into one of the primary study cohorts:

1. **`Case`** – Confirmed Active Tuberculosis. Subdivided strictly per study protocol into:
   - **Microbiologically Confirmed TB Case**: An adult (age $\ge 18$) belonging to an identified high-risk group, eligible for adult BCG vaccination, whose biological specimen tests positive for *Mycobacterium tuberculosis* using a quality-assured molecular diagnostic test (NAAT).
   - **Clinically Diagnosed TB Case**: An adult (age $\ge 18$) belonging to an identified high-risk group, eligible for adult BCG vaccination, who is not microbiologically confirmed, but has been diagnosed with active TB based on supportive clinical evidence (X-ray suggestive of TB, positive histopathology, or extrapulmonary symptoms).
2. **`Control`** – Confirmed Healthy / Non-TB Control (Normal CXR, Negative NAAT, Negative EPTB).
3. **`TPT+BCG`** – Exploratory Cohort: High-risk individual with BCG vaccination and TPT chemoprophylaxis history **without active TB disease**.
4. **`Pending`** – Clinical investigation data pending (CXR, NAAT, or EPTB). **Participants with pending tests are NEVER excluded based on elapsed time (even $\ge 30$ days), ensuring diagnostic delays never cause improper disqualification.**
5. **`Excluded`** – Ineligible for study cohort analysis under three distinct protocol conditions:
   - **Condition 1**: Consent declined (`consent == "No"`).
   - **Condition 2**: Completely uninvestigated / unscreened (`cxr_done == "No"`, PTB not tested & asymptomatic, EPTB not tested & asymptomatic).
   - **Condition 3**: Abnormal non-TB CXR with negative NAAT and negative/asymptomatic EPTB.
6. **`Not Eligible`** – Did not meet preliminary screening criteria (age $< 18$, outside study TB Unit, or no target high-risk criteria).

---

## 2. Input Diagnostic Signals

The engine processes 6 primary input signals before evaluating the decision hierarchy:

| Signal | Source Field(s) | Possible Internal Values | Clinical Interpretation |
| :--- | :--- | :--- | :--- |
| **1. Screening Eligibility** | Preliminary Screening Steps 1–4 | `True` / `False` | Age $\ge 18$, lives in study site/TB Unit, belongs to target high-risk groups. |
| **2. Informed Consent** | Step 4: `consent` | `"Yes"` / `"No"` | Whether participant agreed to provide informed consent. |
| **3. Pulmonary NAAT (MCTB)** | `final_interpretation` or `naat_status` | `POSITIVE`, `NEGATIVE`, `PENDING` | Quality-assured molecular test (CBNAAT, Truenat, FLLPA, culture). Positive on: `"DETECTED"`, `"POSITIVE"`, `"RIF RESISTANT"`, `"RIF SENSITIVE"`, `"GROWTH OF"`. |
| **4. Chest X-Ray (CXR)** | `cxr_done`, `cxr_result`, `cxr_status` | `SUGGESTIVE_OF_TB`, `ABNORMAL_NON_TB`, `NORMAL`, `NOT_DONE`, `PENDING` | CXR suggestive of TB vs non-TB abnormality vs normal (or unperformed in asymptomatic). |
| **5. Extra-Pulmonary TB & Histopathology** | `eptb_answers`, `test_type` | `POSITIVE`, `NEGATIVE`, `PENDING` | Positive biopsy, lymph node FNAC, pleural fluid NAAT, caseating granuloma, or imaging suggestive of TB. |
| **6. TPT + BCG Profile** | `has_hrg`, `eligible_bcg_campaign`, `tpt_undergone`, `bcg_status` | `True` / `False` | Belongs to HRG, eligible for campaign, underwent TPT, and was vaccinated with BCG. |

---

## 3. Decision Hierarchy & Classification Rules

The rules are evaluated in **strict sequential order of precedence**. Confirmed active disease (`Case`) takes priority over exploratory cohort assignments (`TPT+BCG`) and radiological exclusions (`Excluded`).

```
Rule 1: Screening Ineligibility      ──► "Not Eligible" (Underage < 18, outside TU, or non-HRG)
Rule 2: Consent Declined             ──► "Excluded" (Refused consent)
Rule 3: Confirmed Active TB Case     ──► "Case" (Microbiologically Confirmed or Clinically Diagnosed)
Rule 4: TPT + BCG Cohort Check       ──► "TPT+BCG" (High Risk + TPT Yes + BCG Yes without active TB)
Rule 5: Non-TB CXR Pathology         ──► "Excluded" (Abnormal non-TB CXR + NAAT Neg + EPTB Neg)
Rule 6: Completely Uninvestigated    ──► "Excluded" (CXR No + PTB No/Asymptomatic + EPTB No/Asymptomatic)
Rule 7: Healthy / Non-TB Control     ──► "Control" (Normal CXR, NAAT Negative, and EPTB Negative)
Rule 8: Default Fallthrough          ──► "Pending" (Indefinite, with dynamic itemized missing tests)
```

---

### Rule 1: Screening Ineligibility
* **Condition:** `not eligible` (Age $< 18$, outside study TB Unit, or non-HRG).
* **Assigned Classification:** `Not Eligible`
* **Assigned Reason:** `"Participant is ineligible under screening criteria."`
* **Storage Destination:** [`IneligibleIndividual`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L640) table.

---

### Rule 2: Protocol Exclusion – Condition 1 (Consent Declined)
* **Condition:** `consent_declined == True` (`consent == "No"`).
* **Assigned Classification:** `Excluded`
* **Assigned Reason:** `"Excluded from Study: Informed consent not provided"`
* **Action:** Clears clinical diagnostic answers; sets `ptb_screened = False`, `eptb_screened = False`, `bcg_status = "No"`.
* **Storage Destination:** [`Participant`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L180) table with `eligible = False`.

---

### Rule 3: Confirmed Active Tuberculosis (`Case`)

Evaluated **BEFORE** TPT+BCG exploratory checks and Non-TB CXR exclusion, ensuring that any participant with active TB is captured as a Case:

#### Sub-category 3A: Microbiologically Confirmed TB Case
* **Protocol Criteria:** Adult ($\ge 18$), target HRG, eligible for BCG campaign, whose biological specimen tests positive for *M. tuberculosis* using a quality-assured molecular diagnostic test (NAAT / CBNAAT / TrueNat).
* **Condition:** `mctb == "POSITIVE"`
* **Assigned Classification:** `Case`
* **Granular Reasons Assigned:**
  - Both NAAT Positive & CXR Suggestive: `"Microbiologically confirmed TB case: MCTB Positive and CXR suggestive of TB"`
  - NAAT Positive & Normal CXR: `"Microbiologically confirmed TB case: MCTB Positive and Normal CXR"`
  - NAAT Positive only: `"Microbiologically confirmed TB case: MCTB Positive"`

#### Sub-category 3B: Clinically Diagnosed TB Case
* **Protocol Criteria:** Adult ($\ge 18$), target HRG, eligible for BCG campaign, not microbiologically confirmed (`mctb != "POSITIVE"`), but diagnosed with active TB by a clinician based on supportive clinical evidence (X-ray, histopathology, or extrapulmonary symptoms).
* **Condition:** `mctb != "POSITIVE"` AND (`cxr == "SUGGESTIVE_OF_TB"` OR `eptb_status == "POSITIVE"` OR `is_histopathology_positive == True`)
* **Assigned Classification:** `Case`
* **Granular Reasons Assigned:**
  - CXR Suggestive & NAAT Negative: `"Clinically diagnosed TB case: CXR suggestive of TB with MCTB Negative"`
  - CXR Suggestive only: `"Clinically diagnosed TB case: Chest X-Ray suggestive of TB"`
  - EPTB Positive: `"Clinically diagnosed TB case: EPTB Investigation Positive"`
  - Histopathology Positive: `"Clinically diagnosed TB case: Histopathology Investigation Positive"`

##### Deep-Dive: Extra-Pulmonary TB (EPTB) Case Classification Logic
For a participant to become a `Case` via the EPTB pathway:
1. **Screening Gate:** Must be an adult ($\ge 18$), belonging to a target High-Risk Group (HRG), eligible for the adult BCG campaign, with consent provided (`consent == "Yes"`).
2. **Symptom Trigger (Step 6):** Any of the 11 anatomical site symptom questions is checked `"Yes"`:
   - `eptb_q1a`: Swelling in neck/armpit/groin (Lymph Node TB)
   - `eptb_q2a`: Chest pain + breathlessness (Pleural TB)
   - `eptb_q3a`: Headache / altered mental status / seizures (CNS / TB Meningitis)
   - `eptb_q4a`: Abdominal pain / distension / vomiting (Abdominal TB)
   - `eptb_q5a`: Pain in spine / joint region >6 weeks (Spinal TB / Pott's Disease or Bone & Joint TB)
   - `eptb_q6a`: Urinary or scrotal symptoms (Genitourinary TB)
   - `eptb_q7`: Infertility / pelvic pain / menstrual irregularities (Female Genital TB)
   - `eptb_q8`: Ulcer / discharging sinus / skin lesion (Cutaneous TB)
   - `eptb_q9`: Redness / blurred vision / eye pain (Ocular TB)
   - `eptb_q10`: Chest pain + breathlessness + ECG changes (Pericardial TB)
   - `eptb_q11`: Multi-organ involvement + systemic symptoms (Disseminated / Miliary TB)
3. **Investigation & Result Parsing:**
   - For any active site, an investigation must be marked performed (`eptb_investigation_<site>_<inv>_performed == "Yes"`).
   - **Laboratory Tests** (FNAC, Biopsy, Histopathology, CBNAAT/Xpert, Culture, LPA, ADA, Fluid Analysis): checked via `_final_interpretation` or `_result_findings`.
   - **Imaging & Clinical Exams** (Ultrasound, CT, MRI, CXR, Endoscopy): checked via `_result_findings`.
   - **Positivity Criteria:** If the result contains `"POSITIVE"`, `"SUGGESTIVE"`, or `"DETECTED"` (case-insensitive) $\rightarrow$ `eptb_status = "POSITIVE"`.
4. **Classification Priority:**
   - If `mctb != "POSITIVE"` and `eptb_status == "POSITIVE"`, participant is classified as `Case` with reason:
     `"Clinically diagnosed TB case: EPTB Investigation Positive"`
   - If sputum NAAT is also `"POSITIVE"`, microbiological confirmation takes protocol precedence:
     `"Microbiologically confirmed TB case: ..."`
   - An EPTB Case overrides `cxr == "ABNORMAL_NON_TB"` (participant is classified as `Case`, not `Excluded`).
   - An EPTB Case overrides TPT cohort routing (participant is kept as `Case` in `Participant` table).
5. **Pending State:** If EPTB symptoms are present but no investigation has been performed, or the findings are blank / pending, `eptb_status = "PENDING"` and the participant is placed in `Pending`.

* **Storage Destination:** [`Participant`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L180) table.

---

### Rule 4: TPT + BCG Exploratory Cohort
* **Condition:** `is_tpt_bcg == True`  
  *(Criteria: High-Risk Group + BCG campaign eligible + `tpt_undergone == "Yes"` + `bcg_status == "Yes"` + consent provided + **NOT an active TB Case**).*
* **Assigned Classification:** `TPT+BCG`
* **Assigned Reason:** `"Eligible for BCG + TPT Exploratory Cohort"`
* **Storage Destination:** [`TptIndividual`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L460) table.

---

### Rule 5: Protocol Exclusion – Condition 3 (Non-TB CXR Pathology Exclusion)
* **Condition:** `cxr == "ABNORMAL_NON_TB"` AND `mctb == "NEGATIVE"` AND `(eptb_symptoms_val == "NO" or eptb_status == "NEGATIVE")`.
* **Assigned Classification:** `Excluded`
* **Assigned Reason:** `"Abnormal CXR not suggestive of TB with NAAT Negative and Negative EPTB status"`
* **Safeguards & Overrides:**
  - **EPTB Safeguard:** If presumptive EPTB investigation is pending (`eptb_status == "PENDING"`), the participant is held in **`Pending`** because a positive EPTB result promotes the participant to a `Case`.
  - **Active Disease Priority:** If NAAT is positive, microbiological confirmation takes precedence $\rightarrow$ `Case`.

---

### Rule 6: Protocol Exclusion – Condition 2 (Completely Uninvestigated / Unscreened)
* **Condition:**
  1. `cxr_done == "No"` or `cxr_status == "Not Done"`
  2. `undergone_testing == "No"` AND `is_asymptomatic` (no cough $\ge 2$ weeks, fever, hemoptysis, weight loss, night sweats)
  3. `eptb_symptoms_val == "NO"` (no EPTB symptoms selected or `eptb_asymptomatic == "Yes"`)
* **Assigned Classification:** `Excluded`
* **Assigned Reason:** `"Excluded from Study: No clinical investigations or active symptoms (CXR not done, PTB not tested/asymptomatic, EPTB not tested/asymptomatic)"`
* **Clinical Rationale & Presumptive Safeguard:**
  - Individuals without any active symptoms who have not undergone CXR, pulmonary testing, or extrapulmonary investigations cannot be evaluated for Case or Control endpoints and are excluded.
  - **Crucial Safeguard:** If the individual has **active symptoms** (e.g. cough, fever, lymphadenopathy), they are a **presumptive TB suspect**. They are NOT excluded; they are placed into **`Pending`** so the study team can ensure clinical workup is completed.

---

### Rule 7: Healthy / Non-TB Control (`Control`)
* **Study Protocol Criteria:** Adult ($\ge 18$), target HRG, eligible for BCG campaign, informed consent provided, without active TB disease.
* **Pre-requisites:**
  1. **CXR Performed and Normal:** `cxr == "NORMAL"` (CXR **must be taken** `cxr_done == "Yes"` and interpretation is `"Normal"`). If CXR is not taken (`cxr_done == "No"`), the participant is held in **`Pending`** (`"Chest X-Ray has not been performed"`).
  2. **PTB NAAT Performed and Negative:** `mctb == "NEGATIVE"` (Sputum testing **must be undergone** `undergone_testing == "Yes"` and result is `"MTB Not Detected"` / `"Negative"` / `"No growth"`). If NAAT is not undergone, the participant is held in **`Pending`** (`"NAAT (MCTB) is pending because clinical testing has not been undergone"`).
* **Two Control Pathways:**
  - **Pathway 7A (No EPTB Symptoms):**
    - Condition: `eptb_symptoms_val == "NO"` (No EPTB symptoms checked, or `eptb_asymptomatic == "Yes"`).
    - Assigned Reason: `"Normal CXR, Negative NAAT, and Negative EPTB status"`
  - **Pathway 7B (EPTB Symptoms Positive, but Tests Negative):**
    - Condition: `eptb_symptoms_val == "YES"` AND all investigated EPTB sites confirmed negative (`eptb_status == "NEGATIVE"`).
    - Assigned Reason: `"Normal CXR, Negative NAAT, and EPTB investigations confirmed negative"`
* **Assigned Classification:** `Control`
* **Storage Destination:** [`Participant`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L180) table.

---

### Rule 8: Default Fallthrough (`Pending`)
* **Condition:** Does not meet Case, Excluded, or Control criteria because one or more clinical diagnostic tests are unperformed, blank, or pending.
* **Duration Policy:** **Indefinite.** Participants remain in `Pending` regardless of time elapsed ($\ge 30$ days, 60 days, etc.) until diagnostic results are submitted or overridden by a doctor.
* **Assigned Classification:** `Pending`
* **Dynamic Itemized Reasons Generated:**
  - **NAAT Pending:**
    - Testing not undergone: `"NAAT (MCTB) is pending because clinical testing has not been undergone"`
    - Result unrecorded: `"NAAT (MCTB) is pending because test result is blank or not recorded"`
  - **CXR Pending:**
    - CXR not performed: `"Chest X-Ray has not been performed"`
    - Findings unrecorded: `"Chest X-Ray is pending because interpretation findings are blank or not recorded"`
    - Other CXR pending: `"Chest X-Ray investigation is pending"`
  - **EPTB Pending:**
    - Symptoms present but tests missing: `"EPTB is pending because investigation results are not recorded for presumptive EPTB investigation"`
    - Site tests pending: `"EPTB is pending because investigation results are not recorded for <Site Name(s)>"`

---

## 4. Visual Decision Flowchart

```mermaid
flowchart TD
    Start([Participant Registered or Updated]) --> C1{Eligible Adult HRG?<br/>Age >= 18 & HRG & BCG Eligible}
    
    C1 -- No --> R1["Classification: Not Eligible<br/>Destination: IneligibleIndividual table"]
    C1 -- Yes --> C2{Informed Consent<br/>Provided?}
    
    C2 -- No --> R2["Classification: Excluded (Condition 1)<br/>Reason: Consent not provided"]
    C2 -- Yes --> C3{Active TB Confirmed?<br/>• NAAT Positive (Microbiological)<br/>• CXR Suggestive (Clinical)<br/>• EPTB/Histology Positive (Clinical)}
    
    C3 -- Yes --> R3["Classification: Case<br/>Microbiologically Confirmed or Clinically Diagnosed"]
    C3 -- No --> C4{High Risk + TPT Yes +<br/>BCG Yes?}
    
    C4 -- Yes --> R4["Classification: TPT+BCG<br/>Destination: TptIndividual table"]
    C4 -- No --> C5{CXR Abnormal Non-TB &<br/>NAAT Neg & EPTB Neg?}
    
    C5 -- Yes --> R5["Classification: Excluded (Condition 3)<br/>Reason: Non-TB CXR abnormality"]
    C5 -- No --> C6{CXR Not Done &<br/>PTB Asymptomatic/Not Done &<br/>EPTB Asymptomatic?}
    
    C6 -- Yes --> R6["Classification: Excluded (Condition 2)<br/>Reason: Completely uninvestigated & asymptomatic"]
    C6 -- No --> C7{All Tests Negative?<br/>• CXR Normal Done<br/>• NAAT Negative Done<br/>• EPTB Negative/Asymptomatic}
    
    C7 -- Yes --> R7["Classification: Control<br/>Confirmed Healthy / Non-TB Control"]
    C7 -- No --> R8["Classification: Pending (Indefinite)<br/>Itemized missing diagnostic results"]
```

---

## 5. Downstream Workflows & Clinical Overrides

1. **Doctor Clinical Override (`doctor_verify` view):**
   - Authorized roles (`Super Admin`, `Admin`, `Doctor`) can access the clinical verification queue and manually override any participant's classification with an audit-logged clinical rationale.
2. **Reconciliation Module (`reconcile.html`):**
   - Allows site coordinators to compare local aBCG records against Nikshay / Central Registry data for name, age, phone, BCG status, BCG date, BCG scar, and TB classification, marking records as `FULLY_RECONCILED` or `PARTIALLY_RECONCILED`.
3. **Data Quality & Reporting (`data_export_view`):**
   - Both the active `classification` and underlying `classification_reason` are exported to CSV and Excel reports.
