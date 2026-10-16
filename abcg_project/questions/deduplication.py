import re
import json
import logging
from datetime import date, datetime
from collections import defaultdict
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


def normalize_phone(phone):
    """
    Normalizes a phone number to standard 10 digits.
    Strips non-digit characters, leading country codes (+91, 0).
    """
    if not phone:
        return ""
    digits = re.sub(r"\D", "", str(phone).strip())
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    
    if len(digits) == 10:
        return digits
    return digits if len(digits) >= 8 else ""


def normalize_name(name):
    """
    Normalizes a name string for invariant comparison:
    lowercased, stripped of punctuation, and whitespace standardized.
    """
    if not name:
        return ""
    clean = re.sub(r"[^a-zA-Z0-9\s]", "", str(name).lower())
    tokens = [t for t in clean.split() if t]
    return " ".join(tokens)


def get_name_tokens(name):
    """Returns sorted set of normalized name tokens for order-invariant matching."""
    norm = normalize_name(name)
    return set(norm.split()) if norm else set()


def normalize_nikshay(nikshay_id):
    """
    Normalizes a Nikshay surveillance identifier.
    Returns cleaned uppercase string or empty string if placeholder/invalid.
    """
    if not nikshay_id:
        return ""
    val = str(nikshay_id).strip().upper()
    if val in {"", "NONE", "NULL", "UNKNOWN", "NA", "N/A", "0", "-", "--"}:
        return ""
    if len(val) < 4:
        return ""
    return val


def normalize_gender(gender):
    """Normalizes gender representation to M, F, or O."""
    if not gender:
        return ""
    g = str(gender).strip().lower()
    if g in {"male", "m", "1"}:
        return "M"
    if g in {"female", "f", "2"}:
        return "F"
    return "O"


def normalize_dob(dob_val):
    """Returns ISO format date string YYYY-MM-DD if valid, else None."""
    if not dob_val:
        return None
    if isinstance(dob_val, (date, datetime)):
        return dob_val.strftime("%Y-%m-%d")
    s = str(dob_val).strip()
    # Try parsing common formats
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return s if len(s) >= 8 else None


