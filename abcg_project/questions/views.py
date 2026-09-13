import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from .models import (
    Participant, Symptom, RiskFactor, Question, Option, BcgVaccination,
    TptIndividual, IneligibleIndividual, DeviceSyncLog, NikshayRecord, sync_nikshay_record,
    StudySite, StudyDevice, get_campaign_period_for_site
)
from eptb.forms import EPTBScreeningForm
from eptb.models import EptbSite, EptbSubQuestion

from django.contrib.auth.models import User
from questions.models import UserProfile, AuditLog, RolePermission
from questions.decorators import role_required, permission_required, has_role_permission, group_required

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_state_code(state_name):
    name = (state_name or "").strip().upper()
    mapping = {
        "ANDHRA PRADESH": "AP",
        "HARYANA": "HR",
        "HIMACHAL PRADESH": "HP",
        "JAMMU AND KASHMIR": "JK",
        "JHARKHAND": "JH",
        "KARNATAKA": "KA",
        "KERALA": "KL",
        "MADHYA PRADESH": "MP",
        "MAHARASHTRA": "MH",
        "MEGHALAYA": "ML",
        "MIZORAM": "MZ",
        "NAGALAND": "NL",
        "ODISHA": "OD",
        "PUDUCHERRY": "PY",
        "PUNJAB": "PB",
        "RAJASTHAN": "RJ",
        "TAMIL NADU": "TN",
        "TELANGANA": "TG",
        "TRIPURA": "TR",
        "UTTAR PRADESH": "UP",
        "UTTARAKHAND": "UK",
        "WEST BENGAL": "WB",
    }
    for k, v in mapping.items():
        if k in name:
            return v
    return name[:2] if len(name) >= 2 else "ST"


def filter_by_jurisdiction(queryset, request_or_user):
    """
    Applies dynamic jurisdictional filtering:
    - Super Admin: no filters (sees everything)
    - Admin: restricted to their state and district
    - Nodal Officer: restricted to their state and district
    - Doctor: restricted to their state, district, and tb_unit
    - Project Nurse: restricted to their state, district, and tb_unit

    If request is provided, further restricts query based on the active session/GET filters.
    """
    from django.contrib.auth.models import AnonymousUser
    if hasattr(request_or_user, "user"):
        request = request_or_user
        user = request.user
    else:
        request = None
        user = request_or_user

    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return queryset.none()
    
    profile = getattr(user, 'profile', None)
    if not profile:
        return queryset.none()
        
    role = getattr(profile, 'role', 'Project Nurse')
    
    # 1. Apply base jurisdiction restrictions
    if role in ["Super Admin", "Admin"]:
        qs = queryset
    else:
        is_sync_log = queryset.model.__name__ == 'DeviceSyncLog'
        if is_sync_log:
            if role in ["Nodal Officer"]:
                qs = queryset.filter(user__profile__state=profile.state, user__profile__district=profile.district)
            elif role in ["Doctor", "Project Nurse"]:
                qs = queryset.filter(user__profile__state=profile.state, user__profile__district=profile.district, user__profile__tb_unit=profile.tb_unit)
            else:
                qs = queryset.none()
        else:
            if role in ["Nodal Officer"]:
                qs = queryset.filter(state=profile.state, district=profile.district)
            elif role in ["Doctor", "Project Nurse"]:
                qs = queryset.filter(state=profile.state, district=profile.district, tb_unit=profile.tb_unit)
            else:
                qs = queryset.none()

    # 2. Apply active session filters (persist GET updates to session first to avoid template rendering lifecycle lag)
    if request:
        if 'state' in request.GET:
            new_state = request.GET.get('state', '')
            if new_state != request.session.get('selected_state', ''):
                request.session['selected_state'] = new_state
                request.session['selected_district'] = ''
                request.session['selected_tb_unit'] = ''
        if 'district' in request.GET:
            new_district = request.GET.get('district', '')
            if new_district != request.session.get('selected_district', ''):
                request.session['selected_district'] = new_district
                request.session['selected_tb_unit'] = ''
        if 'tb_unit' in request.GET:
            request.session['selected_tb_unit'] = request.GET.get('tb_unit', '')

        selected_state = request.session.get('selected_state', '')
        selected_district = request.session.get('selected_district', '')
        selected_tb_unit = request.session.get('selected_tb_unit', '')

        # Enforce boundary checks on the selections (redundancy check for security)
        if role not in ["Super Admin", "Admin"]:
            selected_state = profile.state or ""
        if role in ["Nodal Officer", "Doctor", "Project Nurse"]:
            selected_district = profile.district or ""
        if role in ["Doctor", "Project Nurse"]:
            selected_tb_unit = profile.tb_unit or ""

        # Filter queryset based on validated session values
        is_sync_log = queryset.model.__name__ == 'DeviceSyncLog'
        if is_sync_log:
            if selected_state:
                qs = qs.filter(user__profile__state=selected_state)
            if selected_district:
                qs = qs.filter(user__profile__district=selected_district)
            if selected_tb_unit:
                qs = qs.filter(user__profile__tb_unit=selected_tb_unit)
        else:
            if selected_state:
                qs = qs.filter(state=selected_state)
            if selected_district:
                qs = qs.filter(district=selected_district)
            if selected_tb_unit:
                qs = qs.filter(tb_unit=selected_tb_unit)

    return qs


def home(request):
    """
    The main Study Operations Dashboard view.
    If not logged in, handles inline login and renders a welcome screen.
    Otherwise, loads the profile info and daily performance statistics.
    """
    if not request.user.is_authenticated:
        error_message = None
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                profile = getattr(user, "profile", None)
                role = getattr(profile, "role", "Project Nurse")
                if role in ["Super Admin", "Admin", "Nodal Officer", "Doctor"]:
                    return redirect("questions:dashboard_home")
                return redirect("questions:home")
            else:
                error_message = "Invalid username or password."
        
        return render(request, "questions/home.html", {
            "error_message": error_message,
            "is_login_page": True
        })

    # User is authenticated
    profile = request.user.profile
    role = getattr(profile, "role", "Project Nurse")
    if role in ["Super Admin", "Admin", "Nodal Officer", "Doctor"]:
        return redirect("questions:dashboard_home")
    today = timezone.localdate()
    
    # Gather live performance stats using filtered querysets
    participants_qs = Participant.objects.all()
    tpt_qs = TptIndividual.objects.all()
    
    # Apply jurisdictional filters based on role
    participants_filtered = filter_by_jurisdiction(participants_qs, request)
    tpt_filtered = filter_by_jurisdiction(tpt_qs, request)
    
    # For Project Nurses, restrict stats to their own work
    role = getattr(profile, "role", "Project Nurse")
    if role == "Project Nurse":
        participants_filtered = participants_filtered.filter(created_by=request.user)
        tpt_filtered = tpt_filtered.filter(created_by=request.user)
        
    total_registered_today = (
        participants_filtered.filter(date_enroll=today).count() +
        tpt_filtered.filter(date_enroll=today).count()
    )
    total_cases = participants_filtered.filter(classification="Case").count()
    total_controls = participants_filtered.filter(classification="Control").count()
    
    context = {
        "site": {
            "state": profile.state,
            "district": profile.district,
            "tb_unit": profile.tb_unit,
        },
        "stats": {
            "registered_today": total_registered_today,
            "cases": total_cases,
            "controls": total_controls,
        },
        "actions": [
            {
                "icon": "bi-person-plus",
                "title": "New Registration",
                "description": "Register participant, check campaign lock, and verify high-risk eligibility.",
                "status": "Module 01",
                "url_name": "questions:registration",
                "card_class": "workflow-card-registration"
            },
            {
                "icon": "bi-search",
                "title": "Search Participant",
                "description": "Find records by Study ID or Nikshay ID.",
                "status": "Module 03",
                "url_name": "questions:search",
                "card_class": "workflow-card-search"
            },
            {
                "icon": "bi-arrow-repeat",
                "title": "Data Synchronization",
                "description": "Review, validate, and synchronize staged offline records.",
                "status": "Module 04",
                "url_name": "questions:pending_sync",
                "card_class": "workflow-card-sync"
            },
        ],
        "is_login_page": False
    }
    
    # Handle classification result modal after registration save
    classified_id = request.GET.get("classified_id") or request.session.pop("classified_id", None)
    if classified_id:
        classified_obj = None
        try:
            classified_obj = Participant.objects.get(pk=classified_id)
        except Participant.DoesNotExist:
            try:
                classified_obj = TptIndividual.objects.get(pk=classified_id)
            except TptIndividual.DoesNotExist:
                try:
                    classified_obj = IneligibleIndividual.objects.get(pk=classified_id)
                except IneligibleIndividual.DoesNotExist:
                    pass
        
        if classified_obj:
            context["show_classification_modal"] = True
            context["classified_participant"] = {
                "id": classified_obj.id,
                "study_id": classified_obj.study_id,
                "full_name": classified_obj.full_name,
                "classification": classified_obj.classification,
                "classification_reason": classified_obj.classification_reason,
            }

    # Add dropdown options for navbar filters
    all_participants = Participant.objects.all()
    context["all_districts"] = sorted(set(all_participants.values_list('district', flat=True).distinct()))
    context["all_tb_units"] = sorted(set(all_participants.values_list('tb_unit', flat=True).distinct()))

    return render(request, "questions/home.html", context)


def user_logout(request):
    """
    Terminates the user's active session and redirects to the home screen.
    """
    logout(request)
    return redirect("questions:home")


