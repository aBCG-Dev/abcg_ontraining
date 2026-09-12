# aBCG Study Investigator Application

> **Field Application Documentation**\
> **Version:** 1.0\
> **Date:** 01 August 2026

------------------------------------------------------------------------

## Table of Contents

1.  Overview
2.  Technology Stack
3.  Project Structure
4.  Database Schema
5.  Data Models
6.  Classification & Eligibility Engine
7.  Application Screens
8.  Summary

------------------------------------------------------------------------

## 1. Overview

This document describes the architecture, database design, participant
classification workflow, and functional modules of the **Adult BCG
Vaccine Effectiveness (aBCG VE) Study Investigator Application**.

The application enables field investigators to register participants,
perform eligibility screening, classify participants, manage offline
data collection, and synchronize records with the central server.

This document provides an "inch-by-inch" architectural overview of the
client-side application utilized by field investigators in the Adult BCG
Vaccine Effectiveness (aBCG VE) Study.

------------------------------------------------------------------------

## 2. Technology Stack & Project Structure

The application is built on **Django 5.2 (Python)**, utilizing **HTML5 /
CSS3 (Vanilla)** for styling, **Bootstrap 5** for UI wrappers, and
**JavaScript (ES6)** for client-side offline telemetry, wizard form
navigation, and rendering.

    abcg_project/
    ├── config/                  # Core Django project configuration
    └── questions/               # Clinical application module
        ├── management/          # Custom CLI commands (e.g. data import tools)
        ├── migrations/          # SQL database schema state migrations
        ├── templates/           # HTML templates layout folders
        ├── models.py            # SQLite/PostgreSQL Database model architectures
        ├── views.py             # View controller request/response logic
        └── tests.py             # Integration test suites

------------------------------------------------------------------------

## 3. Database Schema

The database layers are structured to ensure atomic storage of clinical
history, offline synchronization queue tags, and investigator metadata.

``` mermaid
classDiagram
    class UserProfile {
        +User user
        +String state
        +String district
        +String tb_unit
    }
    class Participant {
        +String study_id
        +String first_name
        +String last_name
        +Integer age
        +String gender
        +Boolean eligible
        +String classification
        +String classification_reason
        +Boolean synced
        +DateTime created_at
    }
    class TptIndividual {
        +String study_id
        +String first_name
        +String last_name
        +String tpt_undergone
        +String classification
        +Boolean synced
    }
    class IneligibleIndividual {
        +String study_id
        +String full_name
        +String classification
        +String classification_reason
        +Boolean synced
    }
    class DeviceSyncLog {
        +User user
        +Float latitude
        +Float longitude
        +Integer battery_level
        +Boolean battery_charging
        +Integer synced_count
        +String device_user_agent
        +DateTime timestamp
    }
    UserProfile --> Participant : Registers
    Participant --> DeviceSyncLog : Logs Sync
```

### Core Schema Definition

#### `UserProfile` (Investigator Metadata)

Associates a logged-in Django user with their geographic jurisdiction
parameters: - `state`: e.g., "Karnataka" - `district`: e.g., "Bengaluru
Urban" - `tb_unit`: e.g., "Malleswaram TU"

#### `Participant` (Active Screening Cohort)

Stores detailed clinical history, demographic values, and final
eligibility classifications. Key fields include: - **Demographics**:
`first_name`, `last_name`, `age`, `gender`, `contact_number`,
`education`, `income`, `smoking`. - **Physical Metrics**: `height_cm`,
`weight_kg`, `bmi`. - **Comorbidities**: `diabetes`, `hiv`,
`chronic_kidney`, `chronic_liver`, `immunosuppressants`. - **TB
Screening**: `ptb_symptoms`, `eptb_symptoms`, `mctb_result` (NAAT),
`cxr_result` (CXR). - **BCG Status**: `bcg_undergone`, `bcg_scar`,
`bcg_scar_file` (Upload), `bcg_card_file` (Upload). - **Classification
Status**: `classification` (`Case`, `Control`, `Excluded`, `Pending`),
`classification_reason`. - **Outbound Metadata**: `synced` (boolean),
`created_at` (timestamp).

#### `TptIndividual` (TPT Cohort)

Stores records of individuals who screened out of the main Case-Control
study but qualify for the *exploratory cohort* (TPT + BCG): -
`study_id`, `first_name`, `last_name`, `tpt_undergone`, `tpt_regimen`,
`classification` (hardcoded to `"TPT+BCG"`), `synced` (boolean).

#### `IneligibleIndividual` (Screen-out Cohort)

Holds records of individuals who failed to satisfy screening rules
(e.g. ineligible due to age, residential boundaries, etc.): -
`study_id`, `full_name`, `classification` (hardcoded to
`"Not Eligible"`), `classification_reason`, `synced` (boolean).

