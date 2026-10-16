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
    phone1 = normalize_phone(getattr(r1, "contact_number", None) or getattr(r1, "primary_phone", None))
    phone2 = normalize_phone(getattr(r2, "contact_number", None) or getattr(r2, "primary_phone", None))
    
    if phone1 and phone2 and len(phone1) == 10 and phone1 == phone2:
        if name_match:
            return True, "TIER_2_PHONE_NAME", f"Identical Phone ({phone1}) and Name ({name1})"
        
        fn1 = normalize_name(getattr(r1, "first_name", ""))
        fn2 = normalize_name(getattr(r2, "first_name", ""))
        ln1 = normalize_name(getattr(r1, "last_name", ""))
        ln2 = normalize_name(getattr(r2, "last_name", ""))
        if fn1 and fn2 and (fn1 == fn2 or fn1 == ln2 or ln1 == fn2):
            return True, "TIER_2_PHONE_NAME", f"Identical Phone ({phone1}) and First Name ({fn1})"

    # 3. Tier 3: Demographic Triangulation (Name + DOB / Age + Gender)
    gender1 = normalize_gender(getattr(r1, "gender", None))
    gender2 = normalize_gender(getattr(r2, "gender", None))
    
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
                    loc1 = str(getattr(r1, "district", "") or getattr(r1, "tb_unit", "")).strip().lower()
                    loc2 = str(getattr(r2, "district", "") or getattr(r2, "tb_unit", "")).strip().lower()
                    if not loc1 or not loc2 or loc1 == loc2:
                        return True, "TIER_3_DEMOGRAPHICS_AGE", f"Matching Name ({name1}), Age ({a1} vs {a2}), and Gender ({gender1})"
            except (ValueError, TypeError):
                pass

    return False, None, None


class DisjointSetUnion:
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
    """
    def __init__(self, model_class=None, logger_instance=None):
        if model_class is None:
            from api.models import Participant
            model_class = Participant
        self.model_class = model_class
        self.logger = logger_instance or logger

    def calculate_completeness_score(self, record):
        score = 0
        classification = getattr(record, "classification", "")
        
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
            
        ptb_res = getattr(record, "ptb_test_result", None)
        if ptb_res and str(ptb_res).strip() and str(ptb_res).upper() not in {"PENDING", "UNKNOWN", "NONE"}:
            score += 25
            
        if getattr(record, "eptb_screened", False):
            score += 10
        eptb_details = getattr(record, "eptb_details", "")
        if eptb_details and eptb_details != "{}" and len(eptb_details) > 10:
            score += 15
            
        if getattr(record, "cxr_record_file", None):
            score += 20
            
        bcg_status = getattr(record, "bcg_status", "")
        if str(bcg_status).startswith("Yes"):
            score += 20
        if getattr(record, "bcg_scar_file", None) or getattr(record, "bcg_record_file", None):
            score += 15
        if getattr(record, "bcg_batch_number", None):
            score += 10
            
        nikshay = normalize_nikshay(getattr(record, "nikshay_id", None))
        if nikshay:
            score += 20
            
        phone = normalize_phone(getattr(record, "contact_number", None))
        if phone:
            score += 15
        if getattr(record, "secondary_phone", None) or getattr(record, "secondary_phone_1", None):
            score += 5
            
        if getattr(record, "address", None) and len(str(record.address).strip()) > 5:
            score += 10
        if getattr(record, "father_husband_name", None):
            score += 5
        if getattr(record, "village", None):
            score += 5
            
        q_ans = getattr(record, "questionnaire_answers", "")
        if q_ans and q_ans != "{}" and len(q_ans) > 10:
            score += 15

        if getattr(record, "sync_receipt_id", None):
            score += 10

        return score

    def select_master_record(self, cluster):
        def sort_key(rec):
            score = self.calculate_completeness_score(rec)
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
        if queryset is None:
            queryset = self.model_class.objects.all()

        records = list(queryset)
        n = len(records)
        if n < 2:
            return []

        dsu = DisjointSetUnion()
        candidate_pairs = set()

        phone_index = defaultdict(list)
        nikshay_index = defaultdict(list)
        demo_index = defaultdict(list)

        for i, rec in enumerate(records):
            phone = normalize_phone(getattr(rec, "contact_number", None))
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

        if n <= 300:
            for a in range(n):
                for b in range(a + 1, n):
                    candidate_pairs.add((a, b))

        for i, j in candidate_pairs:
            is_match, tier, reason = match_participant_records(records[i], records[j])
            if is_match:
                dsu.union(i, j)

        clusters_by_root = defaultdict(list)
        for i in range(n):
            root = dsu.find(i)
            clusters_by_root[root].append(records[i])

        return [cluster for cluster in clusters_by_root.values() if len(cluster) >= 2]

    def merge_cluster(self, cluster, user=None, dry_run=False):
        if len(cluster) < 2:
            return None

        master = self.select_master_record(cluster)
        duplicates = [rec for rec in cluster if rec.pk != master.pk]
        
        fields_updated = []
        
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
                master.save()

                try:
                    from api.models import AuditLog
                    AuditLog.objects.create(
                        actor=user,
                        action=(
                            f"DEDUPLICATION_MERGE: Master '{master.study_id}' absorbed "
                            f"{len(duplicates)} duplicate entries: {', '.join(d.study_id for d in duplicates)}"
                        )
                    )
                except Exception:
                    pass

                for dup in duplicates:
                    dup.delete()

        return merge_report

    def deduplicate_all(self, queryset=None, user=None, dry_run=False):
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

        clean_nik = normalize_nikshay(nikshay_id)
        if clean_nik:
            match = qs.filter(nikshay_id__iexact=clean_nik).first()
            if match:
                return True, match, "TIER_1_NIKSHAY", f"Identical Nikshay ID ({clean_nik})"

        clean_phone = normalize_phone(contact_number)
        if clean_phone and len(clean_phone) == 10:
            for rec in qs.filter(contact_number__icontains=clean_phone):
                is_match, tier, reason = match_participant_records(candidate, rec)
                if is_match:
                    return True, rec, tier, reason

        norm_name = normalize_name(candidate.full_name)
        if norm_name and gender:
            for rec in qs.filter(gender__iexact=gender):
                is_match, tier, reason = match_participant_records(candidate, rec)
                if is_match:
                    return True, rec, tier, reason

        return False, None, None, None