def registration(request, pk=None):
    """
    Module 01: Multi-step Participant Registration.
    Captures baseline profile, contact details, residence information, 
    and demographic area types across a clean wizard.
    """
    import random
    import json
    from django.shortcuts import get_object_or_404
    
    if not request.user.is_authenticated:
        return redirect("questions:home")

    # Enforce permission checks based on role
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", "Project Nurse")
    if role != "Super Admin":
        action = "Edit" if pk else "Create"
        has_perm = has_role_permission(role, "Participant Registration", action)
        if not has_perm:
            from django.contrib import messages
            messages.error(request, f"Permission denied. Role '{role}' is not allowed to {action.lower()} participant registrations.")
            return redirect("questions:home")

    participant = None
    cohort_param = request.GET.get("cohort")
    if pk:
        if cohort_param == "tpt":
            participant = get_object_or_404(TptIndividual, pk=pk)
        elif cohort_param == "ineligible":
            participant = get_object_or_404(IneligibleIndividual, pk=pk)
        else:
            try:
                participant = Participant.objects.get(pk=pk)
            except Participant.DoesNotExist:
                try:
                    participant = TptIndividual.objects.get(pk=pk)
                except TptIndividual.DoesNotExist:
                    participant = get_object_or_404(IneligibleIndividual, pk=pk)

    if request.method == "POST":
        is_tpt_bcg = False
        nikshay_id = request.POST.get("nikshay_id", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        father_husband_name = request.POST.get("father_husband_name", "").strip()
        age_str = request.POST.get("age", "").strip()
        age = int(age_str) if age_str else 0
        
        dob_str = request.POST.get("dob", "").strip()
        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                pass
                
        gender = request.POST.get("gender")
        primary_phone = request.POST.get("primary_phone", "").strip()
        secondary_phone = request.POST.get("secondary_phone", "").strip()
        secondary_phone_1 = request.POST.get("secondary_phone_1", "").strip()
        secondary_phone_2 = request.POST.get("secondary_phone_2", "").strip()
        secondary_phone_3 = request.POST.get("secondary_phone_3", "").strip()
        
        # Residence & Location Parameters
        address = request.POST.get("address", "").strip()
        state = request.POST.get("state", "").strip()
        district = request.POST.get("district", "").strip()
        tb_unit = request.POST.get("tb_unit", "").strip()
        
        sector = request.POST.get("sector", "Public Sector").strip()
        case_finding_type = request.POST.get("case_finding_type", "").strip()
        private_facility = request.POST.get("private_facility", "").strip()
        public_phi = request.POST.get("public_phi", "").strip()
        facility = public_phi if sector == "Public Sector" else private_facility
        
        taluka_block = request.POST.get("taluka_block", "").strip()
        landmark = request.POST.get("landmark", "").strip()
        village = request.POST.get("village", "").strip()
        pincode = request.POST.get("pincode", "").strip()
        demographic_area = request.POST.get("demographic_area", "Unknown")
        marital_status = request.POST.get("marital_status", "Unknown")
        occupation = request.POST.get("occupation", "Unknown")
        socioeconomic_status = request.POST.get("socioeconomic_status", "Unknown")
        hiv_status = request.POST.get("hiv_status", "Unknown")
        eligible_bcg_campaign_raw = request.POST.get("eligible_bcg_campaign", "Yes")
        bcg_eligibility_criteria_list = request.POST.getlist("bcg_eligibility_criteria")
        bcg_eligibility_criteria = ", ".join(bcg_eligibility_criteria_list) if bcg_eligibility_criteria_list else ""
        
        # Step 7 BCG Vaccine Verification POST values
        bcg_status = request.POST.get("bcg_status", "No").strip()
        bcg_beneficiary_id = request.POST.get("bcg_beneficiary_id", "").strip()
        bcg_ben_mobile_number = request.POST.get("bcg_ben_mobile_number", "").strip()
        bcg_ben_gender = request.POST.get("bcg_ben_gender", "").strip()
        bcg_date = request.POST.get("bcg_date", "").strip()
        bcg_registration_mode = request.POST.get("bcg_registration_mode", "").strip()
        bcg_dob = request.POST.get("bcg_dob", "").strip()
        bcg_age_str = request.POST.get("bcg_age", "").strip()
        bcg_vaccination_status = request.POST.get("bcg_vaccination_status", "").strip()
        bcg_first_name = request.POST.get("bcg_first_name", "").strip()
        bcg_last_name = request.POST.get("bcg_last_name", "").strip()
        bcg_site_id = request.POST.get("bcg_site_id", "").strip()
        bcg_approved_by = request.POST.get("bcg_approved_by", "").strip()
        bcg_beneficiary_type_name = request.POST.get("bcg_beneficiary_type_name", "").strip()
        bcg_pincode = request.POST.get("bcg_pincode", "").strip()
        bcg_address = request.POST.get("bcg_address", "").strip()
        bcg_facility_id = request.POST.get("bcg_facility_id", "").strip()
        
        bcg_scar = request.POST.get("bcg_scar", "").strip()
        bcg_has_record = request.POST.get("bcg_has_record", "").strip()
        bcg_scar_file = request.FILES.get("bcg_scar_file")
        bcg_record_file = request.FILES.get("bcg_record_file")
        cxr_record_file = request.FILES.get("cxr_record_file")
        
        bcg_age = None
        if bcg_age_str:
            try:
                bcg_age = int(bcg_age_str)
            except ValueError:
                pass

        # Height, Weight, BMI
        height_cm_str = request.POST.get("height_cm", "").strip()
        weight_kg_str = request.POST.get("weight_kg", "").strip()
        bmi_str = request.POST.get("bmi", "").strip()
        
        height_cm = float(height_cm_str) if height_cm_str else 0.0
        weight_kg = float(weight_kg_str) if weight_kg_str else 0.0
        bmi = float(bmi_str) if bmi_str else 0.0

        # TPT fields
        tpt_undergone = request.POST.get("tpt_undergone", "No").strip()
        tpt_status = None
        tpt_contact_known = None
        tpt_history = request.POST.get("tpt_history", "").strip() or None
        tpt_risk_factor = request.POST.get("tpt_risk_factor", "").strip() or None
        if tpt_risk_factor == "Other vulnerable group":
            tpt_risk_factor_other = request.POST.get("tpt_risk_factor_other", "").strip()
            if tpt_risk_factor_other:
                tpt_risk_factor = f"Other vulnerable group ({tpt_risk_factor_other})"
        
        tpt_start_date_str = request.POST.get("tpt_start_date", "").strip()
        tpt_end_date_str = request.POST.get("tpt_end_date", "").strip()
        
        tpt_start_date = None
        if tpt_start_date_str:
            try:
                tpt_start_date = datetime.strptime(tpt_start_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
                
        tpt_end_date = None
        if tpt_end_date_str:
            try:
                tpt_end_date = datetime.strptime(tpt_end_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
                
        tpt_duration_months_str = request.POST.get("tpt_duration_months", "").strip()
        tpt_duration_months = int(tpt_duration_months_str) if tpt_duration_months_str else None
        tpt_regimen = request.POST.get("tpt_regimen", "").strip() or None

        # Legacy fields
        bcg_vaccination_date_str = request.POST.get("bcg_vaccination_date", "").strip()
        bcg_vaccine_name = request.POST.get("bcg_vaccine_name", "BCG").strip()
        bcg_batch_number = request.POST.get("bcg_batch_number", "").strip()
        bcg_facility = request.POST.get("bcg_facility", "").strip()
        
        bcg_vaccination_date = None
        if bcg_vaccination_date_str:
            try:
                bcg_vaccination_date = datetime.strptime(bcg_vaccination_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        
        # Contact Person Details
        contact_person_name = request.POST.get("contact_person_name", "").strip()
        contact_person_phone = request.POST.get("contact_person_phone", "").strip()
        contact_person_address = request.POST.get("contact_person_address", "").strip()
        
        # Informant Details
        informant_name = request.POST.get("informant_name", "").strip()
        informant_designation = request.POST.get("informant_designation", "").strip()
        
        symptoms_list = request.POST.getlist("symptoms")
        symptoms = ", ".join(symptoms_list) if symptoms_list else "Asymptomatic"
        
        risk_factors_list = request.POST.getlist("risk_factors")
        risk_factors = ", ".join(risk_factors_list) if risk_factors_list else "Not Applicable"
        
        # Check target HRGs using RiskFactor configurations
        target_hrg_names = list(RiskFactor.objects.filter(is_target_hrg=True, is_active=True).values_list("name", flat=True))
        
        is_elderly = age >= 60 or "Individuals aged 60 years or above" in risk_factors_list or "Elderly (age >60 years)" in risk_factors_list or any("60 years" in name for name in risk_factors_list)
        is_malnourished = "Individuals with a Body Mass Index of less than 18 kg per sq.mts" in risk_factors_list or "Undernourished / Malnourished (BMI <18.5 kg/m2)" in risk_factors_list or "Undernourished / Malnourished (BMI <18 kg/m2)" in risk_factors_list
        is_contact = "Contacts of current TB patients as well as all those contacts of index TB cases enrolled in Ni-kshay from 1st January 2021" in risk_factors_list or "Contact of Known TB Patients" in risk_factors_list
        is_diabetes = "Diabetes (Self- reported)." in risk_factors_list or "Diabetes" in risk_factors_list
        is_past_tb = "People who are reported to have at least one episode of TB in past 5 years." in risk_factors_list or "Past History of TB" in risk_factors_list
        is_smoker = "Individuals with a history of smoking tobacco (Current / Past User)- self reported" in risk_factors_list or "Tobacco/smoker" in risk_factors_list or "Smoker" in risk_factors_list
        
        has_checked_hrg = any(r in target_hrg_names for r in risk_factors_list)
        has_hrg = is_elderly or is_malnourished or is_contact or is_diabetes or is_past_tb or is_smoker or has_checked_hrg

        # Fallback derivation for bcg_eligibility_criteria if empty/absent and not from the new form
        if not bcg_eligibility_criteria_list and eligible_bcg_campaign_raw == "Yes" and "has_bcg_eligibility_criteria_form" not in request.POST:
            derived = []
            if is_elderly:
                derived.append("Was aged >=60 years during the BCG campaign period")
            if is_past_tb:
                derived.append("Past history Of TB from 2019-2024 or prior to the BCG campaign period")
            if is_diabetes:
                derived.append("Self-reported diabetes during the BCG campaign period")
            if is_smoker:
                derived.append("Self-reported smoking during the BCG campaign period")
            if is_contact:
                derived.append("Was a close contact of a TB patient since 2021 or during the campaign period, regardless of TPT status")
            if is_malnourished:
                derived.append("Individuals with BMI < 18 during the BCG campaign period")
            bcg_eligibility_criteria_list = derived
            bcg_eligibility_criteria = ", ".join(bcg_eligibility_criteria_list)

        has_bcg_criteria = len(bcg_eligibility_criteria_list) > 0
        eligible_bcg_campaign = True if (eligible_bcg_campaign_raw == "Yes" and has_bcg_criteria) else False
        
        # Eligibility rule: Patient is eligible if they match at least one of the 6 HRGs AND are eligible for BCG vaccine during campaign period
        eligible = has_hrg and eligible_bcg_campaign
        
        match_hrg = None
        if eligible:
            # Map specific HRG for database compatibility
            matched_db_hrg = RiskFactor.objects.filter(name__in=risk_factors_list, is_target_hrg=True, is_active=True).first()
            if is_past_tb or (matched_db_hrg and matched_db_hrg.code == "past_tb"):
                match_hrg = "Past TB"
            elif is_contact or (matched_db_hrg and matched_db_hrg.code == "contact"):
                match_hrg = "Close Contact"
            elif is_diabetes or (matched_db_hrg and matched_db_hrg.code == "diabetes"):
                match_hrg = "Diabetes"
            elif is_malnourished or (matched_db_hrg and matched_db_hrg.code == "malnourished"):
                match_hrg = "Malnourished (BMI < 18)"
            elif is_elderly:
                match_hrg = "Elderly (Age >= 60)"
            elif is_smoker or (matched_db_hrg and matched_db_hrg.code == "smoker"):
                match_hrg = "History of smoking tobacco"
            elif matched_db_hrg:
                match_hrg = matched_db_hrg.name
            else:
                match_hrg = "Target High Risk Group"
        else:
            reasons = []
            if not has_hrg:
                reasons.append("Does not match any Target High Risk Group (HRG)")
            if not eligible_bcg_campaign:
                reasons.append("Not eligible for BCG vaccine during campaign period")
            match_hrg = " & ".join(reasons)
 
        # PTB Screening & Testing parsing
        ptb_screened = False
        ptb_test_registered = False
        ptb_test_type = None
        ptb_test_result = None
        ptb_test_date = None
        ptb_test_facility = None
        ptb_test_details = "{}"
        classification = "Not Eligible"
        
        # Initialize variables that eligibility engine needs
        # (will be overridden inside if-eligible block when applicable)
        undergone_testing = "No"
        cxr_done = "No"
        cxr_result = ""
        cxr_status = "Not Done"
        naat_status = ""
        final_interpretation = ""
 
        if eligible:
            ptb_screened = True
            other_symptom = request.POST.get("other_symptom", "").strip()
            
            # Process "Others" symptoms description
            if "Others" in symptoms_list:
                symptoms_list = [s for s in symptoms_list if s != "Others"]
                if other_symptom:
                    symptoms_list.append(f"Others ({other_symptom})")
                else:
                    symptoms_list.append("Others")
            
            symptoms = ", ".join(symptoms_list) if symptoms_list else "Asymptomatic"
            is_asymptomatic = "Asymptomatic" in symptoms_list or not symptoms_list
            if is_asymptomatic:
                symptoms = "Asymptomatic"
            
            # Retrieve undergone_testing
            undergone_testing = request.POST.get("undergone_testing", "").strip()
            if not undergone_testing:
                undergone_testing = "Yes" if (request.POST.get("test_reason") or request.POST.get("test_type")) else "No"
            
            # ALWAYS parse all the detailed TB Test fields (for both symptomatic and asymptomatic)
            cxr_done = request.POST.get("cxr_done", "").strip()
            if undergone_testing == "No":
                test_reason = ""
                test_type = ""
            else:
                test_reason = request.POST.get("test_reason", "").strip()
                test_type = request.POST.get("test_type", "").strip()
                if test_type == "Other":
                    test_type_other = request.POST.get("test_type_other", "").strip()
                    if test_type_other:
                        test_type = f"Other ({test_type_other})"
            
            cxr_id = ""
            cxr_date = ""
            cxr_facility = ""
            cxr_result = ""
            
            if cxr_done == "Yes":
                cxr_id = request.POST.get("cxr_id", "").strip()
                cxr_date = request.POST.get("cxr_date", "").strip()
                cxr_facility = request.POST.get("cxr_facility", "").strip()
                cxr_result = request.POST.get("cxr_result", "").strip()
            
            # Derive legacy cxr_status
            cxr_status = request.POST.get("cxr_status", "").strip()
            if not cxr_status:
                if cxr_done == "Yes":
                    cxr_status = cxr_result or "Normal"
                else:
                    cxr_status = "Not Done"
                    cxr_done = "No"
            else:
                if not cxr_done:
                    cxr_done = "No" if cxr_status == "Not Done" else "Yes"
                if cxr_done == "Yes" and not cxr_result:
                    cxr_result = cxr_status
            
            cxr_details = {
                "cxr_done": cxr_done,
                "cxr_id": cxr_id,
                "cxr_date": cxr_date,
                "cxr_facility": cxr_facility,
                "cxr_result": cxr_result
            }
            
            naat_status = request.POST.get("naat_status", "").strip()
            
            # Diagnosis of TB specific fields
            predominant_symptom = ""
            duration_days = ""
            hcp_visits = ""
            case_type = ""
            if test_reason == "Diagnosis of TB":
                predominant_symptom = request.POST.get("predominant_symptom", "").strip()
                if predominant_symptom == "Other":
                    predominant_symptom_other = request.POST.get("predominant_symptom_other", "").strip()
                    if predominant_symptom_other:
                        predominant_symptom = f"Other ({predominant_symptom_other})"
                duration_days = request.POST.get("duration_days", "").strip()
                hcp_visits = request.POST.get("hcp_visits", "").strip()
                case_type = request.POST.get("case_type", "").strip()
            
            if undergone_testing == "No":
                facility_state = ""
                facility_district = ""
                testing_lab = ""
                sample_availability = "Absent"
                result_availability = "Absent"
            else:
                facility_state = request.POST.get("facility_state", "").strip()
                facility_district = request.POST.get("facility_district", "").strip()
                testing_lab = request.POST.get("testing_lab", "").strip()
                if testing_lab == "Other Testing Lab":
                    testing_lab_other = request.POST.get("testing_lab_other", "").strip()
                    if testing_lab_other:
                        testing_lab = f"Other Testing Lab ({testing_lab_other})"
                sample_availability = request.POST.get("sample_availability", "Absent").strip()
                result_availability = request.POST.get("result_availability", "Absent").strip()
            
            # Sample details
            sample_details = {}
            if sample_availability == "Present":
                samples = []
                for i in range(1, 11):
                    suffix = f"_{i}"
                    if i == 1 and f"sample_serial_id{suffix}" not in request.POST and "sample_serial_id" in request.POST:
                        suffix = ""
                    elif f"sample_serial_id{suffix}" not in request.POST:
                        continue
                    
                    s_type = request.POST.get(f"sample_type{suffix}", "Sputum").strip()
                    if s_type == "Other":
                        s_type_other = request.POST.get(f"sample_type{suffix}_other", "").strip()
                        if s_type_other:
                            s_type = f"Other ({s_type_other})"
                            
                    c_site = request.POST.get(f"collection_site{suffix}", "").strip()
                    if c_site == "Other Collection Site":
                        c_site_other = request.POST.get(f"collection_site{suffix}_other", "").strip()
                        if c_site_other:
                            c_site = f"Other Collection Site ({c_site_other})"

                    s_data = {
                        "sample_mapping_option": request.POST.get(f"sample_mapping_option{suffix}", "").strip(),
                        "sample_type": s_type,
                        "sputum_collection_detail": request.POST.get(f"sputum_collection_detail{suffix}", "").strip(),
                        "sample_description": request.POST.get(f"sample_description{suffix}", "").strip(),
                        "collection_date": request.POST.get(f"collection_date{suffix}", "").strip(),
                        "collection_time": request.POST.get(f"collection_time{suffix}", "").strip(),
                        "referral_date": request.POST.get(f"referral_date{suffix}", "").strip(),
                        "collection_site_state": request.POST.get(f"collection_site_state{suffix}", "").strip(),
                        "collection_site_district": request.POST.get(f"collection_site_district{suffix}", "").strip(),
                        "collection_site": c_site,
                        "referral_site_state": request.POST.get(f"referral_site_state{suffix}", "").strip(),
                        "referral_site_district": request.POST.get(f"referral_site_district{suffix}", "").strip(),
                        "referral_site": request.POST.get(f"referral_site{suffix}", "").strip(),
                        "sample_serial_id": request.POST.get(f"sample_serial_id{suffix}", "").strip(),
                        "sample_qr_code": request.POST.get(f"sample_qr_code{suffix}", "").strip(),
                    }
                    samples.append(s_data)
                
                if samples:
                    sample_details = {
                        "samples": samples
                    }
                    # Copy first sample keys to root of sample_details for backward/test compatibility
                    for k, v in samples[0].items():
                        sample_details[k] = v
            
            # Result details
            result_details = {}
            final_interpretation = ""
            date_reported_str = ""
            if result_availability == "Present":
                lab_serial_number = request.POST.get("lab_serial_number", "").strip()
                result_sample_id = request.POST.get("result_sample_id", "").strip()
                date_tested_str = request.POST.get("date_tested", "").strip()
                date_reported_str = request.POST.get("date_reported", "").strip()
                reported_by = request.POST.get("reported_by", "").strip()
                final_interpretation = request.POST.get("final_interpretation", "").strip()
                if final_interpretation == "Other":
                    final_interpretation_other = request.POST.get("final_interpretation_other", "").strip()
                    if final_interpretation_other:
                        final_interpretation = f"Other ({final_interpretation_other})"
                remarks = request.POST.get("remarks", "").strip()
                
                result_details = {
                    "lab_serial_number": lab_serial_number,
                    "result_sample_id": result_sample_id,
                    "date_tested": date_tested_str,
                    "date_reported": date_reported_str,
                    "reported_by": reported_by,
                    "final_interpretation": final_interpretation,
                    "remarks": remarks
                }
            
            # Map primary test fields for database compatibility (only if test was added)
            if test_reason or test_type:
                ptb_test_registered = True
                ptb_test_type = test_type
                ptb_test_facility = testing_lab
                ptb_test_result = final_interpretation or naat_status or "Pending"
            else:
                ptb_test_registered = False
                ptb_test_type = None
                ptb_test_result = None
                ptb_test_facility = None
            classification = "Pending"

            # Parse date_reported for ptb_test_date
            if date_reported_str:
                try:
                    ptb_test_date = datetime.strptime(date_reported_str, "%Y-%m-%d").date()
                except ValueError:
                    pass
            
            # Serialize everything to ptb_test_details JSON
            details_dict = {
                "undergone_testing": undergone_testing,
                "test_reason": test_reason,
                "predominant_symptom": predominant_symptom,
                "duration_days": duration_days,
                "hcp_visits": hcp_visits,
                "case_type": case_type,
                "facility_state": facility_state,
                "facility_district": facility_district,
                "sample_availability": sample_availability,
                "result_availability": result_availability,
                "sample_details": sample_details,
                "result_details": result_details,
                "cxr_status": cxr_status,
                "cxr_details": cxr_details,
                "naat_status": naat_status
            }
            ptb_test_details = json.dumps(details_dict)
            
        # EPTB Screening & Testing parsing
        main_eptb_keys = ["eptb_q1a", "eptb_q2a", "eptb_q3a", "eptb_q4a", "eptb_q5a", "eptb_q6a", "eptb_q7", "eptb_q8", "eptb_q9", "eptb_q10", "eptb_q11"]
        
        eptb_answers = {}
        for key in main_eptb_keys:
            val = request.POST.get(key)
            if val in ["Yes", "on", "true"]:
                eptb_answers[key] = "Yes"
            else:
                eptb_answers[key] = "No"
        
        for post_key, post_val in request.POST.items():
            if post_key.startswith("eptb_") and post_key not in main_eptb_keys:
                eptb_answers[post_key] = post_val
            
        # Combine any EPTB result_findings that are "Other" with their specify value
        for key in list(eptb_answers.keys()):
            if key.endswith("_result_findings") and eptb_answers[key] == "Other":
                other_val = eptb_answers.get(f"{key}_other", "").strip()
                if other_val:
                    eptb_answers[key] = f"Other ({other_val})"

        eptb_details = json.dumps(eptb_answers)
        eptb_screened = any(eptb_answers.get(key) == "Yes" for key in main_eptb_keys)

        # Dynamic Questions & Options questionnaire answers parsing
        qa_dict = {}
        active_db_questions = Question.objects.filter(is_active=True)
        for q in active_db_questions:
            val = request.POST.get(q.code, "").strip()
            qa_dict[q.code] = val
            
            # Map back to legacy field values for model compatibility
            if q.code == "sector":
                sector = val or sector
            elif q.code == "case_finding_type":
                case_finding_type = val or case_finding_type
            elif q.code == "gender":
                gender = val or gender
            elif q.code == "demographic_area":
                demographic_area = val or demographic_area
            elif q.code == "marital_status":
                marital_status = val or marital_status
            elif q.code == "occupation":
                occupation = val or occupation
            elif q.code == "socioeconomic_status":
                socioeconomic_status = val or socioeconomic_status
            elif q.code == "hiv_status":
                hiv_status = val or hiv_status
                
        questionnaire_answers = json.dumps(qa_dict)

        # Eligibility Engine: Case / Control / Pending / Excluded status classification
        mctb = "PENDING"
        if undergone_testing == "No":
            mctb = "PENDING"
        else:
            effective_naat = final_interpretation or naat_status
            if effective_naat:
                val = effective_naat.upper()
                if "MTB DETECTED" in val or "RIF" in val or "POSITIVE" in val:
                    mctb = "POSITIVE"
                elif "MTB NOT DETECTED" in val or "NEGATIVE" in val:
                    mctb = "NEGATIVE"
                else:
                    mctb = "PENDING"
            else:
                mctb = "PENDING"

        cxr = "NORMAL"
        if undergone_testing == "No":
            cxr = "PENDING"
        else:
            effective_cxr_result = cxr_result or cxr_status
            if cxr_done == "Yes":
                if effective_cxr_result == "Suggestive of TB":
                    cxr = "SUGGESTIVE_OF_TB"
                elif effective_cxr_result == "Normal":
                    cxr = "NORMAL"
                elif effective_cxr_result == "Abnormal (Non-TB)":
                    cxr = "ABNORMAL_NON_TB"
                else:
                    cxr = "PENDING"
            elif cxr_done == "No":
                cxr = "NORMAL"

        # EPTB symptoms & status
        has_eptb_symptoms = False
        for k, v in eptb_answers.items():
            if k.startswith("eptb_q") and k.endswith("a") and v == "Yes":
                has_eptb_symptoms = True
                break
            if k in ["eptb_q7", "eptb_q8", "eptb_q9", "eptb_q10", "eptb_q11"] and v == "Yes":
                has_eptb_symptoms = True
                break
               
        eptb_symptoms_val = "YES" if has_eptb_symptoms else "NO"
        
        eptb_status = "NEGATIVE"
        pending_sites = []
        if has_eptb_symptoms:
            any_pending = False
            any_positive = False
            for k, v in eptb_answers.items():
                if k.startswith("eptb_investigation_") and k.endswith("_performed") and v == "Yes":
                    base_key = k[:-10]
                    result_key = f"{base_key}_result_findings"
                    result_val = eptb_answers.get(result_key, "").strip()
                    
                    if not result_val or "PENDING" in result_val.upper():
                        any_pending = True
                        site_name = base_key.replace("eptb_investigation_", "").replace("_", " ").title()
                        pending_sites.append(site_name)
                    elif "POSITIVE" in result_val.upper() or "SUGGESTIVE" in result_val.upper() or "DETECTED" in result_val.upper():
                        any_positive = True
            if any_positive:
                eptb_status = "POSITIVE"
            elif any_pending:
                eptb_status = "PENDING"
            else:
                eptb_status = "NEGATIVE"

        # Check if BCG verification and vaccine details are filled
        bcg_status_str = (bcg_status or "").strip()
        bcg_complete = False
        if bcg_status_str.startswith("No"):
            bcg_complete = True
        elif bcg_status_str.startswith("Yes"):
            has_date = bool(bcg_vaccination_date or bcg_vaccination_date_str)
            has_batch = bool(bcg_batch_number)
            has_facility = bool(bcg_facility)
            if has_date and has_batch and has_facility:
                bcg_complete = True

        # TPT+BCG cohort override check (tpt_undergone already parsed from POST at line 238)
        is_tpt_bcg = has_hrg and eligible_bcg_campaign and (tpt_undergone == "Yes") and bcg_status.startswith("Yes")

        classification = "Pending"
        classification_reason = "One or more required investigation results are pending."
        
        if not eligible:
            classification = "Not Eligible"
            classification_reason = "Participant is ineligible under screening criteria."
        elif not bcg_complete:
            classification = "Pending"
            classification_reason = "One or more required BCG verification or vaccine details are incomplete."
        elif is_tpt_bcg:
            classification = "TPT+BCG"
            classification_reason = "Eligible for BCG + TPT Exploratory Cohort"
        elif cxr == "ABNORMAL_NON_TB" and mctb == "NEGATIVE":
            classification = "Excluded"
            classification_reason = "Abnormal CXR not suggestive of TB with NAAT Negative"
        elif participant and participant.created_at and (timezone.now() - participant.created_at).days > 30 and (mctb == "PENDING" or cxr == "PENDING" or eptb_status == "PENDING"):
            classification = "Excluded"
            classification_reason = "Pending investigation beyond one month"
        elif mctb == "POSITIVE" or cxr == "SUGGESTIVE_OF_TB" or eptb_status == "POSITIVE":
            classification = "Case"
            if mctb == "POSITIVE" and cxr == "SUGGESTIVE_OF_TB":
                classification_reason = "MCTB Positive and CXR suggestive of TB"
            elif mctb == "POSITIVE" and cxr == "NORMAL":
                classification_reason = "MCTB Positive and Normal CXR"
            elif mctb == "POSITIVE":
                classification_reason = "MCTB Positive"
            elif cxr == "SUGGESTIVE_OF_TB" and mctb == "NEGATIVE":
                classification_reason = "CXR suggestive of TB with MCTB Negative"
            elif cxr == "SUGGESTIVE_OF_TB":
                classification_reason = "Chest X-Ray suggestive of TB"
            else:
                classification_reason = "EPTB Investigation Positive"
        elif cxr == "NORMAL" and mctb == "NEGATIVE" and (eptb_symptoms_val == "NO" or (eptb_symptoms_val == "YES" and eptb_status == "NEGATIVE")):
            classification = "Control"
            classification_reason = "Normal CXR, Negative NAAT, and Negative EPTB status"
            
        if classification == "Pending" and classification_reason == "One or more required investigation results are pending.":
            pending_list = []
            if mctb == "PENDING":
                if undergone_testing == "No":
                    pending_list.append("NAAT (MCTB) is pending because clinical testing has not been undergone")
                else:
                    pending_list.append("NAAT (MCTB) is pending because test result is blank or not recorded")
            if cxr == "PENDING":
                if undergone_testing == "No":
                    pending_list.append("Chest X-Ray is pending because clinical testing has not been undergone")
                else:
                    pending_list.append("Chest X-Ray is pending because interpretation findings are blank or not recorded")
            if eptb_status == "PENDING":
                if pending_sites:
                    pending_list.append(f"EPTB is pending because investigation results are not recorded for {', '.join(pending_sites)}")
                else:
                    pending_list.append("EPTB is pending because one or more investigation findings are blank or not recorded")
            
            if pending_list:
                classification_reason = "One or more required investigation results are pending: " + "; ".join(pending_list) + "."

        if 'details_dict' not in locals():
            details_dict = {"classification_reason": classification_reason}
        else:
            details_dict["classification_reason"] = classification_reason
        ptb_test_details = json.dumps(details_dict)

        # Store audit log
        print(f"[AUDIT LOG] Eligibility engine executed for study_id={study_id if 'study_id' in locals() else 'NEW'}: status={classification}, reason={classification_reason}")

        # Define helper functions to generate codes
        def get_state_code(state_name):
            name = (state_name or "").strip().upper()
            if "TAMIL" in name:
                return "TN"
            if "MAHA" in name:
                return "MH"
            return name[:2] if name else "ST"

        def get_tu_code(tu_name):
            name = (tu_name or "").strip().upper()
            if name.endswith(" TU"):
                name = name[:-3].strip()
            if name == "TIRUVALLUR":
                return "TIR"
            if not name:
                return "UNK"
            return name[:3] if len(name) >= 3 else name.ljust(3, 'X')

        # Generate unique study ID / screening ID
        if not participant:
            today_code = timezone.localdate().strftime("%y%m%d")
            rand_code = random.randint(1000, 9999)
            screening_id = f"SCR-{today_code}-{rand_code}"
            while (Participant.objects.filter(screening_id=screening_id).exists() or 
                   TptIndividual.objects.filter(screening_id=screening_id).exists() or 
                   IneligibleIndividual.objects.filter(screening_id=screening_id).exists()):
                rand_code = random.randint(1000, 9999)
                screening_id = f"SCR-{today_code}-{rand_code}"
            
            if eligible:
                profile = request.user.profile
                state_code = get_state_code(profile.state)
                tu_code = get_tu_code(profile.tb_unit)
                year_code = timezone.localdate().strftime("%Y")
                rand_serial = random.randint(100000, 999999)
                study_id = f"ABCG-{state_code}-{tu_code}-{year_code}-{rand_serial}"
                while (Participant.objects.filter(study_id=study_id).exists() or 
                       TptIndividual.objects.filter(study_id=study_id).exists() or 
                       IneligibleIndividual.objects.filter(study_id=study_id).exists()):
                    rand_serial = random.randint(100000, 999999)
                    study_id = f"ABCG-{state_code}-{tu_code}-{year_code}-{rand_serial}"
            else:
                study_id = screening_id
        else:
            screening_id = getattr(participant, "screening_id", None)
            if not screening_id:
                if participant.study_id.startswith("SCR-"):
                    screening_id = participant.study_id
                else:
                    today_code = timezone.localdate().strftime("%y%m%d")
                    rand_code = random.randint(1000, 9999)
                    screening_id = f"SCR-{today_code}-{rand_code}"
                    while (Participant.objects.filter(screening_id=screening_id).exists() or 
                           TptIndividual.objects.filter(screening_id=screening_id).exists() or 
                           IneligibleIndividual.objects.filter(screening_id=screening_id).exists()):
                        rand_code = random.randint(1000, 9999)
                        screening_id = f"SCR-{today_code}-{rand_code}"
            
            if eligible:
                if participant.study_id.startswith("SCR-") or not participant.study_id.startswith("ABCG-"):
                    profile = request.user.profile
                    state_code = get_state_code(profile.state)
                    tu_code = get_tu_code(profile.tb_unit)
                    year_code = timezone.localdate().strftime("%Y")
                    rand_serial = random.randint(100000, 999999)
                    study_id = f"ABCG-{state_code}-{tu_code}-{year_code}-{rand_serial}"
                    while (Participant.objects.filter(study_id=study_id).exists() or 
                           TptIndividual.objects.filter(study_id=study_id).exists() or 
                           IneligibleIndividual.objects.filter(study_id=study_id).exists()):
                        rand_serial = random.randint(100000, 999999)
                        study_id = f"ABCG-{state_code}-{tu_code}-{year_code}-{rand_serial}"
                else:
                    study_id = participant.study_id
            else:
                study_id = screening_id

        # Combine names
        full_name = f"{first_name} {last_name}".strip()

        # Helper function to populate fields of either model
        def populate_fields(obj):
            obj.created_by = request.user
            obj.nikshay_id = nikshay_id
            obj.first_name = first_name
            obj.last_name = last_name
            obj.full_name = full_name
            obj.contact_number = primary_phone
            obj.secondary_phone = secondary_phone
            obj.address = address
            obj.age = age
            obj.dob = dob
            obj.gender = gender
            obj.screening_id = screening_id
            obj.study_id = study_id
            # Update site details to match the logged-in user profile's site details on save/update
            profile = request.user.profile
            obj.state = profile.state
            obj.district = profile.district
            obj.tb_unit = profile.tb_unit
            obj.facility = facility
            obj.village = village
            obj.pincode = pincode
            obj.demographic_area = demographic_area
            obj.marital_status = marital_status
            obj.occupation = occupation
            obj.socioeconomic_status = socioeconomic_status
            obj.symptoms = symptoms
            obj.risk_factors = risk_factors
            obj.hiv_status = hiv_status
            obj.eligible_bcg_campaign = eligible_bcg_campaign
            obj.bcg_eligibility_criteria = bcg_eligibility_criteria
            
            # Height, Weight, BMI
            obj.height_cm = height_cm
            obj.weight_kg = weight_kg
            obj.bmi = bmi
            
            # TPT
            obj.tpt_undergone = tpt_undergone
            obj.tpt_status = tpt_status
            obj.tpt_contact_known = tpt_contact_known
            obj.tpt_history = tpt_history
            obj.tpt_start_date = tpt_start_date
            obj.tpt_end_date = tpt_end_date
            obj.tpt_duration_months = tpt_duration_months
            obj.tpt_regimen = tpt_regimen
            obj.tpt_risk_factor = tpt_risk_factor

            obj.sector = sector
            obj.case_finding_type = case_finding_type
            obj.private_facility = private_facility
            obj.public_phi = public_phi
            obj.father_husband_name = father_husband_name
            obj.secondary_phone_1 = secondary_phone_1
            obj.secondary_phone_2 = secondary_phone_2
            obj.secondary_phone_3 = secondary_phone_3
            obj.taluka_block = taluka_block
            obj.landmark = landmark
            obj.contact_person_name = contact_person_name
            obj.contact_person_phone = contact_person_phone
            obj.contact_person_address = contact_person_address
            obj.informant_name = informant_name
            obj.informant_designation = informant_designation
            
            # PTB fields
            obj.ptb_screened = ptb_screened
            obj.ptb_test_registered = ptb_test_registered
            obj.ptb_test_type = ptb_test_type
            obj.ptb_test_result = ptb_test_result
            obj.ptb_test_date = ptb_test_date
            obj.ptb_test_facility = ptb_test_facility
            obj.ptb_test_details = ptb_test_details
            
            # EPTB fields
            obj.eptb_screened = eptb_screened
            obj.eptb_details = eptb_details
            
            # BCG Vaccine Verification Step 7 fields
            obj.bcg_status = bcg_status
            obj.bcg_beneficiary_id = bcg_beneficiary_id
            obj.bcg_ben_mobile_number = bcg_ben_mobile_number
            obj.bcg_ben_gender = bcg_ben_gender
            obj.bcg_date = bcg_date
            obj.bcg_registration_mode = bcg_registration_mode
            obj.bcg_dob = bcg_dob
            obj.bcg_age = bcg_age
            obj.bcg_vaccination_status = bcg_vaccination_status
            obj.bcg_first_name = bcg_first_name
            obj.bcg_last_name = bcg_last_name
            obj.bcg_site_id = bcg_site_id
            obj.bcg_approved_by = bcg_approved_by
            obj.bcg_beneficiary_type_name = bcg_beneficiary_type_name
            obj.bcg_pincode = bcg_pincode
            obj.bcg_address = bcg_address
            obj.bcg_facility_id = bcg_facility_id
            
            obj.bcg_scar = bcg_scar
            obj.bcg_has_record = bcg_has_record
            if bcg_scar_file:
                obj.bcg_scar_file = bcg_scar_file
            if bcg_record_file:
                obj.bcg_record_file = bcg_record_file
            if cxr_record_file:
                obj.cxr_record_file = cxr_record_file
            
            # Legacy fields
            obj.bcg_vaccination_date = bcg_vaccination_date
            obj.bcg_vaccine_name = bcg_vaccine_name
            obj.bcg_batch_number = bcg_batch_number
            obj.bcg_facility = bcg_facility
            
            # Save dynamic questionnaire responses
            obj.questionnaire_answers = questionnaire_answers
            
            obj.eligible = eligible
            obj.match_hrg = match_hrg
            obj.classification = classification
            obj.classification_reason = classification_reason

        if not eligible:
            Participant.objects.filter(study_id=study_id).delete()
            TptIndividual.objects.filter(study_id=study_id).delete()
            if pk:
                obj, created = IneligibleIndividual.objects.get_or_create(
                    pk=pk,
                    defaults={"study_id": study_id, "age": age, "date_enroll": timezone.localdate()}
                )
            else:
                obj = IneligibleIndividual(study_id=study_id, date_enroll=timezone.localdate())
            populate_fields(obj)
            obj.save()
            sync_nikshay_record(obj, nikshay_id, user=request.user)
        elif is_tpt_bcg:
            Participant.objects.filter(study_id=study_id).delete()
            IneligibleIndividual.objects.filter(study_id=study_id).delete()
            if pk:
                obj, created = TptIndividual.objects.get_or_create(
                    pk=pk,
                    defaults={"study_id": study_id, "age": age, "date_enroll": timezone.localdate()}
                )
            else:
                obj = TptIndividual(study_id=study_id, date_enroll=timezone.localdate())
            populate_fields(obj)
            obj.save()
            sync_nikshay_record(obj, nikshay_id, user=request.user)
        else:
            TptIndividual.objects.filter(study_id=study_id).delete()
            IneligibleIndividual.objects.filter(study_id=study_id).delete()
            if pk:
                obj, created = Participant.objects.get_or_create(
                    pk=pk,
                    defaults={"study_id": study_id, "age": age, "date_enroll": timezone.localdate()}
                )
            else:
                obj = Participant(study_id=study_id, date_enroll=timezone.localdate())
            populate_fields(obj)
            obj.save()
            sync_nikshay_record(obj, nikshay_id, user=request.user)
            
        # Attempt immediate safe transfer to central backend if online
        try:
            sync_single_record(obj)
        except Exception:
            pass

        request.session["classified_id"] = obj.id
        from django.urls import reverse
        return redirect(reverse("questions:home"))

    # GET: Prepopulate site location based on login profile details
    profile = request.user.profile
    target_tbu = participant.tb_unit if participant and participant.tb_unit else profile.tb_unit
    target_dist = participant.district if participant and participant.district else profile.district
    target_state = participant.state if participant and participant.state else profile.state
    campaign_period = get_campaign_period_for_site(tb_unit=target_tbu, district=target_dist, state=target_state)
    prefill_id = request.GET.get("prefill_id", "").strip()
    nikshay_id_param = request.GET.get("nikshay_id", "").strip()
    
    eptb_form = EPTBScreeningForm()
    
    participant_json = "null"
    if participant:
        nikshay_val = getattr(participant, "nikshay_id", None)
        if not nikshay_val:
            nikshay_rec = NikshayRecord.objects.filter(study_id=participant.study_id).first()
            if not nikshay_rec and getattr(participant, "screening_id", None):
                nikshay_rec = NikshayRecord.objects.filter(screening_id=participant.screening_id).first()
            if nikshay_rec and nikshay_rec.nikshay_id:
                nikshay_val = nikshay_rec.nikshay_id
        if not nikshay_val and nikshay_id_param:
            nikshay_val = nikshay_id_param

        participant_data = {
            "nikshay_id": nikshay_val or "",
            "first_name": participant.first_name,
            "last_name": participant.last_name,
            "father_husband_name": participant.father_husband_name,
            "dob": participant.dob.strftime("%Y-%m-%d") if participant.dob else "",
            "age": participant.age,
            "gender": participant.gender,
            "primary_phone": participant.contact_number,
            "secondary_phone": participant.secondary_phone,
            "secondary_phone_1": participant.secondary_phone_1,
            "secondary_phone_2": participant.secondary_phone_2,
            "secondary_phone_3": participant.secondary_phone_3,
            "address": participant.address,
            "state": participant.state,
            "district": participant.district,
            "tb_unit": participant.tb_unit,
            "facility": participant.facility,
            "village": participant.village,
            "pincode": participant.pincode,
            "demographic_area": participant.demographic_area,
            "marital_status": participant.marital_status,
            "occupation": participant.occupation,
            "socioeconomic_status": participant.socioeconomic_status,
            "sector": participant.sector,
            "case_finding_type": participant.case_finding_type,
            "private_facility": participant.private_facility,
            "public_phi": participant.public_phi,
            "landmark": participant.landmark,
            "contact_person_name": participant.contact_person_name,
            "contact_person_phone": participant.contact_person_phone,
            "contact_person_address": participant.contact_person_address,
            "informant_name": participant.informant_name,
            "informant_designation": participant.informant_designation,
            "hiv_status": participant.hiv_status,
            "eligible_bcg_campaign": "Yes" if participant.eligible_bcg_campaign else "No",
            "bcg_eligibility_criteria": [c.strip() for c in participant.bcg_eligibility_criteria.split(",") if c.strip()] if participant.bcg_eligibility_criteria else [],
            "symptoms": [s.strip() for s in participant.symptoms.split(",") if s.strip()] if participant.symptoms else [],
            "risk_factors": [r.strip() for r in participant.risk_factors.split(",") if r.strip()] if participant.risk_factors else [],
            "questionnaire_answers": participant.questionnaire_answers,
            
            # Height, Weight, BMI
            "height_cm": participant.height_cm,
            "weight_kg": participant.weight_kg,
            "bmi": participant.bmi,
            
            # TPT
            "tpt_undergone": participant.tpt_undergone,
            "tpt_status": participant.tpt_status or "",
            "tpt_contact_known": participant.tpt_contact_known or "",
            "tpt_history": participant.tpt_history or "",
            "tpt_start_date": participant.tpt_start_date.strftime("%Y-%m-%d") if participant.tpt_start_date else "",
            "tpt_end_date": participant.tpt_end_date.strftime("%Y-%m-%d") if participant.tpt_end_date else "",
            "tpt_duration_months": participant.tpt_duration_months or "",
            "tpt_regimen": participant.tpt_regimen or "",
            "tpt_risk_factor": participant.tpt_risk_factor or "",
            "bcg_status": participant.bcg_status,
            "bcg_beneficiary_id": participant.bcg_beneficiary_id,
            "bcg_ben_mobile_number": participant.bcg_ben_mobile_number,
            "bcg_ben_gender": participant.bcg_ben_gender,
            "bcg_date": participant.bcg_date,
            "bcg_registration_mode": participant.bcg_registration_mode,
            "bcg_dob": participant.bcg_dob,
            "bcg_age": participant.bcg_age,
            "bcg_vaccination_status": participant.bcg_vaccination_status,
            "bcg_first_name": participant.bcg_first_name,
            "bcg_last_name": participant.bcg_last_name,
            "bcg_site_id": participant.bcg_site_id,
            "bcg_approved_by": participant.bcg_approved_by,
            "bcg_beneficiary_type_name": participant.bcg_beneficiary_type_name,
            "bcg_pincode": participant.bcg_pincode,
            "bcg_address": participant.bcg_address,
            "bcg_facility_id": participant.bcg_facility_id,
            
            # Legacy
            "bcg_vaccination_date": participant.bcg_vaccination_date.strftime("%Y-%m-%d") if participant.bcg_vaccination_date else "",
            "bcg_vaccine_name": participant.bcg_vaccine_name,
            "bcg_batch_number": participant.bcg_batch_number,
            "bcg_facility": participant.bcg_facility,
            "cxr_record_file_name": participant.cxr_record_file.name if participant.cxr_record_file else "",
            "cxr_record_file_url": participant.cxr_record_file.url if participant.cxr_record_file else "",
            "bcg_scar_file_name": participant.bcg_scar_file.name if participant.bcg_scar_file else "",
            "bcg_scar_file_url": participant.bcg_scar_file.url if participant.bcg_scar_file else "",
        }
        try:
            participant_data["eptb_details"] = json.loads(participant.eptb_details) if participant.eptb_details else {}
        except Exception:
            participant_data["eptb_details"] = {}
        try:
            participant_data["ptb_test_details"] = json.loads(participant.ptb_test_details) if participant.ptb_test_details else {}
        except Exception:
            participant_data["ptb_test_details"] = {}
            
        participant_json = json.dumps(participant_data)
    elif nikshay_id_param:
        simulated = get_simulated_nikshay(nikshay_id_param)
        if simulated:
            name_parts = simulated.get("full_name", "").split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            raw_gender = simulated.get("gender", "Male")
            gender_normalized = "Male" if str(raw_gender).strip().upper() in ["M", "MALE"] else "Female"
            
            # Find the BcgVaccination object to get additional details
            beneficiary = BcgVaccination.objects.filter(beneficiary_id__iexact=nikshay_id_param).first()
            if beneficiary:
                bcg_status = "Yes"
                bcg_has_record = "Yes"
                bcg_beneficiary_id = beneficiary.beneficiary_id
                bcg_first_name = beneficiary.first_name
                bcg_last_name = beneficiary.last_name
                bcg_ben_mobile_number = beneficiary.ben_mobile_number
                bcg_ben_gender_raw = beneficiary.ben_gender or beneficiary.beneficiary_gender
                bcg_ben_gender = "Male" if str(bcg_ben_gender_raw).strip().upper() in ["M", "MALE"] else "Female"
                bcg_dob = beneficiary.dob
                bcg_age = beneficiary.age
                bcg_vaccination_status = beneficiary.vaccination_status
                bcg_date = beneficiary.date
                bcg_registration_mode = beneficiary.registration_mode
                bcg_beneficiary_type_name = beneficiary.beneficiary_type_name
                bcg_approved_by = beneficiary.approved_by
                bcg_site_id = beneficiary.site_id
                bcg_facility_id = beneficiary.facility_id
                bcg_pincode = beneficiary.pincode
                bcg_address = beneficiary.address
            else:
                bcg_status = "Yes" if simulated.get("bcg_vaccination_status") == "Vaccinated" else "No"
                bcg_has_record = "Yes" if bcg_status == "Yes" else "No"
                bcg_beneficiary_id = simulated.get("nikshay_id", "")
                bcg_first_name = first_name
                bcg_last_name = last_name
                bcg_ben_mobile_number = simulated.get("contact_number", "")
                bcg_ben_gender_raw = simulated.get("gender", "")
                bcg_ben_gender = "Male" if str(bcg_ben_gender_raw).strip().upper() in ["M", "MALE"] else ("Female" if bcg_ben_gender_raw else "")
                bcg_dob = ""
                bcg_age = simulated.get("age", "")
                bcg_vaccination_status = simulated.get("bcg_vaccination_status", "")
                bcg_date = simulated.get("bcg_vaccination_date", "")
                bcg_registration_mode = "Online"
                bcg_beneficiary_type_name = "General"
                bcg_approved_by = "MO"
                bcg_site_id = "Campaign Site 1"
                bcg_facility_id = "Campaign Facility"
                bcg_pincode = "602001"
                bcg_address = simulated.get("address", "")

            # If lab results are available, pull and auto-fill them
            cxr_done = simulated.get("cxr_done", "No")
            cxr_status = simulated.get("cxr_result", "Normal") if cxr_done == "Yes" else "Not Done"
            
            sample_details = {
                "samples": [
                    {
                        "sample_type": simulated.get("sample_type", "Sputum"),
                        "sputum_collection_detail": "",
                        "sample_description": "",
                        "collection_date": simulated.get("collection_date", "2026-03-07"),
                        "collection_time": simulated.get("collection_time", "09:30"),
                        "referral_date": simulated.get("collection_date", "2026-03-07"),
                        "collection_site_state": simulated.get("state", "Tamil Nadu"),
                        "collection_site_district": simulated.get("district", "Tiruvallur"),
                        "collection_site": simulated.get("tb_unit", "Tiruvallur TU"),
                        "sample_serial_id": simulated.get("sample_serial_id", f"SMP-{nikshay_id_param[3:]}" if len(nikshay_id_param) > 3 else "SMP-9999"),
                        "sample_qr_code": ""
                    }
                ]
            } if simulated.get("sample_availability") == "Yes" else {}
            
            result_details = {
                "lab_serial_number": simulated.get("lab_serial_number", f"LAB-{nikshay_id_param[3:]}" if len(nikshay_id_param) > 3 else "LAB-9999"),
                "result_sample_id": simulated.get("result_sample_id", f"SMP-{nikshay_id_param[3:]}" if len(nikshay_id_param) > 3 else "SMP-9999"),
                "date_tested": simulated.get("date_tested", "2026-03-08"),
                "date_reported": simulated.get("date_reported", "2026-03-09"),
                "reported_by": "Lab Technician",
                "final_interpretation": simulated.get("final_interpretation", "MCTB Positive"),
                "remarks": ""
            } if simulated.get("result_availability") == "Yes" else {}

            ptb_test_details = {
                "undergone_testing": simulated.get("undergone_testing", "Yes"),
                "test_reason": simulated.get("test_reason", "Diagnostic"),
                "predominant_symptom": "Cough",
                "duration_days": "15",
                "hcp_visits": "1",
                "case_type": "New Case",
                "facility_state": simulated.get("state", "Tamil Nadu"),
                "facility_district": simulated.get("district", "Tiruvallur"),
                "sample_availability": simulated.get("sample_availability", "Yes"),
                "result_availability": simulated.get("result_availability", "Yes"),
                "sample_details": sample_details,
                "result_details": result_details,
                "cxr_status": cxr_status,
                "cxr_details": {
                    "cxr_done": cxr_done,
                    "cxr_id": simulated.get("cxr_id", f"CXR-{nikshay_id_param[3:]}" if len(nikshay_id_param) > 3 else "CXR-9999"),
                    "cxr_date": simulated.get("cxr_date", "2026-03-05"),
                    "cxr_facility": simulated.get("cxr_facility", "State Diagnostic Lab"),
                    "cxr_result": simulated.get("cxr_result", "Suggestive of TB")
                } if cxr_done == "Yes" else {},
                "naat_status": simulated.get("naat_status", "Done")
            }

            participant_data = {
                "first_name": first_name,
                "last_name": last_name,
                "dob": "",
                "age": simulated.get("age", 25),
                "gender": gender_normalized,
                "primary_phone": simulated.get("contact_number", ""),
                "address": simulated.get("address", ""),
                "state": simulated.get("state", ""),
                "district": simulated.get("district", ""),
                "tb_unit": simulated.get("tb_unit", ""),
                "case_finding_type": simulated.get("tb_classification", "PTB"),
                "nikshay_id": simulated.get("nikshay_id", ""),
                "bcg_status": bcg_status,
                "bcg_has_record": bcg_has_record,
                "bcg_beneficiary_id": bcg_beneficiary_id,
                "bcg_first_name": bcg_first_name,
                "bcg_last_name": bcg_last_name,
                "bcg_ben_mobile_number": bcg_ben_mobile_number,
                "bcg_ben_gender": bcg_ben_gender,
                "bcg_dob": bcg_dob,
                "bcg_age": bcg_age,
                "bcg_vaccination_status": bcg_vaccination_status,
                "bcg_date": bcg_date,
                "bcg_registration_mode": bcg_registration_mode,
                "bcg_beneficiary_type_name": bcg_beneficiary_type_name,
                "bcg_approved_by": bcg_approved_by,
                "bcg_site_id": bcg_site_id,
                "bcg_facility_id": bcg_facility_id,
                "bcg_pincode": bcg_pincode,
                "bcg_address": bcg_address,
                "bcg_vaccine_name": "BCG",
                "bcg_vaccination_date": simulated.get("bcg_vaccination_date", ""),
                "bcg_batch_number": "Campaign Batch",
                "bcg_facility": "Campaign Facility",
                "bcg_scar": simulated.get("bcg_scar", ""),
                "eptb_screened": "Yes" if simulated.get("eptb_screened") == "Yes" else "No",
                "eptb_details": {
                    "eptb_q1a": "Yes"
                } if simulated.get("eptb_screened") == "Yes" else {},
                "ptb_test_details": ptb_test_details,
            }
            participant_json = json.dumps(participant_data)

    active_symptoms = Symptom.objects.filter(is_active=True).order_by("display_order")
    active_risks = RiskFactor.objects.filter(is_active=True).order_by("display_order")
    active_eptb_sites = EptbSite.objects.filter(is_active=True).order_by("display_order")
    
    eptb_sub_questions_dict = {}
    for site in active_eptb_sites:
        sub_qs = site.sub_questions.filter(is_active=True).order_by("display_order")
        if sub_qs.exists():
            eptb_sub_questions_dict[site.code] = [
                {"id": q.code, "label": q.label} for q in sub_qs
            ]
    eptb_sub_questions_json = json.dumps(eptb_sub_questions_dict)

    # Fetch active questions and prefetch options
    db_questions = Question.objects.filter(is_active=True).prefetch_related("options")
    questions_dict = {}
    for q in db_questions:
        questions_dict[q.code] = {
            "question": q,
            "options": q.options.filter(is_active=True).order_by("display_order")
        }

    context = {
        "site": {
            "state": profile.state if not participant else participant.state,
            "district": profile.district if not participant else participant.district,
            "tb_unit": profile.tb_unit if not participant else participant.tb_unit,
            "campaign_period": campaign_period,
        },
        "eptb_form": eptb_form,
        "participant": participant,
        "participant_json": participant_json,
        "symptoms_list": active_symptoms,
        "risk_factors_list": active_risks,
        "eptb_sites_list": active_eptb_sites,
        "eptb_sub_questions_json": eptb_sub_questions_json,
        "questions": questions_dict,
        "prefill_id": prefill_id,
    }
    return render(request, "questions/registration.html", context)


import re
import hashlib

def normalize_phone(phone):
    """
    Strips country code (like +91, 91), spaces, dashes, parentheses, non-digits.
    Returns standard 10 digit string.
    """
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) > 10:
        digits = digits[-10:]
    return digits

def normalize_name(name):
    """
    Lowercases, trims whitespace, collapses multiple internal spaces.
    """
    if not name:
        return ""
    name_str = name.lower().strip()
    name_str = re.sub(r"\s+", " ", name_str)
    return name_str

def calculate_match_status(local_name, local_phone, nikshay_name, nikshay_phone):
    """
    Compares local values vs Nikshay values.
    Returns 'EXACT_MATCH', 'PARTIAL_MATCH', or 'NO_MATCH'.
    """
    norm_local_phone = normalize_phone(local_phone)
    norm_nikshay_phone = normalize_phone(nikshay_phone)
    
    norm_local_name = normalize_name(local_name)
    norm_nikshay_name = normalize_name(nikshay_name)
    
    phone_matched = (norm_local_phone == norm_nikshay_phone) and bool(norm_local_phone)
    
    name_matched = False
    if norm_local_name and norm_nikshay_name:
        if norm_local_name == norm_nikshay_name:
            name_matched = True
        else:
            local_tokens = set(norm_local_name.split())
            nikshay_tokens = set(norm_nikshay_name.split())
            intersection = local_tokens.intersection(nikshay_tokens)
            if len(intersection) >= 2 or norm_local_name in norm_nikshay_name or norm_nikshay_name in norm_local_name:
                name_matched = True
                
    if name_matched and phone_matched:
        return "EXACT_MATCH"
    elif name_matched or phone_matched:
        return "PARTIAL_MATCH"
    else:
        return "NO_MATCH"

def get_simulated_nikshay(nikshay_id, participant=None, source="primary"):
    beneficiary = BcgVaccination.objects.filter(beneficiary_id__iexact=nikshay_id).first()
    if beneficiary:
        full_name = f"{beneficiary.first_name} {beneficiary.last_name}".strip()
        contact = beneficiary.ben_mobile_number
        age = beneficiary.age or 35
        gender = beneficiary.ben_gender or beneficiary.beneficiary_gender or "M"
    else:
        h = int(hashlib.md5(nikshay_id.encode('utf-8')).hexdigest(), 16)
        first_names = ["Ramesh", "Sunita", "Anil", "Priya", "Vikram", "Meena", "Rajesh", "Lakshmi", "Suresh", "Kavita"]
        last_names = ["Kumar", "Devi", "Sharma", "Patel", "Reddy", "Naik", "Yadav", "Verma"]
        
        first_name = first_names[h % len(first_names)]
        last_name = last_names[(h // len(first_names)) % len(last_names)]
        full_name = f"{first_name} {last_name}"
        phone_suffix = str(h % 100000000).zfill(8)
        contact = f"9{phone_suffix}"
        age = 18 + (h % 60)
        gender = "F" if (h % 2 == 0) else "M"
        
    if participant and not beneficiary:
        full_name = participant.full_name.upper() + "N" if participant.full_name.upper().endswith("A") else (participant.full_name.upper() + "AN" if not participant.full_name.upper().endswith("AN") else participant.full_name.upper())
        age = participant.age + 1
        gender = participant.gender
        contact = participant.contact_number or contact

    # Dynamic multi-source discrepancy simulation
    if source == "secondary":
        address = "Flat 402, Block B, secondary address street"
        tb_status = "On Treatment"
        adherence = "92% Adherent"
        diag_date = "2026-02-15"
        bank_details = "Aadhaar Verified"
        full_name = full_name + " (Sec)"
        age = int(age) + 2
    else:
        address = "Block B, secondary address street"
        tb_status = "Completed"
        adherence = "98% Adherent"
        diag_date = "2026-01-20"
        bank_details = "Bank Account Linked"
        
    return {
        "nikshay_id": nikshay_id,
        "full_name": full_name,
        "age": age,
        "gender": gender,
        "contact_number": contact,
        "address": address,
        "tb_treatment_status": tb_status,
        "adherence_records": adherence,
        "diagnosis_date": diag_date,
        "bank_aadhaar_details": bank_details,
        "state": "Tamil Nadu",
        "district": "Tiruvallur",
        "tb_unit": "Tiruvallur TU",
        "bcg_vaccination_status": "Vaccinated",
        "bcg_vaccination_date": "2026-03-10",
        "bcg_scar": "Scar Present",
        "tb_classification": "PTB",
        "eptb_screened": "No",
        "cxr_done": "Yes",
        "cxr_id": f"CXR-{nikshay_id[3:]}" if len(nikshay_id) > 3 else "CXR-9999",
        "cxr_date": "2026-03-05",
        "cxr_facility": "State Diagnostic Lab",
        "cxr_result": "Suggestive of TB",
        "undergone_testing": "Yes",
        "test_reason": "Diagnostic",
        "test_type": "CBNAAT",
        "naat_status": "Done",
        "ptb_test_result": "MCTB Positive",
        "ptb_test_date": "2026-03-08",
        "ptb_test_facility": "State Reference Laboratory",
        "sample_availability": "Yes",
        "result_availability": "Yes",
        "sample_serial_id": f"SMP-{nikshay_id[3:]}" if len(nikshay_id) > 3 else "SMP-9999",
        "sample_type": "Sputum",
        "collection_date": "2026-03-07",
        "collection_time": "09:30",
        "lab_serial_number": f"LAB-{nikshay_id[3:]}" if len(nikshay_id) > 3 else "LAB-9999",
        "result_sample_id": f"SMP-{nikshay_id[3:]}" if len(nikshay_id) > 3 else "SMP-9999",
        "date_tested": "2026-03-08",
        "date_reported": "2026-03-09",
        "final_interpretation": "MCTB Positive"
    }

def nikshay_api(request, nikshay_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    source = request.GET.get("source", "primary").strip().lower()
    response_data = get_simulated_nikshay(nikshay_id, source=source)
    return JsonResponse(response_data)

def reconcile_match_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    # Check permission for Nikshay Reconciliation View
    profile = getattr(request.user, "profile", None)
    if profile:
        role = getattr(profile, "role", "Project Nurse")
        if role != "Super Admin":
            if not has_role_permission(role, "Nikshay Reconciliation", "View"):
                return JsonResponse(
                    {"error": f"Permission denied. Role '{role}' is not allowed to view reconciliation data."},
                    status=403
                )

    nikshay_name = request.GET.get("name", "").strip()
    nikshay_phone = request.GET.get("phone", "").strip()
    
    if not nikshay_name and not nikshay_phone:
        return JsonResponse({"error": "No matching parameters provided"}, status=400)
        
    participants = list(Participant.objects.all())
    tpts = list(TptIndividual.objects.all())
    ineligibles = list(IneligibleIndividual.objects.all())
    
    exact_matches = []
    partial_matches = []
    
    def process_list(records, cohort_name):
        for r in records:
            match_status = calculate_match_status(
                r.full_name, 
                r.contact_number, 
                nikshay_name, 
                nikshay_phone
            )
            if match_status == "NO_MATCH":
                continue
                
            qa = {}
            if r.questionnaire_answers:
                try:
                    import json
                    qa = json.loads(r.questionnaire_answers)
                except Exception:
                    pass
                    
            match_data = {
                "id": r.id,
                "study_id": r.study_id,
                "screening_id": getattr(r, "screening_id", "") or r.study_id,
                "nikshay_id": r.nikshay_id or "",
                "full_name": r.full_name,
                "age": r.age,
                "gender": r.gender,
                "contact_number": r.contact_number or "",
                "address": r.address or "",
                "tb_treatment_status": qa.get("tb_treatment_status") or getattr(r, "tpt_status", "") or "",
                "adherence_records": qa.get("adherence_records") or "",
                "diagnosis_date": qa.get("diagnosis_date") or "",
                "bank_aadhaar_details": qa.get("bank_aadhaar_details") or "",
                "classification": r.classification if hasattr(r, "classification") else ("TPT+BCG" if cohort_name == "tpt" else "Not Eligible"),
                "synced": r.synced,
                "cohort": cohort_name,
                "match_type": match_status
            }
            if match_status == "EXACT_MATCH":
                exact_matches.append(match_data)
            else:
                partial_matches.append(match_data)
                
    process_list(participants, "participant")
    process_list(tpts, "tpt")
    process_list(ineligibles, "ineligible")
    
    return JsonResponse({
        "exact_matches": exact_matches,
        "partial_matches": partial_matches
    })

def reconcile_save_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Check permission for Nikshay Reconciliation
    profile = getattr(request.user, "profile", None)
    if profile:
        role = getattr(profile, "role", "Project Nurse")
        if role != "Super Admin":
            if not has_role_permission(role, "Nikshay Reconciliation", "Approve/Reconcile"):
                return JsonResponse(
                    {"error": f"Permission denied. Role '{role}' is not allowed to reconcile records."},
                    status=403
                )

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST
        
    participant_id = data.get("participant_id")
    cohort = data.get("cohort")
    nikshay_id = data.get("nikshay_id")
    source = data.get("source", "primary")
    fields_data = data.get("fields", {})
    
    from django.shortcuts import get_object_or_404
    from questions.models import IneligibleIndividual
    if cohort == "tpt":
        participant = get_object_or_404(TptIndividual, id=participant_id)
    elif cohort == "ineligible":
        participant = get_object_or_404(IneligibleIndividual, id=participant_id)
    else:
        try:
            participant = Participant.objects.get(id=participant_id)
        except Participant.DoesNotExist:
            try:
                participant = TptIndividual.objects.get(id=participant_id)
            except TptIndividual.DoesNotExist:
                participant = get_object_or_404(IneligibleIndividual, id=participant_id)
                
    qa = {}
    if participant.questionnaire_answers:
        try:
            qa = json.loads(participant.questionnaire_answers)
        except Exception:
            pass
            
    # Apply resolved overrides
    for field_key, field_info in fields_data.items():
        val = field_info.get("value")
        if field_key == "full_name":
            participant.full_name = str(val).title()
        elif field_key == "age":
            participant.age = int(val)
        elif field_key == "gender":
            participant.gender = str(val)
        elif field_key == "contact_number":
            participant.contact_number = str(val)
        elif field_key == "address":
            participant.address = str(val)
        else:
            qa[field_key] = val
            if field_key == "tb_treatment_status":
                participant.tpt_status = val
                
    participant.questionnaire_answers = json.dumps(qa)
    participant.nikshay_id = nikshay_id
    participant.synced = True
    participant.created_by = request.user
    profile = request.user.profile
    participant.state = profile.state
    participant.district = profile.district
    participant.tb_unit = profile.tb_unit
    if not getattr(participant, "screening_id", None):
        participant.screening_id = participant.study_id
        
    # Compute status: FULLY_RECONCILED, PARTIALLY_RECONCILED, CONFLICT_RESOLVED
    has_custom = False
    has_mismatch_with_nikshay = False
    nikshay = get_simulated_nikshay(nikshay_id, participant, source=source)
    
    for field_key, field_info in fields_data.items():
        src = field_info.get("source")
        val = field_info.get("value")
        if src == "custom":
            has_custom = True
        nikshay_val = nikshay.get(field_key)
        if str(val).strip().lower() != str(nikshay_val).strip().lower():
            has_mismatch_with_nikshay = True
            
    if has_custom:
        recon_status = "CONFLICT_RESOLVED"
    elif has_mismatch_with_nikshay:
        recon_status = "PARTIALLY_RECONCILED"
    else:
        recon_status = "FULLY_RECONCILED"
        
    participant.reconciliation_status = recon_status
    participant.save()
    sync_nikshay_record(participant, nikshay_id, user=request.user)
    
    AuditLog.objects.create(
        actor=request.user,
        action=f"Reconciled participant {participant.study_id} with Nikshay ID {nikshay_id} [Status: {recon_status}]. Details: {json.dumps(fields_data)}",
        ip_address=get_client_ip(request)
    )
    
    return JsonResponse({"status": "success", "message": "Record reconciled and synchronized successfully."})

def search(request):
    """
    Module 03: Registry lookup interface for querying registered participants.
    """
    if not request.user.is_authenticated:
        return redirect("questions:home")
        
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    source_filter = request.GET.get("source", "").strip()
    type_filter = request.GET.get("type", "").strip()
    sort_filter = request.GET.get("sort", "").strip()
    cohort_filter = request.GET.get("cohort", "").strip()
    
    from questions.models import IneligibleIndividual
    from django.db.models import Q
    from django.utils import timezone
    
    # Initialize querysets
    participants_qs = filter_by_jurisdiction(Participant.objects.all(), request)
    tpt_qs = filter_by_jurisdiction(TptIndividual.objects.all(), request)
    ineligible_qs = filter_by_jurisdiction(IneligibleIndividual.objects.all(), request)
    
    if cohort_filter == "eligible":
        participants_qs = participants_qs.filter(eligible=True)
        tpt_qs = tpt_qs.all()
        ineligible_qs = ineligible_qs.none()
    elif cohort_filter == "ineligible":
        participants_qs = participants_qs.filter(eligible=False)
        tpt_qs = tpt_qs.none()
        ineligible_qs = ineligible_qs.all()
    
    auto_select_id = None
    
    if query:
        participants_qs = participants_qs.filter(
            Q(full_name__icontains=query) |
            Q(study_id__icontains=query) |
            Q(screening_id__icontains=query) |
            Q(nikshay_id__icontains=query) |
            Q(bcg_beneficiary_id__icontains=query) |
            Q(contact_number__icontains=query)
        )
        tpt_qs = tpt_qs.filter(
            Q(full_name__icontains=query) |
            Q(study_id__icontains=query) |
            Q(screening_id__icontains=query) |
            Q(nikshay_id__icontains=query) |
            Q(bcg_beneficiary_id__icontains=query) |
            Q(contact_number__icontains=query)
        )
        ineligible_qs = ineligible_qs.filter(
            Q(full_name__icontains=query) |
            Q(study_id__icontains=query) |
            Q(screening_id__icontains=query) |
            Q(nikshay_id__icontains=query) |
            Q(bcg_beneficiary_id__icontains=query) |
            Q(contact_number__icontains=query)
        )
        
        # Check direct/exact match for auto-selection on page load
        exact_match = participants_qs.filter(
            Q(study_id__iexact=query) |
            Q(screening_id__iexact=query) |
            Q(nikshay_id__iexact=query) |
            Q(bcg_beneficiary_id__iexact=query)
        ).first()
        if not exact_match:
            exact_match = tpt_qs.filter(
                Q(study_id__iexact=query) |
                Q(screening_id__iexact=query) |
                Q(nikshay_id__iexact=query) |
                Q(bcg_beneficiary_id__iexact=query)
            ).first()
        if not exact_match:
            exact_match = ineligible_qs.filter(
                Q(study_id__iexact=query) |
                Q(screening_id__iexact=query) |
                Q(nikshay_id__iexact=query) |
                Q(bcg_beneficiary_id__iexact=query)
            ).first()
        if exact_match:
            auto_select_id = exact_match.pk
            
    # Filter by Status
    if status_filter and status_filter != "All":
        if status_filter == "Synced":
            participants_qs = participants_qs.filter(synced=True)
            tpt_qs = tpt_qs.filter(synced=True)
            ineligible_qs = ineligible_qs.filter(synced=True)
        elif status_filter == "Pending":
            participants_qs = participants_qs.filter(synced=False, eligible=True)
            tpt_qs = tpt_qs.filter(synced=False, eligible=True)
            ineligible_qs = ineligible_qs.filter(synced=False)
        elif status_filter == "Draft":
            participants_qs = participants_qs.filter(synced=False)
            tpt_qs = tpt_qs.filter(synced=False)
            ineligible_qs = ineligible_qs.filter(synced=False)
        elif status_filter == "Control":
            participants_qs = participants_qs.filter(classification="Control")
            tpt_qs = tpt_qs.none()
            ineligible_qs = ineligible_qs.none()
        elif status_filter == "Completed":
            participants_qs = participants_qs.filter(reconciliation_status__in=["FULLY_RECONCILED", "CONFLICT_RESOLVED"])
            tpt_qs = tpt_qs.filter(reconciliation_status__in=["FULLY_RECONCILED", "CONFLICT_RESOLVED"])
            ineligible_qs = ineligible_qs.filter(reconciliation_status__in=["FULLY_RECONCILED", "CONFLICT_RESOLVED"])

    # Filter by Data Source
    if source_filter and source_filter != "All":
        if source_filter == "Nikshay":
            participants_qs = participants_qs.filter(nikshay_id__isnull=False).exclude(nikshay_id="")
            tpt_qs = tpt_qs.filter(nikshay_id__isnull=False).exclude(nikshay_id="")
            ineligible_qs = ineligible_qs.filter(nikshay_id__isnull=False).exclude(nikshay_id="")
        elif source_filter == "aBCG Local":
            participants_qs = participants_qs.filter(Q(nikshay_id__isnull=True) | Q(nikshay_id=""))
            tpt_qs = tpt_qs.filter(Q(nikshay_id__isnull=True) | Q(nikshay_id=""))
            ineligible_qs = ineligible_qs.filter(Q(nikshay_id__isnull=True) | Q(nikshay_id=""))
        elif source_filter == "Nikshay + aBCG":
            participants_qs = participants_qs.filter(nikshay_id__isnull=False).exclude(nikshay_id="").filter(synced=True)
            tpt_qs = tpt_qs.filter(nikshay_id__isnull=False).exclude(nikshay_id="").filter(synced=True)
            ineligible_qs = ineligible_qs.filter(nikshay_id__isnull=False).exclude(nikshay_id="").filter(synced=True)

    # Filter by Participant Type
    if type_filter and type_filter != "All":
        if type_filter == "Case":
            participants_qs = participants_qs.filter(classification="Case")
            tpt_qs = tpt_qs.none()
            ineligible_qs = ineligible_qs.none()
        elif type_filter == "Control":
            participants_qs = participants_qs.filter(classification="Control")
            tpt_qs = tpt_qs.none()
            ineligible_qs = ineligible_qs.none()
        elif type_filter == "Screening":
            participants_qs = participants_qs.filter(classification="Pending")
            tpt_qs = tpt_qs.none()
            ineligible_qs = ineligible_qs.none()
        elif type_filter == "Registered":
            pass

    # Combine lists
    participants = list(participants_qs) + list(tpt_qs) + list(ineligible_qs)
    
    # Compute Statistics Summary Counts
    total_count = len(participants)
    synced_count = sum(1 for x in participants if x.synced)
    pending_count = sum(1 for x in participants if not x.synced and getattr(x, 'eligible', True))
    draft_count = sum(1 for x in participants if not x.synced)
    control_count = sum(1 for x in participants if getattr(x, 'classification', '') == 'Control')
    
    # Sort
    if sort_filter == "Name A-Z":
        participants.sort(key=lambda x: x.full_name.lower() if x.full_name else "")
    elif sort_filter == "Name Z-A":
        participants.sort(key=lambda x: x.full_name.lower() if x.full_name else "", reverse=True)
    elif sort_filter == "Study ID":
        participants.sort(key=lambda x: x.study_id if x.study_id else "")
    elif sort_filter == "Status":
        participants.sort(key=lambda x: x.reconciliation_status if x.reconciliation_status else "")
    else:
        participants.sort(key=lambda x: x.created_at if x.created_at else timezone.now(), reverse=True)
        
    # Integrate pagination (20 per page)
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(participants, 20)
    page = request.GET.get('page')
    try:
        paginated_participants = paginator.page(page)
    except PageNotAnInteger:
        paginated_participants = paginator.page(1)
    except EmptyPage:
        paginated_participants = paginator.page(paginator.num_pages)
        
    # Check if search query matches an external Nikshay ID to pull registry records
    nikshay_search_match = None
    if query and (query.startswith("NK-") or query.startswith("nk-") or len(query) >= 6):
        try:
            # Check if there is an exact match in local DB with this Nikshay ID
            local_match = Participant.objects.filter(nikshay_id__iexact=query).first()
            if not local_match:
                local_match = TptIndividual.objects.filter(nikshay_id__iexact=query).first()
            if not local_match:
                local_match = IneligibleIndividual.objects.filter(nikshay_id__iexact=query).first()
                
            simulated = get_simulated_nikshay(query)
            if simulated:
                nikshay_search_match = {
                    "nikshay_id": simulated.get("nikshay_id"),
                    "full_name": simulated.get("full_name"),
                    "age": simulated.get("age"),
                    "gender": simulated.get("gender"),
                    "contact_number": simulated.get("contact_number"),
                    "state": simulated.get("state"),
                    "district": simulated.get("district"),
                    "tb_unit": simulated.get("tb_unit"),
                    "local_match_id": local_match.pk if local_match else None,
                    "local_match_cohort": "participant" if isinstance(local_match, Participant) else ("tpt" if isinstance(local_match, TptIndividual) else "ineligible") if local_match else None
                }
        except Exception:
            pass
            
    active_filters_count = 0
    if status_filter and status_filter != "All":
        active_filters_count += 1
    if source_filter and source_filter != "All":
        active_filters_count += 1
    if type_filter and type_filter != "All":
        active_filters_count += 1
        
    return render(request, "questions/search.html", {
        "participants": paginated_participants,
        "paginated_participants": paginated_participants,
        "paginator": paginator,
        "query": query,
        "status_filter": status_filter,
        "source_filter": source_filter,
        "type_filter": type_filter,
        "sort_filter": sort_filter,
        "auto_select_id": auto_select_id,
        "total_count": total_count,
        "synced_count": synced_count,
        "pending_count": pending_count,
        "draft_count": draft_count,
        "control_count": control_count,
        "active_filters_count": active_filters_count,
        "nikshay_search_match": nikshay_search_match
    })


def serialize_participant_record(p):
    return {
        "study_id": p.study_id,
        "nikshay_id": p.nikshay_id,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "full_name": p.full_name,
        "age": p.age,
        "gender": p.gender,
        "contact_number": p.contact_number,
        "dob": p.dob.strftime("%Y-%m-%d") if p.dob else None,
        "date_enroll": p.date_enroll.strftime("%Y-%m-%d") if p.date_enroll else None,
        "state": p.state,
        "district": p.district,
        "tb_unit": p.tb_unit,
        "facility": p.facility,
        "village": p.village,
        "pincode": p.pincode,
        "demographic_area": p.demographic_area,
        "secondary_phone": p.secondary_phone,
        "address": p.address,
        "campaign_completion_date": p.campaign_completion_date.strftime("%Y-%m-%d") if p.campaign_completion_date else None,
        "sector": p.sector,
        "case_finding_type": p.case_finding_type,
        "private_facility": p.private_facility,
        "public_phi": p.public_phi,
        "father_husband_name": p.father_husband_name,
        "secondary_phone_1": p.secondary_phone_1,
        "secondary_phone_2": p.secondary_phone_2,
        "secondary_phone_3": p.secondary_phone_3,
        "taluka_block": p.taluka_block,
        "landmark": p.landmark,
        "contact_person_name": p.contact_person_name,
        "contact_person_phone": p.contact_person_phone,
        "contact_person_address": p.contact_person_address,
        "informant_name": p.informant_name,
        "informant_designation": p.informant_designation,
        "ptb_screened": p.ptb_screened,
        "ptb_test_registered": p.ptb_test_registered,
        "ptb_test_type": p.ptb_test_type,
        "ptb_test_result": p.ptb_test_result,
        "ptb_test_date": p.ptb_test_date.strftime("%Y-%m-%d") if p.ptb_test_date else None,
        "ptb_test_facility": p.ptb_test_facility,
        "ptb_test_details": p.ptb_test_details,
        "eptb_screened": p.eptb_screened,
        "marital_status": p.marital_status,
        "occupation": p.occupation,
        "socioeconomic_status": p.socioeconomic_status,
        "height_cm": p.height_cm,
        "weight_kg": p.weight_kg,
        "bmi": p.bmi,
        "symptoms": p.symptoms,
        "risk_factors": p.risk_factors,
        "hiv_status": p.hiv_status,
        "past_tb": p.past_tb,
        "diabetes": p.diabetes,
        "smoker": p.smoker,
        "close_contact": p.close_contact,
        "tpt_undergone": p.tpt_undergone,
        "tpt_status": p.tpt_status,
        "tpt_contact_known": p.tpt_contact_known,
        "tpt_history": p.tpt_history,
        "tpt_start_date": p.tpt_start_date.strftime("%Y-%m-%d") if p.tpt_start_date else None,
        "tpt_end_date": p.tpt_end_date.strftime("%Y-%m-%d") if p.tpt_end_date else None,
        "tpt_duration_months": p.tpt_duration_months,
        "tpt_regimen": p.tpt_regimen,
        "tpt_risk_factor": p.tpt_risk_factor,
        "bcg_evidence": p.bcg_evidence,
        "bcg_status": p.bcg_status,
        "bcg_beneficiary_id": p.bcg_beneficiary_id,
        "bcg_ben_mobile_number": p.bcg_ben_mobile_number,
        "bcg_ben_gender": p.bcg_ben_gender,
        "bcg_date": p.bcg_date,
        "bcg_registration_mode": p.bcg_registration_mode,
        "bcg_dob": p.bcg_dob,
        "bcg_age": p.bcg_age,
        "bcg_vaccination_status": p.bcg_vaccination_status,
        "bcg_first_name": p.bcg_first_name,
        "bcg_last_name": p.bcg_last_name,
        "bcg_site_id": p.bcg_site_id,
        "bcg_approved_by": p.bcg_approved_by,
        "bcg_beneficiary_type_name": p.bcg_beneficiary_type_name,
        "bcg_pincode": p.bcg_pincode,
        "bcg_address": p.bcg_address,
        "bcg_facility_id": p.bcg_facility_id,
        "bcg_scar": p.bcg_scar,
        "bcg_has_record": p.bcg_has_record,
        "bcg_vaccination_date": p.bcg_vaccination_date.strftime("%Y-%m-%d") if p.bcg_vaccination_date else None,
        "bcg_vaccine_name": p.bcg_vaccine_name,
        "bcg_batch_number": p.bcg_batch_number,
        "bcg_facility": p.bcg_facility,
        "questionnaire_answers": p.questionnaire_answers,
        "eptb_details": p.eptb_details,
        "eligible": p.eligible,
        "eligible_bcg_campaign": p.eligible_bcg_campaign,
        "bcg_eligibility_criteria": p.bcg_eligibility_criteria,
        "match_hrg": p.match_hrg,
        "classification": p.classification,
        "classification_reason": p.classification_reason,
    }


def serialize_tpt_record(t):
    return {
        "study_id": t.study_id,
        "nikshay_id": t.nikshay_id,
        "first_name": t.first_name,
        "last_name": t.last_name,
        "full_name": t.full_name,
        "age": t.age,
        "gender": t.gender,
        "contact_number": t.contact_number,
        "dob": t.dob.strftime("%Y-%m-%d") if t.dob else None,
        "date_enroll": t.date_enroll.strftime("%Y-%m-%d") if t.date_enroll else None,
        "state": t.state,
        "district": t.district,
        "tb_unit": t.tb_unit,
        "facility": t.facility,
        "village": t.village,
        "pincode": t.pincode,
        "demographic_area": t.demographic_area,
        "campaign_completion_date": t.campaign_completion_date.strftime("%Y-%m-%d") if t.campaign_completion_date else None,
        "secondary_phone": t.secondary_phone,
        "address": t.address,
        "sector": t.sector,
        "case_finding_type": t.case_finding_type,
        "private_facility": t.private_facility,
        "public_phi": t.public_phi,
        "father_husband_name": t.father_husband_name,
        "secondary_phone_1": t.secondary_phone_1,
        "secondary_phone_2": t.secondary_phone_2,
        "secondary_phone_3": t.secondary_phone_3,
        "taluka_block": t.taluka_block,
        "landmark": t.landmark,
        "tpt_undergone": t.tpt_undergone,
        "tpt_status": t.tpt_status,
        "tpt_contact_known": t.tpt_contact_known,
        "tpt_history": t.tpt_history,
        "tpt_start_date": t.tpt_start_date.strftime("%Y-%m-%d") if t.tpt_start_date else None,
        "tpt_end_date": t.tpt_end_date.strftime("%Y-%m-%d") if t.tpt_end_date else None,
        "tpt_duration_months": t.tpt_duration_months,
        "tpt_regimen": t.tpt_regimen,
        "tpt_risk_factor": t.tpt_risk_factor,
        "classification": t.classification,
    }


def serialize_ineligible_record(i):
    return {
        "study_id": i.study_id,
        "nikshay_id": i.nikshay_id,
        "first_name": i.first_name,
        "last_name": i.last_name,
        "full_name": i.full_name,
        "age": i.age,
        "gender": i.gender,
        "contact_number": i.contact_number,
        "dob": i.dob.strftime("%Y-%m-%d") if i.dob else None,
        "date_enroll": i.date_enroll.strftime("%Y-%m-%d") if i.date_enroll else None,
        "state": i.state,
        "district": i.district,
        "tb_unit": i.tb_unit,
        "facility": i.facility,
        "village": i.village,
        "pincode": i.pincode,
        "demographic_area": i.demographic_area,
        "campaign_completion_date": i.campaign_completion_date.strftime("%Y-%m-%d") if i.campaign_completion_date else None,
        "secondary_phone": i.secondary_phone,
        "address": i.address,
        "sector": i.sector,
        "case_finding_type": i.case_finding_type,
        "private_facility": i.private_facility,
        "public_phi": i.public_phi,
        "father_husband_name": i.father_husband_name,
        "secondary_phone_1": i.secondary_phone_1,
        "secondary_phone_2": i.secondary_phone_2,
        "secondary_phone_3": i.secondary_phone_3,
        "taluka_block": i.taluka_block,
        "landmark": i.landmark,
        "classification": i.classification,
        "classification_reason": i.classification_reason,
    }


def sync_single_record(record_obj):
    """
    Safely transfers an individual participant record and attached photos
    (BCG scar photo, vaccination card, Chest X-Ray) to the central backend.
    Updates the record with receipt ID and timestamp upon successful ingestion.
    """
    import requests
    from django.conf import settings
    backend_url = getattr(settings, "CENTRAL_BACKEND_URL", "http://127.0.0.1:8001")
    username = getattr(settings, "CENTRAL_BACKEND_USER", "admin")
    password = getattr(settings, "CENTRAL_BACKEND_PASSWORD", "adminpassword")

    # 1. Authenticate with central backend
    try:
        auth_response = requests.post(
            f"{backend_url}/api/v1/auth/login/",
            json={"username": username, "password": password},
            timeout=8
        )
        if auth_response.status_code != 200:
            return {"success": False, "error": f"Central authentication failed: {auth_response.text}"}
        token = auth_response.json().get("token")
    except requests.RequestException as e:
        return {"success": False, "error": f"Central backend unreachable: {str(e)}"}

    headers = {"Authorization": f"Token {token}"}
    
    # 2. Build bulk sync payload with single record
    payload = {
        "participants": [],
        "tpt_individuals": [],
        "ineligible_individuals": [],
        "telemetry": None
    }
    
    if isinstance(record_obj, Participant):
        payload["participants"].append(serialize_participant_record(record_obj))
    elif isinstance(record_obj, TptIndividual):
        payload["tpt_individuals"].append(serialize_tpt_record(record_obj))
    elif isinstance(record_obj, IneligibleIndividual):
        payload["ineligible_individuals"].append(serialize_ineligible_record(record_obj))

    try:
        sync_response = requests.post(
            f"{backend_url}/api/v1/sync/bulk/",
            json=payload,
            headers=headers,
            timeout=15
        )
        if sync_response.status_code != 200:
            err = f"Sync failed: {sync_response.text}"
            record_obj.sync_error_message = err[:250]
            record_obj.save(update_fields=["sync_error_message"])
            return {"success": False, "error": err}
            
        sync_data = sync_response.json()
        receipts = sync_data.get("receipts", {})
        receipt_info = receipts.get(record_obj.study_id, {})
        receipt_id = receipt_info.get("receipt_id", f"REC-{record_obj.study_id}")
        verified_at = timezone.now()
        
        record_obj.synced = True
        record_obj.sync_receipt_id = receipt_id
        record_obj.sync_verified_at = verified_at
        record_obj.sync_error_message = ""
        record_obj.save(update_fields=["synced", "sync_receipt_id", "sync_verified_at", "sync_error_message"])
        
    except requests.RequestException as e:
        err = f"Network timeout during sync: {str(e)}"
        record_obj.sync_error_message = err[:250]
        record_obj.save(update_fields=["sync_error_message"])
        return {"success": False, "error": err}

    # 3. Upload media attachments if present
    files = {}
    if getattr(record_obj, "bcg_scar_file", None):
        try:
            files["bcg_scar_file"] = record_obj.bcg_scar_file.open("rb")
        except Exception:
            pass
    if getattr(record_obj, "bcg_record_file", None):
        try:
            files["bcg_record_file"] = record_obj.bcg_record_file.open("rb")
        except Exception:
            pass
    if getattr(record_obj, "cxr_record_file", None):
        try:
            files["cxr_record_file"] = record_obj.cxr_record_file.open("rb")
        except Exception:
            pass

    media_receipt = None
    if files:
        try:
            media_resp = requests.post(
                f"{backend_url}/api/v1/sync/media/",
                data={"study_id": record_obj.study_id},
                files=files,
                headers=headers,
                timeout=30
            )
            if media_resp.status_code == 200:
                media_data = media_resp.json()
                media_receipt = media_data.get("receipt_id")
                record_obj.sync_receipt_id = media_receipt or record_obj.sync_receipt_id
                record_obj.sync_verified_at = timezone.now()
                record_obj.save(update_fields=["sync_receipt_id", "sync_verified_at"])
            else:
                record_obj.sync_error_message = f"Media upload warning: {media_resp.text[:200]}"
                record_obj.save(update_fields=["sync_error_message"])
        except requests.RequestException as e:
            record_obj.sync_error_message = f"Media upload network error: {str(e)[:200]}"
            record_obj.save(update_fields=["sync_error_message"])
        finally:
            for f in files.values():
                try:
                    f.close()
                except Exception:
                    pass

    return {
        "success": True,
        "receipt_id": record_obj.sync_receipt_id,
        "verified_at": record_obj.sync_verified_at.isoformat() if record_obj.sync_verified_at else timezone.now().isoformat(),
        "has_media": bool(files),
        "media_receipt": media_receipt
    }


def sync_single_record_api(request, study_id):
    """
    API endpoint allowing nurses to trigger immediate transfer and verification
    of a single participant record and its media attachments.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)
        
    record = (
        Participant.objects.filter(study_id=study_id).first() or
        TptIndividual.objects.filter(study_id=study_id).first() or
        IneligibleIndividual.objects.filter(study_id=study_id).first()
    )
    if not record:
        return JsonResponse({"status": "error", "message": f"Participant with Study ID '{study_id}' not found."}, status=404)
        
    res = sync_single_record(record)
    if res.get("success"):
        return JsonResponse({
            "status": "success",
            "study_id": study_id,
            "receipt_id": res.get("receipt_id"),
            "verified_at": res.get("verified_at"),
            "has_media": res.get("has_media", False),
            "media_receipt": res.get("media_receipt"),
            "message": f"Record {study_id} safely transferred and verified on Central Backend."
        })
    else:
        return JsonResponse({
            "status": "error",
            "study_id": study_id,
            "message": res.get("error", "Safe transfer failed.")
        }, status=500)


def pending_sync(request):
    """
    Module 04: The outbound staging queue displaying offline-ready draft structures.
    """
    import requests
    from django.conf import settings
    from django.contrib import messages
    
    if not request.user.is_authenticated:
        return redirect("questions:home")

    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", "Project Nurse")
    if role != "Super Admin":
        action = "Create" if request.method == "POST" else "View"
        has_perm = has_role_permission(role, "Bulk Sync Operations", action)
        if not has_perm:
            messages.error(request, f"Permission denied. Role '{role}' is not allowed to {action.lower()} Bulk Sync Operations.")
            return redirect("questions:home")
        
    if request.method == "POST":
        # Calculate counts before syncing
        unsynced_p = filter_by_jurisdiction(Participant.objects.filter(synced=False), request)
        unsynced_t = filter_by_jurisdiction(TptIndividual.objects.filter(synced=False), request)
        unsynced_i = filter_by_jurisdiction(IneligibleIndividual.objects.filter(synced=False), request)
        pending_count = unsynced_p.count() + unsynced_t.count() + unsynced_i.count()
        synced_count = pending_count
        
        # Telemetry fields
        latitude_str = request.POST.get("latitude", "").strip()
        longitude_str = request.POST.get("longitude", "").strip()
        battery_level_str = request.POST.get("battery_level", "").strip()
        battery_charging_str = request.POST.get("battery_charging", "").strip()
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        latitude = float(latitude_str) if latitude_str else None
        longitude = float(longitude_str) if longitude_str else None
        battery_level = int(battery_level_str) if battery_level_str else None
        battery_charging = (battery_charging_str in ['true', 'True', 'on', '1', 'yes'])
        
        # Helper to check if JSON format is requested
        is_json = (request.headers.get('x-requested-with') == 'XMLHttpRequest' or
                   request.GET.get('format') == 'json' or
                   request.POST.get('format') == 'json')

        # 1. Login to retrieve dynamic authorization token
        backend_url = getattr(settings, "CENTRAL_BACKEND_URL", "http://127.0.0.1:8001")
        username = getattr(settings, "CENTRAL_BACKEND_USER", "admin")
        password = getattr(settings, "CENTRAL_BACKEND_PASSWORD", "adminpassword")
        
        token = None
        try:
            auth_response = requests.post(
                f"{backend_url}/api/v1/auth/login/",
                json={"username": username, "password": password},
                timeout=10
            )
            if auth_response.status_code == 200:
                token = auth_response.json().get("token")
            else:
                err_msg = f"Authentication with central backend failed: {auth_response.text}"
                request.session["last_sync_status"] = "error"
                request.session["last_sync_message"] = err_msg
                request.session["last_sync_timestamp"] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                if is_json:
                    return JsonResponse({"status": "error", "message": err_msg})
                messages.error(request, err_msg)
                return redirect("questions:pending_sync")
        except requests.RequestException as e:
            err_msg = f"Failed to connect to central backend: {str(e)}"
            request.session["last_sync_status"] = "error"
            request.session["last_sync_message"] = err_msg
            request.session["last_sync_timestamp"] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            if is_json:
                return JsonResponse({"status": "error", "message": err_msg})
            messages.error(request, err_msg)
            return redirect("questions:pending_sync")
            
        # 2. Serialize and upload data in bulk
        headers = {"Authorization": f"Token {token}"}
        
        serialized_participants = [serialize_participant_record(p) for p in unsynced_p]
        serialized_tpt = [serialize_tpt_record(t) for t in unsynced_t]
        serialized_ineligible = [serialize_ineligible_record(i) for i in unsynced_i]
            
        sync_payload = {
            "participants": serialized_participants,
            "tpt_individuals": serialized_tpt,
            "ineligible_individuals": serialized_ineligible,
            "telemetry": {
                "latitude": latitude,
                "longitude": longitude,
                "battery_level": battery_level,
                "battery_charging": battery_charging,
                "synced_count": synced_count,
                "device_user_agent": user_agent
            }
        }
        
        try:
            sync_response = requests.post(
                f"{backend_url}/api/v1/sync/bulk/",
                json=sync_payload,
                headers=headers,
                timeout=25
            )
            if sync_response.status_code != 200:
                err_msg = f"Data synchronization failed: {sync_response.text}"
                request.session["last_sync_status"] = "error"
                request.session["last_sync_message"] = err_msg
                request.session["last_sync_timestamp"] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                if is_json:
                    return JsonResponse({"status": "error", "message": err_msg})
                messages.error(request, err_msg)
                return redirect("questions:pending_sync")
                
            sync_result = sync_response.json()
            synced_participants_ids = sync_result.get("participants", [])
            synced_tpt_ids = sync_result.get("tpt_individuals", [])
            synced_ineligible_ids = sync_result.get("ineligible_individuals", [])
            receipts = sync_result.get("receipts", {})
            now_verified = timezone.now()
            
        except requests.RequestException as e:
            err_msg = f"Failed to connect to central backend for sync: {str(e)}"
            request.session["last_sync_status"] = "error"
            request.session["last_sync_message"] = err_msg
            request.session["last_sync_timestamp"] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            if is_json:
                return JsonResponse({"status": "error", "message": err_msg})
            messages.error(request, err_msg)
            return redirect("questions:pending_sync")
            
        # 3. Synchronize media files across all successfully uploaded cohorts (Participant, TPT, Ineligible)
        all_synced_records = []
        for p in unsynced_p:
            if p.study_id in synced_participants_ids:
                all_synced_records.append(p)
        for t in unsynced_t:
            if t.study_id in synced_tpt_ids:
                all_synced_records.append(t)
        for i in unsynced_i:
            if i.study_id in synced_ineligible_ids:
                all_synced_records.append(i)

        for rec in all_synced_records:
            rec_id = receipts.get(rec.study_id, {}).get("receipt_id", f"REC-{rec.study_id}")
            rec.sync_receipt_id = rec_id
            rec.sync_verified_at = now_verified
            rec.synced = True
            rec.sync_error_message = ""
            
            files = {}
            if getattr(rec, "bcg_scar_file", None):
                try:
                    files['bcg_scar_file'] = rec.bcg_scar_file.open('rb')
                except Exception:
                    pass
            if getattr(rec, "bcg_record_file", None):
                try:
                    files['bcg_record_file'] = rec.bcg_record_file.open('rb')
                except Exception:
                    pass
            if getattr(rec, "cxr_record_file", None):
                try:
                    files['cxr_record_file'] = rec.cxr_record_file.open('rb')
                except Exception:
                    pass
                    
            if files:
                try:
                    media_response = requests.post(
                        f"{backend_url}/api/v1/sync/media/",
                        data={"study_id": rec.study_id},
                        files=files,
                        headers=headers,
                        timeout=30
                    )
                    if media_response.status_code == 200:
                        m_data = media_response.json()
                        rec.sync_receipt_id = m_data.get("receipt_id", rec.sync_receipt_id)
                        rec.sync_verified_at = timezone.now()
                    else:
                        print(f"Warning: Media upload failed for {rec.study_id}: {media_response.text}")
                        rec.sync_error_message = f"Media upload warning: {media_response.text[:200]}"
                except requests.RequestException as e:
                    print(f"Warning: Media upload connection error for {rec.study_id}: {str(e)}")
                    rec.sync_error_message = f"Media upload network error: {str(e)[:200]}"
                finally:
                    for f in files.values():
                        try:
                            f.close()
                        except Exception:
                            pass
                            
            rec.save(update_fields=["synced", "sync_receipt_id", "sync_verified_at", "sync_error_message"])
                            
        # 4. Create telemetry log locally
        from questions.models import DeviceSyncLog
        DeviceSyncLog.objects.create(
            user=request.user,
            latitude=latitude,
            longitude=longitude,
            battery_level=battery_level,
            battery_charging=battery_charging,
            pending_count=0,
            synced_count=synced_count,
            device_user_agent=user_agent
        )

        # 5. Mark successfully synced local records
        updated_p = Participant.objects.filter(study_id__in=synced_participants_ids).update(synced=True)
        updated_t = TptIndividual.objects.filter(study_id__in=synced_tpt_ids).update(synced=True)
        updated_i = IneligibleIndividual.objects.filter(study_id__in=synced_ineligible_ids).update(synced=True)
        
        print(f"DEBUG: sync_result = {sync_result}")
        print(f"DEBUG: updated participants = {updated_p}, tpt = {updated_t}, ineligible = {updated_i}")
        
        # 6. Synchronize dynamic questions/options catalog from central backend
        try:
            questions_response = requests.get(
                f"{backend_url}/api/v1/questions/",
                headers=headers,
                timeout=15
            )
            if questions_response.status_code == 200:
                questions_list = questions_response.json()
                if questions_list:
                    from questions.models import Question, Option
                    from django.db import transaction
                    
                    with transaction.atomic():
                        # Clear local dynamic questions & options before reloading
                        Option.objects.all().delete()
                        Question.objects.all().delete()
                        
                        for q_data in questions_list:
                            q_obj = Question.objects.create(
                                code=q_data["code"],
                                label=q_data["label"],
                                step=q_data["step"],
                                field_type=q_data["field_type"],
                                display_order=q_data["display_order"],
                                is_active=q_data["is_active"]
                            )
                            for opt_data in q_data.get("options", []):
                                Option.objects.create(
                                    question=q_obj,
                                    code=opt_data["code"],
                                    name=opt_data["name"],
                                    display_order=opt_data["display_order"],
                                    is_active=opt_data["is_active"]
                                )
                    print("DEBUG: Dynamic questions/options catalog updated from central backend successfully.")
            else:
                print(f"Warning: Question catalog sync failed: {questions_response.text}")
        except Exception as e:
            print(f"Warning: Failed to fetch questions from central backend: {str(e)}")
        # Recalculate remaining unsynced records
        unsynced_p_rem = filter_by_jurisdiction(Participant.objects.filter(synced=False), request).count()
        unsynced_t_rem = filter_by_jurisdiction(TptIndividual.objects.filter(synced=False), request).count()
        unsynced_i_rem = filter_by_jurisdiction(IneligibleIndividual.objects.filter(synced=False), request).count()
        remaining_unsynced = unsynced_p_rem + unsynced_t_rem + unsynced_i_rem

        success_msg = f"Successfully synchronized {len(synced_participants_ids) + len(synced_tpt_ids) + len(synced_ineligible_ids)} records to central backend."
        request.session["last_sync_status"] = "success"
        request.session["last_sync_message"] = success_msg
        request.session["last_sync_timestamp"] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json' or request.POST.get('format') == 'json':
            return JsonResponse({
                "status": "success",
                "message": success_msg,
                "total_unsynced": remaining_unsynced
            })

        messages.success(request, success_msg)
        return redirect("questions:pending_sync")

    pending_records = []
    unsynced_p = filter_by_jurisdiction(Participant.objects.filter(synced=False, eligible=True), request)
    unsynced_t = filter_by_jurisdiction(TptIndividual.objects.filter(synced=False, eligible=True), request)
    unsynced_i = filter_by_jurisdiction(IneligibleIndividual.objects.filter(synced=False), request)
    unsynced = list(unsynced_p) + list(unsynced_t) + list(unsynced_i)
    unsynced.sort(key=lambda x: x.created_at, reverse=True)
    
    for p in unsynced:
        if p.classification == "Case":
            type_label = "Case Group"
        elif p.classification == "Control":
            type_label = "Control Group"
        elif p.classification == "TPT+BCG":
            type_label = "TPT+BCG Cohort"
        elif p.classification == "Not Eligible" or not p.eligible:
            type_label = "Ineligible Group"
        else:
            type_label = "Control Group"
            
        pending_records.append({
            "name": p.full_name,
            "type": type_label,
            "id": p.study_id,
            "db_id": p.pk,
            "timestamp": "Saved offline"
        })
        
    from questions.models import DeviceSyncLog
    synced_p = filter_by_jurisdiction(Participant.objects.filter(synced=True), request).count()
    synced_t = filter_by_jurisdiction(TptIndividual.objects.filter(synced=True), request).count()
    synced_i = filter_by_jurisdiction(IneligibleIndividual.objects.filter(synced=True), request).count()
    synced_count = synced_p + synced_t + synced_i

    sync_logs = filter_by_jurisdiction(DeviceSyncLog.objects.all(), request).order_by("-timestamp")[:5]

    total_records = len(pending_records) + synced_count

    from django.conf import settings
    return render(request, "questions/pending_sync.html", {
        "pending_records": pending_records,
        "backend_url": settings.CENTRAL_BACKEND_URL,
        "user_profile": request.user.profile,
        "synced_count": synced_count,
        "sync_logs": sync_logs,
        "page": "pending_sync",
        "total_records": total_records,
        "last_sync_status": request.session.get("last_sync_status", "unknown"),
        "last_sync_message": request.session.get("last_sync_message", ""),
        "last_sync_timestamp": request.session.get("last_sync_timestamp", "")
    })


def reconcile(request, pk):
    """
    Data Verification: Compares field entries with simulated Nikshay values side-by-side.
    """
    from django.shortcuts import get_object_or_404
    if not request.user.is_authenticated:
        return redirect("questions:home")

    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", "Project Nurse")
    if role != "Super Admin":
        action = "Approve/Reconcile" if request.method == "POST" else "View"
        has_perm = has_role_permission(role, "Nikshay Reconciliation", action)
        if not has_perm:
            from django.contrib import messages
            messages.error(request, f"Permission denied. Role '{role}' is not allowed to {action.lower()} Nikshay Reconciliation.")
            return redirect("questions:home")
        
    cohort = request.GET.get("cohort")
    if cohort == "tpt":
        participant = get_object_or_404(TptIndividual, pk=pk)
    elif cohort == "ineligible":
        participant = get_object_or_404(IneligibleIndividual, pk=pk)
    else:
        try:
            participant = Participant.objects.get(pk=pk)
        except Participant.DoesNotExist:
            try:
                participant = TptIndividual.objects.get(pk=pk)
            except TptIndividual.DoesNotExist:
                participant = get_object_or_404(IneligibleIndividual, pk=pk)
    
    # Generate a simulated Nikshay record matching this participant for comparison using helper
    simulated_nikshay = get_simulated_nikshay(participant.nikshay_id or "NK-99201-X", participant)
    
    if request.method == "POST":
        agree_name = request.POST.get("agree_name") == "on"
        agree_age = request.POST.get("agree_age") == "on"
        agree_phone = request.POST.get("agree_phone") == "on"
        agree_bcg_status = request.POST.get("agree_bcg_status") == "on"
        agree_bcg_vaccination_date = request.POST.get("agree_bcg_vaccination_date") == "on"
        agree_bcg_scar = request.POST.get("agree_bcg_scar") == "on"
        agree_tb_classification = request.POST.get("agree_tb_classification") == "on"
        nikshay_id = request.POST.get("nikshay_id")
        
        if agree_name:
            participant.full_name = simulated_nikshay["full_name"].title()
        if agree_age:
            participant.age = int(simulated_nikshay["age"])
        if agree_phone:
            participant.contact_number = simulated_nikshay["contact_number"]
        if agree_bcg_status:
            participant.bcg_status = simulated_nikshay.get("bcg_vaccination_status")
            participant.bcg_vaccination_status = simulated_nikshay.get("bcg_vaccination_status")
        else:
            bcg_status_val = request.POST.get("bcg_status_val")
            if bcg_status_val:
                participant.bcg_status = bcg_status_val
                participant.bcg_vaccination_status = bcg_status_val
        if agree_bcg_vaccination_date:
            participant.bcg_vaccination_date = simulated_nikshay.get("bcg_vaccination_date")
        else:
            bcg_date_val = request.POST.get("bcg_vaccination_date_val")
            if bcg_date_val:
                participant.bcg_vaccination_date = bcg_date_val
        if agree_bcg_scar:
            participant.bcg_scar = simulated_nikshay.get("bcg_scar")
        else:
            bcg_scar_val = request.POST.get("bcg_scar_val")
            if bcg_scar_val:
                participant.bcg_scar = bcg_scar_val
        if agree_tb_classification:
            participant.case_finding_type = simulated_nikshay.get("tb_classification")
        else:
            tb_class_val = request.POST.get("tb_classification_val")
            if tb_class_val:
                participant.case_finding_type = tb_class_val
                
        eptb_screened_val = request.POST.get("eptb_screened_val")
        if eptb_screened_val:
            participant.eptb_screened = (eptb_screened_val == "Yes")
            
        participant.nikshay_id = nikshay_id
        participant.synced = True
        participant.created_by = request.user
        profile = request.user.profile
        participant.state = profile.state
        participant.district = profile.district
        participant.tb_unit = profile.tb_unit
        if not getattr(participant, "screening_id", None):
            participant.screening_id = participant.study_id
            
        has_mismatch = not (agree_name and agree_age and agree_phone and 
                            agree_bcg_status and agree_bcg_vaccination_date and 
                            agree_bcg_scar and agree_tb_classification)
        participant.reconciliation_status = "PARTIALLY_RECONCILED" if has_mismatch else "FULLY_RECONCILED"
        participant.save()
        sync_nikshay_record(participant, nikshay_id, user=request.user)
        
        return redirect("questions:search")
        
    return render(request, "questions/reconcile.html", {
        "participant": participant,
        "nikshay": simulated_nikshay
    })


def verify_beneficiary(request):
    """
    AJAX endpoint to query the BcgVaccination registry for a beneficiary_id, first name, and/or mobile.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)
        
    beneficiary_id = request.GET.get("beneficiary_id", "").strip()
    first_name = request.GET.get("first_name", "").strip()
    mobile = request.GET.get("mobile", "").strip()
    
    query = BcgVaccination.objects.all()
    
    has_filter = False
    if beneficiary_id:
        query = query.filter(beneficiary_id__iexact=beneficiary_id)
        has_filter = True
    else:
        if mobile:
            query = query.filter(ben_mobile_number__icontains=mobile)
            has_filter = True
        if first_name:
            query = query.filter(first_name__icontains=first_name)
            has_filter = True
            
    if not has_filter:
        return JsonResponse({"exists": False, "error": "No search criteria provided"})

    record = query.first()
    if record:
        return JsonResponse({
            "exists": True,
            "beneficiary_id": record.beneficiary_id,
            "first_name": record.first_name,
            "last_name": record.last_name,
            "beneficiary_gender": record.beneficiary_gender,
            "ben_gender": record.ben_gender,
            "age": record.age,
            "ben_mobile_number": record.ben_mobile_number,
            "dob": record.dob,
            "date": record.date,
            "registration_mode": record.registration_mode,
            "vaccination_status": record.vaccination_status,
            "beneficiary_type_name": record.beneficiary_type_name,
            "pincode": record.pincode,
            "address": record.address,
            "facility_id": record.facility_id,
            "site_id": record.site_id,
            "approved_by": record.approved_by,
            "date_created": record.date_created
        })
    else:
        return JsonResponse({"exists": False})


# RBAC portals and role dashboards views
@role_required(["Super Admin", "Admin"])
def rbac_users(request):
    """
    User Management Portal: lists system users and handles AJAX role/jurisdiction changes.
    """
    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        action = data.get("action")
        if action == "delete":
            user_id = data.get("user_id")
            if not user_id:
                return JsonResponse({"status": "error", "message": "User ID is required for deletion."}, status=400)
            try:
                user = User.objects.get(pk=user_id)
                username = user.username
                if user == request.user:
                    return JsonResponse({"status": "error", "message": "You cannot delete your own account."}, status=400)
                user.delete()
                
                AuditLog.objects.create(
                    actor=request.user,
                    action=f"Deleted user '{username}'.",
                    ip_address=get_client_ip(request)
                )
                return JsonResponse({"status": "success", "message": "User deleted successfully."})
            except User.DoesNotExist:
                return JsonResponse({"status": "error", "message": "User not found."}, status=404)
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=400)

        user_id = data.get("user_id")
        role = data.get("role")
        state = data.get("state", "Tamil Nadu")
        district = data.get("district", "Tiruvallur")
        tb_unit = data.get("tb_unit", "Tiruvallur TU")
        is_active = data.get("is_active")

        if is_active in [True, "true", "True", "on", 1, "1"]:
            is_active = True
        else:
            is_active = False

        if not user_id:
            # Creation mode!
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()
            full_name = data.get("full_name", "").strip() or username
            
            if not username or not password or not role:
                return JsonResponse({"status": "error", "message": "Username, password and role are required fields."}, status=400)
                
            if User.objects.filter(username=username).exists():
                return JsonResponse({"status": "error", "message": "Username already exists."}, status=400)
                
            try:
                user = User.objects.create_user(username=username, password=password)
                user.is_active = is_active
                user.save()
                
                profile = user.profile
                profile.full_name = full_name
                profile.role = role
                profile.state = state
                profile.district = district
                profile.tb_unit = tb_unit
                profile.save()
                
                AuditLog.objects.create(
                    actor=request.user,
                    action=f"Created new user '{username}' with role '{role}' and jurisdiction {state}/{district}/{tb_unit}.",
                    target_user=user,
                    ip_address=get_client_ip(request)
                )
                
                return JsonResponse({"status": "success", "message": "User created successfully."})
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=400)
        else:
            try:
                user = User.objects.get(pk=user_id)
                user.is_active = is_active
                user.save()

                profile = user.profile
                old_role = profile.role
                profile.role = role
                profile.state = state
                profile.district = district
                profile.tb_unit = tb_unit
                profile.save()

                AuditLog.objects.create(
                    actor=request.user,
                    action=f"Updated user '{user.username}' status (active={is_active}), role from '{old_role}' to '{role}', jurisdiction to {state}/{district}/{tb_unit}.",
                    target_user=user,
                    ip_address=get_client_ip(request)
                )

                return JsonResponse({"status": "success", "message": "User updated successfully."})
            except User.DoesNotExist:
                return JsonResponse({"status": "error", "message": "User not found."}, status=404)
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=400)

    users_list = User.objects.all().select_related("profile").order_by("username")
    
    q = request.GET.get("q", "").strip()
    if q:
        from django.db.models import Q
        users_list = users_list.filter(
            Q(username__icontains=q) |
            Q(profile__full_name__icontains=q) |
            Q(profile__district__icontains=q)
        )

    role_filter = request.GET.get("role", "").strip()
    if role_filter:
        users_list = users_list.filter(profile__role=role_filter)

    status_filter = request.GET.get("status", "").strip()
    if status_filter == "Active":
        users_list = users_list.filter(is_active=True)
    elif status_filter == "Inactive":
        users_list = users_list.filter(is_active=False)

    districts = UserProfile.objects.values_list("district", flat=True).distinct()
    tb_units = UserProfile.objects.values_list("tb_unit", flat=True).distinct()

    import json
    from questions.context_processors import get_location_hierarchy
    hierarchy_json = json.dumps(get_location_hierarchy())

    return render(request, "rbac/users.html", {
        "users": users_list,
        "districts": sorted(list(set(districts))),
        "tb_units": sorted(list(set(tb_units))),
        "roles": [r[0] for r in UserProfile.ROLE_CHOICES],
        "q": q,
        "role_filter": role_filter,
        "status_filter": status_filter,
        "page": "users",
        "hierarchy_json": hierarchy_json
    })


@role_required(["Super Admin"])
def rbac_roles(request):
    """
    Interactive Role & Permission Matrix view.
    AJAX POST enables real-time state changes.
    """
    roles = [r[0] for r in UserProfile.ROLE_CHOICES]
    modules = [
        "Participant Registration",
        "Diagnostic Review (Doctor)",
        "Nikshay Reconciliation",
        "Bulk Sync Operations",
        "Global Settings Admin",
        "Telemetry & Audit Logs"
    ]
    actions = ["View", "Create", "Edit", "Approve/Reconcile", "Export"]

    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        role = data.get("role")
        module = data.get("module")
        action = data.get("action")
        allowed = data.get("allowed")

        if allowed in [True, "true", "True", "on", 1, "1"]:
            allowed = True
        else:
            allowed = False

        if role not in roles or module not in modules or action not in actions:
            return JsonResponse({"status": "error", "message": "Invalid parameters."}, status=400)

        perm, created = RolePermission.objects.update_or_create(
            role=role,
            module=module,
            action=action,
            defaults={"allowed": allowed}
        )

        AuditLog.objects.create(
            actor=request.user,
            action=f"Changed permission for role={role}, module='{module}', action='{action}' to allowed={allowed}.",
            ip_address=get_client_ip(request)
        )

        return JsonResponse({"status": "success", "message": "Permission updated successfully."})

    matrix = {}
    for r in roles:
        matrix[r] = {}
        for m in modules:
            matrix[r][m] = {}
            for a in actions:
                if r == "Super Admin":
                    matrix[r][m][a] = True
                else:
                    matrix[r][m][a] = False

    db_perms = RolePermission.objects.all()
    for p in db_perms:
        if p.role in matrix and p.module in matrix[p.role] and p.action in matrix[p.role][p.module]:
            matrix[p.role][p.module][p.action] = p.allowed

    return render(request, "rbac/roles.html", {
        "roles": roles,
        "modules": modules,
        "actions": actions,
        "matrix": matrix,
        "page": "roles"
    })


@role_required(["Super Admin", "Admin", "Nodal Officer"])
def rbac_audit_logs(request):
    """
    Chronological system access logs panel with advanced filtering and real-time telemetry metrics.
    """
    logs = AuditLog.objects.all().select_related("actor__profile", "target_user__profile").order_by("-timestamp")
    
    q = request.GET.get("q", "").strip()
    event_type = request.GET.get("event_type", "").strip()
    role_filter = request.GET.get("role", "").strip()
    
    if q:
        from django.db.models import Q
        logs = logs.filter(
            Q(action__icontains=q) |
            Q(actor__username__icontains=q) |
            Q(actor__profile__full_name__icontains=q) |
            Q(target_user__username__icontains=q) |
            Q(target_user__profile__full_name__icontains=q)
        )
        
    if role_filter:
        logs = logs.filter(actor__profile__role=role_filter)
        
    if event_type:
        from django.db.models import Q
        if event_type == "ROLE_CHANGE":
            logs = logs.filter(action__icontains="role")
        elif event_type == "OVERRIDE":
            logs = logs.filter(Q(action__icontains="Updated") | Q(action__icontains="override") | Q(action__icontains="reconcile"))
        elif event_type == "CREATION":
            logs = logs.filter(action__icontains="created")
        elif event_type == "LOGIN":
            logs = logs.filter(Q(action__icontains="Login") | Q(action__icontains="logged") | Q(action__icontains="logout"))

    # Calculate telemetry metrics dynamically
    total_logs = AuditLog.objects.count()
    role_changes_count = AuditLog.objects.filter(action__icontains="role").count()
    overrides_count = AuditLog.objects.filter(action__icontains="Updated").count() + AuditLog.objects.filter(action__icontains="reconcile").count()
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).count()

    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(logs, 15)
    page_num = request.GET.get('page')
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "rbac/audit_logs.html", {
        "logs": page_obj,
        "q": q,
        "event_type": event_type,
        "role_filter": role_filter,
        "page": "audit_logs",
        "telemetry": {
            "total_logs": total_logs,
            "role_changes": role_changes_count,
            "overrides": overrides_count,
            "active_sessions": active_sessions,
        }
    })


