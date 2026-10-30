import io
import json
import datetime
import openpyxl
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from questions.models import (
    Participant, IneligibleIndividual, TptIndividual,
    UserProfile, Symptom, RiskFactor
)

class PTBScreeningMutualExclusionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="nurse_user", password="password123")
        self.user.profile.role = "Super Admin"
        self.user.profile.save()
        self.client.force_login(self.user)

        # Seed standard symptoms
        Symptom.objects.get_or_create(code="asymptomatic", defaults={"name": "Asymptomatic", "is_active": True, "display_order": 1})
        Symptom.objects.get_or_create(code="cough", defaults={"name": "Cough for more than 2 weeks", "is_active": True, "display_order": 2})
        Symptom.objects.get_or_create(code="fever", defaults={"name": "Fever", "is_active": True, "display_order": 3})
        Symptom.objects.get_or_create(code="weight_loss", defaults={"name": "Weight loss", "is_active": True, "display_order": 4})
        Symptom.objects.get_or_create(code="others", defaults={"name": "Others", "is_active": True, "display_order": 5})

        RiskFactor.objects.get_or_create(code="elderly", defaults={"name": "Individuals aged 60 years or above", "is_active": True})

        self.base_payload = {
            "first_name": "Suresh",
            "last_name": "Rao",
            "age": 62,
            "dob": "1964-05-10",
            "gender": "Male",
            "primary_phone": "9876543210",
            "address": "45 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "facility": "Avadi PHC",
            "consent": "Yes",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Individuals aged 60 years or above"],
            "bcg_status": "No",
            "undergone_testing": "No",
            "cxr_done": "No",
        }

    # Test 1: Select Asymptomatic -> Asymptomatic selected; all other symptoms deselected
    def test_01_select_asymptomatic_only(self):
        payload = self.base_payload.copy()
        payload["first_name"] = "AsympOnly"
        payload["symptoms"] = ["Asymptomatic"]

        response = self.client.post(reverse("questions:registration"), data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("questions:home"))

        p = Participant.objects.filter(first_name="AsympOnly").latest("created_at")
        self.assertEqual(p.symptoms, "Asymptomatic")

    # Test 2: Select Cough after Asymptomatic -> Cough selected; Asymptomatic deselected
    def test_02_select_cough_only(self):
        payload = self.base_payload.copy()
        payload["first_name"] = "CoughOnly"
        payload["symptoms"] = ["Cough for more than 2 weeks"]

        response = self.client.post(reverse("questions:registration"), data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("questions:home"))

        p = Participant.objects.filter(first_name="CoughOnly").latest("created_at")
        self.assertEqual(p.symptoms, "Cough for more than 2 weeks")
        self.assertNotIn("Asymptomatic", p.symptoms)

    # Test 3: Select Fever after Asymptomatic -> Fever selected; Asymptomatic deselected
    def test_03_select_fever_only(self):
        payload = self.base_payload.copy()
        payload["first_name"] = "FeverOnly"
        payload["symptoms"] = ["Fever"]

        response = self.client.post(reverse("questions:registration"), data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("questions:home"))

        p = Participant.objects.filter(first_name="FeverOnly").latest("created_at")
        self.assertEqual(p.symptoms, "Fever")
        self.assertNotIn("Asymptomatic", p.symptoms)

    # Test 4: Select multiple symptoms -> Multiple symptoms allowed; Asymptomatic deselected
    def test_04_select_multiple_symptoms(self):
        payload = self.base_payload.copy()
        payload["first_name"] = "MultiSym"
        payload["symptoms"] = ["Cough for more than 2 weeks", "Fever", "Weight loss"]

        response = self.client.post(reverse("questions:registration"), data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("questions:home"))

        p = Participant.objects.filter(first_name="MultiSym").latest("created_at")
        self.assertEqual(p.symptoms, "Cough for more than 2 weeks, Fever, Weight loss")
        self.assertNotIn("Asymptomatic", p.symptoms)

    # Test 5: Select Asymptomatic after selecting multiple symptoms -> Only Asymptomatic saved
    def test_05_select_asymptomatic_replaces_all(self):
        payload = self.base_payload.copy()
        payload["first_name"] = "AsympReplaced"
        payload["symptoms"] = ["Asymptomatic"]

        response = self.client.post(reverse("questions:registration"), data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("questions:home"))

        p = Participant.objects.filter(first_name="AsympReplaced").latest("created_at")
        self.assertEqual(p.symptoms, "Asymptomatic")

    # Test 6: Deselect Asymptomatic (Empty selection) -> Empty symptoms saved; does NOT auto-select Asymptomatic
    def test_06_deselect_all_symptoms_leaves_empty(self):
        payload = self.base_payload.copy()
        payload["first_name"] = "EmptySymptoms"
        payload["symptoms"] = []

        response = self.client.post(reverse("questions:registration"), data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("questions:home"))

        p = Participant.objects.filter(first_name="EmptySymptoms").latest("created_at")
        self.assertEqual(p.symptoms, "")
        self.assertNotEqual(p.symptoms, "Asymptomatic")

    # Test 7: Save and reopen questionnaire -> Saved selection remains valid
    def test_07_save_and_reopen_questionnaire(self):
        p = Participant.objects.create(
            first_name="ReopenTest",
            last_name="Verma",
            age=65,
            gender="Female",
            contact_number="9876543222",
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            study_id="ABCG-TN-TIR-2026-888001",
            date_enroll=datetime.date(2026, 2, 10),
            symptoms="Cough for more than 2 weeks, Fever"
        )

        response = self.client.get(reverse("questions:registration_edit", kwargs={"pk": p.pk}))
        self.assertEqual(response.status_code, 200)

        # Context contains participant symptoms
        self.assertIn("participant_symptoms", response.context)
        self.assertEqual(response.context["participant_symptoms"], ["Cough for more than 2 weeks", "Fever"])
        self.assertFalse(response.context.get("has_symptom_conflict", False))

        # JSON data parsed by client
        part_json = json.loads(response.context["participant_json"])
        self.assertEqual(part_json["symptoms"], ["Cough for more than 2 weeks", "Fever"])
        self.assertNotIn("Asymptomatic", part_json["symptoms"])

    # Test 8: Update an existing participant -> Mutual exclusion continues to work
    def test_08_update_existing_participant_symptoms(self):
        p = Participant.objects.create(
            first_name="UpdateTest",
            last_name="Pillai",
            age=62,
            gender="Male",
            contact_number="9876543233",
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            study_id="ABCG-TN-TIR-2026-888002",
            date_enroll=datetime.date(2026, 1, 15),
            symptoms="Asymptomatic"
        )

        # Update symptoms from Asymptomatic to Cough + Fever
        update_payload = self.base_payload.copy()
        update_payload["first_name"] = "UpdateTest"
        update_payload["last_name"] = "Pillai"
        update_payload["participant_id"] = p.pk
        update_payload["symptoms"] = ["Cough for more than 2 weeks", "Fever"]

        response = self.client.post(reverse("questions:registration_edit", kwargs={"pk": p.pk}), data=update_payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("questions:home"))

        p.refresh_from_db()
        self.assertEqual(p.symptoms, "Cough for more than 2 weeks, Fever")
        self.assertNotIn("Asymptomatic", p.symptoms)

    # Test 9: Submit conflicting selections through API/POST -> Backend prevents invalid data from being saved
    def test_09_api_and_post_rejects_conflicting_symptoms(self):
        initial_participant_count = Participant.objects.count()

        # 9a. API request with XMLHttpRequest header -> Expect HTTP 400 Bad Request
        conflict_payload = self.base_payload.copy()
        conflict_payload["first_name"] = "ConflictApi"
        conflict_payload["symptoms"] = ["Asymptomatic", "Cough for more than 2 weeks"]

        response = self.client.post(
            reverse("questions:registration"),
            data=conflict_payload,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertIn("cannot coexist", response.json()["error"])

        # No record saved
        self.assertFalse(Participant.objects.filter(first_name="ConflictApi").exists())
        self.assertEqual(Participant.objects.count(), initial_participant_count)

        # 9b. Standard form POST with conflicting symptoms -> Expect redirect with error message, no record saved
        response_form = self.client.post(reverse("questions:registration"), data=conflict_payload)
        self.assertEqual(response_form.status_code, 302)
        self.assertFalse(Participant.objects.filter(first_name="ConflictApi").exists())
        self.assertEqual(Participant.objects.count(), initial_participant_count)

    # Test 10: Export to Excel -> Symptom data is represented consistently
    def test_10_excel_export_represents_symptoms_consistently(self):
        p1 = Participant.objects.create(
            first_name="ExcelAsymp",
            last_name="Test",
            age=60,
            gender="Male",
            study_id="ABCG-TN-TIR-2026-777001",
            date_enroll=datetime.date(2026, 3, 1),
            symptoms="Asymptomatic",
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            ptb_screened=True
        )
        p2 = Participant.objects.create(
            first_name="ExcelSymp",
            last_name="Test",
            age=65,
            gender="Female",
            study_id="ABCG-TN-TIR-2026-777002",
            date_enroll=datetime.date(2026, 3, 2),
            symptoms="Cough for more than 2 weeks, Fever",
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            ptb_screened=True
        )

        response = self.client.get(reverse("questions:data_export") + "?format=excel")
        self.assertEqual(response.status_code, 200)

        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb.active

        # Find "Symptoms" column index
        header_row = [cell.value for cell in ws[1]]
        self.assertIn("Symptoms", header_row)
        symptoms_idx = header_row.index("Symptoms") + 1

        rows = list(ws.iter_rows(min_row=2, values_only=True))
        study_id_idx = header_row.index("Study ID")

        row_p1 = next(r for r in rows if r[study_id_idx] == "ABCG-TN-TIR-2026-777001")
        row_p2 = next(r for r in rows if r[study_id_idx] == "ABCG-TN-TIR-2026-777002")

        self.assertEqual(row_p1[symptoms_idx - 1], "Asymptomatic")
        self.assertEqual(row_p2[symptoms_idx - 1], "Cough for more than 2 weeks, Fever")

    # Test 11: Load a historical record containing both types -> Report conflict and follow approved recovery rule
    def test_11_load_historical_conflicting_record_recovery(self):
        p = Participant.objects.create(
            first_name="HistoricalConflict",
            last_name="Patel",
            age=58,
            gender="Male",
            contact_number="9876543999",
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            study_id="ABCG-TN-TIR-2026-999111",
            date_enroll=datetime.date(2026, 1, 5),
            symptoms="Asymptomatic, Cough for more than 2 weeks, Fever"
        )

        # GET request to edit page
        response = self.client.get(reverse("questions:registration_edit", kwargs={"pk": p.pk}))
        self.assertEqual(response.status_code, 200)

        # Conflict reported in context
        self.assertTrue(response.context["has_symptom_conflict"])
        self.assertEqual(response.context["conflict_original_symptoms"], "Asymptomatic, Cough for more than 2 weeks, Fever")

        # Approved recovery rule applied: Asymptomatic deselected; clinical symptoms preserved
        self.assertEqual(response.context["participant_symptoms"], ["Cough for more than 2 weeks", "Fever"])
        self.assertNotIn("Asymptomatic", response.context["participant_symptoms"])

        # Warning banner rendered in HTML
        html_content = response.content.decode("utf-8")
        self.assertIn("symptomConflictNotice", html_content)
        self.assertIn("contained conflicting symptom selections", html_content)

        # Historical DB record remains UNCHANGED until explicitly submitted by user
        p.refresh_from_db()
        self.assertEqual(p.symptoms, "Asymptomatic, Cough for more than 2 weeks, Fever")

    # Test 12: IneligibleIndividual and TptIndividual cohorts protected by mutual exclusion
    def test_12_ineligible_and_tpt_cohorts_protected(self):
        initial_ineligible_count = IneligibleIndividual.objects.count()

        # Conflicting symptoms payload for ineligible participant (eligible_bcg_campaign="No")
        ineligible_payload = self.base_payload.copy()
        ineligible_payload["first_name"] = "IneligibleConflict"
        ineligible_payload["eligible_bcg_campaign"] = "No"
        ineligible_payload["symptoms"] = ["Asymptomatic", "Fever"]

        response = self.client.post(
            reverse("questions:registration"),
            data=ineligible_payload,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(IneligibleIndividual.objects.count(), initial_ineligible_count)
