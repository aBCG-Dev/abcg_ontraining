from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

from questions.models import Participant, AuditLog
from questions.deduplication import (
    normalize_phone,
    normalize_name,
    normalize_nikshay,
    normalize_gender,
    normalize_dob,
    match_participant_records,
    ParticipantDeduplicator,
)


class DeduplicationUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="nurse_test",
            email="nurse@example.com",
            password="password123"
        )
        self.profile = self.user.profile
        self.profile.role = "Super Admin"
        self.profile.save()

    def test_normalizers(self):
        # Phone normalization
        self.assertEqual(normalize_phone("+91 98765-43210"), "9876543210")
        self.assertEqual(normalize_phone("09876543210"), "9876543210")
        self.assertEqual(normalize_phone("9876543210"), "9876543210")
        self.assertEqual(normalize_phone("123"), "")

        # Name normalization
        self.assertEqual(normalize_name("  Muni,   Ramana! "), "muni ramana")
        self.assertEqual(normalize_name("Dr. S. K. Gupta"), "dr s k gupta")

        # Nikshay ID normalization
        self.assertEqual(normalize_nikshay("  nk-987654  "), "NK-987654")
        self.assertEqual(normalize_nikshay("None"), "")
        self.assertEqual(normalize_nikshay("UNKNOWN"), "")

        # Gender normalization
        self.assertEqual(normalize_gender("Male"), "M")
        self.assertEqual(normalize_gender("female"), "F")
        self.assertEqual(normalize_gender("1"), "M")
        self.assertEqual(normalize_gender("2"), "F")

    def test_multi_tier_matching_tier1_nikshay(self):
        p1 = Participant(study_id="ABCG-01", full_name="John Doe", nikshay_id="NK-123456")
        p2 = Participant(study_id="ABCG-02", full_name="J. Doe", nikshay_id="NK-123456")
        is_match, tier, reason = match_participant_records(p1, p2)
        self.assertTrue(is_match)
        self.assertEqual(tier, "TIER_1_NIKSHAY")

    def test_multi_tier_matching_tier2_phone_name(self):
        # Name tokens order inverted: "Muni Ramana" vs "Ramana Muni"
        p1 = Participant(
            study_id="ABCG-01",
            first_name="Muni",
            last_name="Ramana",
            full_name="Muni Ramana",
            contact_number="9876543210"
        )
        p2 = Participant(
            study_id="ABCG-02",
            first_name="Ramana",
            last_name="Muni",
            full_name="Ramana Muni",
            contact_number="+91 98765-43210"
        )
        is_match, tier, reason = match_participant_records(p1, p2)
        self.assertTrue(is_match)
        self.assertEqual(tier, "TIER_2_PHONE_NAME")

    def test_multi_tier_matching_tier3_demographics(self):
        p1 = Participant(
            study_id="ABCG-01",
            first_name="Priya",
            last_name="Sharma",
            full_name="Priya Sharma",
            gender="Female",
            dob=date(1990, 5, 14),
            district="Tiruvallur"
        )
        p2 = Participant(
            study_id="ABCG-02",
            first_name="Priya",
            last_name="Sharma",
            full_name="Priya Sharma",
            gender="Female",
            dob=date(1990, 5, 14),
            district="Tiruvallur"
        )
        is_match, tier, reason = match_participant_records(p1, p2)
        self.assertTrue(is_match)
        self.assertEqual(tier, "TIER_3_DEMOGRAPHICS_DOB")

    def test_non_matching_records(self):
        p1 = Participant(
            study_id="ABCG-01",
            full_name="Ravi Kumar",
            contact_number="9876543210",
            gender="Male"
        )
        p2 = Participant(
            study_id="ABCG-02",
            full_name="Anita Roy",
            contact_number="9123456789",
            gender="Female"
        )
        is_match, tier, reason = match_participant_records(p1, p2)
        self.assertFalse(is_match)

    def test_completeness_scoring_and_master_selection(self):
        dedup = ParticipantDeduplicator(model_class=Participant)

        # Incomplete draft
        p_draft = Participant.objects.create(
            study_id="ABCG-TN-TIR-2026-000001",
            first_name="Muni",
            last_name="Ramana",
            full_name="Muni Ramana",
            contact_number="9876543210",
            age=45,
            gender="Male",
            date_enroll=timezone.localdate(),
            classification="Pending"
        )

        # Complete confirmed Case with lab diagnostics
        p_complete = Participant.objects.create(
            study_id="ABCG-TN-TIR-2026-000002",
            first_name="Muni",
            last_name="Ramana",
            full_name="Muni Ramana",
            contact_number="9876543210",
            age=45,
            gender="Male",
            date_enroll=timezone.localdate(),
            classification="Case",
            ptb_test_result="POSITIVE",
            bcg_status="Yes (Verified via Registry)",
            bcg_batch_number="BCG-BATCH-2025-A",
            address="123 Temple Road"
        )

        score_draft = dedup.calculate_completeness_score(p_draft)
        score_complete = dedup.calculate_completeness_score(p_complete)
        self.assertGreater(score_complete, score_draft)

        cluster = [p_draft, p_complete]
        master = dedup.select_master_record(cluster)
        self.assertEqual(master.pk, p_complete.pk)

    def test_merge_cluster_safe_enrichment_and_purge(self):
        dedup = ParticipantDeduplicator(model_class=Participant)

        # Master has classification and address, but empty landmark and secondary phone
        p_master = Participant.objects.create(
            study_id="ABCG-TN-TIR-2026-000010",
            first_name="Muni",
            last_name="Ramana",
            full_name="Muni Ramana",
            contact_number="9876543210",
            age=45,
            gender="Male",
            date_enroll=timezone.localdate(),
            classification="Case",
            ptb_test_result="POSITIVE",
            address="123 Temple Road"
        )

        # Duplicate 1 has landmark
        p_dup1 = Participant.objects.create(
            study_id="ABCG-TN-TIR-2026-000011",
            first_name="Muni",
            last_name="Ramana",
            full_name="Muni Ramana",
            contact_number="9876543210",
            age=45,
            gender="Male",
            date_enroll=timezone.localdate(),
            landmark="Near Old Banyan Tree"
        )

        # Duplicate 2 has secondary phone
        p_dup2 = Participant.objects.create(
            study_id="ABCG-TN-TIR-2026-000012",
            first_name="Muni",
            last_name="Ramana",
            full_name="Muni Ramana",
            contact_number="9876543210",
            age=45,
            gender="Male",
            date_enroll=timezone.localdate(),
            secondary_phone="9123456789"
        )

        self.assertEqual(Participant.objects.count(), 3)

        clusters = dedup.find_duplicate_clusters()
        self.assertEqual(len(clusters), 1)
        self.assertEqual(len(clusters[0]), 3)

        report = dedup.merge_cluster(clusters[0], user=self.user, dry_run=False)

        # Only 1 participant should remain in database
        self.assertEqual(Participant.objects.count(), 1)
        remaining = Participant.objects.first()
        self.assertEqual(remaining.study_id, "ABCG-TN-TIR-2026-000010")

        # Verify fields were safely enriched from duplicates
        self.assertEqual(remaining.landmark, "Near Old Banyan Tree")
        self.assertEqual(remaining.secondary_phone, "9123456789")
        self.assertEqual(remaining.address, "123 Temple Road")

        # Verify AuditLog recorded the merge
        log = AuditLog.objects.filter(action__startswith="DEDUPLICATION_MERGE").first()
        self.assertIsNotNone(log)
        self.assertIn("ABCG-TN-TIR-2026-000010", log.action)

    def test_registration_prevents_duplicate_creation(self):
        # Create initial participant
        initial = Participant.objects.create(
            study_id="ABCG-TN-TIR-2026-000099",
            first_name="Muni",
            last_name="Ramana",
            full_name="Muni Ramana",
            contact_number="9876543210",
            age=45,
            gender="Male",
            date_enroll=timezone.localdate(),
            classification="Pending"
        )
        self.assertEqual(Participant.objects.count(), 1)

        # Post identical participant details via registration
        client = Client()
        client.login(username="nurse_test", password="password123")
        
        response = client.post(reverse("questions:registration"), data={
            "first_name": "Muni",
            "last_name": "Ramana",
            "age": 45,
            "dob": "1981-05-12",
            "gender": "Male",
            "primary_phone": "9876543210",
            "state": "Tamil Nadu",
            "district": "Tiruvallur",
            "tb_unit": "Tiruvallur TU",
            "address": "123 Temple Road",
            "mctb": "NEGATIVE",
            "cxr": "NORMAL"
        })

        # Count must remain 1 (no duplicate row created!)
        self.assertEqual(Participant.objects.count(), 1)
        updated = Participant.objects.get(pk=initial.pk)
        self.assertEqual(updated.study_id, "ABCG-TN-TIR-2026-000099")

    def test_check_duplicate_api_endpoint(self):
        Participant.objects.create(
            study_id="ABCG-TN-TIR-2026-000123",
            first_name="Suresh",
            last_name="Raina",
            full_name="Suresh Raina",
            contact_number="9988776655",
            age=38,
            gender="Male",
            date_enroll=timezone.localdate()
        )

        client = Client()
        client.login(username="nurse_test", password="password123")

        # Test positive match
        res = client.get(reverse("questions:api_check_duplicate"), {
            "contact_number": "9988776655",
            "first_name": "Suresh",
            "last_name": "Raina"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["duplicate_found"])
        self.assertEqual(data["match"]["study_id"], "ABCG-TN-TIR-2026-000123")

        # Test non-match
        res_neg = client.get(reverse("questions:api_check_duplicate"), {
            "contact_number": "9111222333",
            "first_name": "Unregistered",
            "last_name": "Person"
        })
        self.assertEqual(res_neg.status_code, 200)
        self.assertFalse(res_neg.json()["duplicate_found"])

    def test_filter_participant_records_on_the_fly_preserves_data(self):
        from questions.deduplication import filter_participant_records_on_the_fly

        # Simulate 8 duplicate submissions of "Karthik Raja" plus 1 distinct person "Priya Kumar"
        mock_records = []
        for i in range(1, 9):
            mock_records.append({
                "pk": i,
                "study_id": f"ABCG-TN-0000{i}",
                "full_name": "Karthik Raja",
                "contact_number": "9840123456",
                "nikshay_id": "NIK-998877",
                "age": 32,
                "gender": "Male",
                "date_enroll": timezone.localdate(),
                "classification": "Pending" if i > 1 else "Case",
                "state": "Tamil Nadu",
                "district": "Chennai",
                "tb_unit": "TU1",
                "facility": "PHC North"
            })
        # Add distinct person
        mock_records.append({
            "pk": 9,
            "study_id": "ABCG-TN-00009",
            "full_name": "Priya Kumar",
            "contact_number": "9840999999",
            "nikshay_id": "NIK-112233",
            "age": 28,
            "gender": "Female",
            "date_enroll": timezone.localdate(),
            "classification": "Control",
            "state": "Tamil Nadu",
            "district": "Chennai",
            "tb_unit": "TU1",
            "facility": "PHC North"
        })

        # 1. Test "unique" mode (collapses 8 submissions into 1 master record)
        unique_results, meta = filter_participant_records_on_the_fly(mock_records, mode="unique")
        self.assertEqual(len(unique_results), 2)
        self.assertEqual(meta["total_raw"], 9)
        self.assertEqual(meta["total_unique"], 2)
        self.assertEqual(meta["duplicates_filtered"], 7)
        self.assertEqual(meta["duplicate_clusters"], 1)

        karthik_master = next(r for r in unique_results if r["full_name"] == "Karthik Raja")
        self.assertTrue(karthik_master["is_duplicate"])
        self.assertEqual(karthik_master["duplicate_count"], 8)
        self.assertEqual(len(karthik_master["duplicate_study_ids"]), 7)

        # 2. Test "all" mode (preserves and returns all 9 records)
        all_results, meta_all = filter_participant_records_on_the_fly(mock_records, mode="all")
        self.assertEqual(len(all_results), 9)

        # 3. Test "duplicates" mode (returns only the 8 duplicate submissions)
        dup_results, meta_dup = filter_participant_records_on_the_fly(mock_records, mode="duplicates")
        self.assertEqual(len(dup_results), 8)