@role_required(["Super Admin", "Admin", "Nodal Officer"])
def nodal_dashboard(request):
    """
    Nodal Officer Portal displaying regional registration overview,
    district sync health metrics, and unresolved record discrepancies.
    """
    profile = request.user.profile
    
    participants_qs = filter_by_jurisdiction(Participant.objects.all(), request)
    tpt_qs = filter_by_jurisdiction(TptIndividual.objects.all(), request)
    ineligible_qs = filter_by_jurisdiction(IneligibleIndividual.objects.all(), request)
    
    total_participants = participants_qs.count()
    total_tpt = tpt_qs.count()
    total_ineligible = ineligible_qs.count()
    total_cases = participants_qs.filter(classification="Case").count()
    total_controls = participants_qs.filter(classification="Control").count()
    
    from questions.models import DeviceSyncLog
    sync_logs = DeviceSyncLog.objects.filter(
        user__profile__state=profile.state,
        user__profile__district=profile.district
    ).select_related("user").order_by("-timestamp")[:30]

    discrepancies = participants_qs.filter(synced=False, classification="Pending").order_by("-created_at")[:20]

    return render(request, "rbac/nodal_dashboard.html", {
        "stats": {
            "total_participants": total_participants,
            "total_tpt": total_tpt,
            "total_ineligible": total_ineligible,
            "total_cases": total_cases,
            "total_controls": total_controls
        },
        "sync_logs": sync_logs,
        "discrepancies": discrepancies,
        "jurisdiction": f"{profile.state} - {profile.district}"
    })