def match_participant_records(r1, r2):
    """
    Evaluates whether two participant records represent the same individual
    using Multi-Tier matching rules:
      - Tier 1: Identical Nikshay ID
      - Tier 2: Identical 10-digit Phone + Matching Name
      - Tier 3: Matching Name + Matching Date of Birth (or Age +/- 1) + Gender
    
    Returns (is_match: bool, tier: str or None, reason: str or None)
    """
    # 1. Tier 1: Nikshay ID Match (National TB surveillance identifier)
    nikshay1 = normalize_nikshay(getattr(r1, "nikshay_id", None))
    nikshay2 = normalize_nikshay(getattr(r2, "nikshay_id", None))
    if nikshay1 and nikshay2 and nikshay1 == nikshay2:
        return True, "TIER_1_NIKSHAY", f"Identical Nikshay ID ({nikshay1})"

    # Prepare demographics
    name1 = getattr(r1, "full_name", None) or f"{getattr(r1, 'first_name', '')} {getattr(r1, 'last_name', '')}".strip()
    name2 = getattr(r2, "full_name", None) or f"{getattr(r2, 'first_name', '')} {getattr(r2, 'last_name', '')}".strip()
    tokens1 = get_name_tokens(name1)
    tokens2 = get_name_tokens(name2)
    name_match = bool(tokens1 and tokens2 and (tokens1 == tokens2 or tokens1.issubset(tokens2) or tokens2.issubset(tokens1)))

    # 2. Tier 2: Primary Phone + Name
    phone1 = normalize_phone(getattr(r1, "contact_number", None) or getattr(r1, "primary_phone", None) or getattr(r1, "ben_mobile_number", None))
    phone2 = normalize_phone(getattr(r2, "contact_number", None) or getattr(r2, "primary_phone", None) or getattr(r2, "ben_mobile_number", None))
    
    if phone1 and phone2 and len(phone1) == 10 and phone1 == phone2:
        if name_match:
            return True, "TIER_2_PHONE_NAME", f"Identical Phone ({phone1}) and Name ({name1})"
        
        # Cross check first_name / last_name specifically
        fn1 = normalize_name(getattr(r1, "first_name", ""))
        fn2 = normalize_name(getattr(r2, "first_name", ""))
        ln1 = normalize_name(getattr(r1, "last_name", ""))
        ln2 = normalize_name(getattr(r2, "last_name", ""))
        if fn1 and fn2 and (fn1 == fn2 or fn1 == ln2 or ln1 == fn2):
            return True, "TIER_2_PHONE_NAME", f"Identical Phone ({phone1}) and First Name ({fn1})"

    # 3. Tier 3: Demographic Triangulation (Name + DOB / Age + Gender)
    gender1 = normalize_gender(getattr(r1, "gender", None) or getattr(r1, "ben_gender", None) or getattr(r1, "beneficiary_gender", None))
    gender2 = normalize_gender(getattr(r2, "gender", None) or getattr(r2, "ben_gender", None) or getattr(r2, "beneficiary_gender", None))
    
    if name_match and gender1 and gender2 and gender1 == gender2:
        dob1 = normalize_dob(getattr(r1, "dob", None))
        dob2 = normalize_dob(getattr(r2, "dob", None))
        
        # Subcase 3A: Exact Date of Birth match
        if dob1 and dob2 and dob1 == dob2:
            return True, "TIER_3_DEMOGRAPHICS_DOB", f"Identical Name ({name1}), DOB ({dob1}), and Gender ({gender1})"
            
        # Subcase 3B: Age match within +/- 1 year
        age1 = getattr(r1, "age", None)
        age2 = getattr(r2, "age", None)
        if age1 is not None and age2 is not None:
            try:
                a1 = int(age1)
                a2 = int(age2)
                if abs(a1 - a2) <= 1 and a1 > 0:
                    # Verify jurisdiction or phone if available to prevent homonym clashes
                    loc1 = str(getattr(r1, "district", "") or getattr(r1, "tb_unit", "")).strip().lower()
                    loc2 = str(getattr(r2, "district", "") or getattr(r2, "tb_unit", "")).strip().lower()
                    if not loc1 or not loc2 or loc1 == loc2:
                        return True, "TIER_3_DEMOGRAPHICS_AGE", f"Matching Name ({name1}), Age ({a1} vs {a2}), and Gender ({gender1})"
            except (ValueError, TypeError):
                pass

    return False, None, None


class DisjointSetUnion:
    """Disjoint Set Union (DSU / Union-Find) data structure for clustering duplicate graph components."""
    def __init__(self):
        self.parent = {}

    def find(self, i):
        if i not in self.parent:
            self.parent[i] = i
            return i
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j


