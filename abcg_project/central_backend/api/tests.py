from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import datetime
from django.utils import timezone
from .models import Participant, TptIndividual, IneligibleIndividual, DeviceSyncLog, GlobalSettings

class CentralBackendSyncTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user, created = User.objects.get_or_create(
            username="admin", 
            defaults={
                "email": "admin@example.com",
                "is_superuser": True,
                "is_staff": True
            }
        )
        self.user.set_password("admin_password")
        self.user.save()
        
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        
        # Ensure GlobalSettings exists
        GlobalSettings.objects.get_or_create(
            name="Study Settings",
            defaults={
                "bmi_threshold": 18.0,
                "age_threshold": 60,
                "campaign_period": "Jan 2025 - Mar 2025"
            }
        )

    def test_auth_login_returns_token(self):
        self.client.credentials()  # Clear auth headers
        response = self.client.post(
            reverse("api:api_login"), 
            data={"username": "admin", "password": "admin_password"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["token"], self.token.key)

    def test_bulk_sync_success(self):
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        payload = {
            "participants": [
                {
                    "study_id": "SCR-123456-7890",
                    "first_name": "Test",
                    "last_name": "Participant",
                    "full_name": "Test Participant",
                    "age": 65,
                    "gender": "Male",
                    "contact_number": "9876543210",
                    "dob": "1960-01-01",
                    "date_enroll": today_str,
                    "state": "Tamil Nadu",
                    "district": "Tiruvallur",
                    "tb_unit": "Tiruvallur TU",
                    "facility": "Local Clinic",
                    "village": "Test Village",
                    "pincode": "600001",
                    "demographic_area": "Rural",
                    "height_cm": 170.0,
                    "weight_kg": 60.0,
                    "bmi": 20.76,
                    "symptoms": "Asymptomatic",
                    "risk_factors": "Individuals aged 60 years or above",
                    "hiv_status": "Negative",
                    "bcg_evidence": "No evidence",
                    "bcg_status": "No",
                    "eligible": True,
                    "eligible_bcg_campaign": True,
                    "bcg_eligibility_criteria": "Was aged >=60 years during the BCG campaign period",
                    "classification": "Control",
                    "classification_reason": "Normal CXR"
                }
            ],
            "tpt_individuals": [
                {
                    "study_id": "SCR-TPT-0001",
                    "first_name": "TPT",
                    "last_name": "User",
                    "full_name": "TPT User",
                    "age": 30,
                    "gender": "Female",
                    "dob": "1996-01-01",
                    "date_enroll": today_str,
                    "state": "Tamil Nadu",
                    "district": "Tiruvallur",
                    "tb_unit": "Tiruvallur TU",
                    "tpt_undergone": "Yes",
                    "tpt_status": "Completed"
                }
            ],
            "ineligible_individuals": [
                {
                    "study_id": "SCR-INEL-0001",
                    "first_name": "Ineligible",
                    "last_name": "User",
                    "full_name": "Ineligible User",
                    "age": 25,
                    "date_enroll": today_str,
                    "state": "Tamil Nadu",
                    "district": "Tiruvallur",
                    "tb_unit": "Tiruvallur TU",
                    "classification": "Not Eligible",
                    "classification_reason": "No Target HRG Match"
                }
            ],
            "telemetry": {
                "latitude": 13.0827,
                "longitude": 80.2707,
                "battery_level": 90,
                "battery_charging": False,
                "device_user_agent": "Mozilla/5.0"
            }
        }

        response = self.client.post(
            reverse("api:bulk_sync"), 
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertIn("SCR-123456-7890", response.data["participants"])
        self.assertIn("SCR-TPT-0001", response.data["tpt_individuals"])
        self.assertIn("SCR-INEL-0001", response.data["ineligible_individuals"])

        # Check DB states
        self.assertEqual(Participant.objects.count(), 1)
        self.assertEqual(TptIndividual.objects.count(), 1)
        self.assertEqual(IneligibleIndividual.objects.count(), 1)
        self.assertEqual(DeviceSyncLog.objects.count(), 1)

        p = Participant.objects.first()
        self.assertEqual(p.study_id, "SCR-123456-7890")
        self.assertTrue(p.eligible)
        self.assertEqual(p.uploaded_by, self.user)

    def test_media_sync_upload(self):
        # Create a participant first
        p = Participant.objects.create(
            study_id="SCR-CXR-8899",
            full_name="Media Tester",
            age=40,
            gender="Female",
            date_enroll=datetime.date.today()
        )

        scar_file = SimpleUploadedFile("scar.jpg", b"dummy_image_data_1", content_type="image/jpeg")
        record_file = SimpleUploadedFile("card.jpg", b"dummy_image_data_2", content_type="image/jpeg")
        cxr_file = SimpleUploadedFile("cxr.jpg", b"dummy_image_data_3", content_type="image/jpeg")

        response = self.client.post(
            reverse("api:media_sync"),
            data={
                "study_id": "SCR-CXR-8899",
                "bcg_scar_file": scar_file,
                "bcg_record_file": record_file,
                "cxr_record_file": cxr_file
            },
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("receipt_id", response.data)
        self.assertIn("checksums", response.data)
        self.assertIn("bcg_scar_file", response.data["checksums"])
        self.assertIn("cxr_record_file", response.data["checksums"])
        
        p.refresh_from_db()
        self.assertTrue(p.bcg_scar_file.name.startswith("bcg_scar_records/scar"))
        self.assertTrue(p.bcg_record_file.name.startswith("bcg_records/card"))
        self.assertTrue(p.cxr_record_file.name.startswith("cxr_records/cxr"))
        self.assertTrue(bool(p.sync_receipt_id))
        self.assertIsNotNone(p.sync_verified_at)
        self.assertIn("bcg_scar_file", p.media_checksums)

    def test_media_sync_ineligible_and_tpt_cohorts(self):
        # Test Ineligible individual photo upload
        inel = IneligibleIndividual.objects.create(
            study_id="INEL-MEDIA-001",
            full_name="Ineligible Media Tester",
            age=35,
            date_enroll=datetime.date.today()
        )
        scar_file = SimpleUploadedFile("inel_scar.jpg", b"ineligible_scar_bytes", content_type="image/jpeg")
        
        resp_inel = self.client.post(
            reverse("api:media_sync"),
            data={"study_id": "INEL-MEDIA-001", "bcg_scar_file": scar_file},
            format="multipart"
        )
        self.assertEqual(resp_inel.status_code, status.HTTP_200_OK)
        self.assertIn("receipt_id", resp_inel.data)
        self.assertEqual(resp_inel.data["cohort"], "IneligibleIndividual")
        
        inel.refresh_from_db()
        self.assertTrue(inel.bcg_scar_file.name.startswith("bcg_scar_records/inel_scar"))
        self.assertTrue(bool(inel.sync_receipt_id))
        self.assertIn("inel_scar.jpg", inel.media_checksums)

        # Test TPT individual CXR upload
        tpt = TptIndividual.objects.create(
            study_id="TPT-MEDIA-002",
            full_name="TPT Media Tester",
            age=50,
            gender="Male",
            date_enroll=datetime.date.today()
        )
        cxr_file = SimpleUploadedFile("tpt_cxr.jpg", b"tpt_cxr_bytes", content_type="image/jpeg")
        resp_tpt = self.client.post(
            reverse("api:media_sync"),
            data={"study_id": "TPT-MEDIA-002", "cxr_record_file": cxr_file},
            format="multipart"
        )
        self.assertEqual(resp_tpt.status_code, status.HTTP_200_OK)
        self.assertIn("receipt_id", resp_tpt.data)
        self.assertEqual(resp_tpt.data["cohort"], "TptIndividual")
        
        tpt.refresh_from_db()
        self.assertTrue(tpt.cxr_record_file.name.startswith("cxr_records/tpt_cxr"))
        self.assertTrue(bool(tpt.sync_receipt_id))

    def test_questions_list_returns_dynamic_questions(self):
        response = self.client.get(reverse("api:questions_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that we got dynamic questions (the seeded database ones)
        self.assertGreater(len(response.data), 0)
        first_q = response.data[0]
        self.assertIn("code", first_q)
        self.assertIn("label", first_q)
        self.assertIn("options", first_q)
        self.assertGreater(len(first_q["options"]), 0)

    def test_rules_engine_evaluates_classification_correctly(self):
        from .eligibility import RulesEngine
        
        # Test case: Case Cohort (MCTB Positive)
        p_case = {
            "age": 45,
            "bmi": 22.0,
            "risk_factors": "Diabetes",
            "eligible_bcg_campaign": True,
            "bcg_eligibility_criteria": "Self-reported diabetes",
            "ptb_test_details": json.dumps({
                "undergone_testing": "Yes",
                "final_interpretation": "MTB Detected"
            })
        }
        classification, reason = RulesEngine.evaluate_classification(p_case)
        self.assertEqual(classification, "Case")
        self.assertIn("MCTB Positive", reason)
        
        # Test case: Control Cohort (Normal CXR, Negative NAAT)
        p_control = {
            "age": 45,
            "bmi": 22.0,
            "risk_factors": "Diabetes",
            "eligible_bcg_campaign": True,
            "bcg_eligibility_criteria": "Self-reported diabetes",
            "ptb_test_details": json.dumps({
                "undergone_testing": "Yes",
                "naat_status": "MTB Not Detected",
                "cxr_done": "Yes",
                "cxr_result": "Normal"
            }),
            "eptb_details": json.dumps({
                "eptb_q1a": "No"
            })
        }
        classification, reason = RulesEngine.evaluate_classification(p_control)
        self.assertEqual(classification, "Control")
        self.assertEqual(reason, "Normal CXR, Negative NAAT, and Negative EPTB status")
        
        # Test case: Excluded Cohort (Abnormal Non-TB CXR)
        p_excluded = {
            "age": 45,
            "bmi": 22.0,
            "risk_factors": "Diabetes",
            "eligible_bcg_campaign": True,
            "bcg_eligibility_criteria": "Self-reported diabetes",
            "ptb_test_details": json.dumps({
                "undergone_testing": "Yes",
                "naat_status": "Negative",
                "cxr_done": "Yes",
                "cxr_result": "Abnormal (Non-TB)"
            })
        }
        classification, reason = RulesEngine.evaluate_classification(p_excluded)
        self.assertEqual(classification, "Excluded")
        self.assertEqual(reason, "Abnormal CXR not suggestive of TB with NAAT Negative")

        # Test case: Incomplete BCG Details (bcg_status="Yes" but details missing)
        p_incomplete_bcg = {
            "age": 45,
            "bmi": 22.0,
            "risk_factors": "Diabetes",
            "eligible_bcg_campaign": True,
            "bcg_eligibility_criteria": "Self-reported diabetes",
            "bcg_status": "Yes", # verified but no date/batch/facility
            "ptb_test_details": json.dumps({
                "undergone_testing": "Yes",
                "final_interpretation": "MTB Detected"
            })
        }
        classification, reason = RulesEngine.evaluate_classification(p_incomplete_bcg)
        self.assertEqual(classification, "Pending")
        self.assertEqual(reason, "One or more required BCG verification or vaccine details are incomplete.")


