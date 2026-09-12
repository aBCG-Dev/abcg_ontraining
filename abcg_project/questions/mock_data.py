import random
from datetime import datetime, timedelta

# Fix random seed for deterministic mock data
random.seed(20260709)

STATES = [
    {
        'code': 'HR',
        'name': 'Haryana',
        'districts': ['Ambala', 'Karnal', 'Hisar', 'Rohtak'],
    },
    {
        'code': 'HP',
        'name': 'Himachal Pradesh',
        'districts': ['Shimla', 'Kangra', 'Mandi', 'Solan'],
    },
    {
        'code': 'MP',
        'name': 'Madhya Pradesh',
        'districts': ['Bhopal', 'Indore', 'Jabalpur', 'Gwalior'],
    },
    {
        'code': 'OD',
        'name': 'Odisha',
        'districts': ['Cuttack', 'Khordha', 'Ganjam', 'Sundargarh'],
    },
    {
        'code': 'MH',
        'name': 'Maharashtra',
        'districts': ['Pune', 'Nagpur', 'Nashik', 'Thane'],
    },
    {
        'code': 'AP',
        'name': 'Andhra Pradesh',
        'districts': ['Guntur', 'Krishna', 'Chittoor', 'Visakhapatnam'],
    },
]

HRG_GROUPS = {
    1: 'Past TB History',
    2: 'Household Contact',
    3: 'Diabetes Mellitus',
    4: 'Elderly (>60y)',
    5: 'Smoker / Tobacco',
    6: 'Low BMI (<18.5)',
}

PTB_FINAL_LABELS = {
    0: 'None',
    1: 'Microbiologically Confirmed',
    2: 'Clinical Diagnosis',
}

CERTAINTY_LABELS = {
    1: 'Microbiological',
    2: 'Clinical',
    3: 'Mixed Form',
    4: 'Base Control Pool',
}

TB_CLASS_LABELS = {
    1: 'PTB Only',
    2: 'EPTB Only',
    3: 'Combined Mixed',
    4: 'Non-TB',
}

BCG_STATUS_LABELS = {
    0: 'Unvaccinated',
    1: 'Vaccinated',
    9: 'Indeterminate',
}

BCG_EVIDENCE_LABELS = {
    1: 'Definite (TBWIN)',
    2: 'Probable (Card)',
    3: 'Scar Assessment',
    4: 'Recall Only',
}

MATCH_STATUS_LABELS = {
    1: 'Complete — Locked',
    2: 'Partial Match',
    3: 'Pending Match',
    4: 'Broken Set',
}

FIRST = [
    'Ramesh', 'Sunita', 'Anil', 'Priya', 'Vikram', 'Meena', 'Rajesh', 'Lakshmi',
    'Suresh', 'Kavita', 'Arjun', 'Deepa', 'Manoj', 'Radha', 'Sanjay', 'Geeta'
]
LAST = [
    'Kumar', 'Devi', 'Sharma', 'Patel', 'Reddy', 'Naik', 'Yadav', 'Verma', 'Das',
    'Singh', 'Rao', 'Thakur'
]

VILLAGES = [
    'Rampur', 'Bishanpur', 'Chandpur', 'Nawada', 'Kishangarh', 'Bagdogra', 'Amrai', 'Sultanpur'
]

def fmt_date(offset_days):
    base = datetime(2026, 7, 9)
    dt = base - timedelta(days=offset_days)
    return dt.strftime('%Y-%m-%d')