class ParticipantDeduplicator:
    """
    Engine to identify, cluster, score, and safely merge duplicate participant records.
    Designed for field database and central backend models.
    """
    def __init__(self, model_class=None, logger_instance=None):
        if model_class is None:
            from questions.models import Participant
            model_class = Participant
        self.model_class = model_class
        self.logger = logger_instance or logger

    def calculate_completeness_score(self, record):
        """
        Calculates an objective clinical and demographic completeness score for a participant record.
        Higher score indicates higher data quality and richer clinical verification.
        """
        score = 0
        classification = getattr(record, "classification", "")
        
        # Classification status priority
        if classification in {"Case", "Control"}:
            score += 60
        elif classification == "TPT+BCG":
            score += 55
        elif classification == "Excluded":
            score += 30
        elif classification == "Not Eligible":
            score += 20
        elif classification == "Pending":
            score += 10
            
        # PTB diagnostic results
        ptb_res = getattr(record, "ptb_test_result", None)
        if ptb_res and str(ptb_res).strip() and str(ptb_res).upper() not in {"PENDING", "UNKNOWN", "NONE"}:
            score += 25
            
        # EPTB screening & findings
        if getattr(record, "eptb_screened", False):
            score += 10
        eptb_details = getattr(record, "eptb_details", "")
        if eptb_details and eptb_details != "{}" and len(eptb_details) > 10:
            score += 15
            
        # CXR record
        if getattr(record, "cxr_record_file", None):
            score += 20
            
        # BCG verification
        bcg_status = getattr(record, "bcg_status", "")
        if str(bcg_status).startswith("Yes"):
            score += 20
        if getattr(record, "bcg_scar_file", None) or getattr(record, "bcg_record_file", None):
            score += 15
        if getattr(record, "bcg_batch_number", None):
            score += 10
            
        # Identifiers & Contact
        nikshay = normalize_nikshay(getattr(record, "nikshay_id", None))
        if nikshay:
            score += 20
        if getattr(record, "reconciliation_status", "") == "RECONCILED":
            score += 10
            
        phone = normalize_phone(getattr(record, "contact_number", None))
        if phone:
            score += 15
        if getattr(record, "secondary_phone", None) or getattr(record, "secondary_phone_1", None):
            score += 5
            
        # Address & demographics
        if getattr(record, "address", None) and len(str(record.address).strip()) > 5:
            score += 10
        if getattr(record, "father_husband_name", None):
            score += 5
        if getattr(record, "village", None):
            score += 5
            
        # Questionnaire answers
        q_ans = getattr(record, "questionnaire_answers", "")
        if q_ans and q_ans != "{}" and len(q_ans) > 10:
            score += 15

        # Synchronization verified
        if getattr(record, "synced", False) or getattr(record, "sync_receipt_id", None):
            score += 10

        return score

    def select_master_record(self, cluster):
        """
        Selects the optimal master record from a cluster of duplicates based on:
        1. Highest clinical completeness score
        2. Tie-breaker: Earliest registration/creation timestamp
        3. Tie-breaker: Lowest primary key ID
        """
        def sort_key(rec):
            score = self.calculate_completeness_score(rec)
            # Timestamp tie-breaker (earlier date preferred)
            created = getattr(rec, "created_at", None) or getattr(rec, "uploaded_at", None) or getattr(rec, "date_enroll", None)
            if created and isinstance(created, datetime):
                time_val = created.timestamp()
            elif created and isinstance(created, date):
                time_val = datetime.combine(created, datetime.min.time()).timestamp()
            else:
                time_val = 9999999999
            
            pk_val = getattr(rec, "pk", 999999999) or 999999999
            return (score, -time_val, -pk_val)

        return max(cluster, key=sort_key)

    def find_duplicate_clusters(self, queryset=None):
        """
        Scans queryset (or all records of model_class) and groups duplicates into clusters using DSU.
        Returns list of clusters, where each cluster is a list of duplicate record objects (len >= 2).
        """
        if queryset is None:
            queryset = self.model_class.objects.all()

        records = list(queryset)
        n = len(records)
        if n < 2:
            return []

        dsu = DisjointSetUnion()
        match_details = {}

        # Optimization: group candidate indices by phone, by nikshay_id, and by (gender, dob/age)
        phone_index = defaultdict(list)
        nikshay_index = defaultdict(list)
        demo_index = defaultdict(list)

        for i, rec in enumerate(records):
            phone = normalize_phone(getattr(rec, "contact_number", None) or getattr(rec, "primary_phone", None))
            if phone:
                phone_index[phone].append(i)
                
            nik = normalize_nikshay(getattr(rec, "nikshay_id", None))
            if nik:
                nikshay_index[nik].append(i)
                
            gender = normalize_gender(getattr(rec, "gender", None))
            dob = normalize_dob(getattr(rec, "dob", None))
            age = getattr(rec, "age", None)
            if gender and (dob or age is not None):
                key = (gender, dob if dob else f"age_{age}")
                demo_index[key].append(i)

        # Generate candidate pairs to check
        candidate_pairs = set()
        
        for idx_list in phone_index.values():
            if len(idx_list) > 1:
                for a in range(len(idx_list)):
                    for b in range(a + 1, len(idx_list)):
                        candidate_pairs.add((min(idx_list[a], idx_list[b]), max(idx_list[a], idx_list[b])))

        for idx_list in nikshay_index.values():
            if len(idx_list) > 1:
                for a in range(len(idx_list)):
                    for b in range(a + 1, len(idx_list)):
                        candidate_pairs.add((min(idx_list[a], idx_list[b]), max(idx_list[a], idx_list[b])))

        for idx_list in demo_index.values():
            if len(idx_list) > 1:
                for a in range(len(idx_list)):
                    for b in range(a + 1, len(idx_list)):
                        candidate_pairs.add((min(idx_list[a], idx_list[b]), max(idx_list[a], idx_list[b])))

        # Fallback for smaller sets (<= 300) to ensure complete pairwise coverage
        if n <= 300:
            for a in range(n):
                for b in range(a + 1, n):
                    candidate_pairs.add((a, b))

        # Evaluate candidate pairs
        for i, j in candidate_pairs:
            is_match, tier, reason = match_participant_records(records[i], records[j])
            if is_match:
                dsu.union(i, j)
                match_details[(i, j)] = (tier, reason)

        # Group indices by root
        clusters_by_root = defaultdict(list)
        for i in range(n):
            root = dsu.find(i)
            clusters_by_root[root].append(records[i])

        # Filter clusters with >= 2 members
        duplicate_clusters = [cluster for cluster in clusters_by_root.values() if len(cluster) >= 2]
        return duplicate_clusters

    def merge_cluster(self, cluster, user=None, dry_run=False):
        """
        Safely merges a duplicate cluster:
          1. Selects the highest scoring master record.
          2. Copies non-empty missing fields from duplicates into master.
          3. Relinks foreign keys (e.g. NikshayRecord, AuditLog).
          4. Creates an audit log of the merge operation.
          5. Deletes redundant duplicate records.
        """
        if len(cluster) < 2:
            return None

        master = self.select_master_record(cluster)
        duplicates = [rec for rec in cluster if rec.pk != master.pk]
        
        fields_updated = []
        
        # Merge scalar and JSON fields
        for field in master._meta.fields:
            fname = field.name
            if fname in {"id", "pk", "study_id", "created_at", "uploaded_at"}:
                continue
                
            master_val = getattr(master, fname, None)
            is_empty = (
                master_val is None or 
                master_val == "" or 
                master_val == 0 or 
                master_val == "{}" or 
                master_val == "Unknown"
            )
            
            if is_empty:
                for dup in duplicates:
                    dup_val = getattr(dup, fname, None)
                    if dup_val not in (None, "", 0, "{}", "Unknown"):
                        setattr(master, fname, dup_val)
                        fields_updated.append(fname)
                        break
                        
        # Merge JSON string dictionaries without overwriting existing keys
        for json_fname in ["questionnaire_answers", "ptb_test_details", "eptb_details"]:
            if hasattr(master, json_fname):
                try:
                    m_data = json.loads(getattr(master, json_fname) or "{}")
                    merged_any = False
                    for dup in duplicates:
                        d_data = json.loads(getattr(dup, json_fname) or "{}")
                        for k, v in d_data.items():
                            if k not in m_data or not m_data[k]:
                                m_data[k] = v
                                merged_any = True
                    if merged_any:
                        setattr(master, json_fname, json.dumps(m_data))
                        fields_updated.append(json_fname)
                except Exception:
                    pass

        merge_report = {
            "master_study_id": master.study_id,
            "master_pk": master.pk,
            "master_name": getattr(master, "full_name", ""),
            "duplicate_count": len(duplicates),
            "merged_study_ids": [d.study_id for d in duplicates],
            "merged_pks": [d.pk for d in duplicates],
            "fields_updated": list(set(fields_updated)),
            "dry_run": dry_run,
        }

        if not dry_run:
            with transaction.atomic():
                # Relink NikshayRecords if model exists
                try:
                    from questions.models import NikshayRecord
                    NikshayRecord.objects.filter(participant__in=duplicates).update(
                        participant=master, study_id=master.study_id
                    )
                except Exception:
                    pass

                # Save the enriched master record
                master.save()

                # Record Audit Log
                try:
                    from questions.models import AuditLog
                    AuditLog.objects.create(
                        actor=user,
                        action=(
                            f"DEDUPLICATION_MERGE: Master '{master.study_id}' absorbed "
                            f"{len(duplicates)} duplicate entries: {', '.join(d.study_id for d in duplicates)}"
                        )
                    )
                except Exception:
                    pass

                # Delete duplicate records
                for dup in duplicates:
                    dup.delete()

        return merge_report

    def deduplicate_all(self, queryset=None, user=None, dry_run=False):
        """
        Executes deduplication across the entire queryset.
        Returns summary statistics and reports of all merged clusters.
        """
        clusters = self.find_duplicate_clusters(queryset=queryset)
        total_duplicates_found = sum(len(c) - 1 for c in clusters)
        
        reports = []
        for cluster in clusters:
            report = self.merge_cluster(cluster, user=user, dry_run=dry_run)
            if report:
                reports.append(report)
                
        return {
            "total_clusters": len(clusters),
            "total_duplicates_detected": total_duplicates_found,
            "merged_clusters_count": len(reports),
            "dry_run": dry_run,
            "reports": reports
        }

    def check_candidate_duplicate(self, first_name="", last_name="", full_name="", contact_number="", nikshay_id="", dob=None, age=None, gender="", exclude_pk=None):
        """
        Real-time check to see if participant details match an existing record before saving.
        Returns (is_duplicate: bool, existing_record: Model or None, tier: str or None, reason: str or None)
        """
        candidate = type("Candidate", (), {})()
        candidate.first_name = first_name
        candidate.last_name = last_name
        candidate.full_name = full_name or f"{first_name} {last_name}".strip()
        candidate.contact_number = contact_number
        candidate.primary_phone = contact_number
        candidate.nikshay_id = nikshay_id
        candidate.dob = dob
        candidate.age = age
        candidate.gender = gender

        qs = self.model_class.objects.all()
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)

        # 1. Quick lookup on Nikshay ID
        clean_nik = normalize_nikshay(nikshay_id)
        if clean_nik:
            match = qs.filter(nikshay_id__iexact=clean_nik).first()
            if match:
                return True, match, "TIER_1_NIKSHAY", f"Identical Nikshay ID ({clean_nik})"

        # 2. Quick lookup on phone
        clean_phone = normalize_phone(contact_number)
        if clean_phone and len(clean_phone) == 10:
            for rec in qs.filter(contact_number__icontains=clean_phone):
                is_match, tier, reason = match_participant_records(candidate, rec)
                if is_match:
                    return True, rec, tier, reason

        # 3. Quick lookup on Name + Gender
        norm_name = normalize_name(candidate.full_name)
        if norm_name and gender:
            for rec in qs.filter(gender__iexact=gender):
                is_match, tier, reason = match_participant_records(candidate, rec)
                if is_match:
                    return True, rec, tier, reason

        return False, None, None, None