#### `DeviceSyncLog` (Silent Telemetry)

Persists metadata for each outbound database synchronization: -
`latitude` / `longitude`: Exact location parameters of sync event. -
`battery_level` / `battery_charging`: Health parameters of sync
device. - `synced_count`: Number of records synced. -
`device_user_agent`: Platform details of the investigator's device.

------------------------------------------------------------------------

## 5. Classification & Eligibility Engine

This section describes the detailed rules, conditions, and logical
outcomes applied during participant registration to classify records
into specific cohorts.

### A. Screening Eligibility Checks

Before a participant is classified into any clinical study group, they
must satisfy screening criteria. - **Pass Condition**:
`eligible = has_hrg AND eligible_bcg_campaign` is `True`. - **High Risk
Group (HRG)**: Participant must either be elderly (age ≥ 60) or match
one of the target HRG risk factors (diabetes, HIV, chronic kidney/liver
disease, immunosuppressants, or past history of TB). - **BCG Campaign
Eligibility**: Must match at least one campaign eligibility criterion
(e.g., aged \> 60, past history of TB, self-reported diabetes or smoking
during campaign, close contact of a TB patient, or undernourished with
BMI \< 18). - **Fail Condition**: If the participant does not meet both
`has_hrg` and `eligible_bcg_campaign`, the record is categorized as
**Not Eligible** and routed to the `IneligibleIndividual` table.

------------------------------------------------------------------------

### B. Cohort Classification Rules

Once screening eligibility is satisfied, the record is evaluated against
the following classification engine rules in descending order:

``` mermaid
graph TD
    Start[Screening Eligible?] -->|No| NotEligible[Not Eligible Cohort]
    Start -->|Yes| TptBcgCheck{TPT Undergone & BCG Verified?}
    TptBcgCheck -->|Yes| TptBcgCohort[TPT+BCG Cohort]
    TptBcgCheck -->|No| ExcludeCheck1{Abnormal Non-TB CXR & NAAT Negative?}
    ExcludeCheck1 -->|Yes| ExcludedCohort[Excluded Cohort]
    ExcludeCheck1 -->|No| ExcludeCheck2{Investigation Pending > 30 Days?}
    ExcludeCheck2 -->|Yes| ExcludedCohort
    ExcludeCheck2 -->|No| CaseCheck{NAAT Positive OR CXR Suggestive OR EPTB Positive?}
    CaseCheck -->|Yes| CaseCohort[Case Cohort]
    CaseCheck -->|No| ControlCheck{NAAT Negative AND CXR Normal AND EPTB Negative?}
    ControlCheck -->|Yes| ControlCohort[Control Cohort]
    ControlCheck -->|No| PendingCohort[Pending Cohort]
```

  --------------------------------------------------------------------------------------------------------------------------------
  Classification    Target Table             Trigger Conditions      Rationale / Classification Reason
  ----------------- ------------------------ ----------------------- -------------------------------------------------------------
  **Not Eligible**  `IneligibleIndividual`   Initial screening       `"Participant is ineligible under screening criteria."`
                                             eligibility check fails 
                                             (`eligible` is          
                                             `False`).               

  **TPT+BCG**       `TptIndividual`          Participant is          `"Eligible for BCG + TPT Exploratory Cohort"`
                                             eligible, has undergone 
                                             BCG vaccination, and    
                                             has `tpt_undergone` ==  
                                             `"Yes"`.                

  **Excluded**      `Participant`            **1. Abnormal Non-TB    **1.**
                                             CXR**: `cxr` ==         `"Abnormal CXR not suggestive of TB with NAAT Negative"`
                                             `"ABNORMAL_NON_TB"` and `<br>`{=html}**2.**
                                             `mctb` == `"NEGATIVE"`. `"Pending investigation beyond one month"`
                                             `<br>`{=html}**2.       
                                             Testing Timeout**:      
                                             Investigation results   
                                             are pending (`mctb` or  
                                             `cxr` or `eptb_status`  
                                             is `"PENDING"`) and     
                                             record creation is over 
                                             30 days old.            

  **Case**          `Participant`            **1. NAAT Positive**:   **Specific Rationale mappings:** `<br>`{=html}- *Both
                                             `mctb` == `"POSITIVE"`. Positive*: `"MCTB Positive and CXR suggestive of TB"`
                                             `<br>`{=html}**2.       `<br>`{=html}- *NAAT Positive + Normal CXR*:
                                             Suggestive CXR**: `cxr` `"MCTB Positive and Normal CXR"` `<br>`{=html}- *NAAT
                                             ==                      Positive + Other CXR*: `"MCTB Positive"` `<br>`{=html}- *CXR
                                             `"SUGGESTIVE_OF_TB"`.   Suggestive + NAAT Negative*:
                                             `<br>`{=html}**3. EPTB  `"CXR suggestive of TB with MCTB Negative"` `<br>`{=html}-
                                             Positive**:             *CXR Suggestive + NAAT Pending*:
                                             `eptb_status` ==        `"Chest X-Ray suggestive of TB"` `<br>`{=html}- *EPTB
                                             `"POSITIVE"`.           Positive (and other PTB negative/pending)*:
                                                                     `"EPTB Investigation Positive"`

  **Control**       `Participant`            `cxr` == `"NORMAL"`     `"Normal CXR, Negative NAAT, and Negative EPTB status"`
                                             **AND** `mctb` ==       
                                             `"NEGATIVE"` **AND**    
                                             active EPTB screening   
                                             symptoms are either     
                                             absent or confirmed     
                                             negative (`eptb_status` 
                                             == `"NEGATIVE"`).       

  **Pending**       `Participant`            **Default state** where `"One or more required investigation results are pending."`
                                             clinical investigations 
                                             are incomplete          
                                             (e.g. testing results   
                                             are blank or            
                                             `undergone_testing` ==  
                                             `"No"`).                
  --------------------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 6. Application Modules

