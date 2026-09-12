from .models import GlobalSettings

class RulesEngine:
    """
    Decoupled clinical eligibility logic engine.
    Reads global thresholds dynamically from the database (GlobalSettings) to easily
    adapt to frequent stakeholder changes without requiring code deployments.
    """
    
    @staticmethod
    def get_settings():
        settings = GlobalSettings.objects.first()
        if not settings:
            # Fallback to standard protocol defaults
            settings = GlobalSettings(
                bmi_threshold=18.0,
                age_threshold=60,
                campaign_period="Jan 2025 - Mar 2025"
            )
        return settings

    @classmethod
    def evaluate_eligibility(cls, participant_data):
        """
        Evaluates the participant against study eligibility gates.
        Returns a tuple: (eligible, match_hrg, reason)
        """
        settings = cls.get_settings()
        age = participant_data.get("age", 0)
        bmi = participant_data.get("bmi", 0.0)
        risk_factors = participant_data.get("risk_factors", "")
        eligible_bcg_campaign_raw = participant_data.get("eligible_bcg_campaign", "Yes")
        bcg_eligibility_criteria = participant_data.get("bcg_eligibility_criteria", "")

        # Extract risk list
        risk_factors_str = risk_factors or ""
        risks_list = [r.strip() for r in risk_factors_str.split(",") if r.strip()]
        
        # 1. Age Gate
        is_elderly = age >= settings.age_threshold or "Individuals aged 60 years or above" in risks_list
        
        # 2. BMI Gate
        is_malnourished = bmi < settings.bmi_threshold or "Individuals with a Body Mass Index of less than 18 kg per sq.mts" in risks_list
        
        # 3. Comorbidities & other HRGs
        is_contact = any("contact" in r.lower() for r in risks_list)
        is_diabetes = any("diabetes" in r.lower() for r in risks_list)
        is_past_tb = any("past history" in r.lower() or "episode of tb" in r.lower() for r in risks_list)
        is_smoker = any("smoking" in r.lower() or "smoker" in r.lower() for r in risks_list)
        
        has_hrg = is_elderly or is_malnourished or is_contact or is_diabetes or is_past_tb or is_smoker
        
        # 4. Campaign period gate
        bcg_criteria_str = bcg_eligibility_criteria or ""
        has_bcg_criteria = len([c.strip() for c in bcg_criteria_str.split(",") if c.strip()]) > 0
        eligible_bcg_campaign = True if (eligible_bcg_campaign_raw in [True, "Yes", "true", "True", 1] and has_bcg_criteria) else False
        
        eligible = has_hrg and eligible_bcg_campaign
        
        match_hrg = "None"
        if eligible:
            if is_past_tb:
                match_hrg = "Past TB"
            elif is_contact:
                match_hrg = "Close Contact"
            elif is_diabetes:
                match_hrg = "Diabetes"
            elif is_malnourished:
                match_hrg = f"Malnourished (BMI < {settings.bmi_threshold})"
            elif is_elderly:
                match_hrg = f"Elderly (Age >= {settings.age_threshold})"
            elif is_smoker:
                match_hrg = "History of smoking tobacco"
            else:
                match_hrg = "Target High Risk Group"
        else:
            reasons = []
            if not has_hrg:
                reasons.append("Does not match any Target High Risk Group (HRG)")
            if not eligible_bcg_campaign:
                reasons.append("Not eligible for BCG vaccine during campaign period")
            match_hrg = " & ".join(reasons)
            
        return eligible, match_hrg, match_hrg

    @classmethod
    def evaluate_classification(cls, participant_data):
        """
        Server-side validation/audit of cohort classification.
        Recomputes classification and classification_reason based on clinical metrics.
        Returns a tuple: (classification, classification_reason)
        """
        import json
        from django.utils import timezone
        
        # 1. Evaluate basic eligibility
        eligible, match_hrg, hrg_reason = cls.evaluate_eligibility(participant_data)
        
        if not eligible:
            return "Not Eligible", "Participant is ineligible under screening criteria."
            
        tpt_undergone = participant_data.get("tpt_undergone", "No")
        bcg_status = participant_data.get("bcg_status", "No") or ""
        
        # Check if BCG verification and vaccine details are filled
        bcg_status_str = bcg_status.strip()
        bcg_complete = False
        if bcg_status_str.startswith("No"):
            bcg_complete = True
        elif bcg_status_str.startswith("Yes"):
            has_date = bool(participant_data.get("bcg_vaccination_date") or participant_data.get("bcg_date"))
            has_batch = bool(participant_data.get("bcg_batch_number"))
            has_facility = bool(participant_data.get("bcg_facility"))
            if has_date and has_batch and has_facility:
                bcg_complete = True
                
        if not bcg_complete:
            return "Pending", "One or more required BCG verification or vaccine details are incomplete."
            
        # TPT+BCG cohort override check
        # Since eligible is True, has_hrg and eligible_bcg_campaign are True
        is_tpt_bcg = (tpt_undergone == "Yes") and bcg_status.startswith("Yes")
        
        if is_tpt_bcg:
            return "TPT+BCG", "Eligible for BCG + TPT Exploratory Cohort"
            
        # Parse ptb_test_details and eptb_details to determine mctb, cxr, and eptb_status
        ptb_details_raw = participant_data.get("ptb_test_details", "{}")
        try:
            ptb_details = json.loads(ptb_details_raw) if isinstance(ptb_details_raw, str) else (ptb_details_raw or {})
        except Exception:
            ptb_details = {}
            
        undergone_testing = ptb_details.get("undergone_testing", "No")
        final_interpretation = ptb_details.get("final_interpretation", "")
        naat_status = ptb_details.get("naat_status", "")
        cxr_result = ptb_details.get("cxr_result", "")
        cxr_status = ptb_details.get("cxr_status", "")
        cxr_done = ptb_details.get("cxr_done", "")
        
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
        eptb_details_raw = participant_data.get("eptb_details", "{}")
        try:
            eptb_answers = json.loads(eptb_details_raw) if isinstance(eptb_details_raw, str) else (eptb_details_raw or {})
        except Exception:
            eptb_answers = {}
            
        has_eptb_symptoms = False
        if isinstance(eptb_answers, dict):
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
        if has_eptb_symptoms and isinstance(eptb_answers, dict):
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
                
        # 30-day testing timeout check
        date_enroll_raw = participant_data.get("date_enroll")
        is_older_than_30_days = False
        if date_enroll_raw:
            try:
                if isinstance(date_enroll_raw, str):
                    import datetime
                    enroll_date = datetime.datetime.strptime(date_enroll_raw, "%Y-%m-%d").date()
                else:
                    enroll_date = date_enroll_raw
                # Avoid timezone issues by using local date
                if (timezone.localdate() - enroll_date).days > 30:
                    is_older_than_30_days = True
            except Exception:
                pass

        classification = "Pending"
        classification_reason = "One or more required investigation results are pending."
        
        if cxr == "ABNORMAL_NON_TB" and mctb == "NEGATIVE":
            classification = "Excluded"
            classification_reason = "Abnormal CXR not suggestive of TB with NAAT Negative"
        elif is_older_than_30_days and (mctb == "PENDING" or cxr == "PENDING" or eptb_status == "PENDING"):
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
                
        return classification, classification_reason

