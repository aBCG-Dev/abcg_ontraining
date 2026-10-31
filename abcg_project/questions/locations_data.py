"""
Centralized Jurisdiction Master Data: State -> District -> Tuberculosis Unit (TBU) -> PHIs
Configured for Adult BCG Vaccine Effectiveness (aBCG VE) Study sites.
"""

JURISDICTION_DATA = {
    "Andhra Pradesh": {
        "Alluri Sitharama Raju": {
            "Paderu DTC": ["GGH Paderu"]
        },
        "Chittoor": {
            "CHITTOOR_DTC": ["CHITTOOR DTC"]
        },
        "Guntur": {
            "Guntur DTC": ["Guntur DTC"],
            "GunturWest": ["Guntur IDH"],
            "MANGALAGIRI": ["AIIMS Medical College Mangalagiri"],
            "Tenali": ["District Hospital"]
        },
        "Krishna": {
            "DTC Machilipatnam": ["Medical College"]
        },
        "Palnadu": {
            "Narasaraopet": ["NARASARAOPETA AH"]
        },
        "Sri Potti Sriramulu Nellore": {
            "NELLORE-1": ["ACSR Medical college"]
        },
        "Sri Sathya Sai": {
            "Dharmavaram": ["NGO RDT Bathalapalli"]
        },
        "Visakhapatnam": {
            "KGH": ["KGH Medical College"],
            "Visakhapatnam_DTC": ["DTC Visakhapatnam"]
        },
        "Vizianagaram": {
            "Vizianagaram_DTC": ["Medical College"]
        },
        "Y.S.R": {
            "Kadapa Rural": ["Kadapa DTC"]
        }
    },
    "Karnataka": {
        "Bengaluru": {
            "Bengaluru TU": ["Bengaluru DTC"]
        },
        "Dharwad": {
            "Dharwad TU": ["Dharwad DTC", "KIMS Hubballi"]
        }
    },
    "Haryana": {
        "Ambala": {
            "Ambala": ["DTC TB Hospital Ambala"],
            "Ambalacantt": ["GH Ambala Cantt"]
        },
        "Bhiwani": {
            "Bhiwani_DTC": ["PHI DTC Bhiwani"],
            "Tosham": ["PHC Tosham"]
        },
        "Hisar": {
            "BARWALA": ["PHC MAMC Agroha"],
            "DTC HISAR": ["DTC HISAR(PHI)"]
        },
        "Jhajjar": {
            "Bahadurgarh": ["CBNAAT District Hospital Jhajjhar"],
            "Jhajjar": ["CBNAAT District Hospital Jhajjhar"]
        },
        "Jind": {
            "TU DTC Jind": ["Jind"]
        },
        "Kaithal": {
            "TU-1 Kaithal": ["Civil Hospital Kaithal"]
        },
        "Mewat": {
            "CHC Nuh": ["SHKM Medical Collage Nalher Mewat"],
            "GH Mandikhera": ["PHC Mandikhera"]
        },
        "Rohtak": {
            "DTC_Rohtak": ["DTC Rohtak"],
            "GH ROHTAK": ["CBNAAT Site PGIMS Rohtak"],
            "Pgims Rohtak": ["PHI PGIMS"]
        },
        "Sirsa": {
            "DTC_Sirsa": ["DTC SIRSA"]
        },
        "Sonipat": {
            "Ganaur": ["CHC PHC DMC GANNAUR"],
            "Gohana TU": ["SDH GOHANA"],
            "Mudlana": ["DMC BPS GMC KHANPUR"]
        }
    },
    "Himachal Pradesh": {
        "Bilaspur-HP": {
            "Markand": ["AIIMS Kothipura Bilaspur"]
        },
        "Kangra": {
            "NURPUR": ["Nurpur CH"],
            "TIARA": ["Govt MC Tanda"]
        },
        "Mandi": {
            "Ratti": ["SLBSGMC Nerchowk"]
        },
        "Sirmaur": {
            "DHAGERA": ["Dr YSPG Medical College Nahan"],
            "Rajpur": ["CH Paonta Sahib"]
        },
        "Una-HP": {
            "TU-Basdehra": ["Regional Hospital Una"]
        }
    },
    "Madhya Pradesh": {
        "ASHOKNAGAR": {
            "Mungaoli": ["AAM CH Mungaoli"]
        },
        "Agar Malwa": {
            "Agar": ["DTC Agar Malwa"]
        },
        "Barwani": {
            "Barwani": ["Barwani"]
        },
        "Bhind": {
            "Gohad": ["CHC Gohad"]
        },
        "Bhopal": {
            "AIIMS HOSPITAL": ["AIIMS Bhopal"],
            "Civil Hospital Bairagarh": ["Chirayu Medical College & Hospital"],
            "DH Jaiprakash Hospital": ["DH Jaiprakash Hospital"],
            "Jawaharlal Nehru Hospital (Gas rahat)": ["JAWAHARLAL NEHRU HOSPITAL (Gas rahat)"],
            "T. B. Hospital": ["TB Hospital Bhopal"]
        },
        "Chhindwara": {
            "DTC CHHINDWARA": ["MEDICAL COLLEGE CHHINDWARA URBAN"],
            "JUNNARDEO": ["CHC Jamai"]
        },
        "Damoh": {
            "DAMOH_DTC": ["DH Damoh"]
        },
        "Dewas": {
            "Dewas DTC": ["Dewas DTC"]
        },
        "Gwalior": {
            "CH gwalior": ["CH Gwalior"],
            "DTC-Gwalior": ["GRMC GWALIOR"],
            "Dabra": ["CH Dabra"],
            "Medical College": ["Madhav Dispencery"],
            "Morar": ["DH Gwalior"]
        },
        "Harda": {
            "Harda": ["DH HARDA"]
        },
        "Hoshangabad": {
            "HOSHANGABAD_DTC": ["DTC Hoshangabad"],
            "PIPARIYA": ["CHC Pipariya"]
        },
        "Katni": {
            "Rithi": ["CHC Rithi"],
            "Umaria Pan": ["CHC Umariyapan"],
            "V_Garh": ["CH Vijayraghavgarh"]
        },
        "Khargone": {
            "KHARGONE DTC": ["DTC KHARGONE"]
        },
        "Mandla": {
            "DTC-Mandla": ["DTC- Mandla"]
        },
        "Morena": {
            "TU PORSA": ["AAM CHC PORSA"],
            "TU-Joura": ["CIVIL HOSPITAL JOURA"],
            "TU-Kailaras": ["AAM CHC KAILARAS"],
            "TU-Morena DTC": ["AAM District Hospital Morena"],
            "TU-Sabalgarh": ["AAM DMC SABALGARH"]
        },
        "Narsinghpur": {
            "Narsinghpur_DTC": ["Narsinghpur-DTC"]
        },
        "Raisen": {
            "Raisen DTC": ["DTC_Raisen"]
        },
        "Ratlam": {
            "JAORA": ["Civil Hospital Jaora"]
        },
        "Satna": {
            "MAIHAR": ["CH Maihar"],
            "Majhgawan": ["CHC Majhagawan"],
            "Satna": ["DMC DH Satna"]
        },
        "Singrauli": {
            "DTC Singrauli": ["WAIDHAN"]
        },
        "Tikamgarh": {
            "Tikamgarh_DTC": ["DTC TIKAMGARH"]
        },
        "Umaria": {
            "Umaria_DTC": ["Umaria"]
        }
    },
    "Maharashtra": {
        "Amravati": {
            "Amravati": ["DTC Amravati"]
        },
        "Kalyan Dombivli MC": {
            "Bai Rukminibai Hospital TU": ["UCHC Bai Rukminibai Hospital"]
        },
        "Latur": {
            "LATUR URBAN": ["Med Col VDGMC LATUR"]
        },
        "Mumbai_Andheri East": {
            "Squatters Colony HEALTH POST": ["SQUATTERS COLONY PHI"]
        },
        "Mumbai_Bandra East": {
            "V.N. Desai Hospital": ["Hospital V. N. DESAI"]
        },
        "Mumbai_Chembur": {
            "Maa Hospital": ["Hospital MAA"]
        },
        "Mumbai_Dadar": {
            "URBAN HEALTH CENTRE, DHARAVI": ["URBAN HEALTH CENTRE, DHARAVI"]
        },
        "Mumbai_Kurla": {
            "K.B. Bhabha Hospital": ["HOSPITAL KURLA BHABHA"]
        },
        "Nagpur MC": {
            "GMC": ["Government Medical College Nagpur"],
            "IGGMC": ["Medcol_Indira Gandhi Government Medical College and Hospital"]
        },
        "Pimpri Chinchwad MC": {
            "YCM ZONE TB UNIT": ["YCM HOSPITALPIMPARI"]
        }
    },
    "Odisha": {
        "Balangir": {
            "Balangir DTC": ["DHH BALANGIR"]
        },
        "Cuttack": {
            "Urban_TU": ["SCB MCH"]
        },
        "Dhenkanal": {
            "Dhenkanal_DTC": ["DHENKANAL DMC"]
        },
        "Jharsuguda": {
            "Jharsuguda": ["Jharsuguda-dtc"]
        },
        "Kalahandi": {
            "DTC Kalahandi.": ["District TB Centre Kalahandi"]
        },
        "Mayurbhanj": {
            "Baripada_DTC": ["District TB Centre Mayurbhanj"],
            "Udala": ["Udala"]
        },
        "Rayagada": {
            "DTC Rayagada": ["DTC Rayagada"]
        },
        "Sundargarh": {
            "Sadar Sundargarh": ["DTC, Sundargarh"]
        }
    },
    "Tamil Nadu": {
        "Chennai": {
            "Chennai Central TU": ["Chennai Central PHI"],
            "TU1": ["Chennai TU1 PHI"]
        },
        "Coimbatore": {
            "TU3": ["Coimbatore TU3 PHI"]
        },
        "Madurai": {
            "TU2": ["Madurai TU2 PHI"]
        },
        "Tiruvallur": {
            "Tiruvallur TU": ["Avadi PHC"]
        }
    }
}

