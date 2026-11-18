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
        ws = wb.active
        self.assertTrue(ws.title.startswith("abcg_primary_data_"))
        self.assertLessEqual(len(ws.title), 31)
        excel_headers = [cell.value for cell in ws[1]]

        expected_key_headers = [
            "PTB Screening Administered", "Symptoms", "PTB Undergone Testing", "PTB Predominant Symptom",
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
        ws = wb.active
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
        ws = wb.active
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
        ws = wb.active
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

    def test_05_ineligible_and_excluded_records_preserve_all_filled_details(self):
        """Verifies ineligible/excluded participants preserve all filled clinical and screening details on dedicated Sheet 2."""
        inel = IneligibleIndividual.objects.create(
            first_name="Ineligible",
            last_name="Individual",
            study_id="INEL-001",
            age=22,
            gender="Male",
            date_enroll=datetime.date(2026, 4, 9),
            classification="Not Eligible",
            classification_reason="Age criteria not met",
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
        # 1. Primary Sheet 1 must NOT contain ineligible individual
        ws1 = wb.active
        s1_headers = [cell.value for cell in ws1[1]]
        s1_sid_col = s1_headers.index("Study ID") + 1
        s1_sids = [ws1.cell(row=r, column=s1_sid_col).value for r in range(2, ws1.max_row + 1)]
        self.assertNotIn("INEL-001", s1_sids)

        # 2. Dedicated Sheet 2 (abcg_ineligible_data) MUST contain ineligible record with reason and all filled clinicals
        self.assertIn("abcg_ineligible_data", wb.sheetnames)
        ws2 = wb["abcg_ineligible_data"]
        headers = [cell.value for cell in ws2[1]]

        study_id_col = headers.index("Study ID") + 1
        inel_reason_col = headers.index("Ineligibility Reason") + 1
        ptb_avail_col = headers.index("PTB Sample Available") + 1
        ptb_res_col = headers.index("PTB Sample Results") + 1
        eptb_avail_col = headers.index("EPTB Sample Available") + 1
        eptb_res_col = headers.index("EPTB Sample Results") + 1

        inel_row = None
        for r in range(2, ws2.max_row + 1):
            if ws2.cell(row=r, column=study_id_col).value == "INEL-001":
                inel_row = r
                break

        self.assertIsNotNone(inel_row)
        self.assertEqual(ws2.cell(row=inel_row, column=inel_reason_col).value, "Age criteria not met")
        self.assertEqual(ws2.cell(row=inel_row, column=ptb_avail_col).value, "Present")
        self.assertEqual(ws2.cell(row=inel_row, column=ptb_res_col).value, "MTB Detected")
        self.assertEqual(ws2.cell(row=inel_row, column=eptb_avail_col).value, "Present")
        self.assertEqual(ws2.cell(row=inel_row, column=eptb_res_col).value, "MTB Detected")

    def test_06_primary_and_secondary_cohort_separation_and_naming(self):
        """Verifies TPT=NO (Primary) and TPT=YES (Secondary) are exported into distinct workbooks with matching tab names."""
        from django.utils import timezone
        from questions.models import TptIndividual
        yymmdd = timezone.now().strftime("%y%m%d")

        # 1. Create a distinct Primary participant (TPT=No)
        p_prim = Participant.objects.create(
            first_name="Primary",
            last_name="Participant",
            study_id="PRIM-TEST-001",
            age=30,
            gender="Male",
            date_enroll=datetime.date(2026, 4, 10),
            tpt_undergone="No"
        )

        # 2. Create a distinct Secondary participant (TPT=Yes, Eligible)
        p_sec = TptIndividual.objects.create(
            first_name="Secondary",
            last_name="Participant",
            study_id="SEC-TEST-001",
            age=32,
            gender="Female",
            date_enroll=datetime.date(2026, 4, 10),
            tpt_undergone="Yes"
        )

        # 3. Create a distinct Secondary participant (TPT=Yes, Ineligible)
        p_sec_inel = TptIndividual.objects.create(
            first_name="SecondaryIneligible",
            last_name="Participant",
            study_id="SEC-INEL-001",
            age=35,
            gender="Female",
            date_enroll=datetime.date(2026, 4, 10),
            tpt_undergone="Yes",
            classification="Not Eligible",
            classification_reason="Contraindicated"
        )

        # --- TEST PRIMARY EXPORT (TPT = NO) ---
        resp_prim_excel = self.client.get(reverse("questions:data_export") + "?format=excel&cohort=primary")
        self.assertEqual(resp_prim_excel.status_code, 200)
        expected_prim_name = f"abcg_primary_data_{yymmdd}"
        self.assertIn(f'filename="{expected_prim_name}.xlsx"', resp_prim_excel["Content-Disposition"])

        wb_prim = openpyxl.load_workbook(io.BytesIO(resp_prim_excel.content))
        # Primary workbook has 3 sheets: primary, ineligible, summary
        self.assertEqual(wb_prim.sheetnames, [expected_prim_name, "abcg_ineligible_data", "Summary Statistics"])
        self.assertLessEqual(len(wb_prim.sheetnames[0]), 31)
        self.assertLessEqual(len(wb_prim.sheetnames[1]), 31)

        ws_prim = wb_prim.active
        prim_headers = [c.value for c in ws_prim[1]]
        sid_col = prim_headers.index("Study ID") + 1
        prim_sids = [ws_prim.cell(row=r, column=sid_col).value for r in range(2, ws_prim.max_row + 1)]
        self.assertIn("PRIM-TEST-001", prim_sids)
        self.assertNotIn("SEC-TEST-001", prim_sids)
        self.assertNotIn("SEC-INEL-001", prim_sids)

        # Primary CSV (ZIP archive containing separate eligible and ineligible CSVs)
        resp_prim_csv = self.client.get(reverse("questions:data_export") + "?format=csv&cohort=primary")
        self.assertEqual(resp_prim_csv.status_code, 200)
        self.assertIn(f'filename="{expected_prim_name}.zip"', resp_prim_csv["Content-Disposition"])
        import zipfile
        zf_prim = zipfile.ZipFile(io.BytesIO(resp_prim_csv.content))
        self.assertIn(f"{expected_prim_name}.csv", zf_prim.namelist())
        self.assertIn(f"abcg_ineligible_data_{yymmdd}.csv", zf_prim.namelist())
        prim_csv_text = zf_prim.read(f"{expected_prim_name}.csv").decode("utf-8")
        self.assertIn("PRIM-TEST-001", prim_csv_text)
        self.assertNotIn("SEC-TEST-001", prim_csv_text)
        self.assertNotIn("SEC-INEL-001", prim_csv_text)

        # --- TEST SECONDARY EXPORT (TPT = YES) ---
        resp_sec_excel = self.client.get(reverse("questions:data_export") + "?format=excel&cohort=secondary")
        self.assertEqual(resp_sec_excel.status_code, 200)
        expected_sec_name = f"abcg_secondary_data_{yymmdd}"
        self.assertIn(f'filename="{expected_sec_name}.xlsx"', resp_sec_excel["Content-Disposition"])

        wb_sec = openpyxl.load_workbook(io.BytesIO(resp_sec_excel.content))
        # Secondary workbook now has 3 sheets: secondary (eligible), ineligible, summary
        self.assertEqual(wb_sec.sheetnames, [expected_sec_name, "abcg_ineligible_data", "Summary Statistics"])
        self.assertLessEqual(len(wb_sec.sheetnames[0]), 31)
        self.assertLessEqual(len(wb_sec.sheetnames[1]), 31)

        # Sheet 1: secondary eligible
        ws_sec = wb_sec.active
        sec_headers = [c.value for c in ws_sec[1]]
        sec_sid_col = sec_headers.index("Study ID") + 1
        sec_sids = [ws_sec.cell(row=r, column=sec_sid_col).value for r in range(2, ws_sec.max_row + 1)]
        self.assertIn("SEC-TEST-001", sec_sids)
        self.assertNotIn("SEC-INEL-001", sec_sids)
        self.assertNotIn("PRIM-TEST-001", sec_sids)

        # Sheet 2: secondary ineligible
        ws_sec_inel = wb_sec["abcg_ineligible_data"]
        sec_inel_headers = [c.value for c in ws_sec_inel[1]]
        sec_inel_sid_col = sec_inel_headers.index("Study ID") + 1
        sec_inel_reason_col = sec_inel_headers.index("Ineligibility Reason") + 1
        sec_inel_sids = [ws_sec_inel.cell(row=r, column=sec_inel_sid_col).value for r in range(2, ws_sec_inel.max_row + 1)]
        self.assertIn("SEC-INEL-001", sec_inel_sids)
        self.assertNotIn("SEC-TEST-001", sec_inel_sids)

        # Secondary CSV (ZIP archive containing separate eligible and ineligible CSVs)
        resp_sec_csv = self.client.get(reverse("questions:data_export") + "?format=csv&cohort=secondary")
        self.assertEqual(resp_sec_csv.status_code, 200)
        self.assertIn(f'filename="{expected_sec_name}.zip"', resp_sec_csv["Content-Disposition"])
        zf_sec = zipfile.ZipFile(io.BytesIO(resp_sec_csv.content))
        self.assertIn(f"{expected_sec_name}.csv", zf_sec.namelist())
        self.assertIn(f"abcg_ineligible_data_{yymmdd}.csv", zf_sec.namelist())
        sec_csv_text = zf_sec.read(f"{expected_sec_name}.csv").decode("utf-8")
        sec_inel_text = zf_sec.read(f"abcg_ineligible_data_{yymmdd}.csv").decode("utf-8")
        self.assertIn("SEC-TEST-001", sec_csv_text)
        self.assertIn("SEC-INEL-001", sec_inel_text)
        self.assertNotIn("PRIM-TEST-001", sec_csv_text)

        # --- EDGE CASE: Missing cohort parameter defaults to primary ---
        resp_default = self.client.get(reverse("questions:data_export") + "?format=excel")
        self.assertIn(f'filename="{expected_prim_name}.xlsx"', resp_default["Content-Disposition"])

        # --- EDGE CASE: Unknown cohort parameter defaults to primary ---
        resp_unknown = self.client.get(reverse("questions:data_export") + "?format=excel&cohort=invalid_cohort")
        self.assertIn(f'filename="{expected_prim_name}.xlsx"', resp_unknown["Content-Disposition"])

    def test_07_ineligible_csv_export_and_per_cohort_dedup(self):
        """Verifies dedicated ineligible CSV export and checks that dedup does not swallow records across cohorts."""
        from django.utils import timezone
        yymmdd = timezone.now().strftime("%y%m%d")

        # Create two individuals with identical phone number: one eligible primary, one ineligible
        p_shared = Participant.objects.create(
            first_name="EligibleUser",
            last_name="Primary",
            study_id="DEDUP-PRIM-001",
            contact_number="9876543210",
            age=35,
            gender="Male",
            date_enroll=datetime.date(2026, 4, 11),
            tpt_undergone="No"
        )
        inel_shared = IneligibleIndividual.objects.create(
            first_name="IneligibleUser",
            last_name="Screened",
            study_id="DEDUP-INEL-001",
            contact_number="9876543210",
            age=16,
            gender="Female",
            date_enroll=datetime.date(2026, 4, 10),
            classification="Not Eligible",
            classification_reason="Age < 18"
        )

        # Ineligible CSV download
        resp_inel_csv = self.client.get(reverse("questions:data_export") + "?format=csv&cohort=ineligible")
        self.assertEqual(resp_inel_csv.status_code, 200)
        expected_inel_name = f"abcg_ineligible_data_{yymmdd}"
        self.assertIn(f'filename="{expected_inel_name}.csv"', resp_inel_csv["Content-Disposition"])
        inel_csv_content = resp_inel_csv.content.decode("utf-8")
        self.assertIn("DEDUP-INEL-001", inel_csv_content)
        self.assertNotIn("DEDUP-PRIM-001", inel_csv_content)

        # Primary Excel export with dedup=unique:
        # Both must survive because dedup is scoped within each cohort!
        resp_excel = self.client.get(reverse("questions:data_export") + "?format=excel&cohort=primary&dedup=unique")
        self.assertEqual(resp_excel.status_code, 200)
        wb = openpyxl.load_workbook(io.BytesIO(resp_excel.content))
        ws_prim = wb.active
        ws_inel = wb["abcg_ineligible_data"]

        prim_headers = [c.value for c in ws_prim[1]]
        prim_sid_col = prim_headers.index("Study ID") + 1
        prim_sids = [ws_prim.cell(row=r, column=prim_sid_col).value for r in range(2, ws_prim.max_row + 1)]
        self.assertIn("DEDUP-PRIM-001", prim_sids)

        inel_headers = [c.value for c in ws_inel[1]]
        inel_sid_col = inel_headers.index("Study ID") + 1
        inel_sids = [ws_inel.cell(row=r, column=inel_sid_col).value for r in range(2, ws_inel.max_row + 1)]
        self.assertIn("DEDUP-INEL-001", inel_sids)


