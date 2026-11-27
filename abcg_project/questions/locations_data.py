"""
Centralized Jurisdiction Master Data: State -> District -> Tuberculosis Unit (TBU) -> PHIs
Configured for Adult BCG Vaccine Effectiveness (aBCG VE) Study sites.
Includes authoritative numeric Codebook IDs (state_id, district_id, tbu_id).
"""

JURISDICTION_DATA = {
    "Andhra Pradesh": {
        "Alluri Sitharama Raju": {
            "Paderu DTC": [
                "GGH Paderu"
            ]
        },
        "Chittoor": {
            "CHITTOOR_DTC": [
                "CHITTOOR DTC"
            ]
        },
        "Guntur": {
            "Guntur DTC": [
                "Guntur DTC"
            ],
            "GunturWest": [
                "Guntur IDH"
            ],
            "MANGALAGIRI": [
                "AIIMS Medical College Mangalagiri"
            ],
            "Tenali": [
                "District Hospital"
            ]
        },
        "Krishna": {
            "DTC Machilipatnam": [
                "Medical College"
            ]
        },
        "Palnadu": {
            "Narasaraopet": [
                "NARASARAOPETA AH"
            ]
        },
        "Sri Potti Sriramulu Nellore": {
            "NELLORE-1": [
                "ACSR Medical college"
            ]
        },
        "Sri Sathya Sai": {
            "Dharmavaram": [
                "NGO RDT Bathalapalli"
            ]
        },
        "Visakhapatnam": {
            "KGH": [
                "KGH Medical College"
            ],
            "Visakhapatnam_DTC": [
                "DTC Visakhapatnam"
            ]
        },
        "Vizianagaram": {
            "Vizianagaram_DTC": [
                "Medical College"
            ]
        },
        "Y.S.R": {
            "Kadapa Rural": [
                "Kadapa DTC"
            ]
        }
    },
    "Haryana": {
        "Ambala": {
            "Ambala": [
                "DTC TB Hospital Ambala"
            ],
            "Ambalacantt": [
                "GH Ambala Cantt"
            ]
        },
        "Bhiwani": {
            "Bhiwani_DTC": [
                "PHI DTC Bhiwani"
            ],
            "Tosham": [
                "PHC Tosham"
            ]
        },
        "Hisar": {
            "BARWALA": [
                "PHC MAMC Agroha"
            ],
            "DTC HISAR": [
                "DTC HISAR(PHI)"
            ]
        },
        "Jhajjar": {
            "Bahadurgarh": [
                "CBNAAT District Hospital Jhajjhar"
            ],
            "Jhajjar": [
                "CBNAAT District Hospital Jhajjhar"
            ]
        },
        "Jind": {
            "TU DTC Jind": [
                "Jind"
            ]
        },
        "Kaithal": {
            "TU-1 Kaithal": [
                "Civil Hospital Kaithal"
            ]
        },
        "Mewat": {
            "CHC Nuh": [
                "SHKM Medical Collage Nalher Mewat"
            ],
            "GH Mandikhera": [
                "PHC Mandikhera"
            ]
        },
        "Rohtak": {
            "DTC_Rohtak": [
                "DTC Rohtak"
            ],
            "GH ROHTAK": [
                "CBNAAT Site PGIMS Rohtak"
            ],
            "Pgims Rohtak": [
                "PHI PGIMS"
            ]
        },
        "Sirsa": {
            "DTC_Sirsa": [
                "DTC SIRSA"
            ]
        },
        "Sonipat": {
            "Ganaur": [
                "CHC PHC DMC GANNAUR"
            ],
            "Gohana TU": [
                "SDH GOHANA"
            ],
            "Mudlana": [
                "DMC BPS GMC KHANPUR"
            ]
        }
    },
    "Himachal Pradesh": {
        "Bilaspur-HP": {
            "Markand": [
                "AIIMS Kothipura Bilaspur"
            ]
        },
        "Kangra": {
            "NURPUR": [
                "Nurpur CH"
            ],
            "TIARA": [
                "Govt MC Tanda"
            ]
        },
        "Mandi": {
            "Ratti": [
                "SLBSGMC Nerchowk"
            ]
        },
        "Sirmaur": {
            "DHAGERA": [
                "Dr YSPG Medical College Nahan"
            ],
            "Rajpur": [
                "CH Paonta Sahib"
            ]
        },
        "Una-HP": {
            "TU-Basdehra": [
                "Regional Hospital Una"
            ]
        }
    },
    "Madhya Pradesh": {
        "ASHOKNAGAR": {
            "Mungaoli": [
                "AAM CH Mungaoli"
            ]
        },
        "Agar Malwa": {
            "Agar": [
                "DTC Agar Malwa"
            ]
        },
        "Barwani": {
            "Barwani": [
                "Barwani"
            ]
        },
        "Bhind": {
            "Gohad": [
                "CHC Gohad"
            ]
        },
        "Bhopal": {
            "AIIMS HOSPITAL": [
                "AIIMS Bhopal"
            ],
            "Civil Hospital Bairagarh": [
                "Chirayu Medical College & Hospital"
            ],
            "DH Jaiprakash Hospital": [
                "DH Jaiprakash Hospital"
            ],
            "Jawaharlal Nehru Hospital (Gas rahat)": [
                "JAWAHARLAL NEHRU HOSPITAL (Gas rahat)"
            ],
            "T. B. Hospital": [
                "TB Hospital Bhopal"
            ]
        },
        "Chhindwara": {
            "DTC CHHINDWARA": [
                "MEDICAL COLLEGE CHHINDWARA URBAN"
            ],
            "JUNNARDEO": [
                "CHC Jamai"
            ]
        },
        "Damoh": {
            "DAMOH_DTC": [
                "DH Damoh"
            ]
        },
        "Dewas": {
            "Dewas DTC": [
                "Dewas DTC"
            ]
        },
        "Gwalior": {
            "CH gwalior": [
                "CH Gwalior"
            ],
            "DTC-Gwalior": [
                "GRMC GWALIOR"
            ],
            "Dabra": [
                "CH Dabra"
            ],
            "Medical College": [
                "Madhav Dispencery"
            ],
            "Morar": [
                "DH Gwalior"
            ]
        },
        "Harda": {
            "Harda": [
                "DH HARDA"
            ]
        },
        "Hoshangabad": {
            "HOSHANGABAD_DTC": [
                "DTC Hoshangabad"
            ],
            "PIPARIYA": [
                "CHC Pipariya"
            ]
        },
        "Katni": {
            "Rithi": [
                "CHC Rithi"
            ],
            "Umaria Pan": [
                "CHC Umariyapan"
            ],
            "V_Garh": [
                "CH Vijayraghavgarh"
            ]
        },
        "Khargone": {
            "KHARGONE DTC": [
                "DTC KHARGONE"
            ]
        },
        "Mandla": {
            "DTC-Mandla": [
                "DTC- Mandla"
            ]
        },
        "Morena": {
            "TU PORSA": [
                "AAM CHC PORSA"
            ],
            "TU-Joura": [
                "CIVIL HOSPITAL JOURA"
            ],
            "TU-Kailaras": [
                "AAM CHC KAILARAS"
            ],
            "TU-Morena DTC": [
                "AAM District Hospital Morena"
            ],
            "TU-Sabalgarh": [
                "AAM DMC SABALGARH"
            ]
        },
        "Narsinghpur": {
            "Narsinghpur_DTC": [
                "Narsinghpur-DTC"
            ]
        },
        "Raisen": {
            "Raisen DTC": [
                "DTC_Raisen"
            ]
        },
        "Ratlam": {
            "JAORA": [
                "Civil Hospital Jaora"
            ]
        },
        "Satna": {
            "MAIHAR": [
                "CH Maihar"
            ],
            "Majhgawan": [
                "CHC Majhagawan"
            ],
            "Satna": [
                "DMC DH Satna"
            ]
        },
        "Singrauli": {
            "DTC Singrauli": [
                "WAIDHAN"
            ]
        },
        "Tikamgarh": {
            "Tikamgarh_DTC": [
                "DTC TIKAMGARH"
            ]
        },
        "Umaria": {
            "Umaria_DTC": [
                "Umaria"
            ]
        }
    },
    "Maharashtra": {
        "Amravati": {
            "Amravati": [
                "DTC Amravati"
            ]
        },
        "Kalyan Dombivli MC": {
            "Bai Rukminibai Hospital TU": [
                "UCHC Bai Rukminibai Hospital"
            ]
        },
        "Latur": {
            "LATUR URBAN": [
                "Med Col VDGMC LATUR"
            ]
        },
        "Mumbai_Andheri East": {
            "Squatters Colony HEALTH POST": [
                "SQUATTERS COLONY PHI"
            ]
        },
        "Mumbai_Bandra East": {
            "V.N. Desai Hospital": [
                "Hospital V. N. DESAI"
            ]
        },
        "Mumbai_Chembur": {
            "Maa Hospital": [
                "Hospital MAA"
            ]
        },
        "Mumbai_Dadar": {
            "URBAN HEALTH CENTRE, DHARAVI": [
                "URBAN HEALTH CENTRE, DHARAVI"
            ]
        },
        "Mumbai_Kurla": {
            "K.B. Bhabha Hospital": [
                "HOSPITAL KURLA BHABHA"
            ]
        },
        "Nagpur MC": {
            "GMC": [
                "Government Medical College Nagpur"
            ],
            "IGGMC": [
                "Medcol_Indira Gandhi Government Medical College and Hospital"
            ]
        },
        "Pimpri Chinchwad MC": {
            "YCM ZONE TB UNIT": [
                "YCM HOSPITALPIMPARI"
            ]
        }
    },
    "Odisha": {
        "Balangir": {
            "Balangir DTC": [
                "DHH BALANGIR"
            ]
        },
        "Cuttack": {
            "Urban_TU": [
                "SCB MCH"
            ]
        },
        "Dhenkanal": {
            "Dhenkanal_DTC": [
                "DHENKANAL DMC"
            ]
        },
        "Jharsuguda": {
            "Jharsuguda": [
                "Jharsuguda-dtc"
            ]
        },
        "Kalahandi": {
            "DTC Kalahandi": [
                "District TB Centre Kalahandi"
            ]
        },
        "Mayurbhanj": {
            "Baripada_DTC": [
                "District TB Centre Mayurbhanj"
            ],
            "Udala": [
                "Udala"
            ]
        },
        "Rayagada": {
            "DTC Rayagada": [
                "DTC Rayagada"
            ]
        },
        "Sundargarh": {
            "Sadar Sundargarh": [
                "DTC, Sundargarh"
            ]
        }
    },
    "Tamil Nadu": {
        "Chennai": {
            "Chennai Central TU": [
                "Chennai Central PHI"
            ],
            "TU1": [
                "Chennai TU1 PHI"
            ]
        },
        "Coimbatore": {
            "TU3": [
                "Coimbatore TU3 PHI"
            ]
        },
        "Madurai": {
            "TU2": [
                "Madurai TU2 PHI"
            ]
        },
        "Tiruvallur": {
            "Tiruvallur TU": [
                "Avadi PHC"
            ]
        }
    },
    "Training State": {
        "Training District": {
            "Training TBU": [
                "Training Facility / PHI"
            ]
        }
    }
}