def build_participants():
    participants_list = []
    case_counter = 0
    for i in range(220):
        st = random.choice(STATES)
        district = random.choice(st['districts'])
        tu_code = f"TU{str(random.randint(1, 18)).zfill(2)}"
        is_case = random.random() < 0.32
        match_hrg = random.randint(1, 6)
        
        hrg_flags = {
            'HRG_ELDERLY': 1 if (match_hrg == 4 or random.random() < 0.3) else 0,
            'HRG_PASTTB': 1 if (match_hrg == 1 or random.random() < 0.2) else 0,
            'HRG_DM': 1 if (match_hrg == 3 or random.random() < 0.25) else 0,
            'HRG_SMOKE': 1 if (match_hrg == 5 or random.random() < 0.3) else 0,
            'HRG_CONTACT': 1 if (match_hrg == 2 or random.random() < 0.2) else 0,
            'HRG_BMI': 1 if (match_hrg == 6 or random.random() < 0.25) else 0,
        }
        
        enrol_offset = random.randint(1, 180)
        disease_roll = random.random()
        disease_type = 'PTB'
        if is_case:
            if disease_roll < 0.62:
                disease_type = 'PTB'
            elif disease_roll < 0.85:
                disease_type = 'EPTB'
            else:
                disease_type = 'Mixed'
                
        micro = is_case and random.random() < 0.6
        
        ptb_final = 0
        if is_case:
            if disease_type == 'EPTB':
                ptb_final = 0
            else:
                ptb_final = 1 if micro else 2
                
        eptb_final = 0
        if is_case:
            if disease_type in ('EPTB', 'Mixed'):
                eptb_final = 1 if micro else 2
                
        tb_class = 4
        if is_case:
            if disease_type == 'PTB':
                tb_class = 1
            elif disease_type == 'EPTB':
                tb_class = 2
            else:
                tb_class = 3
                
        certainty = 4
        if is_case:
            if disease_type == 'Mixed':
                certainty = 3
            else:
                certainty = 1 if micro else 2
                
        if is_case:
            case_counter += 1
            
        match_status = random.choice([1, 1, 1, 2, 3, 4]) if is_case else random.choice([1, 1, 3, 3])
        idx = str(i + 1).zfill(6)
        study_id = f"ABCG-{st['code']}-{tu_code}-2026-{idx}"
        first_name = random.choice(FIRST)
        last_name = random.choice(LAST)
        
        match_set_id = None
        if is_case:
            match_set_id = f"{st['code']}-{tu_code}-2026-C{str(case_counter).zfill(4)}"
        elif random.random() < 0.5:
            match_set_id = f"{st['code']}-{tu_code}-2026-C{str(random.randint(1, max(1, case_counter))).zfill(4)}"
            
        participants_list.append({
            'studyId': study_id,
            'nikshayId': f"NIK{random.randint(1000000, 9999999)}",
            'name': f"{first_name} {last_name}",
            'age': random.randint(19, 78),
            'sex': random.choice(['M', 'F']),
            'mobile': f"9{random.randint(100000000, 999999999)}",
            'village': random.choice(VILLAGES),
            'stateCode': st['code'],
            'stateName': st['name'],
            'district': district,
            'tuCode': tu_code,
            'facility': f"PHC-{random.randint(1, 40)}",
            'enrolmentDate': fmt_date(enrol_offset),
            'hrgEligible': 1,
            'matchHrg': match_hrg,
            'hrgFlags': hrg_flags,
            'ptbNaat': 1 if (is_case and disease_type != 'EPTB' and micro) else 0,
            'ptbCxr': 'Abnormal' if (is_case and disease_type != 'EPTB') else 'Normal',
            'ptbFinal': ptb_final,
            'eptbFinal': eptb_final,
            'bcgStatus': random.choice([0, 1, 1, 9]),
            'bcgEvidence': random.choice([1, 2, 3, 4]),
            'caseControlStatus': 1 if is_case else 0,
            'tbFinalClassification': tb_class,
            'caseCertainty': certainty,
            'matchSetId': match_set_id,
            'matchStatus': match_status,
            'diseaseType': disease_type,
        })
    return participants_list

participants = build_participants()
cases = [p for p in participants if p['caseControlStatus'] == 1]
controls = [p for p in participants if p['caseControlStatus'] == 0]

def get_participant(study_id):
    return next((p for p in participants if p['studyId'] == study_id or p['studyId'].endswith(study_id)), None)

dashboard_metrics = {
    'screened': 48213,
    'enrolled': len(participants) * 47 + 129,
    'confirmedPtb': len([c for c in cases if c['diseaseType'] != 'EPTB']) * 12 + 41,
    'eptb': len([c for c in cases if c['diseaseType'] == 'EPTB']) * 9 + 18,
    'lockedControls': 612,
    'partialSets': 74,
    'pendingAdjudication': 18,
    'activeErrors': 42,
}

registration_trend = []
for i in range(14):
    d = datetime(2026, 7, 9) - timedelta(days=(13 - i))
    registration_trend.append({
        'date': d.strftime('%m-%d'),
        'cases': random.randint(8, 34),
        'controls': random.randint(24, 96),
    })