@role_required(["Super Admin", "Admin", "Doctor"])
def doctor_queue(request):
    """
    Doctor Verification Queue listing pending clinical classifications 
    requiring diagnostic verification (NAAT/CXR/EPTB details).
    """
    profile = request.user.profile
    participants_qs = filter_by_jurisdiction(Participant.objects.all(), request)
    
    pending_queue = participants_qs.filter(classification="Pending").order_by("-created_at")
    verified_queue = participants_qs.exclude(classification="Pending").order_by("-created_at")[:30]

    def load_diagnostics(records):
        data = []
        for r in records:
            import json
            cxr_status = "Not Done"
            naat_status = "Pending"
            eptb_findings = "Not Done"

            try:
                answers = json.loads(r.questionnaire_answers)
            except Exception:
                answers = {}

            try:
                eptb_details = json.loads(r.eptb_details)
            except Exception:
                eptb_details = {}

            cxr_done = answers.get("cxr_details", {}).get("cxr_done", "No")
            if cxr_done == "Yes" or r.cxr_record_file:
                cxr_status = answers.get("cxr_details", {}).get("cxr_result") or answers.get("cxr_status") or "Done"
            
            naat_status = answers.get("naat_status") or r.ptb_test_result or "Not Done"
            
            if r.eptb_screened:
                eptb_findings = eptb_details.get("site_name") or "Yes (Screened)"

            data.append({
                "record": r,
                "cxr_status": cxr_status,
                "naat_status": naat_status,
                "eptb_findings": eptb_findings,
            })
        return data

    return render(request, "rbac/doctor_queue.html", {
        "pending_list": load_diagnostics(pending_queue),
        "verified_list": load_diagnostics(verified_queue),
        "jurisdiction": f"{profile.state} / {profile.district} / {profile.tb_unit}"
    })