### Screen 1: Dashboard Home (`/`)

-   **Connectivity Status**: Real-time status dot checking browser
    offline/online state (`navigator.onLine`).
-   **Sync Metrics Panel**: Shows investigator's local stats for
    "Registered Today", "Total Cases", and "Total Controls".
-   **Workflow Access Cards**:
    -   **New Registration (Module 01)**: Opens the multi-step
        registration wizard.
    -   **Search Participant (Module 03)**: Opens the participant file
        browser.
    -   **Data Synchronization (Module 04)**: Opens the staging sync
        manager.

### Screen 2: Registration Wizard (`/registration/`)

A multi-step progressive form that validates clinical metrics at each
gate before proceeding. - **Dynamic Mobile Progress Stepper**: Stepper
scales down to a single progress bar on small devices to prevent visual
overlapping. - **Section Details**: 1. **Site Location**: Auto-fills the
investigator's district/state parameters. 2. **Personal Profile**:
Standard demographic variables. Calculates BMI dynamically based on
height and weight. 3. **Socio-demographics**: Captures education levels,
housing details, smoking patterns, and alcohol intake. 4. **High Risk
Groups**: Checklist of chronic medical conditions. 5. **PTB Symptoms**:
Selectable pulmonary symptoms checklist. 6. **EPTB Symptoms**:
Selectable extra-pulmonary symptoms checklist. 7. **Diagnosis**:
Clinical test fields (NAAT results, Chest X-Ray interpretation). 8.
**BCG Verification**: File upload fields for BCG scar and vaccination
cards. - **Classification Modal**: Fires dynamically on registration
completion, showing final eligibility and classification rationale.

### Screen 3: Search Registry (`/search/`)

A split-pane (Master-Detail) viewer designed to manage study records: -
**Filter Controls**: Search input (Study ID, Name) and filter dropdowns
(Synced, Pending, Case, Control, Ineligible). - **Master List**:
Displays matching cards. Shows badges for synced status, name, age, and
classification. - **Detail Pane**: Renders clinical details (symptoms
checklists, diagnosis, BCG details) when a participant is selected. -
Hides on mobile viewports. On mobile, tapping a card activates a smooth
drawer navigation transition, switching views and providing a "Back to
List" button. - Provides direct access to the **Reconciliation**
workflow if discrepancies are found.

### Screen 4: Nikshay Data Reconciliation (`/reconcile/<id>/`)

Enables cross-checking offline field records against the simulated
National Nikshay Registry database response. - **Side-by-Side
Comparison**: Displays field inputs side-by-side with Nikshay columns
(e.g. Name, Age, Contact). - **Agreement Checklist**: Checkboxes allow
investigators to resolve discrepancy values before committing the final
record state.

### Screen 5: Data Synchronization Portal (`/pending-sync/`)

Acts as the staging environment before data is uploaded: -
**Informational Alert Banner**: Explains browser-local sandbox caching
logic. - **Offline Staging Queue**: Lists all records where
`synced=False`. Permits editing a record before final sync submission. -
**Silent Telemetry Panel**: Gathers browser-level GPS coordinates and
battery metrics asynchronously. Telemetry variables are silently stored
in `DeviceSyncLog` on submission.

------------------------------------------------------------------------

## 7. Summary

### Key Features

-   Offline-first field application
-   Multi-step participant registration
-   Automated eligibility and classification engine
-   TPT, Case, Control and Ineligible cohort management
-   Local synchronization queue
-   Device telemetry logging
-   Nikshay reconciliation workflow
-   Responsive mobile interface
-   Django-based architecture with Bootstrap UI

------------------------------------------------------------------------

## Revision History

  Version   Date          Description
  --------- ------------- -----------------------
  1.0       01-Aug-2026   Initial documentation