def get_base_hierarchy():
    """
    Returns a dictionary of { State: { District: [TBU, ...] } }
    derived from the master JURISDICTION_DATA.
    """
    hierarchy = {}
    for state, districts in JURISDICTION_DATA.items():
        hierarchy[state] = {}
        for district, tbus in districts.items():
            hierarchy[state][district] = sorted(list(tbus.keys()))
    return hierarchy


STATE_CODE_TO_NAME = {
    "TN": "Tamil Nadu",
    "KA": "Karnataka",
    "OD": "Odisha",
    "AP": "Andhra Pradesh",
    "AN": "Andhra Pradesh",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
}

TU_CODE_TO_TBU = {
    "TIR": ("Tiruvallur", "Tiruvallur TU"),
    "BEN": ("Bengaluru", "Bengaluru TU"),
    "URB": ("Cuttack", "Urban_TU"),
    "NEL": ("Sri Potti Sriramulu Nellore", "NELLORE-1"),
    "GUN": ("Guntur", "Guntur DTC"),
    "BAR": ("Mayurbhanj", "Baripada_DTC"),
}

def get_location_by_facility(facility_name):
    if not facility_name:
        return None
    fac_clean = str(facility_name).strip().lower()
    # Pass 1: Exact facility match (highest confidence)
    for state, dists in JURISDICTION_DATA.items():
        for dist, tbus in dists.items():
            for tbu, phis in tbus.items():
                for phi in phis:
                    if phi.strip().lower() == fac_clean:
                        return (state, dist, tbu)
    # Pass 2: Substring match (skip generic tokens like 'medical college')
    for state, dists in JURISDICTION_DATA.items():
        for dist, tbus in dists.items():
            for tbu, phis in tbus.items():
                for phi in phis:
                    p_clean = phi.strip().lower()
                    if len(p_clean) >= 6 and (p_clean in fac_clean or fac_clean in p_clean):
                        return (state, dist, tbu)
    return None

