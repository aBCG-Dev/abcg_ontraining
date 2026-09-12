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