MASTER_JURISDICTION_RECORDS = [
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 1, 'district': 'Alluri Sitharama Raju', 'tbu_id': 1, 'tb_unit': 'Paderu DTC'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 2, 'district': 'Chittoor', 'tbu_id': 2, 'tb_unit': 'Chittoor_DTC'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 3, 'district': 'Guntur', 'tbu_id': 3, 'tb_unit': 'GunturWest'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 3, 'district': 'Guntur', 'tbu_id': 4, 'tb_unit': 'Guntur DTC'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 3, 'district': 'Guntur', 'tbu_id': 5, 'tb_unit': 'Mangalagiri'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 3, 'district': 'Guntur', 'tbu_id': 6, 'tb_unit': 'Tenali'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 4, 'district': 'Krishna', 'tbu_id': 7, 'tb_unit': 'DTC Machilipatnam'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 5, 'district': 'Palnadu', 'tbu_id': 8, 'tb_unit': 'Narasaraopet'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 6, 'district': 'Sri Potti Sriramulu Nellore', 'tbu_id': 9, 'tb_unit': 'Nellore-1'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 7, 'district': 'Sri Sathya Sai', 'tbu_id': 10, 'tb_unit': 'Dharmavaram'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 8, 'district': 'Visakhapatnam', 'tbu_id': 11, 'tb_unit': 'Visakhapatnam_DTC'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 8, 'district': 'Visakhapatnam', 'tbu_id': 12, 'tb_unit': 'KGH'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 9, 'district': 'Vizianagaram', 'tbu_id': 13, 'tb_unit': 'Vizianagaram_DTC'},
    {'state_id': 1, 'state': 'Andhra Pradesh', 'district_id': 10, 'district': 'Y.S.R', 'tbu_id': 14, 'tb_unit': 'Kadapa Rural'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 11, 'district': 'Ambala', 'tbu_id': 15, 'tb_unit': 'Ambala'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 11, 'district': 'Ambala', 'tbu_id': 16, 'tb_unit': 'Ambalacantt'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 12, 'district': 'Bhiwani', 'tbu_id': 17, 'tb_unit': 'Tosham'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 12, 'district': 'Bhiwani', 'tbu_id': 18, 'tb_unit': 'Bhiwani_DTC'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 13, 'district': 'Hisar', 'tbu_id': 19, 'tb_unit': 'DTC Hisar'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 13, 'district': 'Hisar', 'tbu_id': 20, 'tb_unit': 'Barwala'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 14, 'district': 'Jhajjar', 'tbu_id': 21, 'tb_unit': 'Jhajjar'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 14, 'district': 'Jhajjar', 'tbu_id': 22, 'tb_unit': 'Bahadurgarh'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 15, 'district': 'Jind', 'tbu_id': 23, 'tb_unit': 'TU DTC Jind'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 16, 'district': 'Kaithal', 'tbu_id': 24, 'tb_unit': 'TU-1 Kaithal'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 17, 'district': 'Mewat', 'tbu_id': 25, 'tb_unit': 'GH Mandikhera'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 17, 'district': 'Mewat', 'tbu_id': 26, 'tb_unit': 'CHC Nuh'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 18, 'district': 'Rohtak', 'tbu_id': 27, 'tb_unit': 'GH Rohtak'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 18, 'district': 'Rohtak', 'tbu_id': 28, 'tb_unit': 'DTC_Rohtak'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 18, 'district': 'Rohtak', 'tbu_id': 29, 'tb_unit': 'PGIMS Rohtak'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 19, 'district': 'Sirsa', 'tbu_id': 30, 'tb_unit': 'DTC_Sirsa'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 20, 'district': 'Sonipat', 'tbu_id': 31, 'tb_unit': 'Ganaur'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 20, 'district': 'Sonipat', 'tbu_id': 32, 'tb_unit': 'Mudlana'},
    {'state_id': 2, 'state': 'Haryana', 'district_id': 20, 'district': 'Sonipat', 'tbu_id': 33, 'tb_unit': 'Gohana TU'},
    {'state_id': 3, 'state': 'Himachal Pradesh', 'district_id': 21, 'district': 'Bilaspur-HP', 'tbu_id': 34, 'tb_unit': 'Markand'},
    {'state_id': 3, 'state': 'Himachal Pradesh', 'district_id': 22, 'district': 'Sirmaur', 'tbu_id': 35, 'tb_unit': 'Rajpur'},
    {'state_id': 3, 'state': 'Himachal Pradesh', 'district_id': 22, 'district': 'Sirmaur', 'tbu_id': 36, 'tb_unit': 'Dhagera'},
    {'state_id': 3, 'state': 'Himachal Pradesh', 'district_id': 23, 'district': 'Kangra', 'tbu_id': 37, 'tb_unit': 'Tiara'},
    {'state_id': 3, 'state': 'Himachal Pradesh', 'district_id': 23, 'district': 'Kangra', 'tbu_id': 38, 'tb_unit': 'Nurpur'},
    {'state_id': 3, 'state': 'Himachal Pradesh', 'district_id': 24, 'district': 'Una-HP', 'tbu_id': 39, 'tb_unit': 'TU-Basdehra'},
    {'state_id': 3, 'state': 'Himachal Pradesh', 'district_id': 25, 'district': 'Mandi', 'tbu_id': 40, 'tb_unit': 'Ratti'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 26, 'district': 'Agar Malwa', 'tbu_id': 41, 'tb_unit': 'Agar'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 27, 'district': 'Ashoknagar', 'tbu_id': 42, 'tb_unit': 'Mungaoli'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 28, 'district': 'Barwani', 'tbu_id': 43, 'tb_unit': 'Barwani'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 29, 'district': 'Bhind', 'tbu_id': 44, 'tb_unit': 'Gohad'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 30, 'district': 'Bhopal', 'tbu_id': 45, 'tb_unit': 'DH Jaiprakash Hospital'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 30, 'district': 'Bhopal', 'tbu_id': 46, 'tb_unit': 'Jawaharlal Nehru Hospital (Gas Rahat)'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 30, 'district': 'Bhopal', 'tbu_id': 47, 'tb_unit': 'AIIMS Hospital'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 30, 'district': 'Bhopal', 'tbu_id': 48, 'tb_unit': 'Civil Hospital Bairagarh'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 30, 'district': 'Bhopal', 'tbu_id': 49, 'tb_unit': 'T. B. Hospital'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 31, 'district': 'Chhindwara', 'tbu_id': 50, 'tb_unit': 'Junnardeo'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 31, 'district': 'Chhindwara', 'tbu_id': 51, 'tb_unit': 'DTC Chhindwara'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 32, 'district': 'Damoh', 'tbu_id': 52, 'tb_unit': 'Damoh_DTC'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 33, 'district': 'Dewas', 'tbu_id': 53, 'tb_unit': 'Dewas DTC'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 34, 'district': 'Gwalior', 'tbu_id': 54, 'tb_unit': 'CH Gwalior'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 34, 'district': 'Gwalior', 'tbu_id': 55, 'tb_unit': 'Dabra'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 34, 'district': 'Gwalior', 'tbu_id': 56, 'tb_unit': 'Morar'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 34, 'district': 'Gwalior', 'tbu_id': 57, 'tb_unit': 'Medical College'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 34, 'district': 'Gwalior', 'tbu_id': 58, 'tb_unit': 'DTC-Gwalior'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 35, 'district': 'Harda', 'tbu_id': 59, 'tb_unit': 'Harda'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 36, 'district': 'Hoshangabad', 'tbu_id': 60, 'tb_unit': 'Pipariya'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 36, 'district': 'Hoshangabad', 'tbu_id': 61, 'tb_unit': 'Hoshangabad_DTC'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 37, 'district': 'Katni', 'tbu_id': 62, 'tb_unit': 'Rithi'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 37, 'district': 'Katni', 'tbu_id': 63, 'tb_unit': 'Umaria Pan'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 37, 'district': 'Katni', 'tbu_id': 64, 'tb_unit': 'V_Garh'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 38, 'district': 'Khargone', 'tbu_id': 65, 'tb_unit': 'Khargone DTC'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 39, 'district': 'Mandla', 'tbu_id': 66, 'tb_unit': 'DTC-Mandla'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 40, 'district': 'Morena', 'tbu_id': 67, 'tb_unit': 'TU-Kailaras'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 40, 'district': 'Morena', 'tbu_id': 68, 'tb_unit': 'TU-Sabalgarh'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 40, 'district': 'Morena', 'tbu_id': 69, 'tb_unit': 'TU Porsa'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 40, 'district': 'Morena', 'tbu_id': 70, 'tb_unit': 'TU-Joura'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 40, 'district': 'Morena', 'tbu_id': 71, 'tb_unit': 'TU-Morena DTC'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 41, 'district': 'Narsinghpur', 'tbu_id': 72, 'tb_unit': 'Narsinghpur_DTC'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 42, 'district': 'Raisen', 'tbu_id': 73, 'tb_unit': 'Raisen DTC'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 43, 'district': 'Ratlam', 'tbu_id': 74, 'tb_unit': 'Jaora'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 44, 'district': 'Satna', 'tbu_id': 75, 'tb_unit': 'Majhgawan'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 44, 'district': 'Satna', 'tbu_id': 76, 'tb_unit': 'Satna'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 44, 'district': 'Satna', 'tbu_id': 77, 'tb_unit': 'Maihar'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 45, 'district': 'Singrauli', 'tbu_id': 78, 'tb_unit': 'DTC Singrauli'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 46, 'district': 'Tikamgarh', 'tbu_id': 79, 'tb_unit': 'Tikamgarh_DTC'},
    {'state_id': 4, 'state': 'Madhya Pradesh', 'district_id': 47, 'district': 'Umaria', 'tbu_id': 80, 'tb_unit': 'Umaria_DTC'},
    {'state_id': 5, 'state': 'Maharashtra', 'district_id': 48, 'district': 'Amravati', 'tbu_id': 81, 'tb_unit': 'Amravati'},
    {'state_id': 5, 'state': 'Maharashtra', 'district_id': 49, 'district': 'Kalyan Dombivli MC', 'tbu_id': 82, 'tb_unit': 'Bai Rukminibai Hospital TU'},
    {'state_id': 5, 'state': 'Maharashtra', 'district_id': 50, 'district': 'Latur', 'tbu_id': 83, 'tb_unit': 'Latur Urban'},
    {'state_id': 5, 'state': 'Maharashtra', 'district_id': 51, 'district': 'Mumbai_Andheri East', 'tbu_id': 84, 'tb_unit': 'Squatters Colony Health Post'},
    {'state_id': 5, 'state': 'Maharashtra', 'district_id': 52, 'district': 'Mumbai_Bandra East', 'tbu_id': 85, 'tb_unit': 'V.N. Desai Hospital'},
    {'state_id': 5, 'state': 'Maharashtra', 'district_id': 53, 'district': 'Mumbai_Chembur', 'tbu_id': 86, 'tb_unit': 'Maa Hospital'},
    {'state_id': 5, 'state': 'Maharashtra', 'district_id': 54, 'district': 'Mumbai_Dadar', 'tbu_id': 87, 'tb_unit': 'Urban Health Centre, Dharavi'},
    {'state_id': 5, 'state': 'Maharashtra', 'district_id': 55, 'district': 'Mumbai_Kurla', 'tbu_id': 88, 'tb_unit': 'K.B. Bhabha Hospital'},
    {'state_id': 5, 'state': 'Maharashtra', 'district_id': 56, 'district': 'Nagpur MC', 'tbu_id': 89, 'tb_unit': 'GMC'},
    {'state_id': 5, 'state': 'Maharashtra', 'district_id': 56, 'district': 'Nagpur MC', 'tbu_id': 90, 'tb_unit': 'IGGMC'},
    {'state_id': 5, 'state': 'Maharashtra', 'district_id': 57, 'district': 'Pimpri Chinchwad MC', 'tbu_id': 91, 'tb_unit': 'YCM Zone TB Unit'},
    {'state_id': 6, 'state': 'Odisha', 'district_id': 58, 'district': 'Balangir', 'tbu_id': 92, 'tb_unit': 'Balangir DTC'},
    {'state_id': 6, 'state': 'Odisha', 'district_id': 59, 'district': 'Cuttack', 'tbu_id': 93, 'tb_unit': 'Urban_TU'},
    {'state_id': 6, 'state': 'Odisha', 'district_id': 60, 'district': 'Dhenkanal', 'tbu_id': 94, 'tb_unit': 'Dhenkanal_DTC'},
    {'state_id': 6, 'state': 'Odisha', 'district_id': 61, 'district': 'Jharsuguda', 'tbu_id': 95, 'tb_unit': 'Jharsuguda'},
    {'state_id': 6, 'state': 'Odisha', 'district_id': 62, 'district': 'Kalahandi', 'tbu_id': 96, 'tb_unit': 'DTC Kalahandi'},
    {'state_id': 6, 'state': 'Odisha', 'district_id': 63, 'district': 'Mayurbhanj', 'tbu_id': 97, 'tb_unit': 'Baripada_DTC'},
    {'state_id': 6, 'state': 'Odisha', 'district_id': 63, 'district': 'Mayurbhanj', 'tbu_id': 98, 'tb_unit': 'Udala'},
    {'state_id': 6, 'state': 'Odisha', 'district_id': 64, 'district': 'Rayagada', 'tbu_id': 99, 'tb_unit': 'DTC Rayagada'},
    {'state_id': 6, 'state': 'Odisha', 'district_id': 65, 'district': 'Sundargarh', 'tbu_id': 100, 'tb_unit': 'Sadar Sundargarh'},
    {'state_id': 7, 'state': 'Tamil Nadu', 'district_id': 66, 'district': 'Chennai', 'tbu_id': 101, 'tb_unit': 'Chennai Central TU'},
    {'state_id': 7, 'state': 'Tamil Nadu', 'district_id': 66, 'district': 'Chennai', 'tbu_id': 102, 'tb_unit': 'TU1'},
    {'state_id': 7, 'state': 'Tamil Nadu', 'district_id': 67, 'district': 'Coimbatore', 'tbu_id': 103, 'tb_unit': 'TU3'},
    {'state_id': 7, 'state': 'Tamil Nadu', 'district_id': 68, 'district': 'Madurai', 'tbu_id': 104, 'tb_unit': 'TU2'},
    {'state_id': 7, 'state': 'Tamil Nadu', 'district_id': 69, 'district': 'Tiruvallur', 'tbu_id': 105, 'tb_unit': 'Tiruvallur TU'},
    {'state_id': 99, 'state': 'Training State', 'district_id': 999, 'district': 'Training District', 'tbu_id': 999, 'tb_unit': 'Training TBU'},
]