def recover_location_from_evidence(study_id=None, facility=None, screening_id=None, pincode=None):
    """
    Recovers verified (state, district, tb_unit) from evidence when a record was corrupted to GLOBAL.
    """
    sid = str(study_id or screening_id or "").upper().strip()
    if "ABCG-" in sid:
        parts = sid.split("-")
        if len(parts) >= 3:
            st_code = parts[1]
            tu_code = parts[2]
            st_name = STATE_CODE_TO_NAME.get(st_code)
            dist_tbu = TU_CODE_TO_TBU.get(tu_code)
            if st_name and dist_tbu:
                return st_name, dist_tbu[0], dist_tbu[1]
            elif st_name and st_name in JURISDICTION_DATA:
                first_dist = next(iter(JURISDICTION_DATA[st_name].keys()))
                first_tbu = next(iter(JURISDICTION_DATA[st_name][first_dist].keys()))
                return st_name, first_dist, first_tbu

    fac_loc = get_location_by_facility(facility)
    if fac_loc:
        return fac_loc

    pin_str = str(pincode or "").strip()
    if pin_str.startswith("60"):
        return "Tamil Nadu", "Tiruvallur", "Tiruvallur TU"
    elif pin_str.startswith("56"):
        return "Karnataka", "Bengaluru", "Bengaluru TU"
    elif pin_str.startswith("75"):
        return "Odisha", "Cuttack", "Urban_TU"

    return "Tamil Nadu", "Tiruvallur", "Tiruvallur TU"