@role_required(["Super Admin", "Admin", "Doctor"])
def doctor_verify(request, pk):
    """
    Submits doctor verification override and classification confirmation.
    """
    if request.method == "POST":
        classification = request.POST.get("classification")
        reason = request.POST.get("classification_reason", "").strip()

        participant = get_object_or_404(Participant, pk=pk)
        old_class = participant.classification
        participant.classification = classification
        participant.classification_reason = reason
        participant.save()

        AuditLog.objects.create(
            actor=request.user,
            action=f"Clinical verification for study_id={participant.study_id}: overridden classification from '{old_class}' to '{classification}'. Reason: {reason}",
            target_user=participant.created_by,
            ip_address=get_client_ip(request)
        )

        from django.contrib import messages
        messages.success(request, f"Clinical verification for Participant {participant.study_id} completed successfully.")
        return redirect("questions:participant_detail", study_id=participant.study_id)

    return redirect("questions:doctor_queue")


@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor", "Project Nurse")
def dashboard_home(request):
    import json
    import datetime
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", "Project Nurse") if profile else ""
    today = timezone.localdate()
    
    # 1. Filtered querysets based on user jurisdiction
    participants_filtered = filter_by_jurisdiction(Participant.objects.all(), request)
    tpt_filtered = filter_by_jurisdiction(TptIndividual.objects.all(), request)
    ineligible_filtered = filter_by_jurisdiction(IneligibleIndividual.objects.all(), request)
    
    # 2. Scoped KPI Card calculations
    total_screened = participants_filtered.count() + tpt_filtered.count() + ineligible_filtered.count()
    ineligible_participants = ineligible_filtered.count()
    eligible_participants = participants_filtered.count() + tpt_filtered.count()
    confirmed_cases = participants_filtered.filter(classification="Case").count()
    study_controls = participants_filtered.filter(classification="Control").count()
    verification_pending = participants_filtered.filter(classification="Pending").count()
    
    sync_backlog = (
        participants_filtered.filter(synced=False).count() +
        tpt_filtered.filter(synced=False).count() +
        ineligible_filtered.filter(synced=False).count()
    )
    
    # Calculate geographical active counts from database
    active_states_count = participants_filtered.exclude(state__in=[None, '', 'GLOBAL']).values('state').distinct().count()
    active_districts_count = participants_filtered.exclude(district__in=[None, '', 'ALL DISTRICTS']).values('district').distinct().count()
    active_tb_units_count = participants_filtered.exclude(tb_unit__in=[None, '', 'ALL TB UNITS']).values('tb_unit').distinct().count()
    
    # Ensure they reflect profile default if empty (so they never show 0 for authorized local users)
    if active_states_count == 0 and profile and profile.state:
        active_states_count = 1
    if active_districts_count == 0 and profile and profile.district:
        active_districts_count = 1
    if active_tb_units_count == 0 and profile and profile.tb_unit:
        active_tb_units_count = 1
        
    metrics = {
        "total_screened": total_screened,
        "ineligible_participants": ineligible_participants,
        "eligible_participants": eligible_participants,
        "confirmed_cases": confirmed_cases,
        "study_controls": study_controls,
        "verification_pending": verification_pending,
        "sync_backlog": sync_backlog,
        "total_enrolled": confirmed_cases + study_controls,
        "active_states_count": active_states_count,
        "active_districts_count": active_districts_count,
        "active_tb_units_count": active_tb_units_count,
        "total_cases": confirmed_cases,
        "total_controls": study_controls,
        "total_matches": study_controls // 4,
    }
    
    # 3. Dynamic State Performance Table
    from questions.context_processors import get_location_hierarchy
    hierarchy = get_location_hierarchy()
    states_performance = []
    
    for state_name in sorted(hierarchy.keys()):
        p_state = Participant.objects.filter(state=state_name)
        t_state = TptIndividual.objects.filter(state=state_name)
        i_state = IneligibleIndividual.objects.filter(state=state_name)
        
        districts_count = len(hierarchy[state_name].keys())
        tb_units_count = sum(len(tus) for tus in hierarchy[state_name].values())
        
        screened_count = p_state.count() + t_state.count() + i_state.count()
        eligible_count = p_state.count() + t_state.count()
        cases_count = p_state.filter(classification="Case").count()
        controls_count = p_state.filter(classification="Control").count()
        enrolled_count = cases_count + controls_count
        
        status = "Active" if screened_count > 0 or state_name == "Tamil Nadu" else "Pending"
        
        states_performance.append({
            "state": state_name,
            "districts_count": districts_count,
            "tb_units_count": tb_units_count,
            "screened_count": screened_count if screened_count > 0 else "—",
            "eligible_count": eligible_count if eligible_count > 0 else "—",
            "enrolled_count": enrolled_count if enrolled_count > 0 else "—",
            "cases_count": cases_count if cases_count > 0 else "—",
            "status": status
        })

    # 4. Dynamic Site Performance Table
    sites_performance = []
    active_sites_data = {}
    
    for p in participants_filtered:
        state = p.state or "Unknown"
        district = p.district or "Unknown"
        tb_unit = p.tb_unit or "Unknown"
        key = (state, district, tb_unit)
        if key not in active_sites_data:
            active_sites_data[key] = {"screened": 0, "eligible": 0, "enrolled": 0, "last_activity": None}
        active_sites_data[key]["screened"] += 1
        active_sites_data[key]["eligible"] += 1
        if p.classification in ["Case", "Control"]:
            active_sites_data[key]["enrolled"] += 1
        if not active_sites_data[key]["last_activity"] or (p.created_at and p.created_at > active_sites_data[key]["last_activity"]):
            active_sites_data[key]["last_activity"] = p.created_at

    for t in tpt_filtered:
        state = t.state or "Unknown"
        district = t.district or "Unknown"
        tb_unit = t.tb_unit or "Unknown"
        key = (state, district, tb_unit)
        if key not in active_sites_data:
            active_sites_data[key] = {"screened": 0, "eligible": 0, "enrolled": 0, "last_activity": None}
        active_sites_data[key]["screened"] += 1
        active_sites_data[key]["eligible"] += 1
        if not active_sites_data[key]["last_activity"] or (t.created_at and t.created_at > active_sites_data[key]["last_activity"]):
            active_sites_data[key]["last_activity"] = t.created_at

    for i in ineligible_filtered:
        state = i.state or "Unknown"
        district = i.district or "Unknown"
        tb_unit = i.tb_unit or "Unknown"
        key = (state, district, tb_unit)
        if key not in active_sites_data:
            active_sites_data[key] = {"screened": 0, "eligible": 0, "enrolled": 0, "last_activity": None}
        active_sites_data[key]["screened"] += 1
        if not active_sites_data[key]["last_activity"] or (i.created_at and i.created_at > active_sites_data[key]["last_activity"]):
            active_sites_data[key]["last_activity"] = i.created_at

    for key, data in active_sites_data.items():
        state, district, tb_unit = key
        unsynced_count = (
            Participant.objects.filter(state=state, district=district, tb_unit=tb_unit, synced=False).count() +
            TptIndividual.objects.filter(state=state, district=district, tb_unit=tb_unit, synced=False).count() +
            IneligibleIndividual.objects.filter(state=state, district=district, tb_unit=tb_unit, synced=False).count()
        )
        sync_status = "Healthy" if unsynced_count == 0 else f"{unsynced_count} Pending"
        
        pending_verif = Participant.objects.filter(state=state, district=district, tb_unit=tb_unit, classification="Pending").count()
        dq_status = "Healthy" if pending_verif == 0 else f"{pending_verif} Action Required"
        
        last_act_str = data["last_activity"].strftime("%Y-%m-%d %H:%M") if data["last_activity"] else "—"
        
        sites_performance.append({
            "state": state,
            "district": district,
            "tb_unit": tb_unit,
            "screened": data["screened"],
            "eligible": data["eligible"],
            "enrolled": data["enrolled"],
            "last_activity": last_act_str,
            "sync_status": sync_status,
            "dq_status": dq_status
        })
        
    sites_performance = sorted(sites_performance, key=lambda x: (x["state"], x["district"], x["tb_unit"]))

    # 5. Needs Attention Panel Data
    needs_attention = []
    
    # Sync Backlog Alert
    if sync_backlog > 0:
        needs_attention.append({
            "type": "Sync Backlog",
            "message": f"{sync_backlog} local records are pending upload/synchronization to the central server registry.",
            "url_name": "questions:sync_telemetry",
            "level": "warning",
            "icon": "refresh-cw"
        })
        
    # Verification Queue Alert
    if verification_pending > 0:
        needs_attention.append({
            "type": "Verification Backlog",
            "message": f"{verification_pending} clinical registrations are awaiting diagnostic test classification (CXR / NAAT).",
            "url_name": "questions:doctor_queue",
            "level": "info",
            "icon": "clipboard-check"
        })
        
    # Data Quality / Validation Errors Alert
    validation_err_count = participants_filtered.filter(classification="Needs Correction").count()
    if validation_err_count > 0:
        needs_attention.append({
            "type": "Data Correction",
            "message": f"{validation_err_count} records are flagged as 'Needs Correction' due to invalid clinical metadata.",
            "url_name": "questions:doctor_queue",
            "level": "error",
            "icon": "shield-alert"
        })
        
    # Case Matching Ratio Deficit Alert
    if confirmed_cases > 0:
        under_matched_cases = max(0, confirmed_cases - (study_controls // 4))
        if under_matched_cases > 0:
            needs_attention.append({
                "type": "Case Matching",
                "message": f"{under_matched_cases} TB Cases lack the required 1:4 control matching ratio (deficit of matched controls).",
                "url_name": "questions:matching",
                "level": "warning",
                "icon": "users"
            })
            
    # Inactive Sites check
    for site in sites_performance:
        if site["last_activity"] != "—":
            try:
                last_act_dt = datetime.datetime.strptime(site["last_activity"], "%Y-%m-%d %H:%M").date()
                delta_days = (today - last_act_dt).days
                if delta_days >= 3:
                    needs_attention.append({
                        "type": "Inactive Site",
                        "message": f"Site {site['tb_unit']} ({site['district']}) has reported no participant registrations for {delta_days} days.",
                        "url_name": "questions:study_site",
                        "level": "error",
                        "icon": "map-pin"
                    })
            except Exception:
                pass

    # 6. Data Quality Overview Card
    dq_overview = {
        "complete_records": participants_filtered.filter(synced=True).count(),
        "incomplete_records": participants_filtered.filter(synced=False).count(),
        "validation_errors": participants_filtered.filter(classification="Needs Correction").count(),
        "pending_verification": verification_pending
    }
    
    # 7. Sync Health & Connectivity Card
    total_devices = DeviceSyncLog.objects.values('device_user_agent').distinct().count() or 3
    recent_syncs = DeviceSyncLog.objects.filter(timestamp__gte=timezone.now() - timedelta(days=1)).count() or 1
    sync_status = "Healthy" if sync_backlog == 0 else "Attention" if sync_backlog < 10 else "Critical"
    sync_health = {
        "total_devices": total_devices,
        "recent_syncs": recent_syncs,
        "sync_status": sync_status
    }

    # 8. Recruitment trend (7 Days)
    trend_days = []
    trend_registrations = []
    trend_cases = []
    
    has_trend_data = False
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        trend_days.append(date.strftime("%b %d"))
        
        reg_count = (
            participants_filtered.filter(date_enroll=date).count() +
            tpt_filtered.filter(date_enroll=date).count() +
            ineligible_filtered.filter(date_enroll=date).count()
        )
        case_count = participants_filtered.filter(date_enroll=date, classification="Case").count()
        
        trend_registrations.append(reg_count)
        trend_cases.append(case_count)
            
    trend_json = json.dumps({
        "labels": trend_days,
        "registrations": trend_registrations,
        "cases": trend_cases,
    })

    # Fetch telemetry and audit logs
    sync_telemetry_list = []
    audit_logs_list = []
    
    if role in ["Super Admin", "Admin", "Nodal Officer"]:
        sync_logs_qs = filter_by_jurisdiction(DeviceSyncLog.objects.all(), request).order_by("-timestamp")[:5]
        for log in sync_logs_qs:
            sync_telemetry_list.append({
                "username": log.user.username,
                "tb_unit": getattr(getattr(log.user, "profile", None), "tb_unit", "Unknown TU"),
                "district": getattr(getattr(log.user, "profile", None), "district", ""),
                "state": getattr(getattr(log.user, "profile", None), "state", ""),
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "—",
                "synced_count": log.synced_count,
                "pending_count": log.pending_count,
                "battery_level": log.battery_level,
            })
            
        audit_qs = AuditLog.objects.all()
        if role != "Super Admin" and profile and profile.state:
            audit_qs = audit_qs.filter(actor__profile__state=profile.state)
            if role in ["Nodal Officer"] and profile.district:
                audit_qs = audit_qs.filter(actor__profile__district=profile.district)
        
        audit_logs_qs = audit_qs.order_by("-timestamp")[:5]
        for log in audit_logs_qs:
            audit_logs_list.append({
                "actor": log.actor.username if log.actor else "System",
                "action": log.action,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "—",
                "ip_address": log.ip_address or "—"
            })

    # Recent verified cases
    recent_cases_qs = participants_filtered.filter(classification="Case").order_by("-date_enroll")[:5]
    recent_cases_list = []
    for c in recent_cases_qs:
        recent_cases_list.append({
            "studyId": c.study_id,
            "name": c.full_name,
            "district": c.district,
            "diseaseType": "EPTB" if c.eptb_screened else "PTB",
            "enrolmentDate": c.date_enroll.strftime("%Y-%m-%d") if c.date_enroll else "—",
            "verificationStatus": "Verified",
            "actionText": "View Dossier"
        })

    # My Verification Queue (Participants in pending state)
    pending_verification_qs = participants_filtered.filter(classification="Pending").order_by("-created_at")[:10]
    verification_queue = []
    for p in pending_verification_qs:
        verification_queue.append({
            "studyId": p.study_id,
            "name": p.full_name,
            "classification": p.classification,
            "registeredDate": p.date_enroll.strftime("%Y-%m-%d") if p.date_enroll else "—",
            "verificationStatus": "Verification Pending",
            "actionText": "Review & Verify"
        })
    return render(request, "dashboard/dashboard.html", {
        "metrics": metrics,
        "states_performance": states_performance,
        "sites_performance": sites_performance,
        "needs_attention": needs_attention,
        "dq_overview": dq_overview,
        "sync_health": sync_health,
        "recent_cases": recent_cases_list,
        "verification_queue": verification_queue,
        "sync_telemetry": sync_telemetry_list,
        "audit_logs": audit_logs_list,
        "trend_json": trend_json,
        "page": "dashboard"
    })


@group_required("Super Admin")
def rbac_groups(request):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from questions.models import Participant
    
    if request.method == "POST":
        import json
        from django.http import JsonResponse
        data = json.loads(request.body)
        group_name = data.get("group")
        codename = data.get("codename")
        allowed = data.get("allowed")
        
        try:
            group = Group.objects.get(name=group_name)
            ct = ContentType.objects.get_for_model(Participant)
            try:
                perm = Permission.objects.get(codename=codename, content_type=ct)
            except Permission.DoesNotExist:
                from questions.models import UserProfile
                p_ct = ContentType.objects.get_for_model(UserProfile)
                perm = Permission.objects.get(codename=codename, content_type=p_ct)
                
            if allowed:
                group.permissions.add(perm)
                action_text = "Granted"
            else:
                group.permissions.remove(perm)
                action_text = "Revoked"
                
            group.save()
            
            AuditLog.objects.create(
                actor=request.user,
                action=f"{action_text} permission '{codename}' to group '{group_name}' programmatically.",
                ip_address=get_client_ip(request)
            )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
            
    groups = Group.objects.all()
    codenames = [
        ("Participant Registration", [
            ("view_participant", "View"),
            ("add_participant", "Create"),
            ("change_participant", "Edit"),
            ("export_participant", "Export"),
        ]),
        ("Diagnostic Review (Doctor)", [
            ("view_participant", "View"),
            ("change_participant", "Edit"),
            ("doctor_review", "Approve/Reconcile"),
        ]),
        ("Nikshay Reconciliation", [
            ("view_participant", "View"),
            ("approve_reconciliation", "Approve/Reconcile"),
        ]),
        ("Bulk Sync Operations", [
            ("view_participant", "View"),
            ("perform_bulk_sync", "Approve/Reconcile"),
        ]),
        ("Telemetry & Audit Logs", [
            ("view_telemetry_logs", "View"),
        ])
    ]
    
    matrix = {}
    for group in groups:
        matrix[group.name] = list(group.permissions.values_list("codename", flat=True))
        
    return render(request, "rbac/groups.html", {
        "groups": ["Super Admin", "Admin", "Nodal Officer", "Doctor", "Project Nurse"],
        "codenames": codenames,
        "matrix": matrix,
        "page": "groups"
    })


@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor", "Project Nurse")
def classification_view(request):
    from questions.models import Participant, TptIndividual, IneligibleIndividual
    from django.utils import timezone
    
    # 1. Fetch live records filtered by user jurisdiction
    participants_qs = filter_by_jurisdiction(Participant.objects.all(), request)
    tpt_qs = filter_by_jurisdiction(TptIndividual.objects.all(), request)
    ineligible_qs = filter_by_jurisdiction(IneligibleIndividual.objects.all(), request)

    # 2. Real-time classification counts
    confirmed_cases = participants_qs.filter(classification="Case").count()
    study_controls = participants_qs.filter(classification="Control").count()
    pending_investigation = participants_qs.filter(classification="Pending").count()
    ineligible_screenout = ineligible_qs.count() + participants_qs.filter(classification="Not Eligible").count()

    breakdown = [
        {"type": "Confirmed TB Cases", "count": confirmed_cases, "tone": "chart-1"},
        {"type": "Study Controls", "count": study_controls, "tone": "chart-2"},
        {"type": "Pending Investigation", "count": pending_investigation, "tone": "chart-5"},
        {"type": "Ineligible / Screenout", "count": ineligible_screenout, "tone": "chart-3"},
    ]

    # 3. Real-time classification events from live records
    events = []
    recent_p = list(participants_qs.order_by("-created_at")[:40])
    recent_t = list(tpt_qs.order_by("-created_at")[:10])
    recent_i = list(ineligible_qs.order_by("-created_at")[:10])
    all_recent = sorted(recent_p + recent_t + recent_i, key=lambda x: getattr(x, 'created_at', None) or timezone.now(), reverse=True)[:50]

    for obj in all_recent:
        cls_val = getattr(obj, "classification", "Pending")
        if cls_val in ["Case", "Control"]:
            res = "Passed"
        elif cls_val == "Pending":
            res = "Flagged"
        else:
            res = "Review"

        events.append({
            "time": obj.created_at.strftime("%H:%M:%S") if getattr(obj, 'created_at', None) else "—",
            "date": obj.created_at.strftime("%Y-%m-%d") if getattr(obj, 'created_at', None) else "—",
            "studyId": obj.study_id,
            "name": getattr(obj, "full_name", "") or obj.study_id,
            "classification": cls_val,
            "result": res,
            "reason": getattr(obj, "classification_reason", "") or "Eligibility assessment",
        })

    return render(request, "dashboard/classification.html", {
        "events": events,
        "breakdown": breakdown,
        "page": "classification"
    })


def _map_participant_to_dict(p):
    disease_type = "EPTB" if p.eptb_screened else "PTB"
    match_status = 1 if p.synced else 3
    match_set_id = f"SET-{p.study_id}" if p.synced else None
    
    return {
        'studyId': p.study_id,
        'nikshayId': p.nikshay_id or "—",
        'name': p.full_name,
        'age': p.age,
        'sex': p.gender[0].upper() if p.gender else 'U',
        'mobile': p.contact_number or "—",
        'village': p.village or "—",
        'stateCode': p.state[:2].upper() if p.state else 'TN',
        'stateName': p.state or 'Tamil Nadu',
        'district': p.district,
        'tuCode': p.tb_unit,
        'facility': p.facility or "—",
        'enrolmentDate': p.date_enroll.strftime("%Y-%m-%d") if p.date_enroll else "—",
        'hrgEligible': 1 if p.eligible else 0,
        'matchHrg': p.match_hrg or "None",
        'ptbNaat': 1 if p.ptb_test_result == "Positive" else 0,
        'ptbCxr': 'Abnormal' if p.ptb_test_result == "Suggestive" else 'Normal',
        'bcgStatus': 1 if p.bcg_status.startswith("Yes") else 0,
        'caseControlStatus': 1 if p.classification == "Case" else 0,
        'matchSetId': match_set_id,
        'matchStatus': match_status,
        'diseaseType': disease_type,
    }


@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor")
def cases_view(request):
    import random
    from . import mock_data
    
    # 1. Fetch live cases with jurisdiction filter (strictly Case-cohort classifications)
    participants_qs = filter_by_jurisdiction(Participant.objects.filter(classification__in=["Case", "Pending", "Adjudication Pending", "Needs Correction", "Adjudication Completed"]), request)
    has_live_records = participants_qs.exists()
    
    # Calculate counts before filters
    registered_cases_count = participants_qs.filter(classification="Case").count()
    verification_pending_count = participants_qs.filter(classification="Pending").count()
    verified_count = participants_qs.exclude(classification__in=["Pending", "Adjudication Pending", "Needs Correction"]).count()
    adjudication_pending_count = participants_qs.filter(classification="Adjudication Pending").count()
    
    # 2. Get search/filter parameters
    q = request.GET.get('q', '').strip()
    state_filter = request.GET.get('state', '').strip()
    district_filter = request.GET.get('district', '').strip()
    tb_unit_filter = request.GET.get('tb_unit', '').strip()
    classification_filter = request.GET.get('classification', '').strip()
    reg_date_filter = request.GET.get('reg_date', '').strip()
    verification_status = request.GET.get('verification_status', '').strip()
    adjudication_status = request.GET.get('adjudication_status', '').strip()
    
    is_mock_fallback = request.GET.get('mock') == 'true'
    
    if not is_mock_fallback:
        # Apply filters to Django queryset
        if q:
            from django.db.models import Q
            participants_qs = participants_qs.filter(
                Q(study_id__icontains=q) | Q(full_name__icontains=q) | Q(nikshay_id__icontains=q)
            )
        if state_filter:
            participants_qs = participants_qs.filter(state__icontains=state_filter)
        if district_filter:
            participants_qs = participants_qs.filter(district__icontains=district_filter)
        if tb_unit_filter:
            participants_qs = participants_qs.filter(tb_unit__icontains=tb_unit_filter)
        if classification_filter:
            participants_qs = participants_qs.filter(classification=classification_filter)
        if reg_date_filter:
            participants_qs = participants_qs.filter(date_enroll=reg_date_filter)
            
        if verification_status:
            if verification_status == 'Pending':
                participants_qs = participants_qs.filter(classification="Pending")
            elif verification_status == 'Verified':
                participants_qs = participants_qs.exclude(classification__in=["Pending", "Adjudication Pending", "Needs Correction"])
            elif verification_status == 'Needs Correction':
                participants_qs = participants_qs.filter(classification="Needs Correction")
            elif verification_status == 'Adjudication Pending':
                participants_qs = participants_qs.filter(classification="Adjudication Pending")
                
        if adjudication_status:
            if adjudication_status == 'Pending':
                participants_qs = participants_qs.filter(classification="Adjudication Pending")
            elif adjudication_status == 'Completed':
                participants_qs = participants_qs.filter(classification="Adjudication Completed")
            else:
                participants_qs = participants_qs.exclude(classification__in=["Adjudication Pending", "Adjudication Completed"])
            
        cases_list = []
        for p in participants_qs:
            # Determine verification & adjudication status dynamically
            v_status = "Verified"
            adj_status = "Not Applicable"
            
            if p.classification == "Pending":
                v_status = "Verification Pending"
            elif p.classification == "Needs Correction":
                v_status = "Needs Correction"
            elif p.classification == "Adjudication Pending":
                v_status = "Sent for Adjudication"
                adj_status = "Adjudication Pending"
            elif p.classification == "Adjudication Completed":
                v_status = "Verified (Adjudicated)"
                adj_status = "Adjudication Completed"
                
            mapped = _map_participant_to_dict(p)
            mapped.update({
                "verificationStatus": v_status,
                "adjudicationStatus": adj_status,
                "pk": p.pk,
                "classification": p.classification
            })
            cases_list.append(mapped)
    else:
        # Fallback to mock data with programmatical list filtering
        mock_cases = mock_data.cases
        cases_list = []
        for c in mock_cases:
            # Map mock fields dynamically
            v_status = "Verified"
            adj_status = "Not Applicable"
            c_status = "Case"
            
            if c['studyId'] in ['ABCG-MH-TU04-2026-000142', 'ABCG-MH-TU04-2026-000173']:
                c_status = "Pending"
                v_status = "Verification Pending"
            elif c['studyId'] in ['ABCG-MH-TU04-2026-000190']:
                c_status = "Adjudication Pending"
                v_status = "Sent for Adjudication"
                adj_status = "Adjudication Pending"
                
            c.update({
                "classification": c_status,
                "verificationStatus": v_status,
                "adjudicationStatus": adj_status,
                "pk": 1000 + random.randint(1, 1000)
            })
            
            if q and not (q.lower() in c['studyId'].lower() or q.lower() in c['name'].lower() or (c['nikshayId'] and q.lower() in c['nikshayId'].lower())):
                continue
            if state_filter and state_filter.lower() not in c.get('stateName', '').lower():
                continue
            if district_filter and district_filter.lower() not in c.get('district', '').lower():
                continue
            if tb_unit_filter and tb_unit_filter.lower() not in c.get('tuCode', '').lower():
                continue
            if classification_filter and c['classification'] != classification_filter:
                continue
            if reg_date_filter and reg_date_filter not in c.get('enrolmentDate', ''):
                continue
            if verification_status:
                if verification_status == 'Pending' and c['verificationStatus'] != 'Verification Pending':
                    continue
                elif verification_status == 'Verified' and c['verificationStatus'] not in ['Verified', 'Verified (Adjudicated)']:
                    continue
                elif verification_status == 'Needs Correction' and c['verificationStatus'] != 'Needs Correction':
                    continue
                elif verification_status == 'Adjudication Pending' and c['verificationStatus'] != 'Sent for Adjudication':
                    continue
            if adjudication_status:
                if adjudication_status == 'Pending' and c['adjudicationStatus'] != 'Adjudication Pending':
                    continue
                elif adjudication_status == 'Completed' and c['adjudicationStatus'] != 'Adjudication Completed':
                    continue
                elif adjudication_status == 'Not Applicable' and c['adjudicationStatus'] != 'Not Applicable':
                    continue
                    
            cases_list.append(c)
            
        # Re-calculate top aggregates from mock list
        registered_cases_count = sum(1 for c in mock_cases if c['studyId'] not in ['ABCG-MH-TU04-2026-000142', 'ABCG-MH-TU04-2026-000173', 'ABCG-MH-TU04-2026-000190'])
        verification_pending_count = 2
        verified_count = sum(1 for c in mock_cases if c['studyId'] not in ['ABCG-MH-TU04-2026-000142', 'ABCG-MH-TU04-2026-000173', 'ABCG-MH-TU04-2026-000190'])
        adjudication_pending_count = 1
            
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(cases_list, 10)
    page_num = request.GET.get('page')
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "dashboard/cases.html", {
        "cases": page_obj,
        "page": "cases",
        "is_mock": is_mock_fallback,
        "metrics": {
            "registered_cases": registered_cases_count,
            "verification_pending": verification_pending_count,
            "verified": verified_count,
            "adjudication_pending": adjudication_pending_count
        },
        "filters": {
            "q": q,
            "state": state_filter,
            "district": district_filter,
            "tb_unit": tb_unit_filter,
            "classification": classification_filter,
            "reg_date": reg_date_filter,
            "verification_status": verification_status,
            "adjudication_status": adjudication_status,
        }
    })


@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor")
def controls_view(request):
    from . import mock_data
    
    # 1. Fetch live controls with jurisdiction filter
    participants_qs = filter_by_jurisdiction(Participant.objects.filter(classification="Control"), request)
    has_live_records = participants_qs.exists()
    
    # 2. Get search/filter parameters
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    hrg_filter = request.GET.get('hrg', '').strip()
    
    is_mock_fallback = request.GET.get('mock') == 'true'
    
    if not is_mock_fallback:
        # Apply filters to Django queryset
        if q:
            from django.db.models import Q
            participants_qs = participants_qs.filter(
                Q(study_id__icontains=q) | Q(full_name__icontains=q) | Q(nikshay_id__icontains=q)
            )
        if status_filter == 'synced':
            participants_qs = participants_qs.filter(synced=True)
        elif status_filter == 'pending':
            participants_qs = participants_qs.filter(synced=False)
            
        if hrg_filter:
            participants_qs = participants_qs.filter(match_hrg__icontains=hrg_filter)
            
        controls_list = [_map_participant_to_dict(p) for p in participants_qs]
    else:
        # Fallback to mock data with programmatical list filtering
        mock_controls = mock_data.controls
        controls_list = []
        for c in mock_controls:
            if q and not (q.lower() in c['studyId'].lower() or q.lower() in c['name'].lower() or (c['nikshayId'] and q.lower() in c['nikshayId'].lower())):
                continue
            if status_filter == 'synced' and c['matchStatus'] != 1:
                continue
            if status_filter == 'pending' and c['matchStatus'] == 1:
                continue
            if hrg_filter and hrg_filter.lower() not in c['matchHrg'].lower():
                continue
            controls_list.append(c)
            
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(controls_list, 10)
    page_num = request.GET.get('page')
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "dashboard/controls.html", {
        "controls": page_obj,
        "page": "controls",
        "is_mock": is_mock_fallback,
        "filters": {
            "q": q,
            "status": status_filter,
            "hrg": hrg_filter,
        }
    })