sites = []
for i in range(100):
    st = STATES[i % len(STATES)]
    roll = random.random()
    status = 'synced'
    if roll < 0.72:
        status = 'synced'
    elif roll < 0.9:
        status = 'delayed'
    else:
        status = 'offline'
        
    last_check_in = ''
    if status == 'synced':
        last_check_in = f"{random.randint(1, 22)}h ago"
    elif status == 'delayed':
        last_check_in = f"{random.randint(25, 68)}h ago"
    else:
        last_check_in = f"{random.randint(4, 12)}d ago"
        
    sites.append({
        'tuCode': f"TU{str((i % 18) + 1).zfill(2)}",
        'district': random.choice(st['districts']),
        'stateCode': st['code'],
        'stateName': st['name'],
        'x': 12 + random.random() * 76,
        'y': 12 + random.random() * 72,
        'status': status,
        'lastCheckIn': last_check_in,
        'cases': random.randint(4, 40),
        'controls': random.randint(16, 160),
        'errorRate': round(random.random() * (12 if status == 'offline' else 4), 1),
    })

classification_events = []
for i in range(14):
    p = participants[i]
    status = random.choice(['Passed', 'Passed', 'Passed', 'Flagged', 'Review'])
    classification_events.append({
        'time': f"{str(random.randint(0, 23)).zfill(2)}:{str(random.randint(0, 59)).zfill(2)}:{str(random.randint(0, 59)).zfill(2)}",
        'studyId': p['studyId'],
        'steps': [
            'Parsing Nikshay diagnostics labs',
            'Evaluating extra-pulmonary symptom arrays',
            'Resolving BCG ascertainment evidence',
            'CASE_CONTROL_STATUS resolution',
        ],
        'result': status,
        'classification': TB_CLASS_LABELS[p['tbFinalClassification']],
    })

classification_breakdown = [
    { 'type': 'PTB Only', 'count': 1284, 'tone': 'chart-1' },
    { 'type': 'EPTB Only', 'count': 412, 'tone': 'chart-3' },
    { 'type': 'Mixed', 'count': 188, 'tone': 'chart-5' },
    { 'type': 'Non-TB (Control)', 'count': 3910, 'tone': 'chart-2' },
]

certainty_ratio = [
    { 'name': 'Microbiological', 'value': 962 },
    { 'name': 'Clinical', 'value': 510 },
    { 'name': 'Mixed', 'value': 188 },
]

matching_queue = []
for c in cases[:14]:
    matching_queue.append({
        'studyId': c['studyId'],
        'stateName': c['stateName'],
        'tuCode': c['tuCode'],
        'matchHrg': c['matchHrg'],
        'enrolmentDate': c['enrolmentDate'],
        'daysRemaining': random.randint(-2, 21),
        'matched': min(4, random.randint(0, 4)),
        'status': c['matchStatus'],
    })

recommended_controls = [
    { 'studyId': 'ABCG-MH-TU04-2026-000118', 'margin': 12, 'valid': True },
    { 'studyId': 'ABCG-MH-TU04-2026-000142', 'margin': -4, 'valid': True },
    { 'studyId': 'ABCG-MH-TU04-2026-000173', 'margin': 22, 'valid': True },
    { 'studyId': 'ABCG-MH-TU04-2026-000190', 'margin': -18, 'valid': True },
    { 'studyId': 'ABCG-MH-TU04-2026-000205', 'margin': 34, 'valid': False },
]

adjudication_queue = []
for p in participants[:18]:
    adjudication_queue.append({
        'studyId': p['studyId'],
        'stateName': p['stateName'],
        'tuCode': p['tuCode'],
        'conflict': random.choice([
            'NAAT positive but CXR normal',
            'EPTB positive on 2 tracks, no biopsy',
            'Control flagged with ATT history',
            'Discordant smear vs culture',
            'Physician diagnosis vs rule engine mismatch',
        ]),
        'reviewer': random.choice([
            'Dr. A. Menon',
            'Dr. S. Iyer',
            'Dr. R. Bose',
            'Unassigned',
        ]),
        'priority': random.choice(['High', 'High', 'Medium', 'Low']),
        'raised': fmt_date(random.randint(1, 20)),
    })

dq_exceptions = []
for i, p in enumerate(participants[:42]):
    dq_exceptions.append({
        'exceptionId': f"DQ-2026-{str(i + 1).zfill(5)}",
        'studyId': p['studyId'],
        'rule': random.choice([
            'MISSING_NAAT_RESULT',
            'MISSING_CXR_RECORD',
            'INVALID_MOBILE_FORMAT',
            'HRG_FLAG_CONFLICT',
            'DUPLICATE_NIKSHAY_ID',
            'CXR_IMAGE_MISSING',
        ]),
        'severity': random.choice(['Critical', 'High', 'High', 'Medium', 'Low']),
        'note': random.choice([
            'NAAT result field empty after lab sync window',
            'Chest X-Ray record image corrupt or unreadable',
            'Mobile number fails 10-digit validation',
            'HRG_DM=1 but no glucose reading recorded',
        ]),
        'raised': fmt_date(random.randint(1, 30)),
        'status': random.choice(['Open', 'Open', 'Revision Requested', 'Resolved']),
    })

