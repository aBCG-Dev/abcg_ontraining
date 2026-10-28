import json
import csv
import io
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from questions.models import Participant, TptIndividual, IneligibleIndividual, RiskFactor

class ConsentQuestionTestCase(TestCase):
    def setUp(self):
        self.username = "nurse_test"
        self.password = "password123"
        self.user = User.objects.create_user(
            username=self.username,
            email="nurse@example.com",
            password=self.password,
            first_name="Nurse",
            last_name="Test"
        )
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

        RiskFactor.objects.get_or_create(
            code="elderly",
            defaults={
                "name": "Individuals aged 60 years or above",
                "is_target_hrg": True,
                "is_active": True
            }
        )

    def test_registration_form_contains_consent_question_no_default_selection(self):
        """1. Make the Consent question mandatory, with no default selection."""
        response = self.client.get(reverse("questions:registration"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        
        # Verify consent question section exists
        self.assertIn('id="consent_section"', content)
        self.assertIn('name="consent"', content)
        self.assertIn('id="consentYes"', content)
        self.assertIn('id="consentNo"', content)
        self.assertIn('id="consentExcludedNotice"', content)
        
        # Verify no default selection (neither radio button has 'checked')
        self.assertNotIn('id="consentYes" value="Yes" checked', content)
        self.assertNotIn('id="consentNo" value="No" checked', content)

    def test_consent_yes_allows_proceeding_and_saves_data(self):
        """2. If Yes is selected, allow user to proceed and save consent response and clinical details."""
        post_data = {
            "first_name": "Ravi",
            "last_name": "Kumar",
            "father_husband_name": "Suresh",
            "age": 62,
            "dob": "1964-01-01",
            "gender": "Male",
            "primary_phone": "9876543210",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "facility": "Avadi PHC",
            "sector": "Public Sector",
            "eligible_bcg_campaign": "Yes",
            "has_bcg_eligibility_criteria_form": "true",
            "bcg_eligibility_criteria": ["Was aged >=60 years during the BCG campaign period"],
            "consent": "Yes",
            "symptoms": ["Asymptomatic"],
            "undergone_testing": "No",
            "cxr_done": "No",
            "bcg_status": "No",
        }
        response = self.client.post(reverse("questions:registration"), data=post_data)
        self.assertEqual(response.status_code, 302)

        participant = Participant.objects.filter(first_name="Ravi", last_name="Kumar").first()
        self.assertIsNotNone(participant)
        self.assertEqual(participant.consent, "Yes")
        self.assertNotEqual(participant.classification, "Excluded")

    def test_consent_no_stops_data_collection_and_marks_excluded(self):
        """3 & 7. If No is selected: mark Excluded from Study, stop collection, backend enforcement."""
        post_data = {
            "first_name": "Sita",
            "last_name": "Devi",
            "father_husband_name": "Ram",
            "age": 65,
            "dob": "1961-05-15",
            "gender": "Female",
            "primary_phone": "9876500001",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "facility": "Avadi PHC",
            "sector": "Public Sector",
            "eligible_bcg_campaign": "Yes",
            "has_bcg_eligibility_criteria_form": "true",
            "bcg_eligibility_criteria": ["Was aged >=60 years during the BCG campaign period"],
            "consent": "No",
            # Attempt to submit subsequent questionnaire data (backend must ignore/clear them)
            "symptoms": ["Cough > 2 weeks", "Fever"],
            "undergone_testing": "Yes",
            "test_reason": "Diagnosis of TB",
            "test_type": "NAAT",
            "final_interpretation": "MTB DETECTED",
            "cxr_done": "Yes",
            "cxr_result": "Suggestive of TB",
            "bcg_status": "Yes (Verified via Registry)",
            "bcg_beneficiary_id": "BEN12345",
        }
        response = self.client.post(reverse("questions:registration"), data=post_data)
        self.assertEqual(response.status_code, 302)

        participant = Participant.objects.filter(first_name="Sita", last_name="Devi").first()
        self.assertIsNotNone(participant)
        self.assertEqual(participant.consent, "No")
        self.assertEqual(participant.classification, "Excluded")
        self.assertEqual(participant.classification_reason, "Excluded from Study: Informed consent not provided")
        
        # Verify subsequent questionnaire data was cleared/not collected
        self.assertFalse(participant.ptb_screened)
        self.assertFalse(participant.ptb_test_registered)
        self.assertEqual(participant.bcg_status, "No")
        self.assertEqual(participant.ptb_test_details, "{}")

    def test_reopening_saved_record_displays_consent_and_exclusion(self):
        """4. When reopening a saved record, display previously selected consent and exclusion status."""
        # Create excluded participant
        excluded_p = Participant.objects.create(
            first_name="Anand",
            last_name="Verma",
            full_name="Anand Verma",
            study_id="ABCG-TN-TIR-2026-111111",
            contact_number="9876511111",
            age=63,
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            facility="Avadi PHC",
            consent="No",
            classification="Excluded",
            classification_reason="Excluded from Study: Informed consent not provided",
            date_enroll=timezone.localdate()
        )
        
        # GET edit view
        response = self.client.get(reverse("questions:registration_edit", kwargs={"pk": excluded_p.pk}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        
        # Check draftData in registration.html contains consent No and classification Excluded
        self.assertIn('"consent": "No"', content)
        self.assertIn('"classification": "Excluded"', content)

        # Also check participant detail view
        detail_resp = self.client.get(reverse("questions:participant_detail", kwargs={"study_id": excluded_p.study_id}))
        self.assertEqual(detail_resp.status_code, 200)
        detail_content = detail_resp.content.decode("utf-8")
        self.assertIn("Excluded from Study", detail_content)
        self.assertIn("Declined (Excluded)", detail_content)

    def test_excel_and_csv_export_includes_consent_and_exclusion(self):
        """5. Include the Consent response and exclusion status in export."""
        # Excluded participant
        Participant.objects.create(
            first_name="Kavita",
            last_name="Singh",
            full_name="Kavita Singh",
            study_id="ABCG-TN-TIR-2026-222222",
            contact_number="9876522222",
            age=61,
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            facility="Avadi PHC",
            consent="No",
            classification="Excluded",
            classification_reason="Excluded from Study: Informed consent not provided",
            date_enroll=timezone.localdate()
        )

        # Consented participant
        Participant.objects.create(
            first_name="Manoj",
            last_name="Gupta",
            full_name="Manoj Gupta",
            study_id="ABCG-TN-TIR-2026-333333",
            contact_number="9876533333",
            age=62,
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            facility="Avadi PHC",
            consent="Yes",
            classification="Control",
            classification_reason="Normal CXR, Negative NAAT, and Negative EPTB status",
            date_enroll=timezone.localdate()
        )

        # CSV export (ensure role permits export)
        profile = self.user.profile
        profile.role = "Super Admin"
        profile.save()

        csv_resp = self.client.get(reverse("questions:data_export") + "?format=csv")
        self.assertEqual(csv_resp.status_code, 200)
        csv_content = csv_resp.content.decode("utf-8")
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        headers = rows[0]
        
        self.assertIn("Informed Consent", headers)
        self.assertIn("Exclusion Status", headers)
        self.assertIn("Classification", headers)

        consent_idx = headers.index("Informed Consent")
        excl_idx = headers.index("Exclusion Status")
        class_idx = headers.index("Classification")
        study_id_idx = headers.index("Study ID")

        excluded_row = next(r for r in rows[1:] if r[study_id_idx] == "ABCG-TN-TIR-2026-222222")
        self.assertEqual(excluded_row[consent_idx], "No")
        self.assertEqual(excluded_row[excl_idx], "Excluded from Study")
        self.assertEqual(excluded_row[class_idx], "Excluded")

        consented_row = next(r for r in rows[1:] if r[study_id_idx] == "ABCG-TN-TIR-2026-333333")
        self.assertEqual(consented_row[consent_idx], "Yes")
        self.assertEqual(consented_row[excl_idx], "")
        self.assertEqual(consented_row[class_idx], "Control")

    def test_existing_records_preserved_safely(self):
        """6. Existing records with consent=None are safely preserved without errors."""
        legacy_p = Participant.objects.create(
            first_name="Legacy",
            last_name="Record",
            full_name="Legacy Record",
            study_id="ABCG-TN-TIR-2026-444444",
            contact_number="9876544444",
            age=40,
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            facility="Avadi PHC",
            consent=None,
            classification="Control",
            classification_reason="Legacy enrolled control",
            date_enroll=timezone.localdate()
        )
        
        # GET edit view does not crash and renders
        response = self.client.get(reverse("questions:registration_edit", kwargs={"pk": legacy_p.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Detail view renders cleanly
        detail_resp = self.client.get(reverse("questions:participant_detail", kwargs={"study_id": legacy_p.study_id}))
        self.assertEqual(detail_resp.status_code, 200)
