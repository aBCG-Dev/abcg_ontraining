from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.utils import timezone
from questions import views

class QuestionsRoutingAndViewsTestCase(TestCase):
    def setUp(self):
        # Create a test user and their profile is created automatically by signals
        self.username = "teststaff"
        self.password = "password123"
        self.user = User.objects.create_user(
            username=self.username,
            email="teststaff@example.com",
            password=self.password
        )
        self.user.first_name = "Test"
        self.user.last_name = "Staff"
        self.user.save()
        
    def test_home_url_resolves(self):
        url = reverse("questions:home")
        self.assertEqual(resolve(url).func, views.home)
        
    def test_home_page_renders_login_for_anonymous(self):
        response = self.client.get(reverse("questions:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_login_page"])
        self.assertTemplateUsed(response, "questions/home.html")
        
    def test_login_post_redirects_to_home(self):
        response = self.client.post(reverse("questions:home"), {
            "username": self.username,
            "password": self.password
        })
        self.assertRedirects(response, reverse("questions:home"))
        
    def test_login_post_redirects_to_dashboard_for_doctor(self):
        profile = self.user.profile
        profile.role = "Doctor"
        profile.save()
        response = self.client.post(reverse("questions:home"), {
            "username": self.username,
            "password": self.password
        })
        self.assertRedirects(response, reverse("questions:dashboard_home"))
        
    def test_home_page_renders_dashboard_for_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("questions:home"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_login_page"])
        self.assertEqual(response.context["site"]["state"], "Tamil Nadu")
        
    def test_home_page_redirects_for_authenticated_doctor(self):
        profile = self.user.profile
        profile.role = "Doctor"
        profile.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("questions:home"))
        self.assertRedirects(response, reverse("questions:dashboard_home"))
        
    def test_registration_page_redirects_anonymous(self):
        response = self.client.get(reverse("questions:registration"))
        self.assertRedirects(response, reverse("questions:home"))
        
    def test_registration_page_get_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("questions:registration"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "questions/registration.html")
        
    def test_registration_page_post_creates_participant(self):
        self.client.login(username=self.username, password=self.password)
        # Verify initial database count
        from questions.models import Participant
        initial_count = Participant.objects.count()
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Muni",
            "last_name": "Ramana",
            "father_husband_name": "Father Name",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543210",
            "secondary_phone": "9123456789",
            "secondary_phone_1": "9876543211",
            "secondary_phone_2": "9876543212",
            "secondary_phone_3": "9876543213",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "public_phi": "Avadi PHC",
            "taluka_block": "Avadi Taluka",
            "landmark": "Near Temple",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "contact_person_name": "Contact Name",
            "contact_person_phone": "9876543219",
            "contact_person_address": "456 Main St",
            "informant_name": "Informant Name",
            "informant_designation": "Staff Nurse",
            "symptoms": ["Fever", "Weight loss"],
            "risk_factors": ["Diabetes", "Tobacco/smoker"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Self-reported diabetes during the BCG campaign period"]
        })
        self.assertRedirects(response, reverse("questions:home"))
        
        # Verify database record creation
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        
        self.assertEqual(p.first_name, "Muni")
        self.assertEqual(p.last_name, "Ramana")
        self.assertEqual(p.full_name, "Muni Ramana")
        self.assertEqual(p.father_husband_name, "Father Name")
        self.assertEqual(p.age, 45)
        self.assertEqual(p.gender, "Male")
        self.assertEqual(p.contact_number, "9876543210")
        self.assertEqual(p.secondary_phone, "9123456789")
        self.assertEqual(p.secondary_phone_1, "9876543211")
        self.assertEqual(p.secondary_phone_2, "9876543212")
        self.assertEqual(p.secondary_phone_3, "9876543213")
        self.assertEqual(p.sector, "Public Sector")
        self.assertEqual(p.case_finding_type, "Passive (Routine programme)")
        self.assertEqual(p.public_phi, "Avadi PHC")
        self.assertEqual(p.facility, "Avadi PHC")
        self.assertEqual(p.taluka_block, "Avadi Taluka")
        self.assertEqual(p.landmark, "Near Temple")
        self.assertEqual(p.village, "Karani Village")
        self.assertEqual(p.pincode, "602001")
        self.assertEqual(p.demographic_area, "Rural")
        self.assertEqual(p.marital_status, "Single")
        self.assertEqual(p.occupation, "Teaching professional")
        self.assertEqual(p.socioeconomic_status, "APL")
        self.assertEqual(p.contact_person_name, "Contact Name")
        self.assertEqual(p.contact_person_phone, "9876543219")
        self.assertEqual(p.contact_person_address, "456 Main St")
        self.assertEqual(p.informant_name, "Informant Name")
        self.assertEqual(p.informant_designation, "Staff Nurse")
        self.assertEqual(p.symptoms, "Fever, Weight loss")
        self.assertEqual(p.risk_factors, "Diabetes, Tobacco/smoker")
        self.assertEqual(p.hiv_status, "Non Reactive / Negative")
        self.assertTrue(p.eligible_bcg_campaign)
        self.assertTrue(p.eligible)
        self.assertEqual(p.classification, "Pending")
        self.assertTrue(p.study_id.startswith("ABCG-"))
        self.assertTrue(p.screening_id.startswith("SCR-"))
        
    def test_registration_page_post_creates_eligible_participant_asymptomatic(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        initial_count = Participant.objects.count()
        
        # Asymptomatic with an HRG (Diabetes) should be ELIGIBLE now
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Asymptomatic",
            "last_name": "Eligible",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543211",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "facility": "Tiruvallur PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "symptoms": ["Asymptomatic"],
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative"
        })
        self.assertRedirects(response, reverse("questions:home"))
        
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        self.assertTrue(p.eligible)
        self.assertEqual(p.classification, "Pending")
        self.assertEqual(p.match_hrg, "Diabetes")

    def test_registration_page_post_creates_ineligible_participant_no_hrg(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant, IneligibleIndividual
        initial_count = Participant.objects.count()
        initial_ineligible_count = IneligibleIndividual.objects.count()
        
        # Has symptoms but NO target HRG (HIV / AIDS is NOT in the 6 HRGs) should be INELIGIBLE
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Symptomatic",
            "last_name": "Ineligible",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543212",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "facility": "Tiruvallur PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "symptoms": ["Fever"],
            "risk_factors": ["HIV / AIDS"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Self-reported diabetes during the BCG campaign period"]
        })
        self.assertRedirects(response, reverse("questions:home"))
        
        self.assertEqual(Participant.objects.count(), initial_count)
        self.assertEqual(IneligibleIndividual.objects.count(), initial_ineligible_count + 1)
        p = IneligibleIndividual.objects.latest("created_at")
        self.assertFalse(p.eligible)
        self.assertEqual(p.classification, "Not Eligible")
        self.assertEqual(p.match_hrg, "Does not match any Target High Risk Group (HRG)")

    def test_registration_page_post_creates_eligible_participant_smoker(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        initial_count = Participant.objects.count()
        
        # Tobacco/smoker should be ELIGIBLE under the new 6 target HRGs rule
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Smoker",
            "last_name": "Eligible",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543216",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "facility": "Tiruvallur PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "symptoms": ["Fever"],
            "risk_factors": ["Individuals with a history of smoking tobacco (Current / Past User)- self reported"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Self-reported smoking during the BCG campaign period"]
        })
        self.assertRedirects(response, reverse("questions:home"))
        
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        self.assertTrue(p.eligible)
        self.assertEqual(p.classification, "Pending")
        self.assertEqual(p.match_hrg, "History of smoking tobacco")

        
    def test_registration_page_post_creates_ineligible_participant_no_bcg_campaign(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant, IneligibleIndividual
        initial_count = Participant.objects.count()
        initial_ineligible_count = IneligibleIndividual.objects.count()
        
        # Has target HRG (Diabetes) but NO BCG campaign eligibility ("No") should be INELIGIBLE
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Campaign",
            "last_name": "Ineligible",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543215",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "facility": "Tiruvallur PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "symptoms": ["Fever"],
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "No"
        })
        self.assertRedirects(response, reverse("questions:home"))
        
        self.assertEqual(Participant.objects.count(), initial_count)
        self.assertEqual(IneligibleIndividual.objects.count(), initial_ineligible_count + 1)
        p = IneligibleIndividual.objects.latest("created_at")
        self.assertFalse(p.eligible)
        self.assertEqual(p.classification, "Not Eligible")
        self.assertEqual(p.match_hrg, "Not eligible for BCG vaccine during campaign period")

    def test_search_page_get_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("questions:search"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "questions/search.html")
        
    def test_pending_sync_page_get_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("questions:pending_sync"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "questions/pending_sync.html")

    def test_reconcile_page_redirects_anonymous(self):
        from questions.models import Participant
        p = Participant.objects.create(
            full_name="Muni Ramana",
            study_id="SCR-TEMP-781",
            age=45,
            gender="Male",
            date_enroll="2026-07-17"
        )
        response = self.client.get(reverse("questions:reconcile", args=[p.pk]))
        self.assertRedirects(response, reverse("questions:home"))
        
    def test_reconcile_page_get_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        p = Participant.objects.create(
            full_name="Muni Ramana",
            study_id="SCR-TEMP-781",
            age=45,
            gender="Male",
            date_enroll="2026-07-17"
        )
        response = self.client.get(reverse("questions:reconcile", args=[p.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "questions/reconcile.html")
        
    def test_reconcile_page_post_reconciles_data(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        p = Participant.objects.create(
            full_name="Muni Ramana",
            study_id="SCR-TEMP-781",
            age=45,
            gender="Male",
            date_enroll="2026-07-17"
        )
        response = self.client.post(reverse("questions:reconcile", args=[p.pk]), data={
            "agree_name": "on",
            "agree_age": "on",
            "nikshay_id": "NK-88301-B"
        })
        self.assertRedirects(response, reverse("questions:search"))
        
        p.refresh_from_db()
        self.assertEqual(p.full_name, "Muni Ramanan")
        self.assertEqual(p.age, 46)
        self.assertEqual(p.nikshay_id, "NK-88301-B")
        self.assertTrue(p.synced)

    def test_registration_asymptomatic(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        initial_count = Participant.objects.count()
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Muni",
            "last_name": "Ramana",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543210",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "public_phi": "Avadi PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "symptoms": ["Asymptomatic"],
            "test_reason": "Diagnosis of TB",
            "test_type": "CBNAAT",
            "cxr_status": "Normal",
            "naat_status": "MTB Not Detected",
            "facility_state": "Karnataka",
            "facility_district": "Dharwad",
            "testing_lab": "SDM College of Medical Sciences Lab"
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        self.assertTrue(p.eligible)
        self.assertTrue(p.ptb_screened)
        self.assertTrue(p.ptb_test_registered)
        self.assertEqual(p.symptoms, "Asymptomatic")
        self.assertEqual(p.classification, "Control")

    def test_registration_symptomatic_positive(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        initial_count = Participant.objects.count()
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Muni",
            "last_name": "Ramana",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543210",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "public_phi": "Avadi PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "symptoms": ["Cough for more than 2 weeks", "Fever"],
            "test_reason": "Diagnosis of TB",
            "test_type": "CBNAAT",
            "cxr_status": "Suggestive of TB",
            "naat_status": "MTB Detected",
            "predominant_symptom": "Cough",
            "duration_days": "15",
            "hcp_visits": "2",
            "case_type": "New",
            "facility_state": "Karnataka",
            "facility_district": "Dharwad",
            "testing_lab": "Dharwad District TB Centre Lab",
            "sample_availability": "Present",
            "result_availability": "Present",
            "sample_mapping_option": "Add New Sample",
            "sample_type": "Sputum",
            "sputum_collection_detail": "Supervised",
            "sample_description": "Purulent",
            "collection_date": "2026-07-20",
            "collection_time": "10:30",
            "collection_site_state": "Karnataka",
            "collection_site_district": "Dharwad",
            "collection_site": "Dharwad Hospital Site",
            "sample_serial_id": "SMP-99120",
            "lab_serial_number": "LAB-88301",
            "result_sample_id": "Sample 1",
            "date_tested": "2026-07-20",
            "date_reported": "2026-07-20",
            "final_interpretation": "MTB Detected"
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        self.assertTrue(p.eligible)
        self.assertTrue(p.ptb_screened)
        self.assertTrue(p.ptb_test_registered)
        self.assertEqual(p.symptoms, "Cough for more than 2 weeks, Fever")
        self.assertEqual(p.ptb_test_type, "CBNAAT")
        self.assertEqual(p.ptb_test_result, "MTB Detected")
        self.assertEqual(p.classification, "Case")
        
        # Check serialization
        import json
        details = json.loads(p.ptb_test_details)
        self.assertEqual(details["test_reason"], "Diagnosis of TB")
        self.assertEqual(details["sample_details"]["sample_serial_id"], "SMP-99120")
        self.assertEqual(details["result_details"]["final_interpretation"], "MTB Detected")

    def test_registration_symptomatic_negative(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        initial_count = Participant.objects.count()
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Muni",
            "last_name": "Ramana",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543210",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "public_phi": "Avadi PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "symptoms": ["Cough for more than 2 weeks", "Others"],
            "other_symptom": "Chest tightness",
            "test_reason": "Diagnosis of TB",
            "test_type": "Chest X Ray",
            "cxr_status": "Normal",
            "naat_status": "MTB Not Detected",
            "predominant_symptom": "Other",
            "duration_days": "10",
            "hcp_visits": "1",
            "case_type": "New",
            "facility_state": "Karnataka",
            "facility_district": "Dharwad",
            "testing_lab": "SDM College of Medical Sciences Lab",
            "sample_availability": "Absent",
            "result_availability": "Present",
            "lab_serial_number": "LAB-88302",
            "result_sample_id": "Sample 1",
            "date_tested": "2026-07-20",
            "date_reported": "2026-07-20",
            "final_interpretation": "MTB Not Detected"
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        self.assertTrue(p.eligible)
        self.assertTrue(p.ptb_screened)
        self.assertTrue(p.ptb_test_registered)
        self.assertEqual(p.symptoms, "Cough for more than 2 weeks, Others (Chest tightness)")
        self.assertEqual(p.ptb_test_type, "Chest X Ray")
        self.assertEqual(p.ptb_test_result, "MTB Not Detected")
        self.assertEqual(p.classification, "Control")

    def test_registration_edit_draft(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        
        # 1. Create a draft participant first
        p = Participant.objects.create(
            first_name="DraftFirst",
            last_name="DraftLast",
            full_name="DraftFirst DraftLast",
            study_id="SCR-990011-0000",
            contact_number="9999999999",
            age=30,
            date_enroll=timezone.localdate(),
            synced=False,
            eligible=True,
            classification="Pending"
        )
        
        # Verify initial values
        self.assertEqual(Participant.objects.count(), 1)
        
        # 2. Submit edit form post with updated parameters
        response = self.client.post(reverse("questions:registration_edit", kwargs={"pk": p.pk}), data={
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast",
            "age": 35,
            "dob": "1991-01-01",
            "gender": "Female",
            "primary_phone": "8888888888",
            "address": "456 Edit Street",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "public_phi": "Avadi PHC",
            "village": "Avadi Village",
            "pincode": "600054",
            "demographic_area": "Urban",
            "marital_status": "Married",
            "occupation": "Clerical and related workers",
            "socioeconomic_status": "BPL",
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "symptoms": ["Asymptomatic"],
            "test_reason": "Diagnosis of TB",
            "test_type": "CBNAAT",
            "cxr_status": "Suggestive of TB",
            "naat_status": "MTB Detected",
            "facility_state": "Karnataka",
            "facility_district": "Dharwad",
            "testing_lab": "SDM College of Medical Sciences Lab"
        })
        self.assertRedirects(response, reverse("questions:home"))
        
        # Verify database count did not change (updated instead of created)
        self.assertEqual(Participant.objects.count(), 1)
        
        # Reload participant and assert changes
        p.refresh_from_db()
        self.assertEqual(p.first_name, "UpdatedFirst")
        self.assertEqual(p.last_name, "UpdatedLast")
        self.assertEqual(p.full_name, "UpdatedFirst UpdatedLast")
        self.assertEqual(p.contact_number, "8888888888")
        self.assertEqual(p.age, 35)
        self.assertEqual(p.gender, "Female")
        self.assertEqual(p.classification, "Case") # Since NAAT is MTB Detected
        self.assertTrue(p.ptb_test_registered)

    def test_registration_asymptomatic_no_test(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        initial_count = Participant.objects.count()
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Muni",
            "last_name": "Ramana",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543210",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "public_phi": "Avadi PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "symptoms": ["Asymptomatic"],
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        self.assertTrue(p.eligible)
        self.assertTrue(p.ptb_screened)
        self.assertFalse(p.ptb_test_registered)
        self.assertEqual(p.symptoms, "Asymptomatic")
        self.assertEqual(p.classification, "Pending")

    def test_registration_multiple_samples(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        import json
        initial_count = Participant.objects.count()
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Muni",
            "last_name": "Ramana",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543210",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "public_phi": "Avadi PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "symptoms": ["Fever"],
            "test_reason": "Diagnosis of TB",
            "test_type": "CBNAAT",
            "cxr_status": "Normal",
            "naat_status": "MTB Detected",
            "facility_state": "Karnataka",
            "facility_district": "Dharwad",
            "testing_lab": "SDM College of Medical Sciences Lab",
            "sample_availability": "Present",
            "result_availability": "Present",
            
            # Sample 1 (index suffix _1)
            "sample_mapping_option_1": "Add New Sample",
            "sample_type_1": "Sputum",
            "sputum_collection_detail_1": "Supervised",
            "sample_description_1": "Purulent",
            "collection_date_1": "2026-07-22",
            "collection_time_1": "10:00",
            "referral_date_1": "2026-07-22",
            "collection_site_state_1": "Karnataka",
            "collection_site_district_1": "Dharwad",
            "collection_site_1": "SDM Site",
            "sample_serial_id_1": "SMP-1001",
            "sample_qr_code_1": "QR-SMP-1001",
            
            # Sample 2 (index suffix _2)
            "sample_mapping_option_2": "Map Existing Sample",
            "sample_type_2": "Blood",
            "sputum_collection_detail_2": "",
            "sample_description_2": "",
            "collection_date_2": "2026-07-22",
            "collection_time_2": "11:00",
            "referral_date_2": "2026-07-22",
            "collection_site_state_2": "Karnataka",
            "collection_site_district_2": "Dharwad",
            "collection_site_2": "KIMS Hubli Site",
            "sample_serial_id_2": "SMP-1002",
            "sample_qr_code_2": "QR-SMP-1002",
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        self.assertTrue(p.eligible)
        self.assertTrue(p.ptb_test_registered)
        self.assertEqual(p.classification, "Case")
        
        # Verify both samples are saved correctly in ptb_test_details
        details = json.loads(p.ptb_test_details)
        sample_details = details.get("sample_details", {})
        samples = sample_details.get("samples", [])
        self.assertEqual(len(samples), 2)
        
        # Verify first sample
        self.assertEqual(samples[0]["sample_serial_id"], "SMP-1001")
        self.assertEqual(samples[0]["sample_type"], "Sputum")
        
        # Verify second sample
        self.assertEqual(samples[1]["sample_serial_id"], "SMP-1002")
        self.assertEqual(samples[1]["sample_type"], "Blood")
        
        # Verify backward compatibility (first sample fields in root)
        self.assertEqual(sample_details["sample_serial_id"], "SMP-1001")
        self.assertEqual(sample_details["sample_type"], "Sputum")

    def test_registration_single_cxr_details(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        import json
        initial_count = Participant.objects.count()
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Muni",
            "last_name": "Ramana",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543210",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "public_phi": "Avadi PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "symptoms": ["Fever"],
            "test_reason": "Diagnosis of TB",
            "test_type": "CBNAAT",
            "cxr_done": "Yes",
            
            # Single CXR details
            "cxr_id": "CXR-A01",
            "cxr_date": "2026-07-22",
            "cxr_facility": "Avadi Hospital",
            "cxr_result": "Suggestive of TB",
            
            "naat_status": "",
            "facility_state": "Karnataka",
            "facility_district": "Dharwad",
            "testing_lab": "SDM College of Medical Sciences Lab",
            "sample_availability": "Absent",
            "result_availability": "Absent",
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        self.assertTrue(p.eligible)
        self.assertTrue(p.ptb_test_registered)
        
        # Verify CXR details saved correctly
        details = json.loads(p.ptb_test_details)
        cxr_details = details.get("cxr_details", {})
        self.assertEqual(cxr_details.get("cxr_done"), "Yes")
        self.assertEqual(cxr_details.get("cxr_id"), "CXR-A01")
        self.assertEqual(cxr_details.get("cxr_date"), "2026-07-22")
        self.assertEqual(cxr_details.get("cxr_facility"), "Avadi Hospital")
        self.assertEqual(cxr_details.get("cxr_result"), "Suggestive of TB")
        
        # Verify legacy cxr_status value derived from CXR result
        self.assertEqual(details["cxr_status"], "Suggestive of TB")
        
        # Should classify as Case since CXR is suggestive of TB (and NAAT is empty)
        self.assertEqual(p.classification, "Case")


class DynamicQuestionsTestCase(TestCase):
    def setUp(self):
        self.username = "adminuser"
        self.password = "pass123"
        self.user = User.objects.create_user(
            username=self.username,
            email="admin@example.com",
            password=self.password
        )
        self.user.save()

    def test_dynamic_questions_in_context(self):
        from questions.models import Question, Option
        # Create a new dynamic question
        q = Question.objects.create(
            code="custom_question",
            label="Custom Test Question",
            step=1,
            field_type="select",
            display_order=99
        )
        Option.objects.create(
            question=q,
            code="opt_one",
            name="Option One",
            display_order=1
        )

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("questions:registration"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("questions", response.context)
        
        # Verify the new question and option is present in context
        questions_dict = response.context["questions"]
        self.assertIn("custom_question", questions_dict)
        self.assertEqual(questions_dict["custom_question"]["question"].label, "Custom Test Question")
        self.assertEqual(questions_dict["custom_question"]["options"][0].name, "Option One")

    def test_registration_saves_eptb_questionnaire_details(self):
        from questions.models import Participant
        import json
        self.client.login(username=self.username, password=self.password)
        initial_count = Participant.objects.count()
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Eptb",
            "last_name": "Tester",
            "age": 30,
            "dob": "1996-05-12",
            "gender": "Female",
            "primary_phone": "9876543299",
            "address": "123 Green Ave",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "facility": "Tiruvallur PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Married",
            "occupation": "Other",
            "socioeconomic_status": "BPL",
            "symptoms": ["Fever"],
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Self-reported diabetes during the BCG campaign period"],
            "eptb_q1a": "Yes",
            "eptb_q1b": "Yes",
            "eptb_q1c": "No",
            "eptb_q1d": "Don't know",
            "eptb_q2a": "No"
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        
        # Verify EPTB JSON details saved correctly
        eptb = json.loads(p.eptb_details)
        self.assertEqual(eptb.get("eptb_q1a"), "Yes")
        self.assertEqual(eptb.get("eptb_q1b"), "Yes")
        self.assertEqual(eptb.get("eptb_q1c"), "No")
        self.assertEqual(eptb.get("eptb_q1d"), "Don't know")
        self.assertEqual(eptb.get("eptb_q2a"), "No")

    def test_registration_saves_cxr_file(self):
        from questions.models import Participant
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username=self.username, password=self.password)
        initial_count = Participant.objects.count()
        
        cxr_file = SimpleUploadedFile("test_cxr.jpg", b"file_content", content_type="image/jpeg")
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "CxrFile",
            "last_name": "Tester",
            "age": 35,
            "dob": "1991-05-12",
            "gender": "Male",
            "primary_phone": "9876543290",
            "address": "123 Green Ave",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "facility": "Tiruvallur PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Married",
            "occupation": "Other",
            "socioeconomic_status": "BPL",
            "symptoms": ["Fever"],
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Self-reported diabetes during the BCG campaign period"],
            "cxr_record_file": cxr_file
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        self.assertTrue("test_cxr" in p.cxr_record_file.name)

    def test_registration_saves_bcg_scar_file(self):
        from questions.models import Participant
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username=self.username, password=self.password)
        initial_count = Participant.objects.count()
        
        scar_file = SimpleUploadedFile("test_scar.jpg", b"scar_content", content_type="image/jpeg")
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "ScarFile",
            "last_name": "Tester",
            "age": 35,
            "dob": "1991-05-12",
            "gender": "Male",
            "primary_phone": "9876543291",
            "address": "123 Green Ave",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "facility": "Tiruvallur PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Married",
            "occupation": "Other",
            "socioeconomic_status": "BPL",
            "symptoms": ["Fever"],
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Self-reported diabetes during the BCG campaign period"],
            "bcg_scar": "Yes",
            "bcg_scar_file": scar_file
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        self.assertTrue("test_scar" in p.bcg_scar_file.name)

    def test_registration_saves_eptb_investigations(self):
        from questions.models import Participant
        import json
        self.client.login(username=self.username, password=self.password)
        initial_count = Participant.objects.count()
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "EptbInv",
            "last_name": "Tester",
            "age": 30,
            "dob": "1996-05-12",
            "gender": "Female",
            "primary_phone": "9876543292",
            "address": "123 Green Ave",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "facility": "Tiruvallur PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Married",
            "occupation": "Other",
            "socioeconomic_status": "BPL",
            "symptoms": ["Fever"],
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Self-reported diabetes during the BCG campaign period"],
            
            "eptb_q5a": "Yes",
            "eptb_investigation_spinal_tb_pott_s_disease_mri_performed": "Yes",
            "eptb_investigation_spinal_tb_pott_s_disease_mri_date": "2026-07-01",
            "eptb_investigation_spinal_tb_pott_s_disease_mri_facility": "Apollo",
            "eptb_investigation_spinal_tb_pott_s_disease_mri_result_findings": "Suggestive of TB",
            "eptb_investigation_spinal_tb_pott_s_disease_mri_date_reported": "2026-07-02"
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        
        eptb = json.loads(p.eptb_details)
        self.assertEqual(eptb.get("eptb_q5a"), "Yes")
        self.assertEqual(eptb.get("eptb_investigation_spinal_tb_pott_s_disease_mri_performed"), "Yes")
        self.assertEqual(eptb.get("eptb_investigation_spinal_tb_pott_s_disease_mri_date"), "2026-07-01")
        self.assertEqual(eptb.get("eptb_investigation_spinal_tb_pott_s_disease_mri_facility"), "Apollo")
        self.assertEqual(eptb.get("eptb_investigation_spinal_tb_pott_s_disease_mri_result_findings"), "Suggestive of TB")
        self.assertEqual(eptb.get("eptb_investigation_spinal_tb_pott_s_disease_mri_date_reported"), "2026-07-02")

    def test_registration_saves_undergone_testing_no(self):
        from questions.models import Participant
        import json
        self.client.login(username=self.username, password=self.password)
        initial_count = Participant.objects.count()
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "NoTest",
            "last_name": "Tester",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543293",
            "address": "123 Green Ave",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "facility": "Tiruvallur PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Married",
            "occupation": "Other",
            "socioeconomic_status": "BPL",
            "symptoms": ["Fever"],
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Self-reported diabetes during the BCG campaign period"],
            "undergone_testing": "No"
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        
        ptb_details = json.loads(p.ptb_test_details)
        self.assertEqual(ptb_details.get("undergone_testing"), "No")
        self.assertEqual(ptb_details.get("test_reason"), "")
        self.assertIsNone(p.ptb_test_type)

    def test_registration_saves_undergone_testing_waiting(self):
        from questions.models import Participant
        import json
        self.client.login(username=self.username, password=self.password)
        initial_count = Participant.objects.count()
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "WaitingTest",
            "last_name": "Tester",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543294",
            "address": "123 Green Ave",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "facility": "Tiruvallur PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Married",
            "occupation": "Other",
            "socioeconomic_status": "BPL",
            "symptoms": ["Fever"],
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Self-reported diabetes during the BCG campaign period"],
            "undergone_testing": "Yes, waiting for results",
            "test_reason": "Diagnosis of TB",
            "test_type": "CBNAAT"
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        
        ptb_details = json.loads(p.ptb_test_details)
        self.assertEqual(ptb_details.get("undergone_testing"), "Yes, waiting for results")
        self.assertEqual(ptb_details.get("test_reason"), "Diagnosis of TB")
        self.assertEqual(p.ptb_test_type, "CBNAAT")

    def test_registration_without_bcg_eligibility_criteria_makes_participant_ineligible(self):
        from questions.models import Participant, IneligibleIndividual
        self.client.login(username=self.username, password=self.password)
        initial_count = Participant.objects.count()
        initial_ineligible_count = IneligibleIndividual.objects.count()
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "NoBcg",
            "last_name": "Criteria",
            "age": 30,
            "dob": "1996-05-12",
            "gender": "Female",
            "primary_phone": "9876543291",
            "address": "123 Green Ave",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "facility": "Tiruvallur PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Married",
            "occupation": "Other",
            "socioeconomic_status": "BPL",
            "symptoms": ["Fever"],
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": [],
            "has_bcg_eligibility_criteria_form": "true"
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count)
        self.assertEqual(IneligibleIndividual.objects.count(), initial_ineligible_count + 1)
        p = IneligibleIndividual.objects.latest("created_at")
        self.assertFalse(p.eligible)
        self.assertFalse(p.eligible_bcg_campaign)
        self.assertEqual(p.classification, "Not Eligible")

    def test_verify_beneficiary_anonymous_fails(self):
        response = self.client.get(reverse("questions:verify_beneficiary") + "?beneficiary_id=123")
        self.assertEqual(response.status_code, 401)

    def test_verify_beneficiary_success(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import BcgVaccination
        # Create a mock beneficiary
        b = BcgVaccination.objects.create(
            beneficiary_id="test-ben-99",
            first_name="Alice",
            last_name="Johnson",
            beneficiary_gender="Female",
            ben_gender="2",
            age=40,
            ben_mobile_number="9876543210",
            dob="01-Jan-1986",
            date="15",
            registration_mode="in_session",
            vaccination_status="1",
            beneficiary_type_name="Diabetes",
            address="Test Address",
            pincode="600001",
            facility_id="10565",
            site_id="790441",
            approved_by="881627",
            date_created="2024-11-20T11:12:50.026Z"
        )
        
        # Test found
        response = self.client.get(reverse("questions:verify_beneficiary") + "?beneficiary_id=test-ben-99")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["exists"])
        self.assertEqual(data["first_name"], "Alice")
        self.assertEqual(data["last_name"], "Johnson")
        self.assertEqual(data["ben_gender"], "2")
        self.assertEqual(data["site_id"], "790441")
        self.assertEqual(data["approved_by"], "881627")

        # Test not found
        response = self.client.get(reverse("questions:verify_beneficiary") + "?beneficiary_id=nonexistent")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["exists"])

    def test_registration_with_bcg_verification_details(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant
        initial_count = Participant.objects.count()
        
        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "Verified",
            "last_name": "User",
            "father_husband_name": "Father Name",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543210",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "public_phi": "Avadi PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            "symptoms": ["Fever"],
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Self-reported diabetes during the BCG campaign period"],
            
            # Step 7 fields
            "bcg_status": "Yes",
            "bcg_scar": "Yes",
            "bcg_has_record": "Yes",
            "bcg_beneficiary_id": "test-ben-99",
            "bcg_first_name": "Alice",
            "bcg_last_name": "Johnson",
            "bcg_ben_mobile_number": "9876543210",
            "bcg_ben_gender": "2",
            "bcg_dob": "01-Jan-1986",
            "bcg_age": "40",
            "bcg_vaccination_status": "1",
            "bcg_date": "15",
            "bcg_registration_mode": "in_session",
            "bcg_beneficiary_type_name": "Diabetes",
            "bcg_approved_by": "881627",
            "bcg_site_id": "790441",
            "bcg_facility_id": "10565",
            "bcg_pincode": "600001",
            "bcg_address": "Test Address",
            
            # Legacy fields for form validation compatibility
            "bcg_vaccination_date": "2024-11-20",
            "bcg_vaccine_name": "BCG",
            "bcg_batch_number": "BATCH123",
            "bcg_facility": "Test GH"
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_count + 1)
        p = Participant.objects.latest("created_at")
        self.assertEqual(p.bcg_status, "Yes")
        self.assertEqual(p.bcg_beneficiary_id, "test-ben-99")
        self.assertEqual(p.bcg_first_name, "Alice")
        self.assertEqual(p.bcg_site_id, "790441")
        self.assertEqual(p.bcg_approved_by, "881627")

    def test_tpt_bcg_cohort_eligibility(self):
        self.client.login(username=self.username, password=self.password)
        from questions.models import Participant, TptIndividual
        initial_participant_count = Participant.objects.count()
        initial_tpt_count = TptIndividual.objects.count()

        response = self.client.post(reverse("questions:registration"), data={
            "first_name": "TPTBCG",
            "last_name": "CohortParticipant",
            "father_husband_name": "Father Name",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543210",
            "address": "123 Temple Road",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "sector": "Public Sector",
            "case_finding_type": "Passive (Routine programme)",
            "public_phi": "Avadi PHC",
            "village": "Karani Village",
            "pincode": "602001",
            "demographic_area": "Rural",
            "marital_status": "Single",
            "occupation": "Teaching professional",
            "socioeconomic_status": "APL",
            
            # Height, Weight, BMI
            "height_cm": "170.0",
            "weight_kg": "75.0",
            "bmi": "25.95",

            # High Risk Factors (Step 4)
            "symptoms": ["Fever"],
            "risk_factors": ["Diabetes"],
            "hiv_status": "Non Reactive / Negative",
            "eligible_bcg_campaign": "Yes",
            "bcg_eligibility_criteria": ["Self-reported diabetes during the BCG campaign period"],
            
            # TPT details (Step 4)
            "tpt_undergone": "Yes",
            "tpt_risk_factor": "Diabetes mellitus",
            "tpt_history": "Past",
            "tpt_start_date": "2024-01-01",
            "tpt_end_date": "2024-04-01",
            "tpt_duration_months": "3",
            "tpt_regimen": "3HP – 3 months weekly Isoniazid + Rifapentine",

            # Step 7 BCG verification details
            "bcg_status": "Yes",
            "bcg_scar": "Yes",
            "bcg_has_record": "Yes",
            "bcg_beneficiary_id": "test-ben-99",
            "bcg_first_name": "Alice",
            "bcg_last_name": "Johnson",
            "bcg_ben_mobile_number": "9876543210",
            "bcg_ben_gender": "2",
            "bcg_dob": "01-Jan-1986",
            "bcg_age": "40",
            "bcg_vaccination_status": "1",
            "bcg_date": "15",
            "bcg_registration_mode": "in_session",
            "bcg_beneficiary_type_name": "Diabetes",
            "bcg_approved_by": "881627",
            "bcg_site_id": "790441",
            "bcg_facility_id": "10565",
            "bcg_pincode": "600001",
            "bcg_address": "Test Address",
            
            # Legacy fields for form validation compatibility
            "bcg_vaccination_date": "2024-11-20",
            "bcg_vaccine_name": "BCG",
            "bcg_batch_number": "BATCH123",
            "bcg_facility": "Test GH"
        })
        self.assertRedirects(response, reverse("questions:home"))
        self.assertEqual(Participant.objects.count(), initial_participant_count)
        self.assertEqual(TptIndividual.objects.count(), initial_tpt_count + 1)
        p = TptIndividual.objects.latest("created_at")
        
        # Verify Height, Weight, BMI
        self.assertEqual(p.height_cm, 170.0)
        self.assertEqual(p.weight_kg, 75.0)
        self.assertEqual(p.bmi, 25.95)

        # Verify TPT
        self.assertEqual(p.tpt_undergone, "Yes")
        self.assertEqual(p.tpt_risk_factor, "Diabetes mellitus")
        self.assertEqual(p.tpt_history, "Past")
        self.assertEqual(str(p.tpt_start_date), "2024-01-01")
        self.assertEqual(str(p.tpt_end_date), "2024-04-01")
        self.assertEqual(p.tpt_duration_months, 3)
        self.assertEqual(p.tpt_regimen, "3HP – 3 months weekly Isoniazid + Rifapentine")

        # Verify TPT+BCG cohort classification override
        self.assertEqual(p.classification, "TPT+BCG")

    def test_pending_sync_saves_device_telemetry(self):
        from unittest.mock import patch, MagicMock
        from questions.models import DeviceSyncLog, Participant
        self.client.login(username=self.username, password=self.password)
        
        # Create an unsynced participant first
        Participant.objects.create(
            first_name="Unsynced",
            last_name="Test",
            study_id="SCR-990011-2222",
            synced=False,
            eligible=True,
            age=40,
            date_enroll=timezone.localdate()
        )
        
        # Verify counts before sync
        self.assertEqual(Participant.objects.filter(synced=False).count(), 1)
        self.assertEqual(DeviceSyncLog.objects.count(), 0)
        
        # Mock requests.post and requests.get calls
        with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
            mock_auth_resp = MagicMock()
            mock_auth_resp.status_code = 200
            mock_auth_resp.json.return_value = {"token": "mock-token-123"}
            
            mock_sync_resp = MagicMock()
            mock_sync_resp.status_code = 200
            mock_sync_resp.json.return_value = {
                "status": "success",
                "participants": ["SCR-990011-2222"],
                "tpt_individuals": [],
                "ineligible_individuals": []
            }
            
            mock_post.side_effect = [mock_auth_resp, mock_sync_resp]
            
            mock_get_resp = MagicMock()
            mock_get_resp.status_code = 200
            mock_get_resp.json.return_value = [
                {
                    "code": "sector",
                    "label": "Sector",
                    "step": 1,
                    "field_type": "radio",
                    "display_order": 0,
                    "is_active": True,
                    "options": [
                        {"code": "public_sector", "name": "Public Sector", "display_order": 0, "is_active": True}
                    ]
                }
            ]
            mock_get.return_value = mock_get_resp
            
            # Submit POST sync request with telemetry
            response = self.client.post(reverse("questions:pending_sync"), data={
                "latitude": "12.9716",
                "longitude": "77.5946",
                "battery_level": "85",
                "battery_charging": "true"
            })
            
            self.assertEqual(mock_post.call_count, 2)
            self.assertEqual(mock_get.call_count, 1)
        
        # Verify redirect
        self.assertRedirects(response, reverse("questions:pending_sync"))
        
        # Verify records are now synced
        self.assertEqual(Participant.objects.filter(synced=False).count(), 0)
        
        # Verify DeviceSyncLog creation and details
        self.assertEqual(DeviceSyncLog.objects.count(), 1)
        log = DeviceSyncLog.objects.first()
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.latitude, 12.9716)
        self.assertEqual(log.longitude, 77.5946)
        self.assertEqual(log.battery_level, 85)
        self.assertTrue(log.battery_charging)
        self.assertEqual(log.synced_count, 1)

    def test_pending_sync_ajax_error_handling(self):
        from unittest.mock import patch, MagicMock
        from questions.models import Participant
        self.client.login(username=self.username, password=self.password)
        
        Participant.objects.create(
            first_name="Unsynced",
            last_name="Test",
            study_id="SCR-990011-2222",
            synced=False,
            eligible=True,
            age=40,
            date_enroll=timezone.localdate()
        )
        
        with patch("requests.post") as mock_post:
            mock_auth_resp = MagicMock()
            mock_auth_resp.status_code = 401
            mock_auth_resp.text = "Unauthorized credentials"
            mock_post.return_value = mock_auth_resp
            
            response = self.client.post(
                reverse("questions:pending_sync"),
                data={"format": "json"},
                HTTP_X_REQUESTED_WITH="XMLHttpRequest"
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "error")
            self.assertIn("Authentication with central backend failed", data["message"])

    def test_dashboard_statistics_by_login_and_site(self):
        from questions.models import TptIndividual, Participant
        # Create a second user and configure their profile with a different site
        from django.contrib.auth.models import User
        user_b = User.objects.create_user(
            username="teststaff_b",
            email="teststaff_b@example.com",
            password="password123"
        )
        profile_b = user_b.profile
        profile_b.state = "Karnataka"
        profile_b.district = "Bengaluru"
        profile_b.tb_unit = "Bengaluru TU"
        profile_b.save()

        # Define today
        today = timezone.localdate()

        # Create Participant under self.user (Tamil Nadu TU site)
        # 1. Case (Registered today, Tamil Nadu TU site)
        Participant.objects.create(
            first_name="Tamil Nadu",
            last_name="Case Today",
            study_id="SCR-111111-0001",
            age=40,
            date_enroll=today,
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            classification="Case",
            created_by=self.user
        )

        # 2. Control (Registered today, Tamil Nadu TU site)
        Participant.objects.create(
            first_name="Tamil Nadu",
            last_name="Control Today",
            study_id="SCR-111111-0002",
            age=45,
            date_enroll=today,
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            classification="Control",
            created_by=self.user
        )

        # 3. TptIndividual (Registered today, Tamil Nadu TU site)
        TptIndividual.objects.create(
            first_name="Tamil Nadu",
            last_name="Tpt Today",
            study_id="SCR-111111-0003",
            age=50,
            date_enroll=today,
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            classification="TPT+BCG",
            created_by=self.user
        )

        # 4. Participant under self.user but with a different site (Karnataka site)
        Participant.objects.create(
            first_name="Tamil Nadu User",
            last_name="Wrong Site",
            study_id="SCR-111111-0004",
            age=30,
            date_enroll=today,
            state="Karnataka",
            district="Bengaluru",
            tb_unit="Bengaluru TU",
            classification="Case",
            created_by=self.user
        )

        # 5. Participant under user_b (Karnataka site)
        Participant.objects.create(
            first_name="Karnataka User",
            last_name="Case",
            study_id="SCR-222222-0001",
            age=35,
            date_enroll=today,
            state="Karnataka",
            district="Bengaluru",
            tb_unit="Bengaluru TU",
            classification="Case",
            created_by=user_b
        )

        # Now test dashboard stats for self.user
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("questions:home"))
        self.assertEqual(response.status_code, 200)
        
        # Stats should only count first three (total registered today = 3)
        # It should exclude SCR-111111-0004 (wrong site) and SCR-222222-0001 (wrong login)
        self.assertEqual(response.context["stats"]["registered_today"], 3)
        # Total cases should be 1 (Tamil Nadu Case Today)
        self.assertEqual(response.context["stats"]["cases"], 1)
        # Total controls should be 1 (Tamil Nadu Control Today)
        self.assertEqual(response.context["stats"]["controls"], 1)

        # Log out and log in as user_b
        self.client.logout()
        self.client.login(username="teststaff_b", password="password123")
        response_b = self.client.get(reverse("questions:home"))
        self.assertEqual(response_b.status_code, 200)
        
        # Stats for user_b should only count SCR-222222-0001 (total registered today = 1)
        self.assertEqual(response_b.context["stats"]["registered_today"], 1)
        self.assertEqual(response_b.context["stats"]["cases"], 1)
        self.assertEqual(response_b.context["stats"]["controls"], 0)

    def test_dashboard_statistics_updated_on_edit_and_reconcile(self):
        from questions.models import Participant
        # Create a participant with no created_by and different site (legacy record)
        p = Participant.objects.create(
            first_name="Legacy",
            last_name="Record",
            study_id="SCR-888888-0001",
            age=40,
            date_enroll=timezone.localdate(),
            state="Karnataka",
            district="Bengaluru",
            tb_unit="Bengaluru TU",
            classification="Case",
            created_by=None
        )

        # Log in as self.user (Tamil Nadu TU site)
        self.client.login(username=self.username, password=self.password)

        # Reconcile the legacy participant
        response = self.client.post(
            reverse("questions:reconcile", kwargs={"pk": p.pk}),
            data={
                "agree_name": "on",
                "agree_age": "on",
                "nikshay_id": "NK-12345-RECONCILED"
            }
        )
        self.assertRedirects(response, reverse("questions:search"))

        # Verify participant is now updated with self.user and self.user's profile site!
        p.refresh_from_db()
        self.assertEqual(p.created_by, self.user)
        self.assertEqual(p.state, "Tamil Nadu")
        self.assertEqual(p.district, "Tiruvallur")
        self.assertEqual(p.tb_unit, "Tiruvallur TU")

        # Now test that post-edit also updates created_by and site fields if modified by another user
        # Create user_b (Karnataka site)
        from django.contrib.auth.models import User
        user_b = User.objects.create_user(
            username="teststaff_b2",
            email="teststaff_b2@example.com",
            password="password123"
        )
        profile_b = user_b.profile
        profile_b.state = "Karnataka"
        profile_b.district = "Bengaluru"
        profile_b.tb_unit = "Bengaluru TU"
        profile_b.save()

        # Log in as user_b
        self.client.logout()
        self.client.login(username="teststaff_b2", password="password123")

        # Edit/register participant via POST
        response_edit = self.client.post(
            reverse("questions:registration_edit", kwargs={"pk": p.pk}),
            data={
                "first_name": "Legacy",
                "last_name": "Updated By User B",
                "father_husband_name": "Father Name",
                "age": 41,
                "dob": "1985-05-12",
                "gender": "Male",
                "primary_phone": "9876543210",
                "address": "123 Temple Road",
                "sector": "Public Sector",
                "case_finding_type": "Passive (Routine programme)",
                "public_phi": "Avadi PHC",
                "taluka_block": "Avadi Taluka",
                "village": "Karani Village",
                "pincode": "602001",
                "demographic_area": "Rural",
                "marital_status": "Single",
                "occupation": "Teaching professional",
                "socioeconomic_status": "APL",
                "symptoms": ["Fever"],
                "risk_factors": ["Diabetes"],
                "hiv_status": "Non Reactive / Negative",
                "eligible_bcg_campaign": "Yes",
                "bcg_eligibility_criteria": ["Self-reported diabetes during the BCG campaign period"]
            }
        )
        self.assertRedirects(response_edit, reverse("questions:home"))

        # Verify participant's created_by and site fields are now updated to user_b's
        p.refresh_from_db()
        self.assertEqual(p.created_by, user_b)
        self.assertEqual(p.state, "Karnataka")
        self.assertEqual(p.district, "Bengaluru")
        self.assertEqual(p.tb_unit, "Bengaluru TU")


class SearchReconciliationTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        from questions.models import Participant
        
        self.username = "test_FI"
        self.password = "password123"
        self.user = User.objects.create_user(
            username=self.username,
            email="fi@example.com",
            password=self.password
        )
        self.profile = self.user.profile
        self.profile.role = "Super Admin"
        self.profile.state = "Tamil Nadu"
        self.profile.district = "Tiruvallur"
        self.profile.tb_unit = "Tiruvallur TU"
        self.profile.save()
        
        # Create a test participant with known values
        self.participant = Participant.objects.create(
            first_name="Ramesh",
            last_name="Kumar",
            full_name="Ramesh Kumar",
            study_id="ABCG-HR-0001",
            screening_id="SCR-111111-9999",
            nikshay_id="NK-55555",
            contact_number="9876543210",
            age=30,
            gender="Male",
            date_enroll=timezone.localdate(),
            state="Tamil Nadu",
            district="Tiruvallur",
            tb_unit="Tiruvallur TU",
            classification="Case",
            created_by=self.user
        )

    def test_phone_normalization(self):
        from questions.views import normalize_phone
        self.assertEqual(normalize_phone("+91 98765-43210"), "9876543210")
        self.assertEqual(normalize_phone("919876543210"), "9876543210")
        self.assertEqual(normalize_phone("9876543210"), "9876543210")
        self.assertEqual(normalize_phone(""), "")

    def test_name_normalization(self):
        from questions.views import normalize_name
        self.assertEqual(normalize_name("  Ramesh   Kumar  "), "ramesh kumar")
        self.assertEqual(normalize_name("RAMESH KUMAR"), "ramesh kumar")

    def test_match_scoring(self):
        from questions.views import calculate_match_status
        # Exact Match
        self.assertEqual(calculate_match_status("Ramesh Kumar", "9876543210", "Ramesh Kumar", "9876543210"), "EXACT_MATCH")
        # Partial Match (Phone matches, name doesn't)
        self.assertEqual(calculate_match_status("Ramesh Kumar", "9876543210", "Suresh Kumar", "9876543210"), "PARTIAL_MATCH")
        # Partial Match (Name matches, phone doesn't)
        self.assertEqual(calculate_match_status("Ramesh Kumar", "9876543210", "Ramesh Kumar", "1111122222"), "PARTIAL_MATCH")
        # No Match
        self.assertEqual(calculate_match_status("Ramesh Kumar", "9876543210", "Suresh Dev", "1111122222"), "NO_MATCH")

    def test_search_by_multiple_ids(self):
        self.client.login(username=self.username, password=self.password)
        
        # Query by screening_id
        response = self.client.get(reverse("questions:search"), {"q": "SCR-111111-9999"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["auto_select_id"], self.participant.pk)

        # Query by study_id
        response = self.client.get(reverse("questions:search"), {"q": "ABCG-HR-0001"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["auto_select_id"], self.participant.pk)

        # Query by nikshay_id
        response = self.client.get(reverse("questions:search"), {"q": "NK-55555"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["auto_select_id"], self.participant.pk)

    def test_simulated_nikshay_api(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("questions:nikshay_api", kwargs={"nikshay_id": "NK-TEST"}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["nikshay_id"], "NK-TEST")
        self.assertIn("full_name", data)

    def test_reconcile_match_api(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("questions:reconcile_match_api"), {
            "name": "Ramesh Kumar",
            "phone": "9876543210"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["exact_matches"]) > 0)
        self.assertEqual(data["exact_matches"][0]["study_id"], "ABCG-HR-0001")

    def test_reconcile_save_api(self):
        self.client.login(username=self.username, password=self.password)
        
        import json
        payload = {
            "participant_id": self.participant.id,
            "cohort": "participant",
            "nikshay_id": "NK-NEW-SYNCED",
            "source": "primary",
            "fields": {
                "full_name": {"source": "nikshay", "value": "Ramesh Kumar Synced"},
                "age": {"source": "local", "value": 30},
                "gender": {"source": "local", "value": "Male"},
                "contact_number": {"source": "local", "value": "9876543210"},
                "address": {"source": "custom", "value": "123 Custom Street"},
                "tb_treatment_status": {"source": "nikshay", "value": "Completed"},
                "adherence_records": {"source": "nikshay", "value": "98% Adherent"},
                "diagnosis_date": {"source": "nikshay", "value": "2026-01-20"},
                "bank_aadhaar_details": {"source": "nikshay", "value": "Bank Account Linked"}
            }
        }
        
        response = self.client.post(
            reverse("questions:reconcile_save_api"),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        
        self.participant.refresh_from_db()
        self.assertTrue(self.participant.synced)
        self.assertEqual(self.participant.nikshay_id, "NK-NEW-SYNCED")
        self.assertEqual(self.participant.reconciliation_status, "CONFLICT_RESOLVED")
        self.assertEqual(self.participant.address, "123 Custom Street")

    def test_participant_detail_view(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("questions:participant_detail", kwargs={"study_id": self.participant.study_id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.participant.full_name)
        self.assertContains(response, self.participant.study_id)

    def test_cases_view_authenticated(self):
        from questions.models import Participant
        self.client.login(username=self.username, password=self.password)
        Participant.objects.create(
            first_name="Sita", last_name="Devi", full_name="Sita Devi",
            study_id="ABCG-HR-0002", age=25, gender="Female",
            date_enroll=timezone.localdate(), state="Tamil Nadu",
            district="Tiruvallur", tb_unit="Tiruvallur TU",
            classification="Control", created_by=self.user
        )
        
        response = self.client.get(reverse("questions:cases"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ABCG-HR-0001")
        self.assertNotContains(response, "ABCG-HR-0002")
        
        # Test search query
        response_search = self.client.get(reverse("questions:cases"), {"q": "Ramesh"})
        self.assertEqual(response_search.status_code, 200)
        self.assertContains(response_search, "ABCG-HR-0001")
        
        response_search_none = self.client.get(reverse("questions:cases"), {"q": "NonExistent"})
        self.assertEqual(response_search_none.status_code, 200)
        self.assertNotContains(response_search_none, "ABCG-HR-0001")

    def test_controls_view_authenticated(self):
        from questions.models import Participant
        self.client.login(username=self.username, password=self.password)
        Participant.objects.create(
            first_name="Sita", last_name="Devi", full_name="Sita Devi",
            study_id="ABCG-HR-0002", age=25, gender="Female",
            date_enroll=timezone.localdate(), state="Tamil Nadu",
            district="Tiruvallur", tb_unit="Tiruvallur TU",
            classification="Control", created_by=self.user,
            match_hrg="Past TB"
        )
        
        response = self.client.get(reverse("questions:controls"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ABCG-HR-0002")
        self.assertNotContains(response, "ABCG-HR-0001")
        
        # Filter by HRG Group
        response_hrg = self.client.get(reverse("questions:controls"), {"hrg": "Past TB"})
        self.assertEqual(response_hrg.status_code, 200)
        self.assertContains(response_hrg, "ABCG-HR-0002")
        
        # Filter by different HRG Group
        response_hrg_none = self.client.get(reverse("questions:controls"), {"hrg": "Diabetes"})
        self.assertEqual(response_hrg_none.status_code, 200)
        self.assertNotContains(response_hrg_none, "ABCG-HR-0002")

    def test_doctor_verify_redirects_to_participant_detail(self):
        self.client.login(username=self.username, password=self.password)
        profile = self.user.profile
        profile.role = "Doctor"
        profile.save()
        
        response = self.client.post(reverse("questions:doctor_verify", kwargs={"pk": self.participant.pk}), {
            "classification": "Case",
            "classification_reason": "Confirmed microbiologically"
        })
        self.assertRedirects(response, reverse("questions:participant_detail", kwargs={"study_id": self.participant.study_id}))
        self.participant.refresh_from_db()
        self.assertEqual(self.participant.classification, "Case")
        self.assertEqual(self.participant.classification_reason, "Confirmed microbiologically")
