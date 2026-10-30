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
    UserProfile
)

class ExportSampleDetailsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username="export_admin", password="password123")
        self.admin_user.profile.role = "Super Admin"
        self.admin_user.profile.save()
        self.client.force_login(self.admin_user)

    def test_01_excel_and_csv_headers_contain_ptb_and_eptb_sample_fields(self):
        """Verifies both Excel and CSV export headers contain sample available and sample results for PTB and EPTB."""
        # 1. Excel export
        response_excel = self.client.get(reverse("questions:data_export") + "?format=excel")
        self.assertEqual(response_excel.status_code, 200)

        wb = openpyxl.load_workbook(io.BytesIO(response_excel.content))
        ws = wb["Master Registry"]
        excel_headers = [cell.value for cell in ws[1]]

        expected_key_headers = [
            "PTB Screened", "Symptoms", "PTB Undergone Testing", "PTB Predominant Symptom",
            "PTB Symptom Duration (Days)", "PTB HCP Visits", "PTB Case Type",
            "EPTB Screened", "EPTB Asymptomatic", "EPTB Symptoms", "EPTB Doctor History",
            "EPTB Lymph Node Swelling", "EPTB Pleural Symptoms", "EPTB CNS / Meningitis Symptoms",
            "EPTB Abdominal Symptoms", "EPTB Spine / Joint Symptoms", "EPTB Genitourinary Symptoms",
            "EPTB Female Genital Symptoms", "EPTB Cutaneous Symptoms", "EPTB Ocular Symptoms",
            "EPTB Pericardial Symptoms", "EPTB Disseminated Symptoms",
            "PTB Test Registered", "PTB Test Reason", "PTB Test Type",
            "PTB Testing Facility State", "PTB Testing Facility District", "PTB Test Facility",
            "PTB Sample Available", "PTB Sample Type", "PTB Sputum Collection Detail",
            "PTB Sample Description", "PTB Sample Serial ID", "PTB Sample QR Code",
            "PTB Sample Collection Date", "PTB Sample Collection Time", "PTB Sample Collection Site",
            "PTB Sample Referral Site", "PTB Sample Referral Date",
            "PTB Result Available", "PTB Lab Serial Number", "PTB Result Sample ID",
            "PTB Date Tested", "PTB Date Reported", "PTB Reported By", "PTB NAAT Status",
            "PTB Sample Results", "PTB Test Result", "PTB Test Date", "PTB Test Remarks",
            "EPTB Investigations Performed", "EPTB Investigation Facility", "EPTB Investigation Date",
            "EPTB Sample Available", "EPTB Sample Type", "EPTB Sample Serial ID", "EPTB Sample QR Code",
            "EPTB Collection Date", "EPTB Collection Time", "EPTB Collection Site",
            "EPTB Result Available", "EPTB Lab Serial Number", "EPTB Date Tested",
            "EPTB Date Reported", "EPTB Reported By", "EPTB Sample Results", "EPTB Remarks",
            "EPTB Classification Status"
        ]

        for h in expected_key_headers:
            self.assertIn(h, excel_headers)

        # 2. CSV export
        response_csv = self.client.get(reverse("questions:data_export") + "?format=csv")
        self.assertEqual(response_csv.status_code, 200)
        csv_content = response_csv.content.decode("utf-8")
        csv_headers = [h.strip() for h in csv_content.split("\n")[0].split(",")]

        for h in expected_key_headers:
            self.assertIn(h, csv_headers)

    def test_02_ptb_sample_available_and_results_exported_accurately(self):
        """Verifies PTB sample availability and sample results are properly extracted into Excel."""
        # Participant 1: PTB sample present with MTB Detected result
        p1 = Participant.objects.create(
            first_name="PtbPresent",
            last_name="Sharma",
            study_id="ABCG-PTB-001",
            age=62,
            gender="Male",
            date_enroll=datetime.date(2026, 4, 1),
            ptb_screened=True,
            ptb_test_registered=True,
            ptb_test_type="TrueNat / CBNAAT",
            ptb_test_result="M. tuberculosis Detected (Rifampicin Resistance Not Detected)",
            ptb_test_details=json.dumps({
                "sample_availability": "Present",
                "sample_details": {
                    "samples": [{
                        "sample_type": "Sputum",
                        "sample_serial_id": "SP-001",
                        "collection_date": "2026-04-01"
                    }]
                },
                "result_availability": "Present",
                "final_interpretation": "M. tuberculosis Detected (Rifampicin Resistance Not Detected)"
            })
        )

        # Participant 2: PTB sample absent, no test result
        p2 = Participant.objects.create(
            first_name="PtbAbsent",
            last_name="Kumar",
            study_id="ABCG-PTB-002",
            age=64,
            gender="Female",
            date_enroll=datetime.date(2026, 4, 2),
            ptb_screened=True,
            ptb_test_registered=False,
            ptb_test_details=json.dumps({
                "sample_availability": "Absent",
                "undergone_testing": "No"
            })
        )

        response = self.client.get(reverse("questions:data_export") + "?format=excel")
        self.assertEqual(response.status_code, 200)

        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb["Master Registry"]
        headers = [cell.value for cell in ws[1]]

        study_id_col = headers.index("Study ID") + 1
        ptb_avail_col = headers.index("PTB Sample Available") + 1
        ptb_res_col = headers.index("PTB Sample Results") + 1

        row_p1 = None
        row_p2 = None
        for r in range(2, ws.max_row + 1):
            sid = ws.cell(row=r, column=study_id_col).value
            if sid == "ABCG-PTB-001":
                row_p1 = r
            elif sid == "ABCG-PTB-002":
                row_p2 = r

        self.assertIsNotNone(row_p1)
        self.assertIsNotNone(row_p2)

        # Assert Participant 1
        self.assertEqual(ws.cell(row=row_p1, column=ptb_avail_col).value, "Present")
        self.assertEqual(ws.cell(row=row_p1, column=ptb_res_col).value, "M. tuberculosis Detected (Rifampicin Resistance Not Detected)")

        # Assert Participant 2
        self.assertEqual(ws.cell(row=row_p2, column=ptb_avail_col).value, "Absent")
        self.assertIn(ws.cell(row=row_p2, column=ptb_res_col).value, ["", None])

    def test_03_eptb_sample_available_and_results_exported_accurately(self):
        """Verifies EPTB sample availability and sample results are properly extracted into Excel."""
        # Participant 3: EPTB with Lymph Node FNAC (lab test)
        p3 = Participant.objects.create(
            first_name="EptbLab",
            last_name="Reddy",
            study_id="ABCG-EPTB-001",
            age=55,
            gender="Female",
            date_enroll=datetime.date(2026, 4, 5),
            eptb_screened=True,
            eptb_details=json.dumps({
                "eptb_asymptomatic": "No",
                "eptb_q1a": "Yes",
                "eptb_investigation_lymph_node_tb_fnac_performed": "Yes",
                "eptb_investigation_lymph_node_tb_fnac_sample_available": "Present",
                "eptb_investigation_lymph_node_tb_fnac_sample_type": "Lymph Node Aspirate",
                "eptb_investigation_lymph_node_tb_fnac_sample_serial_id": "LNA-9001",
                "eptb_investigation_lymph_node_tb_fnac_result_available": "Present",
                "eptb_investigation_lymph_node_tb_fnac_final_interpretation": "MTB Detected"
            })
        )

        # Participant 4: EPTB with Spine MRI (imaging test)
        p4 = Participant.objects.create(
            first_name="EptbImaging",
            last_name="Patel",
            study_id="ABCG-EPTB-002",
            age=58,
            gender="Male",
            date_enroll=datetime.date(2026, 4, 6),
            eptb_screened=True,
            eptb_details=json.dumps({
                "eptb_asymptomatic": "No",
                "eptb_q5a": "Yes",
                "eptb_investigation_spinal_tb_pott_s_disease_mri_performed": "Yes",
                "eptb_investigation_spinal_tb_pott_s_disease_mri_result_available": "Present",
                "eptb_investigation_spinal_tb_pott_s_disease_mri_result_findings": "Suggestive of TB"
            })
        )

        # Participant 5: EPTB Asymptomatic
        p5 = Participant.objects.create(
            first_name="EptbAsymp",
            last_name="Nair",
            study_id="ABCG-EPTB-003",
            age=61,
            gender="Male",
            date_enroll=datetime.date(2026, 4, 7),
            eptb_screened=False,
            eptb_details=json.dumps({
                "eptb_asymptomatic": "Yes"
            })
        )

        response = self.client.get(reverse("questions:data_export") + "?format=excel")
        self.assertEqual(response.status_code, 200)

        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb["Master Registry"]
        headers = [cell.value for cell in ws[1]]

        study_id_col = headers.index("Study ID") + 1
        eptb_avail_col = headers.index("EPTB Sample Available") + 1
        eptb_res_col = headers.index("EPTB Sample Results") + 1

        row_map = {}
        for r in range(2, ws.max_row + 1):
            sid = ws.cell(row=r, column=study_id_col).value
            if sid in ["ABCG-EPTB-001", "ABCG-EPTB-002", "ABCG-EPTB-003"]:
                row_map[sid] = r

        # Assert Participant 3 (Lab test)
        self.assertEqual(ws.cell(row=row_map["ABCG-EPTB-001"], column=eptb_avail_col).value, "Present")
        self.assertEqual(ws.cell(row=row_map["ABCG-EPTB-001"], column=eptb_res_col).value, "MTB Detected")

        # Assert Participant 4 (Imaging test)
        self.assertEqual(ws.cell(row=row_map["ABCG-EPTB-002"], column=eptb_res_col).value, "Suggestive of TB")

        # Assert Participant 5 (Asymptomatic)
        self.assertIn(ws.cell(row=row_map["ABCG-EPTB-003"], column=eptb_avail_col).value, ["", None])
        self.assertIn(ws.cell(row=row_map["ABCG-EPTB-003"], column=eptb_res_col).value, ["", None])

    def test_04_multiple_eptb_investigations_joined_cleanly(self):
        """Verifies multiple EPTB investigations are cleanly aggregated with semicolon separators."""
        p = Participant.objects.create(
            first_name="MultiEptb",
            last_name="Das",
            study_id="ABCG-EPTB-MULTI",
            age=49,
            gender="Female",
            date_enroll=datetime.date(2026, 4, 8),
            eptb_screened=True,
            eptb_details=json.dumps({
                "eptb_asymptomatic": "No",
                "eptb_q1a": "Yes",
                "eptb_q2a": "Yes",
                "eptb_investigation_lymph_node_tb_fnac_performed": "Yes",
                "eptb_investigation_lymph_node_tb_fnac_sample_available": "Present",
                "eptb_investigation_lymph_node_tb_fnac_final_interpretation": "MTB Detected",
                "eptb_investigation_pleural_tb_pleural_fluid_analysis_performed": "Yes",
                "eptb_investigation_pleural_tb_pleural_fluid_analysis_sample_available": "Present",
                "eptb_investigation_pleural_tb_pleural_fluid_analysis_final_interpretation": "MTB Not Detected"
            })
        )

        response = self.client.get(reverse("questions:data_export") + "?format=excel")
        self.assertEqual(response.status_code, 200)

        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb["Master Registry"]
        headers = [cell.value for cell in ws[1]]

        study_id_col = headers.index("Study ID") + 1
        eptb_avail_col = headers.index("EPTB Sample Available") + 1
        eptb_res_col = headers.index("EPTB Sample Results") + 1

        for r in range(2, ws.max_row + 1):
            if ws.cell(row=r, column=study_id_col).value == "ABCG-EPTB-MULTI":
                self.assertEqual(ws.cell(row=r, column=eptb_avail_col).value, "Present")
                res_val = ws.cell(row=r, column=eptb_res_col).value
                self.assertIn("MTB Detected", res_val)
                self.assertIn("MTB Not Detected", res_val)
                break

    def test_05_ineligible_records_have_blanked_clinical_sample_data(self):
        """Verifies ineligible participants have clinical sample available and results blanked."""
        inel = IneligibleIndividual.objects.create(
            first_name="Ineligible",
            last_name="Individual",
            study_id="INEL-001",
            age=22,
            gender="Male",
            date_enroll=datetime.date(2026, 4, 9),
            classification="Not Eligible",
            ptb_test_details=json.dumps({
                "sample_availability": "Present",
                "final_interpretation": "MTB Detected"
            }),
            eptb_details=json.dumps({
                "eptb_investigation_lymph_node_tb_fnac_sample_available": "Present",
                "eptb_investigation_lymph_node_tb_fnac_final_interpretation": "MTB Detected"
            })
        )

        response = self.client.get(reverse("questions:data_export") + "?format=excel")
        self.assertEqual(response.status_code, 200)

        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb["Master Registry"]
        headers = [cell.value for cell in ws[1]]

        study_id_col = headers.index("Study ID") + 1
        ptb_avail_col = headers.index("PTB Sample Available") + 1
        ptb_res_col = headers.index("PTB Sample Results") + 1
        eptb_avail_col = headers.index("EPTB Sample Available") + 1
        eptb_res_col = headers.index("EPTB Sample Results") + 1

        for r in range(2, ws.max_row + 1):
            if ws.cell(row=r, column=study_id_col).value == "INEL-001":
                self.assertIn(ws.cell(row=r, column=ptb_avail_col).value, ["", None])
                self.assertIn(ws.cell(row=r, column=ptb_res_col).value, ["", None])
                self.assertIn(ws.cell(row=r, column=eptb_avail_col).value, ["", None])
                self.assertIn(ws.cell(row=r, column=eptb_res_col).value, ["", None])
                break

