# Participant Classification & Eligibility Rules Engine

**Document Version:** 1.5 (Updated: Protocol TPT Cohort Definition & Routing)  
**Target Codebase Location:** [`abcg_project/questions/views.py`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/views.py#L995-L1170) and [`abcg_project/central_backend/api/eligibility.py`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/central_backend/api/eligibility.py#L40-L160)  
**Database Models:** [`Participant`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L180), [`TptIndividual`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L377), [`IneligibleIndividual`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L640)  

---

## 1. Overview & Purpose

The **Eligibility & Clinical Classification Engine** automatically evaluates each screened individual during registration (and upon clinical record updates) to categorize them into one of the primary study cohorts:

1. **`TPT`** – TB Preventive Treatment Cohort: Any individual who has undergone TPT (`tpt_undergone == "Yes"`), **irrespective of BCG vaccination status** and **irrespective of Case, Control, Pending, or Excluded clinical investigation results**. Stored in the dedicated [`TptIndividual`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L377) table.
2. **`Case`** – Confirmed Active Tuberculosis (for regular participants with `tpt_undergone == "No"`). Subdivided strictly per study protocol into:
   - **Microbiologically Confirmed TB Case**: Biological specimen tests positive for *Mycobacterium tuberculosis* using a quality-assured molecular diagnostic test (NAAT).
   - **Clinically Diagnosed TB Case**: Not microbiologically confirmed, but diagnosed with active TB by a clinician based on supportive clinical evidence (X-ray suggestive of TB, positive histopathology, or extrapulmonary symptoms).
3. **`Control`** – Confirmed Healthy / Non-TB Control (Normal CXR, Negative NAAT, Negative EPTB).
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
| **3. TPT Status** | Step 4: `tpt_undergone` | `"Yes"` / `"No"` | Whether individual has undergone TB Preventive Treatment (TPT). |
| **4. Pulmonary NAAT (MCTB)** | `final_interpretation` or `naat_status` | `POSITIVE`, `NEGATIVE`, `PENDING` | Quality-assured molecular test (CBNAAT, Truenat, FLLPA, culture). Positive on: `"DETECTED"`, `"POSITIVE"`, `"RIF RESISTANT"`, `"RIF SENSITIVE"`, `"GROWTH OF"`. |
| **5. Chest X-Ray (CXR)** | `cxr_done`, `cxr_result`, `cxr_status` | `SUGGESTIVE_OF_TB`, `ABNORMAL_NON_TB`, `NORMAL`, `NOT_DONE`, `PENDING` | CXR suggestive of TB vs non-TB abnormality vs normal (or unperformed in asymptomatic). |
| **6. Extra-Pulmonary TB & Histopathology** | `eptb_answers`, `test_type` | `POSITIVE`, `NEGATIVE`, `PENDING` | Positive biopsy, lymph node FNAC, pleural fluid NAAT, caseating granuloma, or imaging suggestive of TB. |

---

## 3. Decision Hierarchy & Classification Rules

The rules are evaluated in **strict sequential order of precedence**:

```
Rule 1: Screening Ineligibility      ──► "Not Eligible" (Underage < 18, outside TU, or non-HRG) -> IneligibleIndividual
Rule 2: Consent Declined             ──► "Excluded" (Refused consent) -> Participant (eligible=False)
Rule 3: TPT Undergone                ──► "TPT" (tpt_undergone == "Yes") -> TptIndividual [IRRESPECTIVE OF BCG & CLINICAL STATUS]
Rule 4: Confirmed Active TB Case     ──► "Case" (Microbiologically Confirmed or Clinically Diagnosed) -> Participant
Rule 5: Non-TB CXR Pathology         ──► "Excluded" (Abnormal non-TB CXR + NAAT Neg + EPTB Neg) -> Participant
Rule 6: Completely Uninvestigated    ──► "Excluded" (CXR No + PTB No/Asymptomatic + EPTB No/Asymptomatic) -> Participant
Rule 7: Healthy / Non-TB Control     ──► "Control" (Normal CXR, NAAT Negative, and EPTB Negative) -> Participant
Rule 8: Default Fallthrough          ──► "Pending" (Indefinite, with dynamic itemized missing tests) -> Participant
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

### Rule 3: TB Preventive Treatment Cohort (`TPT`)
* **Condition:** `tpt_undergone == "Yes"` (and consent provided).
* **Key Protocol Rules:**
  1. **TPT == Yes:** Any individual who has taken TPT is classified as **`TPT`**.
  2. **Irrespective of BCG:** Does not require adult BCG vaccination (`bcg_status` can be Yes, No, or unrecorded).
  3. **Irrespective of Case, Control, Pending, or Excluded:** Even if the individual has active TB (NAAT positive or CXR suggestive), normal findings, pending tests, or non-TB abnormalities, they are routed to the **`TptIndividual`** table.
  4. **Full Clinical Preservation:** All clinical details (sputum results, X-rays, EPTB site findings) are fully recorded and preserved inside `ptb_test_details` and `eptb_details` on their `TptIndividual` record.
* **Assigned Classification:** `TPT` (Cohort badge: `TPT Cohort`, NOT `TPT+BCG`).
* **Assigned Reason:** `"Eligible for TPT Cohort: Individual has undergone TB Preventive Treatment (TPT)"`.
* **Storage Destination:** [`TptIndividual`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L377) table.

---

### Rule 4: Confirmed Active Tuberculosis (`Case`)

Applies to regular study participants (`tpt_undergone == "No"`):

#### Sub-category 4A: Microbiologically Confirmed TB Case
* **Protocol Criteria:** Biological specimen tests positive for *M. tuberculosis* using a quality-assured molecular diagnostic test (NAAT / CBNAAT / TrueNat).
* **Condition:** `mctb == "POSITIVE"`
* **Assigned Classification:** `Case`
* **Granular Reasons Assigned:**
  - Both NAAT Positive & CXR Suggestive: `"Microbiologically confirmed TB case: MCTB Positive and CXR suggestive of TB"`
  - NAAT Positive & Normal CXR: `"Microbiologically confirmed TB case: MCTB Positive and Normal CXR"`
  - NAAT Positive only: `"Microbiologically confirmed TB case: MCTB Positive"`

#### Sub-category 4B: Clinically Diagnosed TB Case
* **Protocol Criteria:** Not microbiologically confirmed (`mctb != "POSITIVE"`), but diagnosed with active TB by a clinician based on supportive clinical evidence (X-ray, histopathology, or extrapulmonary symptoms).
* **Condition:** `mctb != "POSITIVE"` AND (`cxr == "SUGGESTIVE_OF_TB"` OR `eptb_status == "POSITIVE"` OR `is_histopathology_positive == True`)
* **Assigned Classification:** `Case`
* **Granular Reasons Assigned:**
  - CXR Suggestive & NAAT Negative: `"Clinically diagnosed TB case: CXR suggestive of TB with MCTB Negative"`
  - CXR Suggestive only: `"Clinically diagnosed TB case: Chest X-Ray suggestive of TB"`
  - EPTB Positive: `"Clinically diagnosed TB case: EPTB Investigation Positive"`
  - Histopathology Positive: `"Clinically diagnosed TB case: Histopathology Investigation Positive"`

* **Storage Destination:** [`Participant`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L180) table.

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
* **Presumptive Safeguard:** If the individual has **active symptoms** (cough, fever, lymphadenopathy), they are a **presumptive TB suspect**. They are NOT excluded; they remain in **`Pending`** for diagnostic workup.

---

### Rule 7: Healthy / Non-TB Control (`Control`)
* **Study Protocol Criteria:** Adult ($\ge 18$), target HRG, eligible for BCG campaign, informed consent provided, without active TB disease (`tpt_undergone == "No"`).
* **Pre-requisites:**
  1. **CXR Performed and Normal:** `cxr == "NORMAL"` (`cxr_done == "Yes"` and interpretation is `"Normal"`). If CXR is not taken, participant is held in **`Pending`**.
  2. **PTB NAAT Performed and Negative:** `mctb == "NEGATIVE"` (`undergone_testing == "Yes"` and result is `"MTB Not Detected"`). If NAAT is not undergone, participant is held in **`Pending`**.
* **Two Control Pathways:**
  - **Pathway 7A (No EPTB Symptoms):** `eptb_symptoms_val == "NO"` $\longrightarrow$ `"Normal CXR, Negative NAAT, and Negative EPTB status"`.
  - **Pathway 7B (EPTB Symptoms Positive, but Tests Negative):** `eptb_status == "NEGATIVE"` $\longrightarrow$ `"Normal CXR, Negative NAAT, and EPTB investigations confirmed negative"`.
* **Assigned Classification:** `Control`
* **Storage Destination:** [`Participant`](file:///c:/Users/IPEGlobal60/Desktop/abcg_training_application/abcg_ontraining/abcg_project/questions/models.py#L180) table.

---

### Rule 8: Default Fallthrough (`Pending`)
* **Condition:** Does not meet Case, Excluded, or Control criteria because one or more clinical diagnostic tests (NAAT, CXR, EPTB) are unperformed, blank, or pending.
* **BCG Details Safeguard:** Missing or incomplete BCG vaccine details (vaccination date, batch number, or facility) **NEVER** cause a participant to be marked as `Pending`. Participant clinical classification is governed strictly by clinical diagnostic tests and findings.
* **Duration Policy:** **Indefinite.** Participants remain in `Pending` regardless of time elapsed ($\ge 30$ days, 60 days, etc.) until diagnostic results are submitted or overridden by a doctor.
* **Assigned Classification:** `Pending`
* **Dynamic Itemized Reasons Generated:**
  - `NAAT (MCTB) is pending because clinical testing has not been undergone`
  - `NAAT (MCTB) is pending because test result is blank or not recorded`
  - `Chest X-Ray has not been performed`
  - `Chest X-Ray is pending because interpretation findings are blank or not recorded`
  - `EPTB is pending because investigation results are not recorded for presumptive EPTB investigation`

---

## 4. Visual Decision Flowchart

```mermaid
flowchart TD
    Start([Participant Registered or Updated]) --> C1{Eligible Adult HRG?<br/>Age >= 18 & HRG & BCG Eligible}
    
    C1 -- No --> R1["Classification: Not Eligible<br/>Destination: IneligibleIndividual table"]
    C1 -- Yes --> C2{Informed Consent<br/>Provided?}
    
    C2 -- No --> R2["Classification: Excluded<br/>Reason: Consent not provided"]
    C2 -- Yes --> C3{TPT Undergone?<br/>tpt_undergone == 'Yes'}
    
    C3 -- Yes --> R3["Classification: TPT<br/>Destination: TptIndividual table<br/>Irrespective of BCG or Clinical Results"]
    C3 -- No --> C4{Active TB Confirmed?<br/>• NAAT Positive (Microbiological)<br/>• CXR Suggestive (Clinical)<br/>• EPTB/Histology Positive (Clinical)}
    
    C4 -- Yes --> R4["Classification: Case<br/>Microbiologically Confirmed or Clinically Diagnosed"]
    C4 -- No --> C5{CXR Abnormal Non-TB &<br/>NAAT Neg & EPTB Neg?}
    
    C5 -- Yes --> R5["Classification: Excluded (Condition 3)<br/>Reason: Non-TB CXR abnormality"]
    C5 -- No --> C6{CXR Not Done &<br/>PTB Asymptomatic/Not Done &<br/>EPTB Asymptomatic?}
    
    C6 -- Yes --> R6["Classification: Excluded (Condition 2)<br/>Reason: Completely uninvestigated & asymptomatic"]
    C6 -- No --> C7{All Tests Negative?<br/>• CXR Normal Done<br/>• NAAT Negative Done<br/>• EPTB Negative/Asymptomatic}
    
    C7 -- Yes --> R7["Classification: Control<br/>Confirmed Healthy / Non-TB Control"]
    C7 -- No --> R8["Classification: Pending (Indefinite)<br/>Itemized missing diagnostic results"]
```