audit_logs = []
for p in participants[:40]:
    audit_logs.append({
        'time': f"2026-07-{str(random.randint(1, 9)).zfill(2)} {str(random.randint(0, 23)).zfill(2)}:{str(random.randint(0, 59)).zfill(2)}",
        'user': random.choice([
            'admin.national',
            'coord.haryana',
            'coord.mp',
            'reviewer.iyer',
            'system.rule-engine',
        ]),
        'role': random.choice([
            'Super Admin',
            'State Coordinator',
            'Committee Reviewer',
            'System',
        ]),
        'event': random.choice([
            'RECORD_UPDATE',
            'MATCH_SET_LOCK',
            'CASE_OVERRIDE',
            'DQ_REVISION_REQUEST',
            'LOGIN',
            'EXPORT_GENERATED',
        ]),
        'entity': p['studyId'],
        'field': random.choice(['PTB_FINAL', 'MATCH_STATUS', 'BCG_STATUS', 'CASE_CONTROL_STATUS']),
        'from': random.choice(['0', '1', '2', '9', '—']),
        'to': random.choice(['0', '1', '2', '9']),
    })

devices = []
for i in range(28):
    st = STATES[i % len(STATES)]
    roll = random.random()
    devices.append({
        'deviceId': f"TAB-{st['code']}-{str(random.randint(100, 999))}",
        'tuCode': f"TU{str((i % 18) + 1).zfill(2)}",
        'stateName': st['name'],
        'battery': random.randint(8, 100),
        'appVersion': random.choice(['3.4.1', '3.4.1', '3.4.0', '3.3.9']),
        'queued': random.randint(0, 12) if roll < 0.7 else random.randint(40, 210),
        'lastSeen': f"{random.randint(1, 20)}h ago" if roll < 0.7 else f"{random.randint(2, 9)}d ago",
        'status': 'online' if roll < 0.7 else ('delayed' if roll < 0.9 else 'offline'),
    })

sync_throughput = []
for i in range(24):
    sync_throughput.append({
        'hour': f"{str(i).zfill(2)}:00",
        'payloads': random.randint(120, 940),
        'queue': random.randint(0, 320),
    })

sync_jobs = [
    {
        'name': 'Nikshay Nightly Integration',
        'schedule': '02:00 IST daily',
        'lastRun': '2026-07-09 02:14',
        'duration': '11m 42s',
        'status': 'success',
        'records': 8421,
    },
    {
        'name': 'TBWIN CTD File Dump',
        'schedule': 'Weekly (Mon)',
        'lastRun': '2026-07-06 04:30',
        'duration': '3m 08s',
        'status': 'success',
        'records': 1902,
    },
]

export_history = [
    {
        'id': 'EXP-2026-0042',
        'dataset': 'Case-Control Regression Set',
        'format': 'CSV',
        'rows': 4794,
        'by': 'admin.national',
        'at': '2026-07-08 17:22',
        'status': 'ready',
    },
    {
        'id': 'EXP-2026-0041',
        'dataset': 'BCG Ascertainment Extract',
        'format': 'Excel',
        'rows': 4794,
        'by': 'coord.mp',
        'at': '2026-07-07 11:05',
        'status': 'ready',
    },
    {
        'id': 'EXP-2026-0040',
        'dataset': 'Full Participant Dump',
        'format': 'JSON',
        'rows': 10344,
        'by': 'admin.national',
        'at': '2026-07-05 09:40',
        'status': 'expired',
    },
]

campaign_sites = []
for i in range(18):
    st = STATES[i % len(STATES)]
    campaign_sites.append({
        'siteCode': f"{st['code']}-TU{str((i % 18) + 1).zfill(2)}",
        'stateName': st['name'],
        'launch': fmt_date(random.randint(200, 400)),
        'conclusion': fmt_date(-random.randint(60, 200)),
        'active': random.random() < 0.85,
    })

EPTB_TRACKS = [
    'Lymph Node', 'Pleural', 'Spine / Skeletal', 'CNS / Meningeal',
    'Abdominal', 'Genitourinary', 'Pericardial', 'Cutaneous',
    'Ocular', 'Laryngeal', 'Disseminated / Miliary'
]