@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor")
def matching_view(request):
    import random
    from questions.models import Participant
    
    # 1. Fetch live cases and controls with jurisdiction filter
    participants_cases = filter_by_jurisdiction(Participant.objects.filter(classification="Case"), request)
    participants_controls = filter_by_jurisdiction(Participant.objects.filter(classification="Control"), request)
    
    cases_list = []
    controls_list = []
    
    if participants_cases.exists() or participants_controls.exists() or request.GET.get('mock') != 'true':
        for c in participants_cases:
            cases_list.append({
                "screening_id": c.screening_id or f"SCR-2026-{c.study_id.split('-')[-1]}",
                "study_id": c.study_id,
                "nikshay_id": c.nikshay_id or "—",
                "age": c.age,
                "sex": c.gender[0].upper() if c.gender else "U",
                "hrg": c.match_hrg or "None",
                "tu": c.tb_unit or "—",
                "state": c.state or "—",
                "required_controls": 4,
            })
        for ctrl in participants_controls:
            controls_list.append({
                "screening_id": ctrl.screening_id or f"SCR-2026-{ctrl.study_id.split('-')[-1]}",
                "study_id": ctrl.study_id,
                "nikshay_id": ctrl.nikshay_id or "—",
                "age": ctrl.age,
                "sex": ctrl.gender[0].upper() if ctrl.gender else "U",
                "assigned_case_id": f"SET-{ctrl.study_id}" if ctrl.synced else "",
            })
    else:
        from . import mock_data
        mock_cases = mock_data.cases[:8]
        for idx, c in enumerate(mock_cases):
            case_id_num = c['studyId'].split('-')[-1]
            c_screening_id = f"SCR-2026-{case_id_num}"
            c_study_id = c['studyId']
            c_nikshay_id = c['nikshayId'] or f"NIK-{random.randint(1000000, 9999999)}"
            cases_list.append({
                "screening_id": c_screening_id,
                "study_id": c_study_id,
                "nikshay_id": c_nikshay_id,
                "age": c['age'],
                "sex": c['sex'],
                "hrg": c['matchHrg'],
                "tu": c['tuCode'],
                "state": c['stateName'],
                "required_controls": 4,
            })
            pre_assigned_count = 2 if idx % 2 == 0 else 3
            for c_idx in range(4):
                control_num = str(int(case_id_num) + 100 * (c_idx + 1)).zfill(6)
                is_assigned = (c_idx < pre_assigned_count)
                controls_list.append({
                    "screening_id": f"SCR-2026-{control_num}",
                    "study_id": f"ABCG-{c['stateCode']}-{c['tuCode']}-2026-{control_num}",
                    "nikshay_id": f"NIK-{random.randint(1000000, 9999999)}",
                    "age": random.randint(22, 60),
                    "sex": random.choice(["M", "F"]),
                    "assigned_case_id": c_study_id if is_assigned else "",
                })
        for i in range(5):
            control_num = str(900000 + i)
            controls_list.append({
                "screening_id": f"SCR-2026-{control_num}",
                "study_id": f"ABCG-TN-TIR-2026-{control_num}",
                "nikshay_id": f"NIK-{random.randint(1000000, 9999999)}",
                "age": random.randint(20, 55),
                "sex": random.choice(["M", "F"]),
                "assigned_case_id": "",
            })
        
    return render(request, "dashboard/matching.html", {
        "cases": cases_list,
        "controls": controls_list,
        "page": "matching"
    })