def resolve_operational_location(participant=None, user=None, session=None, submitted_state=None, submitted_district=None, submitted_tb_unit=None):
    """
    Authoritative location resolver:
    Ensures participant registration and editing always receive a valid operational location.
    Guarantees 'GLOBAL', 'ALL DISTRICTS', and 'ALL TB UNITS' are NEVER used as participant coordinates.
    """
    def is_generic(val):
        s = str(val or "").strip().upper()
        return not s or s in ("GLOBAL", "ALL DISTRICTS", "ALL TB UNITS", "ALL", "NONE", "NULL", "UNDEFINED")

    # 1. Existing participant priority: strictly preserve participant's original study location
    if participant:
        p_state = getattr(participant, "state", "")
        p_dist = getattr(participant, "district", "")
        p_tbu = getattr(participant, "tb_unit", "")
        
        if not is_generic(p_state) and not is_generic(p_dist) and not is_generic(p_tbu):
            return p_state.strip(), p_dist.strip(), p_tbu.strip()
        
        # Corrupted to GLOBAL: recover from authoritative evidence (Study ID prefix, Facility, Pincode)
        return recover_location_from_evidence(
            study_id=getattr(participant, "study_id", None),
            facility=getattr(participant, "facility", None) or getattr(participant, "public_phi", None),
            screening_id=getattr(participant, "screening_id", None),
            pincode=getattr(participant, "pincode", None)
        )

    # 2. Check submitted form values: respect valid operational location entered for new registration
    if not is_generic(submitted_state) and not is_generic(submitted_district) and not is_generic(submitted_tb_unit):
        return submitted_state.strip(), submitted_district.strip(), submitted_tb_unit.strip()

    # 3. Check User Profile (if nurse/doctor with specific assignment)
    if user and hasattr(user, "profile"):
        prof = user.profile
        if not is_generic(prof.state) and not is_generic(prof.district) and not is_generic(prof.tb_unit):
            return prof.state.strip(), prof.district.strip(), prof.tb_unit.strip()

    # 4. Check active session filter (e.g. if Admin selected an active site in navbar)
    if session:
        s_state = session.get("selected_state", "")
        s_dist = session.get("selected_district", "")
        s_tbu = session.get("selected_tb_unit", "")
        if not is_generic(s_state) and not is_generic(s_dist) and not is_generic(s_tbu):
            return s_state.strip(), s_dist.strip(), s_tbu.strip()
        elif not is_generic(s_state) and s_state in JURISDICTION_DATA:
            first_dist = next(iter(JURISDICTION_DATA[s_state].keys()))
            first_tbu = next(iter(JURISDICTION_DATA[s_state][first_dist].keys()))
            return s_state.strip(), first_dist, first_tbu

    # 5. Fallback to active StudySite or study default
    try:
        from questions.models import StudySite
        site_obj = StudySite.objects.filter(is_active=True).first()
        if site_obj and not is_generic(site_obj.state) and not is_generic(site_obj.district) and not is_generic(site_obj.tb_unit):
            return site_obj.state.strip(), site_obj.district.strip(), site_obj.tb_unit.strip()
    except Exception:
        pass

    return "Tamil Nadu", "Tiruvallur", "Tiruvallur TU"