def filter_participant_records_on_the_fly(records_list, mode="unique"):
    """
    On-the-fly, non-destructive deduplication filter for participant records.
    Clusters records in memory using multi-tier matching without modifying or deleting 
    ANY database rows. All original data is 100% preserved.
    
    Args:
        records_list (list of dicts): List of record dictionaries as prepared in views.
        mode (str):
            - "unique": Returns master records only (unique individuals), collapsing duplicate submissions.
            - "duplicates": Returns records that have duplicate submissions.
            - "all": Returns all raw records annotated with duplication metadata.
            
    Returns:
        (filtered_records, meta):
            filtered_records (list): Resulting list of records based on mode.
            meta (dict): Statistics including total_raw, total_unique, duplicates_filtered, duplicate_clusters.
    """
    if not records_list:
        return [], {
            "total_raw": 0,
            "total_unique": 0,
            "duplicates_filtered": 0,
            "duplicate_clusters": 0,
            "mode": mode,
        }

    n = len(records_list)
    dsu = DisjointSetUnion()

    # Index by phone and nikshay for rapid matching
    phone_map = defaultdict(list)
    nikshay_map = defaultdict(list)
    demo_map = defaultdict(list)

    for i, r in enumerate(records_list):
        phone = normalize_phone(r.get("contact_number"))
        if phone and len(phone) == 10:
            phone_map[phone].append(i)

        nik = normalize_nikshay(r.get("nikshay_id"))
        if nik:
            nikshay_map[nik].append(i)

        g = normalize_gender(r.get("gender"))
        age = r.get("age")
        if g and age not in [None, "", "—"]:
            try:
                age_num = int(age)
                demo_map[(g, age_num)].append(i)
            except (ValueError, TypeError):
                pass

    # Tier 1: Union identical Nikshay IDs
    for nik, indices in nikshay_map.items():
        if len(indices) > 1:
            for idx in indices[1:]:
                dsu.union(indices[0], idx)

    # Tier 2: Union identical 10-digit Phone + Name match
    for phone, indices in phone_map.items():
        if len(indices) > 1:
            for a_idx in range(len(indices)):
                for b_idx in range(a_idx + 1, len(indices)):
                    i1, i2 = indices[a_idx], indices[b_idx]
                    t1 = get_name_tokens(records_list[i1].get("full_name", ""))
                    t2 = get_name_tokens(records_list[i2].get("full_name", ""))
                    if t1 and t2 and (t1 == t2 or t1.issubset(t2) or t2.issubset(t1)):
                        dsu.union(i1, i2)

    # Tier 3: Demographics (Gender + Age +/- 1) + Name match
    for (g, age), indices in demo_map.items():
        candidate_indices = list(indices)
        for d_age in (-1, 1):
            candidate_indices.extend(demo_map.get((g, age + d_age), []))
        candidate_indices = list(set(candidate_indices))
        if len(candidate_indices) > 1:
            for a_idx in range(len(candidate_indices)):
                for b_idx in range(a_idx + 1, len(candidate_indices)):
                    i1, i2 = candidate_indices[a_idx], candidate_indices[b_idx]
                    if i1 != i2:
                        t1 = get_name_tokens(records_list[i1].get("full_name", ""))
                        t2 = get_name_tokens(records_list[i2].get("full_name", ""))
                        if t1 and t2 and t1 == t2:
                            dsu.union(i1, i2)

    # Group into clusters
    clusters_dict = defaultdict(list)
    for i in range(n):
        root = dsu.find(i)
        clusters_dict[root].append(records_list[i])

    def record_score(rec):
        s = 0
        if rec.get("nikshay_id") and rec["nikshay_id"] != "—":
            s += 30
        if rec.get("contact_number") and rec["contact_number"] != "—":
            s += 20
        if rec.get("date_enroll"):
            s += 10
        if rec.get("classification") and rec["classification"] not in ["Pending", "—"]:
            s += 15
        if rec.get("state") and rec["state"] != "—":
            s += 5
        if rec.get("district") and rec["district"] != "—":
            s += 5
        return s

    unique_masters = []
    duplicate_records_all = []
    annotated_all = []
    duplicate_cluster_count = 0

    for root, cluster in clusters_dict.items():
        is_cluster_duplicate = len(cluster) > 1
        if is_cluster_duplicate:
            duplicate_cluster_count += 1

        def master_sort_key(r):
            sc = record_score(r)
            d = r.get("date_enroll")
            time_val = d.strftime("%Y-%m-%d") if d and hasattr(d, "strftime") else "9999-99-99"
            pk_val = r.get("pk") or 999999999
            try:
                time_num = int(str(time_val).replace("-", ""))
            except Exception:
                time_num = 99999999
            return (sc, -time_num, -pk_val)

        master = max(cluster, key=master_sort_key)
        all_ids = [r.get("study_id") for r in cluster]

        for item in cluster:
            item["duplicate_count"] = len(cluster)
            item["is_duplicate"] = is_cluster_duplicate
            item["is_duplicate_master"] = (item.get("study_id") == master.get("study_id"))
            item["duplicate_study_ids"] = [sid for sid in all_ids if sid != item.get("study_id")]
            item["master_study_id"] = master.get("study_id")
            annotated_all.append(item)
            if is_cluster_duplicate:
                duplicate_records_all.append(item)

        unique_masters.append(master)

    def sort_by_date(item_list):
        def key_func(r):
            d = r.get("date_enroll")
            if d and hasattr(d, "isoformat"):
                return d.isoformat()
            if d:
                return str(d)
            return "1970-01-01"
        return sorted(item_list, key=key_func, reverse=True)

    total_raw = len(records_list)
    total_unique = len(unique_masters)
    duplicates_filtered = total_raw - total_unique

    meta = {
        "total_raw": total_raw,
        "total_unique": total_unique,
        "duplicates_filtered": duplicates_filtered,
        "duplicate_clusters": duplicate_cluster_count,
        "mode": mode,
    }

    if mode == "all":
        return sort_by_date(annotated_all), meta
    elif mode == "duplicates":
        return sort_by_date(duplicate_records_all), meta
    else:  # default "unique"
        return sort_by_date(unique_masters), meta