def _clean_str(val):
    if not val:
        return ""
    return str(val).strip().lower().replace("_", " ").replace("-", " ").replace(".", "")

# Lookup indices for fast O(1) resolution
TBU_NORM_MAP = {}
TBU_ID_MAP = {}
for rec in MASTER_JURISDICTION_RECORDS:
    TBU_ID_MAP[rec["tbu_id"]] = rec
    norm_tu = _clean_str(rec["tb_unit"])
    norm_dist = _clean_str(rec["district"])
    norm_state = _clean_str(rec["state"])
    TBU_NORM_MAP[(norm_state, norm_dist, norm_tu)] = rec
    TBU_NORM_MAP[(norm_dist, norm_tu)] = rec
    if norm_tu not in TBU_NORM_MAP:
        TBU_NORM_MAP[norm_tu] = rec

def lookup_jurisdiction_by_tbu(tbu_name, district_name=None, state_name=None):
    """
    Matches a TB Unit (with optional district and state hints)
    to its authoritative jurisdiction record with numeric IDs.
    Tolerates casing, underscores, hyphens, and whitespace variations.
    """
    if not tbu_name:
        return None
    norm_tu = _clean_str(tbu_name)
    norm_dist = _clean_str(district_name) if district_name else None
    norm_state = _clean_str(state_name) if state_name else None

    if norm_state and norm_dist:
        match = TBU_NORM_MAP.get((norm_state, norm_dist, norm_tu))
        if match:
            return match
    if norm_dist:
        match = TBU_NORM_MAP.get((norm_dist, norm_tu))
        if match:
            return match
    return TBU_NORM_MAP.get(norm_tu)