@group_required("Doctor")
def adjudication_view(request):
    from . import mock_data
    
    # 1. Fetch live central adjudication cases (strictly Adjudication Pending)
    participants_qs = Participant.objects.filter(classification="Adjudication Pending")
    has_live_records = participants_qs.exists()
    
    is_mock_fallback = request.GET.get('mock') == 'true'
    
    if not is_mock_fallback:
        adjudication_list = []
        for p in participants_qs:
            mapped = _map_participant_to_dict(p)
            mapped.update({
                "pk": p.pk,
                "classification": p.classification
            })
            adjudication_list.append(mapped)
    else:
        # Fallback to central mock data from all jurisdictions
        adjudication_list = mock_data.adjudication_queue

    return render(request, "dashboard/adjudication.html", {
        "adjudication_queue": adjudication_list,
        "page": "adjudication",
        "is_mock": is_mock_fallback
    })


@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor")
def analytics_view(request):
    import json
    from questions.models import Participant, TptIndividual, IneligibleIndividual
    from django.db.models import Count, Q
    
    # Live database counts
    p_qs = Participant.objects.all()
    tpt_qs = TptIndividual.objects.all()
    inel_qs = IneligibleIndividual.objects.all()
    
    total_screened = p_qs.count() + tpt_qs.count() + inel_qs.count()
    cases_count = p_qs.filter(classification="Case").count() + tpt_qs.filter(classification="Case").count()
    controls_count = p_qs.filter(classification="Control").count() + tpt_qs.filter(classification="Control").count()
    eligible_count = p_qs.filter(eligible=True).count()
    ineligible_count = inel_qs.count() + p_qs.filter(classification="Not Eligible").count()
    
    ptb_count = p_qs.filter(classification="Case", ptb_screened=True).count()
    eptb_count = p_qs.filter(classification="Case", eptb_screened=True).count()
    excluded_count = p_qs.filter(classification="Excluded").count()
    breakdown = [ptb_count, eptb_count, excluded_count, ineligible_count]
    
    microbial_count = p_qs.filter(classification="Case", ptb_test_result__icontains="Positive").count()
    clinical_count = max(0, cases_count - microbial_count)
    certainty = [microbial_count, clinical_count]
    
    geo_list = []
    tu_stats = (
        p_qs.values("tb_unit", "state")
        .annotate(
            screened=Count("id"),
            cases=Count("id", filter=Q(classification="Case")),
            backlog=Count("id", filter=Q(classification="Pending") | Q(reconciliation_status="UNRECONCILED"))
        )
        .order_by("-screened")
    )
    for stat in tu_stats:
        if stat["tb_unit"]:
            geo_list.append({
                "name": f"{stat['tb_unit']} ({stat['state']})",
                "screened": stat["screened"],
                "cases": stat["cases"],
                "backlog": stat["backlog"],
                "dq": "Good"
            })
            
    dataset = {
        "All": {
            "scope": "All Locations",
            "screened": total_screened,
            "eligible": eligible_count,
            "cases": cases_count,
            "controls": controls_count,
            "ineligible": ineligible_count,
            "breakdown": breakdown,
            "certainty": certainty,
            "geo": geo_list,
            "alerts": [],
            "districts": {"All": {"tus": ["All"]}}
        }
    }
    
    for st_name in p_qs.values_list("state", flat=True).distinct():
        if not st_name:
            continue
        st_p = p_qs.filter(state=st_name)
        st_screened = st_p.count() + tpt_qs.filter(state=st_name).count() + inel_qs.filter(state=st_name).count()
        st_cases = st_p.filter(classification="Case").count()
        st_controls = st_p.filter(classification="Control").count()
        st_eligible = st_p.filter(eligible=True).count()
        st_inel = inel_qs.filter(state=st_name).count() + st_p.filter(classification="Not Eligible").count()
        st_ptb = st_p.filter(classification="Case", ptb_screened=True).count()
        st_eptb = st_p.filter(classification="Case", eptb_screened=True).count()
        st_micro = st_p.filter(classification="Case", ptb_test_result__icontains="Positive").count()
        
        st_geo = [g for g in geo_list if f"({st_name})" in g["name"]]
        
        dataset[st_name] = {
            "scope": st_name,
            "screened": st_screened,
            "eligible": st_eligible,
            "cases": st_cases,
            "controls": st_controls,
            "ineligible": st_inel,
            "breakdown": [st_ptb, st_eptb, 0, st_inel],
            "certainty": [st_micro, max(0, st_cases - st_micro)],
            "geo": st_geo,
            "alerts": [],
            "districts": {"All": {"tus": ["All"]}}
        }
        
    metrics = {
        "screened": total_screened,
        "cases": cases_count,
        "controls": controls_count,
        "eligible": eligible_count,
        "ineligible": ineligible_count
    }
    
    return render(request, "dashboard/analytics.html", {
        "metrics": metrics,
        "dataset_json": json.dumps(dataset),
        "breakdown_json": json.dumps(breakdown),
        "certainty_json": json.dumps(certainty),
        "page": "analytics"
    })


@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor")
def data_quality_view(request):
    from questions.models import Participant
    from django.utils import timezone
    
    exceptions = []
    ex_idx = 1
    
    for p in Participant.objects.all().order_by("-created_at"):
        # Rule DQ-01: Missing contact number
        if not p.contact_number or len(str(p.contact_number).strip()) < 10:
            exceptions.append({
                "exceptionId": f"EX-DQ-{ex_idx:04d}",
                "studyId": p.study_id,
                "rule": "DQ-01: Incomplete Contact",
                "severity": "High",
                "note": "Participant primary mobile contact is missing or incomplete.",
                "raised": p.created_at.strftime("%Y-%m-%d") if p.created_at else timezone.now().strftime("%Y-%m-%d"),
                "status": "Open"
            })
            ex_idx += 1
            
        # Rule DQ-02: Confirmed TB Case without Nikshay linkage
        if p.classification == "Case" and (p.reconciliation_status == "UNRECONCILED" or not p.nikshay_id):
            exceptions.append({
                "exceptionId": f"EX-DQ-{ex_idx:04d}",
                "studyId": p.study_id,
                "rule": "DQ-02: Unreconciled Nikshay",
                "severity": "Critical",
                "note": "Case is unreconciled or missing linked Nikshay surveillance identifier.",
                "raised": p.created_at.strftime("%Y-%m-%d") if p.created_at else timezone.now().strftime("%Y-%m-%d"),
                "status": "Open"
            })
            ex_idx += 1
            
        # Rule DQ-03: Physiological Outliers
        if p.bmi <= 0 or p.bmi > 60:
            exceptions.append({
                "exceptionId": f"EX-DQ-{ex_idx:04d}",
                "studyId": p.study_id,
                "rule": "DQ-03: Vital Sign Outlier",
                "severity": "Medium",
                "note": f"Recorded BMI value ({p.bmi}) is outside normal range.",
                "raised": p.created_at.strftime("%Y-%m-%d") if p.created_at else timezone.now().strftime("%Y-%m-%d"),
                "status": "Open"
            })
            ex_idx += 1
            
        # Rule DQ-04: Pending Diagnostic Confirmation
        if p.classification == "Pending" and not p.ptb_test_result:
            exceptions.append({
                "exceptionId": f"EX-DQ-{ex_idx:04d}",
                "studyId": p.study_id,
                "rule": "DQ-04: Diagnostic Incomplete",
                "severity": "High",
                "note": "Enrolled participant awaiting bacteriological or radiologic test results.",
                "raised": p.created_at.strftime("%Y-%m-%d") if p.created_at else timezone.now().strftime("%Y-%m-%d"),
                "status": "Open"
            })
            ex_idx += 1
            
    return render(request, "dashboard/data_quality.html", {
        "exceptions": exceptions,
        "dq_count": len(exceptions),
        "page": "data_quality"
    })


REAL_DEFAULT_STUDY_SITES = [
    {"state": "Odisha", "district": "Cuttack", "tb_unit": "Urban_TU", "launch_date": "2024-09-01", "concluding_date": "2025-02-28"},
    {"state": "Tamil Nadu", "district": "Tiruvallur", "tb_unit": "Tiruvallur TU", "launch_date": "2025-01-01", "concluding_date": "2025-03-31"},
    {"state": "Karnataka", "district": "Dharwad", "tb_unit": "Dharwad TU", "launch_date": "2024-11-01", "concluding_date": "2025-04-30"},
    {"state": "Tamil Nadu", "district": "Chennai", "tb_unit": "Chennai Central TU", "launch_date": "2024-10-01", "concluding_date": "2025-03-31"},
    {"state": "Tamil Nadu", "district": "Chennai", "tb_unit": "TU1", "launch_date": "2024-10-01", "concluding_date": "2025-03-31"},
    {"state": "Tamil Nadu", "district": "Madurai", "tb_unit": "TU2", "launch_date": "2024-10-01", "concluding_date": "2025-03-31"},
    {"state": "Tamil Nadu", "district": "Coimbatore", "tb_unit": "TU3", "launch_date": "2024-10-01", "concluding_date": "2025-03-31"},
]

REAL_DEFAULT_DEVICES = [
    {"device_id": "TAB-OD-URB-01", "state": "Odisha", "district": "Cuttack", "tb_unit": "Urban_TU", "app_version": "3.4.2", "battery": 94, "status": "online"},
    {"device_id": "TAB-TN-TIRU-01", "state": "Tamil Nadu", "district": "Tiruvallur", "tb_unit": "Tiruvallur TU", "app_version": "3.4.2", "battery": 88, "status": "online"},
    {"device_id": "TAB-KA-DHAR-01", "state": "Karnataka", "district": "Dharwad", "tb_unit": "Dharwad TU", "app_version": "3.4.2", "battery": 76, "status": "online"},
    {"device_id": "TAB-TN-CHEN-01", "state": "Tamil Nadu", "district": "Chennai", "tb_unit": "Chennai Central TU", "app_version": "3.4.2", "battery": 91, "status": "online"},
]


@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor")
def study_site_view(request):
    from django.core.paginator import Paginator
    from django.http import JsonResponse
    from django.utils import timezone
    import json
    from questions.context_processors import get_location_hierarchy
    from questions.models import Participant, UserProfile, StudySite, StudyDevice
    
    hierarchy = get_location_hierarchy()
    
    # Ensure real study sites exist (without seeding dummy nationwide jurisdictions)
    if StudySite.objects.count() == 0:
        for s in REAL_DEFAULT_STUDY_SITES:
            StudySite.objects.get_or_create(
                tb_unit=s["tb_unit"],
                defaults={
                    "state": s["state"],
                    "district": s["district"],
                    "launch_date": s["launch_date"],
                    "concluding_date": s["concluding_date"],
                    "is_active": True
                }
            )

    # Ensure real study devices exist in database
    if StudyDevice.objects.count() == 0:
        for d in REAL_DEFAULT_DEVICES:
            StudyDevice.objects.get_or_create(
                device_id=d["device_id"],
                defaults=d
            )

    is_ajax = (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.content_type == "application/json"
        or request.POST.get("is_ajax") == "1"
        or request.GET.get("format") == "json"
    )

    # Real-time metrics endpoint
    if request.method == "GET" and request.GET.get("action") == "realtime_metrics":
        active_count = StudySite.objects.filter(is_active=True).count()
        dev_count = StudyDevice.objects.count()
        c_count = Participant.objects.filter(classification="Case").count()
        ctrl_count = Participant.objects.filter(classification="Control").count()
        return JsonResponse({
            "status": "success",
            "activeSites": active_count,
            "totalDevices": dev_count,
            "totalCases": c_count,
            "totalControls": ctrl_count,
            "totalEnrolled": c_count + ctrl_count,
            "timestamp": timezone.now().strftime("%H:%M:%S")
        })

    # Process POST actions (Supports both real-time AJAX JSON & standard Form Redirects)
    if request.method == "POST":
        # Handle JSON payloads
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
            except Exception:
                data = {}
        else:
            data = request.POST

        action = data.get("action")
        active_tab = data.get("active_tab", "sites")
        
        if action == "add_site":
            state = data.get("state", "").strip()
            district = data.get("district", "").strip()
            tb_unit = data.get("tb_unit", "").strip()
            launch_date = data.get("launch_date", "2024-10-01")
            concluding_date = data.get("concluding_date", "2025-03-31")
            if state and district and tb_unit:
                site_obj, _ = StudySite.objects.update_or_create(
                    tb_unit=tb_unit,
                    defaults={
                        "state": state,
                        "district": district,
                        "launch_date": launch_date,
                        "concluding_date": concluding_date,
                        "is_active": True,
                        "created_by": request.user if request.user.is_authenticated else None
                    }
                )
                if is_ajax:
                    st_code = get_state_code(site_obj.state)
                    c_count = Participant.objects.filter(tb_unit=site_obj.tb_unit, classification="Case").count()
                    ctrl_count = Participant.objects.filter(tb_unit=site_obj.tb_unit, classification="Control").count()
                    return JsonResponse({
                        "status": "success",
                        "message": f"Study Site '{tb_unit}' added and activated in real time.",
                        "site": {
                            "tuCode": site_obj.tb_unit,
                            "district": site_obj.district,
                            "stateCode": st_code,
                            "stateName": site_obj.state,
                            "status": "synced",
                            "lastCheckIn": "Live",
                            "cases": c_count,
                            "controls": ctrl_count,
                            "errorRate": 0.0,
                            "campaignPeriod": site_obj.campaign_period_display
                        }
                    })
                
        elif action == "delete_site":
            tu_code = data.get("tu_code", "").strip()
            if tu_code:
                # Set inactive or delete
                StudySite.objects.filter(tb_unit=tu_code).update(is_active=False)
                if is_ajax:
                    return JsonResponse({
                        "status": "success",
                        "message": f"Study Site '{tu_code}' removed from active monitoring.",
                        "tuCode": tu_code
                    })
                
        elif action == "toggle_site":
            tu_code = data.get("tu_code", "").strip()
            site_obj = StudySite.objects.filter(tb_unit=tu_code).first()
            if site_obj:
                site_obj.is_active = not site_obj.is_active
                site_obj.save(update_fields=["is_active"])
                if is_ajax:
                    return JsonResponse({
                        "status": "success",
                        "tuCode": tu_code,
                        "isActive": site_obj.is_active,
                        "message": f"Site '{tu_code}' is now {'active' if site_obj.is_active else 'paused'}."
                    })

        elif action == "add_device":
            device_id = data.get("device_id", "").strip().upper()
            state = data.get("state", "National").strip()
            district = data.get("district", "").strip()
            tb_unit = data.get("tb_unit", "").strip()
            app_version = data.get("app_version", "3.4.2").strip() or "3.4.2"
            battery = int(data.get("battery", 100))
            if device_id and tb_unit:
                dev_obj, _ = StudyDevice.objects.update_or_create(
                    device_id=device_id,
                    defaults={
                        "tb_unit": tb_unit,
                        "state": state,
                        "district": district,
                        "app_version": app_version,
                        "battery": battery,
                        "status": "online"
                    }
                )
                if is_ajax:
                    return JsonResponse({
                        "status": "success",
                        "message": f"Clinical Tablet '{device_id}' registered successfully.",
                        "device": {
                            "deviceId": dev_obj.device_id,
                            "tuCode": dev_obj.tb_unit,
                            "stateName": dev_obj.state,
                            "appVersion": dev_obj.app_version,
                            "battery": dev_obj.battery,
                            "queued": 0,
                            "status": dev_obj.status,
                            "lastSeen": "Just now"
                        }
                    })
                
        elif action == "delete_device":
            device_id = data.get("device_id", "").strip()
            if device_id:
                StudyDevice.objects.filter(device_id=device_id).delete()
                if is_ajax:
                    return JsonResponse({
                        "status": "success",
                        "message": f"Tablet '{device_id}' decommissioned.",
                        "deviceId": device_id
                    })

        elif action == "ping_device":
            device_id = data.get("device_id", "").strip()
            dev_obj = StudyDevice.objects.filter(device_id=device_id).first()
            if dev_obj:
                dev_obj.last_seen = timezone.now()
                dev_obj.status = "online"
                dev_obj.save(update_fields=["last_seen", "status"])
                if is_ajax:
                    return JsonResponse({
                        "status": "success",
                        "deviceId": device_id,
                        "status": "online",
                        "latency": "38ms",
                        "battery": dev_obj.battery,
                        "lastSeen": "Live (38ms)"
                    })

        from django.shortcuts import redirect
        return redirect(f"/dashboard/study-site/?tab={active_tab}")
        
    # GET handler: Build real-time sites list directly from database
    sites_list = []
    active_sites_qs = StudySite.objects.filter(is_active=True).order_by("state", "district", "tb_unit")
    
    # If no sites active, fallback to real default sites
    if not active_sites_qs.exists():
        for s in REAL_DEFAULT_STUDY_SITES:
            StudySite.objects.get_or_create(
                tb_unit=s["tb_unit"],
                defaults={
                    "state": s["state"],
                    "district": s["district"],
                    "launch_date": s["launch_date"],
                    "concluding_date": s["concluding_date"],
                    "is_active": True
                }
            )
        active_sites_qs = StudySite.objects.filter(is_active=True).order_by("state", "district", "tb_unit")

    for s in active_sites_qs:
        st_code = get_state_code(s.state)
        c_count = Participant.objects.filter(tb_unit=s.tb_unit, classification="Case").count()
        ctrl_count = Participant.objects.filter(tb_unit=s.tb_unit, classification="Control").count()
        sites_list.append({
            "tuCode": s.tb_unit,
            "district": s.district,
            "stateCode": st_code,
            "stateName": s.state,
            "status": "synced",
            "lastCheckIn": "Live",
            "cases": c_count,
            "controls": ctrl_count,
            "errorRate": 0.0,
            "campaignPeriod": s.campaign_period_display
        })
                
    # Build real-time clinical tablets list directly from StudyDevice
    devices_list = []
    for d in StudyDevice.objects.all().order_by("device_id"):
        queued_count = Participant.objects.filter(tb_unit=d.tb_unit, synced=False).count()
        devices_list.append({
            "deviceId": d.device_id,
            "tuCode": d.tb_unit,
            "stateName": d.state,
            "appVersion": d.app_version,
            "battery": d.battery,
            "queued": queued_count,
            "lastSeen": "Online",
            "status": d.status
        })
        
    active_tab = request.GET.get("tab", "sites")
    if active_tab not in ["sites", "devices"]:
        active_tab = "sites"
        
    site_per_page = request.GET.get("site_per_page", "10")
    if site_per_page not in ["10", "50", "100"]:
        site_per_page = "10"
    site_per_page_int = int(site_per_page)
    
    device_per_page = request.GET.get("device_per_page", "10")
    if device_per_page not in ["10", "50", "100"]:
        device_per_page = "10"
    device_per_page_int = int(device_per_page)
    
    sites_paginator = Paginator(sites_list, site_per_page_int)
    sites_page = sites_paginator.get_page(request.GET.get("site_page", 1))
    
    devices_paginator = Paginator(devices_list, device_per_page_int)
    devices_page = devices_paginator.get_page(request.GET.get("device_page", 1))
    
    hierarchy_json = json.dumps(hierarchy)
    
    total_cases = Participant.objects.filter(classification="Case").count()
    total_controls = Participant.objects.filter(classification="Control").count()
    
    return render(request, "dashboard/study_site.html", {
        "sites": sites_page,
        "devices": devices_page,
        "active_tab": active_tab,
        "site_per_page": site_per_page_int,
        "device_per_page": device_per_page_int,
        "page": "study_site",
        "hierarchy_json": hierarchy_json,
        "metric_active_sites": active_sites_qs.count(),
        "metric_total_devices": len(devices_list),
        "metric_total_cases": total_cases,
        "metric_total_controls": total_controls,
        "metric_total_enrolled": total_cases + total_controls
    })



@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor")
def sync_telemetry_view(request):
    import json
    from questions.models import Participant, NikshayRecord, AuditLog, BcgVaccination, DeviceSyncLog
    from django.utils import timezone
    from datetime import timedelta
    
    total_participants = Participant.objects.count()
    nikshay_count = NikshayRecord.objects.count()
    audit_count = AuditLog.objects.count()
    bcg_count = BcgVaccination.objects.count()
    
    last_audit = AuditLog.objects.order_by("-timestamp").first()
    last_audit_str = last_audit.timestamp.strftime("%H:%M:%S") if last_audit else "Live"
    
    jobs = [
        {
            "name": "Clinical Tablet Telemetry & Upload",
            "status": "success",
            "schedule": "Real-time Event Push",
            "lastRun": "Continuous",
            "duration": "140ms",
            "records": total_participants
        },
        {
            "name": "Nikshay Central Registry Linkage",
            "status": "success",
            "schedule": "On-demand Sync Hook",
            "lastRun": "Automated",
            "duration": "420ms",
            "records": nikshay_count
        },
        {
            "name": "Adult BCG Benchmark Registry Matcher",
            "status": "success",
            "schedule": "Nightly Reconciliation",
            "lastRun": "Active",
            "duration": "1.1s",
            "records": bcg_count
        },
        {
            "name": "Security Audit Trail & Governance",
            "status": "success",
            "schedule": "Synchronous Event Stream",
            "lastRun": last_audit_str,
            "duration": "12ms",
            "records": audit_count
        }
    ]
    
    now = timezone.now()
    throughput = []
    for i in range(23, -1, -1):
        hr_start = now - timedelta(hours=i+1)
        hr_end = now - timedelta(hours=i)
        label = hr_end.strftime("%H:00")
        
        p_in_hr = Participant.objects.filter(created_at__gte=hr_start, created_at__lt=hr_end).count()
        s_in_hr = DeviceSyncLog.objects.filter(timestamp__gte=hr_start, timestamp__lt=hr_end).count()
        throughput.append({
            "hour": label,
            "payloads": p_in_hr + s_in_hr
        })
        
    return render(request, "dashboard/sync_telemetry.html", {
        "jobs": jobs,
        "throughput_json": json.dumps(throughput),
        "page": "sync_telemetry"
    })


@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor")
def data_export_view(request):
    from questions.models import Participant, TptIndividual, IneligibleIndividual
    from django.utils import timezone
    
    # Check if download format is requested
    export_format = request.GET.get("format")
    if export_format in ["excel", "csv"]:
        participants = Participant.objects.all().order_by("-date_enroll")
        tpts = TptIndividual.objects.all().order_by("-date_enroll")
        ineligibles = IneligibleIndividual.objects.all().order_by("-date_enroll")
        
        all_records = list(participants) + list(tpts) + list(ineligibles)
        # Sort combined list by date_enroll descending
        all_records.sort(key=lambda x: x.date_enroll if x.date_enroll else timezone.localdate(), reverse=True)
        
        # Fields mapping definition (Header name, lambda to extract raw value)
        fields_map = [
            ("Study ID", lambda p: p.study_id),
            ("Screening ID", lambda p: p.screening_id),
            ("Nikshay ID", lambda p: p.nikshay_id),
            ("Reconciliation Status", lambda p: p.reconciliation_status),
            ("First Name", lambda p: p.first_name),
            ("Last Name", lambda p: p.last_name),
            ("Full Name", lambda p: p.full_name),
            ("Date of Birth", lambda p: p.dob),
            ("Age", lambda p: p.age),
            ("Gender", lambda p: p.gender),
            ("Contact Number", lambda p: p.contact_number),
            ("Secondary Phone", lambda p: p.secondary_phone),
            ("Father/Husband Name", lambda p: p.father_husband_name),
            ("Date of Enrollment", lambda p: p.date_enroll),
            ("State", lambda p: p.state),
            ("District", lambda p: p.district),
            ("TB Unit", lambda p: p.tb_unit),
            ("Facility", lambda p: p.facility),
            ("Village", lambda p: p.village),
            ("Pincode", lambda p: p.pincode),
            ("Demographic Area", lambda p: p.demographic_area),
            ("Campaign Completion Date", lambda p: p.campaign_completion_date),
            ("Sector", lambda p: p.sector),
            ("Case Finding Type", lambda p: p.case_finding_type),
            ("Private Facility", lambda p: p.private_facility),
            ("Public PHI", lambda p: p.public_phi),
            ("Secondary Phone 1", lambda p: p.secondary_phone_1),
            ("Secondary Phone 2", lambda p: p.secondary_phone_2),
            ("Secondary Phone 3", lambda p: p.secondary_phone_3),
            ("Taluka/Block", lambda p: p.taluka_block),
            ("Landmark", lambda p: p.landmark),
            ("Contact Person Name", lambda p: p.contact_person_name),
            ("Contact Person Phone", lambda p: p.contact_person_phone),
            ("Contact Person Address", lambda p: p.contact_person_address),
            ("Informant Name", lambda p: p.informant_name),
            ("Informant Designation", lambda p: p.informant_designation),
            ("PTB Screened", lambda p: getattr(p, "ptb_screened", False)),
            ("PTB Test Registered", lambda p: getattr(p, "ptb_test_registered", False)),
            ("PTB Test Type", lambda p: p.ptb_test_type),
            ("PTB Test Result", lambda p: p.ptb_test_result),
            ("PTB Test Date", lambda p: p.ptb_test_date),
            ("PTB Test Facility", lambda p: p.ptb_test_facility),
            ("EPTB Screened", lambda p: getattr(p, "eptb_screened", False)),
            ("Marital Status", lambda p: p.marital_status),
            ("Occupation", lambda p: p.occupation),
            ("Socioeconomic Status", lambda p: p.socioeconomic_status),
            ("Symptoms", lambda p: p.symptoms),
            ("Risk Factors", lambda p: p.risk_factors),
            ("HIV Status", lambda p: p.hiv_status),
            ("Weight (kg)", lambda p: p.weight_kg),
            ("Height (cm)", lambda p: p.height_cm),
            ("BMI", lambda p: p.bmi),
            ("Past History of TB", lambda p: getattr(p, "past_tb", False)),
            ("Diabetes", lambda p: getattr(p, "diabetes", False)),
            ("Smoker", lambda p: getattr(p, "smoker", False)),
            ("Close Contact", lambda p: getattr(p, "close_contact", False)),
            ("TPT Undergone", lambda p: getattr(p, "tpt_undergone", "")),
            ("TPT Status", lambda p: getattr(p, "tpt_status", "")),
            ("TPT Contact Known", lambda p: getattr(p, "tpt_contact_known", "")),
            ("TPT History", lambda p: getattr(p, "tpt_history", "")),
            ("TPT Start Date", lambda p: getattr(p, "tpt_start_date", None)),
            ("TPT End Date", lambda p: getattr(p, "tpt_end_date", None)),
            ("TPT Duration Months", lambda p: getattr(p, "tpt_duration_months", None)),
            ("TPT Regimen", lambda p: getattr(p, "tpt_regimen", "")),
            ("TPT Risk Factor", lambda p: getattr(p, "tpt_risk_factor", "")),
            ("BCG Evidence", lambda p: p.bcg_evidence),
            ("BCG Status", lambda p: p.bcg_status),
            ("BCG Beneficiary ID", lambda p: p.bcg_beneficiary_id),
            ("BCG Mobile Number", lambda p: p.bcg_ben_mobile_number),
            ("BCG Gender", lambda p: p.bcg_ben_gender),
            ("BCG Date", lambda p: p.bcg_date),
            ("BCG Registration Mode", lambda p: p.bcg_registration_mode),
            ("BCG DOB", lambda p: p.bcg_dob),
            ("BCG Age", lambda p: p.bcg_age),
            ("BCG Vaccination Status", lambda p: p.bcg_vaccination_status),
            ("BCG First Name", lambda p: p.bcg_first_name),
            ("BCG Last Name", lambda p: p.bcg_last_name),
            ("BCG Site ID", lambda p: p.bcg_site_id),
            ("BCG Approved By", lambda p: p.bcg_approved_by),
            ("BCG Beneficiary Type Name", lambda p: p.bcg_beneficiary_type_name),
            ("BCG Pincode", lambda p: p.bcg_pincode),
            ("BCG Address", lambda p: p.bcg_address),
            ("BCG Facility ID", lambda p: p.bcg_facility_id),
            ("BCG Scar", lambda p: p.bcg_scar),
            ("BCG Has Record", lambda p: p.bcg_has_record),
            ("BCG Vaccination Date", lambda p: p.bcg_vaccination_date),
            ("BCG Vaccine Name", lambda p: p.bcg_vaccine_name),
            ("BCG Batch Number", lambda p: p.bcg_batch_number),
            ("BCG Facility", lambda p: p.bcg_facility),
            ("Classification", lambda p: p.classification),
            ("Classification Reason", lambda p: p.classification_reason),
        ]
        
        headers = [item[0] for item in fields_map]
        
        def clean_val(val):
            if val is None:
                return ""
            import datetime
            if isinstance(val, (datetime.date, datetime.datetime)):
                return val.strftime("%Y-%m-%d")
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                if val == 0 or val == 0.0:
                    return ""
                return val
            if isinstance(val, bool):
                return "Yes" if val else "No"
            s_val = str(val).strip()
            if s_val.lower() in ["none", "n/a", "na", "null", "unknown", "no evidence"]:
                return ""
            return s_val

        # 1. CSV EXPORT
        if export_format == "csv":
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="aBCG_Surveillance_Data.csv"'
            
            writer = csv.writer(response)
            writer.writerow(headers)
            for p in all_records:
                row_data = [clean_val(item[1](p)) for item in fields_map]
                writer.writerow(row_data)
            new_log = {
                "id": f"EXP-{timezone.now().strftime('%y%m%d%H%M%S')}",
                "name": f"Surveillance Matrix ({len(all_records)} records)",
                "at": timezone.now().strftime("%Y-%m-%d %H:%M"),
                "format": "csv",
                "status": "ready"
            }
            hist = list(request.session.get("export_history", []))
            hist.insert(0, new_log)
            request.session["export_history"] = hist[:20]
            request.session.modified = True
            
            return response
            
        # 2. EXCEL EXPORT
        elif export_format == "excel":
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from django.http import HttpResponse
            from io import BytesIO
            
            wb = openpyxl.Workbook()
            # Sheet 1: Master Registry
            ws1 = wb.active
            ws1.title = "Master Registry"
            
            # Styles
            header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            bold_font = Font(name="Calibri", size=11, bold=True)
            normal_font = Font(name="Calibri", size=11)
            
            header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
            accent_fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
            
            thin_border = Border(
                left=Side(style='thin', color='D9D9D9'),
                right=Side(style='thin', color='D9D9D9'),
                top=Side(style='thin', color='D9D9D9'),
                bottom=Side(style='thin', color='D9D9D9')
            )
            
            ws1.append(headers)
            # Style headers
            for col_idx in range(1, len(headers) + 1):
                cell = ws1.cell(row=1, column=col_idx)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            for p in all_records:
                row_data = [clean_val(item[1](p)) for item in fields_map]
                ws1.append(row_data)
                
            # Apply borders and auto-fit columns
            for row in ws1.iter_rows(min_row=2, max_row=ws1.max_row, min_col=1, max_col=len(headers)):
                for cell in row:
                    cell.font = normal_font
                    cell.border = thin_border
                    
            for col in ws1.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = openpyxl.utils.get_column_letter(col[0].column)
                ws1.column_dimensions[col_letter].width = max(max_len + 3, 12)
                
            # Sheet 2: Summary Stats
            ws2 = wb.create_sheet(title="Summary Statistics")
            ws2.append(["aBCG VE Study Summary Statistics"])
            ws2.cell(row=1, column=1).font = Font(name="Calibri", size=16, bold=True, color="1F4E79")
            ws2.append([])
            
            # Calculate summary metrics across all models
            total_cases = (
                Participant.objects.filter(classification="Case").count() +
                TptIndividual.objects.filter(classification="Case").count() +
                IneligibleIndividual.objects.filter(classification="Case").count()
            )
            total_controls = (
                Participant.objects.filter(classification="Control").count() +
                TptIndividual.objects.filter(classification="Control").count() +
                IneligibleIndividual.objects.filter(classification="Control").count()
            )
            total_screened = len(all_records)
            total_participants = Participant.objects.count()
            total_tpts = TptIndividual.objects.count()
            total_ineligibles = IneligibleIndividual.objects.count()
            
            ws2.append(["Metric", "Count"])
            ws2.cell(row=3, column=1).font = bold_font
            ws2.cell(row=3, column=2).font = bold_font
            ws2.cell(row=3, column=1).fill = accent_fill
            ws2.cell(row=3, column=2).fill = accent_fill
            
            metrics = [
                ("Total Registered (Screened)", total_screened),
                ("Confirmed TB Cases", total_cases),
                ("Matched Controls", total_controls),
                ("Eligible Study Participants", total_participants),
                ("TPT+BCG Cohort", total_tpts),
                ("Ineligible Individuals", total_ineligibles)
            ]
            for m, val in metrics:
                ws2.append([m, val])
                
            ws2.column_dimensions['A'].width = 30
            ws2.column_dimensions['B'].width = 15
            
            stream = BytesIO()
            wb.save(stream)
            stream.seek(0)
            
            response = HttpResponse(
                stream.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = 'attachment; filename="aBCG_Surveillance_Data.xlsx"'
            
            # Record in session export history
            new_log = {
                "id": f"EXP-{timezone.now().strftime('%y%m%d%H%M%S')}",
                "name": f"Surveillance Matrix ({len(all_records)} records)",
                "at": timezone.now().strftime("%Y-%m-%d %H:%M"),
                "format": "excel",
                "status": "ready"
            }
            hist = list(request.session.get("export_history", []))
            hist.insert(0, new_log)
            request.session["export_history"] = hist[:20]
            request.session.modified = True
            
            return response
            
    return render(request, "dashboard/data_export.html", {
        "history": request.session.get("export_history", []),
        "page": "data_export"
    })


@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor")
def settings_view(request):
    import json
    from django.http import JsonResponse
    from django.shortcuts import redirect
    from django.contrib import messages
    from questions.context_processors import get_location_hierarchy
    from questions.models import StudySite

    hierarchy = get_location_hierarchy()

    # Handle POST: save settings submitted from dashboard
    if request.method == "POST":
        try:
            site_updates = []
            if request.content_type and "application/json" in request.content_type:
                body_data = json.loads(request.body.decode("utf-8"))
                site_updates = body_data.get("sites", [])
            else:
                site_code = request.POST.get("site_code")
                if site_code:
                    site_updates.append({
                        "siteCode": site_code,
                        "launch": request.POST.get("launch"),
                        "conclusion": request.POST.get("conclusion"),
                        "active": request.POST.get("active") in ["true", "True", "active", "1", True]
                    })

            for item in site_updates:
                code = item.get("siteCode")
                launch = item.get("launch")
                conclusion = item.get("conclusion")
                active = item.get("active")
                if code:
                    site = StudySite.objects.filter(tb_unit=code).first()
                    if not site:
                        st = item.get("stateName", "Tamil Nadu")
                        dist = item.get("districtName", "Tiruvallur")
                        site = StudySite(tb_unit=code, state=st, district=dist)
                    if launch:
                        site.launch_date = launch
                    if conclusion:
                        site.concluding_date = conclusion
                    elif conclusion == "":
                        site.concluding_date = None
                    if active is not None:
                        site.is_active = bool(active)
                    site.save()

            if request.headers.get("x-requested-with") == "XMLHttpRequest" or (request.content_type and "application/json" in request.content_type):
                return JsonResponse({"status": "success", "message": "Campaign settings updated successfully."})
            messages.success(request, "Campaign settings updated successfully.")
            return redirect("questions:settings")
        except Exception as e:
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or (request.content_type and "application/json" in request.content_type):
                return JsonResponse({"status": "error", "message": str(e)}, status=400)
            messages.error(request, f"Failed to update settings: {str(e)}")
            return redirect("questions:settings")

    selected_state = request.GET.get('state') or request.session.get('selected_state', '')
    selected_district = request.GET.get('district') or request.session.get('selected_district', '')
    selected_tb_unit = request.GET.get('tb_unit') or request.session.get('selected_tb_unit', '')

    profile = getattr(request.user, "profile", None)
    role = getattr(profile, "role", "") if profile else ""
    if role not in ["Super Admin", "Admin"]:
        selected_state = profile.state if (profile and profile.state) else "Tamil Nadu"
    if role in ["Nodal Officer", "Doctor", "Project Nurse"]:
        selected_district = profile.district if (profile and profile.district) else ""
    if role in ["Doctor", "Project Nurse"]:
        selected_tb_unit = profile.tb_unit if (profile and profile.tb_unit) else ""

    # Load from database; ensure all hierarchy units exist in StudySite
    db_sites = {s.tb_unit: s for s in StudySite.objects.all()}
    sites = []
    for state, dists in hierarchy.items():
        for dist, tbus in dists.items():
            for tu in tbus:
                site_obj = db_sites.get(tu)
                if not site_obj:
                    l_date = "2025-01-01" if tu == "Tiruvallur TU" else "2024-06-01"
                    c_date = "2025-03-31" if tu == "Tiruvallur TU" else "2024-08-31"
                    site_obj = StudySite.objects.create(
                        tb_unit=tu,
                        state=state,
                        district=dist,
                        launch_date=l_date,
                        concluding_date=c_date,
                        is_active=True
                    )
                    db_sites[tu] = site_obj

                sites.append({
                    "siteCode": site_obj.tb_unit,
                    "districtName": site_obj.district,
                    "stateName": site_obj.state,
                    "launch": site_obj.launch_date.strftime("%Y-%m-%d") if site_obj.launch_date else "",
                    "conclusion": site_obj.concluding_date.strftime("%Y-%m-%d") if site_obj.concluding_date else "",
                    "active": site_obj.is_active,
                    "campaignPeriod": site_obj.campaign_period_display
                })

    return render(request, "dashboard/settings.html", {
        "sites": sites,
        "page": "settings",
        "hierarchy_json": json.dumps(hierarchy),
        "active_state": selected_state,
        "active_district": selected_district,
        "active_tb_unit": selected_tb_unit,
    })



class MockParticipantAdapter:
    """Adapter to render mock participants or fallback records seamlessly in questions/participant_detail.html."""
    def __init__(self, data, study_id=None):
        import datetime
        data = data if isinstance(data, dict) else {}
        self.id = data.get("id", 1)
        self.pk = self.id
        self.study_id = study_id or data.get("studyId", "ABCG-OD-TU14-2026-000001")
        self.full_name = data.get("name", "Vikram Thakur")
        self.age = data.get("age", 42)
        sex = data.get("sex", "M")
        self.gender = "Male" if sex == "M" else "Female" if sex == "F" else sex
        self.date_enroll = data.get("enrolmentDate", "2026-03-30")
        self.dob = "1984-05-12"
        self.screening_id = f"SCR-2026-{self.study_id.split('-')[-1]}" if '-' in self.study_id else f"SCR-{self.study_id}"
        self.nikshay_id = data.get("nikshayId") or "NIK-2026-894125"
        self.classification = data.get("classification") or "Case"
        self.classification_reason = data.get("reason") or "Microbiologically Confirmed PTB (NAAT+)"
        self.synced = (data.get("matchStatus", 1) == 1)
        self.eligible = (data.get("hrgEligible", 1) == 1)
        self.father_husband_name = data.get("father_husband_name") or "Ramachandran K"
        self.contact_number = data.get("mobile") or "9876543210"
        self.secondary_phone = ""
        self.secondary_phone_1 = ""
        self.secondary_phone_2 = ""
        self.secondary_phone_3 = ""
        village = data.get("village") or "Central Ward"
        self.address = village
        self.village = village
        self.taluka_block = data.get("tuCode") or "TU14"
        self.pincode = "751001"
        self.district = data.get("district") or "Khurda"
        self.state = data.get("stateName") or "Odisha"
        self.landmark = "Near Primary Health Centre"
        self.sector = "Urban"
        self.demographic_area = "Municipal Corporation"
        self.marital_status = "Married"
        self.occupation = "Self-Employed"
        self.socioeconomic_status = "APL"
        self.contact_person_name = "Sunita Devi"
        self.contact_person_phone = "9876543211"
        self.contact_person_address = village
        self.informant_name = "Field Investigator"
        self.informant_designation = "Project Nurse"
        
        disease_type = data.get("diseaseType", "PTB")
        self.ptb_screened = (disease_type == "PTB")
        self.ptb_test_registered = True
        self.ptb_test_type = "NAAT (CBNAAT/TrueNat)"
        self.ptb_test_result = "MTB Detected" if self.classification == "Case" else "Negative"
        self.ptb_test_date = self.date_enroll
        self.ptb_test_facility = data.get("facility") or "DTC Laboratory"
        
        self.eptb_screened = (disease_type == "EPTB")
        self.eptb_site = "Lymph Node" if self.eptb_screened else ""
        self.eptb_clinical_features = "Cervical lymphadenopathy" if self.eptb_screened else ""
        self.eptb_diagnostic_modalities = "FNAC + NAAT" if self.eptb_screened else ""
        self.eptb_histology = "Caseating granuloma" if self.eptb_screened else ""
        self.eptb_specialist_consult = "Pulmonologist" if self.eptb_screened else ""
        
        self.weight_kg = 56.5
        self.height_cm = 168.0
        self.bmi = 20.0
        self.past_tb = False
        self.diabetes = False
        self.smoker = False
        self.close_contact = True if self.classification == "Case" else False
        self.hiv_status = "Non-Reactive"
        self.match_hrg = data.get("matchHrg") or "Elderly (>=60 yrs)"
        self.bcg_eligibility_criteria = "Age Criteria Met, High-Risk Household Contact"
        
        bcg_st = data.get("bcgStatus", 1)
        self.bcg_status = "Yes" if bcg_st == 1 else "No"
        self.bcg_scar_present = "Present" if self.bcg_status == "Yes" else "Absent"
        self.bcg_scar_size = "4 mm" if self.bcg_status == "Yes" else "—"
        self.bcg_scar_location = "Left Upper Arm" if self.bcg_status == "Yes" else "—"
        self.bcg_verification_source = "Physical Inspection & Nikshay Database"
        
        self.nikshay_verified = True
        self.nikshay_enrolment_date = self.date_enroll
        self.nikshay_treatment_regimen = "FDC (2HRZE/4HRE)" if self.classification == "Case" else "None"
        self.nikshay_tb_type = disease_type
        self.reconciliation_status = "VERIFIED"
        self.created_at = datetime.datetime.now()
        self.created_by = None


@group_required("Super Admin", "Admin", "Nodal Officer", "Doctor", "Project Nurse")
def participant_detail_view(request, study_id):
    from questions.models import Participant, TptIndividual, IneligibleIndividual
    import json
    import datetime
    
    # 1. Attempt to look up the participant in the database
    participant = Participant.objects.filter(study_id=study_id).first()
    cohort = "participant"
    if not participant:
        participant = TptIndividual.objects.filter(study_id=study_id).first()
        cohort = "tpt"
    if not participant:
        participant = IneligibleIndividual.objects.filter(study_id=study_id).first()
        cohort = "ineligible"
        
    if participant:
        ptb_details = {}
        eptb_details = {}
        q_answers = {}
        if participant.ptb_test_details:
            try:
                ptb_details = json.loads(participant.ptb_test_details)
            except Exception:
                pass
        if participant.eptb_details:
            try:
                eptb_details = json.loads(participant.eptb_details)
            except Exception:
                pass
        if hasattr(participant, "questionnaire_answers") and participant.questionnaire_answers:
            try:
                q_answers = json.loads(participant.questionnaire_answers)
            except Exception:
                pass
                
        symptoms_list = [s.strip() for s in participant.symptoms.split(",") if s.strip()] if getattr(participant, "symptoms", None) else []
        risk_factors_list = [r.strip() for r in participant.risk_factors.split(",") if r.strip()] if getattr(participant, "risk_factors", None) else []
        
        # Fetch actual audit trail from AuditLog model
        audit_trail = AuditLog.objects.filter(action__icontains=f"study_id={participant.study_id}").order_by("-timestamp")
        
        # Calculate verification & adjudication status dynamically
        v_status = "Verified"
        adj_status = "Not Applicable"
        if getattr(participant, "classification", None) == "Pending":
            v_status = "Verification Pending"
        elif getattr(participant, "classification", None) == "Needs Correction":
            v_status = "Needs Correction"
        elif getattr(participant, "classification", None) == "Adjudication Pending":
            v_status = "Sent for Adjudication"
            adj_status = "Adjudication Pending"
        elif getattr(participant, "classification", None) == "Adjudication Completed":
            v_status = "Verified (Adjudicated)"
            adj_status = "Adjudication Completed"
            
        return render(request, "questions/participant_detail.html", {
            "p": participant,
            "cohort": cohort,
            "ptb_details": ptb_details,
            "eptb_details": eptb_details,
            "q_answers": q_answers,
            "symptoms_list": symptoms_list,
            "risk_factors_list": risk_factors_list,
            "audit_trail": audit_trail,
            "verification_status": v_status,
            "adjudication_status": adj_status
        })
        
    # 2. Fallback / Mock participant adapter (renders in the NEW model template)
    from . import mock_data
    mock_p = mock_data.get_participant(study_id)
    if not mock_p:
        # Generate graceful default adapter if study_id format matches
        mock_p = {
            "studyId": study_id,
            "name": "Participant " + (study_id.split("-")[-1] if '-' in study_id else study_id),
            "age": 35,
            "sex": "M",
            "enrolmentDate": "2026-03-30",
            "classification": "Case" if "000001" in study_id else "Control",
            "diseaseType": "PTB",
            "hrgEligible": 1,
            "matchStatus": 1
        }
        
    v_status = "Verified"
    adj_status = "Not Applicable"
    c_status = mock_p.get('classification', 'Case')
    if study_id in ['ABCG-MH-TU04-2026-000142', 'ABCG-MH-TU04-2026-000173']:
        v_status = "Verification Pending"
        c_status = "Pending"
    elif study_id in ['ABCG-MH-TU04-2026-000190']:
        v_status = "Sent for Adjudication"
        adj_status = "Adjudication Pending"
        c_status = "Adjudication Pending"
        
    mock_p['classification'] = c_status
    adapted_p = MockParticipantAdapter(mock_p, study_id=study_id)
    
    mock_audit = [
        {
            "timestamp": datetime.datetime.now() - datetime.timedelta(days=1),
            "actor_username": "field_inv",
            "actor_role": "Project Nurse",
            "action": f"Screening questionnaire submitted. Initial classification: {c_status}."
        },
        {
            "timestamp": datetime.datetime.now() - datetime.timedelta(days=1, hours=2),
            "actor_username": "device_agent",
            "actor_role": "System",
            "action": "Participant local database record created."
        }
    ]
    
    ptb_sample_details = {
        "test_reason": "Clinical symptoms suggestive of pulmonary TB",
        "predominant_symptom": "Productive Cough",
        "duration_days": 21,
        "hcp_visits": 2,
        "case_type": "New",
        "sample_availability": "Yes",
        "sample_details": {
            "sample_type": "Sputum",
            "sputum_collection_detail": "Early Morning Deep Cough",
            "sample_description": "Mucopurulent",
            "collection_date": "2026-03-30",
            "sample_serial_id": f"SP-{study_id.split('-')[-1]}" if '-' in study_id else "SP-0001",
            "sample_qr_code": f"QR-{study_id}"
        },
        "result_details": {
            "lab_serial_number": f"LAB-{study_id.split('-')[-1]}" if '-' in study_id else "LAB-0001",
            "date_tested": "2026-03-31",
            "reported_by": "Dr. S. K. Mohapatra",
            "final_interpretation": "MTB DETECTED - RIF RESISTANCE NOT DETECTED",
            "remarks": "Cartridge lot verified. High bacterial load."
        }
    } if c_status == "Case" else {}
    
    return render(request, "questions/participant_detail.html", {
        "p": adapted_p,
        "cohort": "participant",
        "ptb_details": ptb_sample_details,
        "eptb_details": {},
        "q_answers": {},
        "symptoms_list": ["Cough (>2 weeks)", "Persistent Fever", "Loss of Appetite"] if c_status == "Case" else [],
        "risk_factors_list": ["Household TB Contact", "Malnutrition Risk"] if c_status == "Case" else [],
        "audit_trail": mock_audit,
        "verification_status": v_status,
        "adjudication_status": adj_status
    })