def lookup_jurisdiction_by_id(tbu_id):
    if tbu_id is None:
        return None
    try:
        return TBU_ID_MAP.get(int(tbu_id))
    except (ValueError, TypeError):
        return None

def get_master_codebook():
    return list(MASTER_JURISDICTION_RECORDS)

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
    "OD": "Odisha",
    "AP": "Andhra Pradesh",
    "AN": "Andhra Pradesh",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "TR": "Training State",
    "TS": "Training State",
}

TU_CODE_TO_TBU = {
    "TIR": ("Tiruvallur", "Tiruvallur TU"),
    "URB": ("Cuttack", "Urban_TU"),
    "NEL": ("Sri Potti Sriramulu Nellore", "Nellore-1"),
    "GUN": ("Guntur", "Guntur DTC"),
    "BAR": ("Mayurbhanj", "Baripada_DTC"),
    "TRN": ("Training District", "Training TBU"),
    "TBU": ("Training District", "Training TBU"),
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
    Supports both new hierarchical format (ABCG-1-3-4-000001, SCREENED-1-3-4-000001) and legacy format.
    """
    sid = str(study_id or screening_id or "").upper().strip()
    if sid.startswith("ABCG-") or sid.startswith("SCREENED-"):
        parts = sid.split("-")
        if len(parts) >= 4 and parts[1].isdigit() and parts[2].isdigit() and parts[3].isdigit():
            rec = lookup_jurisdiction_by_id(int(parts[1]), int(parts[2]), int(parts[3]))
            if rec:
                return rec["state"], rec["district"], rec["tb_unit"]
        elif "ABCG-" in sid and len(parts) >= 3:
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
    elif pin_str.startswith("75"):
        return "Odisha", "Cuttack", "Urban_TU"
    elif pin_str.startswith("99"):
        return "Training State", "Training District", "Training TBU"

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


def generate_next_study_id(state_id, district_id, tbu_id):
    """
    Generates the next sequential Study ID for an enrolled participant at a specific TB Unit:
    Format: ABCG-{state_id}-{district_id}-{tbu_id}-{serial:06d}
    e.g. ABCG-1-3-4-000001
    """
    from questions.models import Participant, TptIndividual, IneligibleIndividual
    prefix = f"ABCG-{state_id}-{district_id}-{tbu_id}-"
    
    p_ids = list(Participant.objects.filter(study_id__startswith=prefix).values_list("study_id", flat=True))
    tpt_ids = list(TptIndividual.objects.filter(study_id__startswith=prefix).values_list("study_id", flat=True))
    inel_ids = list(IneligibleIndividual.objects.filter(study_id__startswith=prefix).values_list("study_id", flat=True))
    
    all_matching = p_ids + tpt_ids + inel_ids
    max_serial = 0
    for sid in all_matching:
        try:
            val = int(sid.split("-")[-1])
            if val > max_serial:
                max_serial = val
        except (ValueError, IndexError):
            pass
            
    next_serial = max_serial + 1
    while True:
        candidate = f"{prefix}{next_serial:06d}"
        if not (Participant.objects.filter(study_id=candidate).exists() or
                TptIndividual.objects.filter(study_id=candidate).exists() or
                IneligibleIndividual.objects.filter(study_id=candidate).exists()):
            return candidate
        next_serial += 1


def generate_next_screening_id(state_id, district_id, tbu_id):
    """
    Generates the next sequential Screening ID for any screened individual at a specific TB Unit:
    Format: SCREENED-{state_id}-{district_id}-{tbu_id}-{serial:06d}
    e.g. SCREENED-1-3-4-000001
    """
    from questions.models import Participant, TptIndividual, IneligibleIndividual
    prefix = f"SCREENED-{state_id}-{district_id}-{tbu_id}-"
    
    p_ids = list(Participant.objects.filter(screening_id__startswith=prefix).values_list("screening_id", flat=True))
    tpt_ids = list(TptIndividual.objects.filter(screening_id__startswith=prefix).values_list("screening_id", flat=True))
    inel_ids = list(IneligibleIndividual.objects.filter(screening_id__startswith=prefix).values_list("screening_id", flat=True))
    
    all_matching = p_ids + tpt_ids + inel_ids
    max_serial = 0
    for sid in all_matching:
        try:
            val = int(sid.split("-")[-1])
            if val > max_serial:
                max_serial = val
        except (ValueError, IndexError):
            pass
            
    next_serial = max_serial + 1
    while True:
        candidate = f"{prefix}{next_serial:06d}"
        if not (Participant.objects.filter(screening_id=candidate).exists() or
                TptIndividual.objects.filter(screening_id=candidate).exists() or
                IneligibleIndividual.objects.filter(screening_id=candidate).exists() or
                IneligibleIndividual.objects.filter(study_id=candidate).exists()):
            return candidate
        next_serial += 1
