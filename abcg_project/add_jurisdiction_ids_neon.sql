-- ============================================================================
-- aBCG VE Study: Complete Jurisdiction Cleanup & Seeding Script
-- Target: Neon PostgreSQL
-- Resolves: Fills ALL rows with valid IDs, removes duplicates/NULLs, deletes Karnataka
-- ============================================================================
BEGIN;

-- 1. Ensure columns and indexes exist on all relevant tables
ALTER TABLE questions_studysite ADD COLUMN IF NOT EXISTS state_id INTEGER;
ALTER TABLE questions_studysite ADD COLUMN IF NOT EXISTS district_id INTEGER;
ALTER TABLE questions_studysite ADD COLUMN IF NOT EXISTS tbu_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_studysite_state_id ON questions_studysite(state_id);
CREATE INDEX IF NOT EXISTS idx_studysite_district_id ON questions_studysite(district_id);
CREATE INDEX IF NOT EXISTS idx_studysite_tbu_id ON questions_studysite(tbu_id);

ALTER TABLE questions_participant ADD COLUMN IF NOT EXISTS state_id INTEGER;
ALTER TABLE questions_participant ADD COLUMN IF NOT EXISTS district_id INTEGER;
ALTER TABLE questions_participant ADD COLUMN IF NOT EXISTS tbu_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_participant_state_id ON questions_participant(state_id);
CREATE INDEX IF NOT EXISTS idx_participant_district_id ON questions_participant(district_id);
CREATE INDEX IF NOT EXISTS idx_participant_tbu_id ON questions_participant(tbu_id);

ALTER TABLE questions_tptindividual ADD COLUMN IF NOT EXISTS state_id INTEGER;
ALTER TABLE questions_tptindividual ADD COLUMN IF NOT EXISTS district_id INTEGER;
ALTER TABLE questions_tptindividual ADD COLUMN IF NOT EXISTS tbu_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_tpt_state_id ON questions_tptindividual(state_id);
CREATE INDEX IF NOT EXISTS idx_tpt_district_id ON questions_tptindividual(district_id);
CREATE INDEX IF NOT EXISTS idx_tpt_tbu_id ON questions_tptindividual(tbu_id);

ALTER TABLE questions_ineligibleindividual ADD COLUMN IF NOT EXISTS state_id INTEGER;
ALTER TABLE questions_ineligibleindividual ADD COLUMN IF NOT EXISTS district_id INTEGER;
ALTER TABLE questions_ineligibleindividual ADD COLUMN IF NOT EXISTS tbu_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_ineligible_state_id ON questions_ineligibleindividual(state_id);
CREATE INDEX IF NOT EXISTS idx_ineligible_district_id ON questions_ineligibleindividual(district_id);
CREATE INDEX IF NOT EXISTS idx_ineligible_tbu_id ON questions_ineligibleindividual(tbu_id);

ALTER TABLE questions_userprofile ADD COLUMN IF NOT EXISTS state_id INTEGER;
ALTER TABLE questions_userprofile ADD COLUMN IF NOT EXISTS district_id INTEGER;
ALTER TABLE questions_userprofile ADD COLUMN IF NOT EXISTS tbu_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_userprofile_state_id ON questions_userprofile(state_id);
CREATE INDEX IF NOT EXISTS idx_userprofile_district_id ON questions_userprofile(district_id);
CREATE INDEX IF NOT EXISTS idx_userprofile_tbu_id ON questions_userprofile(tbu_id);

-- 2. Delete Karnataka records (as per study requirement: Karnataka is removed)
DELETE FROM questions_studysite WHERE LOWER(state) = 'karnataka';

-- 3. Upsert / synchronize all 106 authoritative study sites
-- First remove any duplicate uppercase variations that would collide with canonical names:
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Paderu DTC') AND tb_unit != 'Paderu DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Chittoor DTC') AND tb_unit != 'Chittoor_DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('GunturWest') AND tb_unit != 'GunturWest';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Guntur DTC') AND tb_unit != 'Guntur DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Mangalagiri') AND tb_unit != 'Mangalagiri';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Tenali') AND tb_unit != 'Tenali';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('DTC Machilipatnam') AND tb_unit != 'DTC Machilipatnam';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Narasaraopet') AND tb_unit != 'Narasaraopet';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Nellore 1') AND tb_unit != 'Nellore-1';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Dharmavaram') AND tb_unit != 'Dharmavaram';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Visakhapatnam DTC') AND tb_unit != 'Visakhapatnam_DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('KGH') AND tb_unit != 'KGH';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Vizianagaram DTC') AND tb_unit != 'Vizianagaram_DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Kadapa Rural') AND tb_unit != 'Kadapa Rural';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Ambala') AND tb_unit != 'Ambala';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Ambalacantt') AND tb_unit != 'Ambalacantt';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Tosham') AND tb_unit != 'Tosham';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Bhiwani DTC') AND tb_unit != 'Bhiwani_DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('DTC Hisar') AND tb_unit != 'DTC Hisar';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Barwala') AND tb_unit != 'Barwala';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Jhajjar') AND tb_unit != 'Jhajjar';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Bahadurgarh') AND tb_unit != 'Bahadurgarh';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('TU DTC Jind') AND tb_unit != 'TU DTC Jind';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('TU 1 Kaithal') AND tb_unit != 'TU-1 Kaithal';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('GH Mandikhera') AND tb_unit != 'GH Mandikhera';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('CHC Nuh') AND tb_unit != 'CHC Nuh';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('GH Rohtak') AND tb_unit != 'GH Rohtak';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('DTC Rohtak') AND tb_unit != 'DTC_Rohtak';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('PGIMS Rohtak') AND tb_unit != 'PGIMS Rohtak';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('DTC Sirsa') AND tb_unit != 'DTC_Sirsa';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Ganaur') AND tb_unit != 'Ganaur';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Mudlana') AND tb_unit != 'Mudlana';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Gohana TU') AND tb_unit != 'Gohana TU';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Markand') AND tb_unit != 'Markand';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Rajpur') AND tb_unit != 'Rajpur';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Dhagera') AND tb_unit != 'Dhagera';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Tiara') AND tb_unit != 'Tiara';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Nurpur') AND tb_unit != 'Nurpur';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('TU Basdehra') AND tb_unit != 'TU-Basdehra';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Ratti') AND tb_unit != 'Ratti';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Agar') AND tb_unit != 'Agar';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Mungaoli') AND tb_unit != 'Mungaoli';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Barwani') AND tb_unit != 'Barwani';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Gohad') AND tb_unit != 'Gohad';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('DH Jaiprakash Hospital') AND tb_unit != 'DH Jaiprakash Hospital';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Jawaharlal Nehru Hospital (Gas Rahat)') AND tb_unit != 'Jawaharlal Nehru Hospital (Gas Rahat)';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('AIIMS Hospital') AND tb_unit != 'AIIMS Hospital';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Civil Hospital Bairagarh') AND tb_unit != 'Civil Hospital Bairagarh';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('T B Hospital') AND tb_unit != 'T. B. Hospital';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Junnardeo') AND tb_unit != 'Junnardeo';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('DTC Chhindwara') AND tb_unit != 'DTC Chhindwara';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Damoh DTC') AND tb_unit != 'Damoh_DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Dewas DTC') AND tb_unit != 'Dewas DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('CH Gwalior') AND tb_unit != 'CH Gwalior';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Dabra') AND tb_unit != 'Dabra';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Morar') AND tb_unit != 'Morar';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Medical College') AND tb_unit != 'Medical College';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('DTC Gwalior') AND tb_unit != 'DTC-Gwalior';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Harda') AND tb_unit != 'Harda';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Pipariya') AND tb_unit != 'Pipariya';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Hoshangabad DTC') AND tb_unit != 'Hoshangabad_DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Rithi') AND tb_unit != 'Rithi';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Umaria Pan') AND tb_unit != 'Umaria Pan';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('V Garh') AND tb_unit != 'V_Garh';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Khargone DTC') AND tb_unit != 'Khargone DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('DTC Mandla') AND tb_unit != 'DTC-Mandla';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('TU Kailaras') AND tb_unit != 'TU-Kailaras';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('TU Sabalgarh') AND tb_unit != 'TU-Sabalgarh';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('TU Porsa') AND tb_unit != 'TU Porsa';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('TU Joura') AND tb_unit != 'TU-Joura';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('TU Morena DTC') AND tb_unit != 'TU-Morena DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Narsinghpur DTC') AND tb_unit != 'Narsinghpur_DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Raisen DTC') AND tb_unit != 'Raisen DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Jaora') AND tb_unit != 'Jaora';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Majhgawan') AND tb_unit != 'Majhgawan';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Satna') AND tb_unit != 'Satna';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Maihar') AND tb_unit != 'Maihar';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('DTC Singrauli') AND tb_unit != 'DTC Singrauli';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Tikamgarh DTC') AND tb_unit != 'Tikamgarh_DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Umaria DTC') AND tb_unit != 'Umaria_DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Amravati') AND tb_unit != 'Amravati';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Bai Rukminibai Hospital TU') AND tb_unit != 'Bai Rukminibai Hospital TU';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Latur Urban') AND tb_unit != 'Latur Urban';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Squatters Colony Health Post') AND tb_unit != 'Squatters Colony Health Post';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('VN Desai Hospital') AND tb_unit != 'V.N. Desai Hospital';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Maa Hospital') AND tb_unit != 'Maa Hospital';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Urban Health Centre, Dharavi') AND tb_unit != 'Urban Health Centre, Dharavi';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('KB Bhabha Hospital') AND tb_unit != 'K.B. Bhabha Hospital';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('GMC') AND tb_unit != 'GMC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('IGGMC') AND tb_unit != 'IGGMC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('YCM Zone TB Unit') AND tb_unit != 'YCM Zone TB Unit';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Balangir DTC') AND tb_unit != 'Balangir DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Urban TU') AND tb_unit != 'Urban_TU';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Dhenkanal DTC') AND tb_unit != 'Dhenkanal_DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Jharsuguda') AND tb_unit != 'Jharsuguda';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('DTC Kalahandi') AND tb_unit != 'DTC Kalahandi';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Baripada DTC') AND tb_unit != 'Baripada_DTC';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Udala') AND tb_unit != 'Udala';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('DTC Rayagada') AND tb_unit != 'DTC Rayagada';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Sadar Sundargarh') AND tb_unit != 'Sadar Sundargarh';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Chennai Central TU') AND tb_unit != 'Chennai Central TU';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('TU1') AND tb_unit != 'TU1';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('TU3') AND tb_unit != 'TU3';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('TU2') AND tb_unit != 'TU2';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Tiruvallur TU') AND tb_unit != 'Tiruvallur TU';
DELETE FROM questions_studysite WHERE LOWER(REPLACE(REPLACE(REPLACE(tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER('Training TBU') AND tb_unit != 'Training TBU';

-- Insert / Update the 106 Canonical Study Sites:
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 1, 'Alluri Sitharama Raju', 1, 'Paderu DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 2, 'Chittoor', 2, 'Chittoor_DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 3, 'Guntur', 3, 'GunturWest', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 3, 'Guntur', 4, 'Guntur DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 3, 'Guntur', 5, 'Mangalagiri', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 3, 'Guntur', 6, 'Tenali', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 4, 'Krishna', 7, 'DTC Machilipatnam', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 5, 'Palnadu', 8, 'Narasaraopet', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 6, 'Sri Potti Sriramulu Nellore', 9, 'Nellore-1', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 7, 'Sri Sathya Sai', 10, 'Dharmavaram', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 8, 'Visakhapatnam', 11, 'Visakhapatnam_DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 8, 'Visakhapatnam', 12, 'KGH', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 9, 'Vizianagaram', 13, 'Vizianagaram_DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (1, 'Andhra Pradesh', 10, 'Y.S.R', 14, 'Kadapa Rural', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 11, 'Ambala', 15, 'Ambala', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 11, 'Ambala', 16, 'Ambalacantt', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 12, 'Bhiwani', 17, 'Tosham', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 12, 'Bhiwani', 18, 'Bhiwani_DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 13, 'Hisar', 19, 'DTC Hisar', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 13, 'Hisar', 20, 'Barwala', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 14, 'Jhajjar', 21, 'Jhajjar', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 14, 'Jhajjar', 22, 'Bahadurgarh', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 15, 'Jind', 23, 'TU DTC Jind', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 16, 'Kaithal', 24, 'TU-1 Kaithal', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 17, 'Mewat', 25, 'GH Mandikhera', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 17, 'Mewat', 26, 'CHC Nuh', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 18, 'Rohtak', 27, 'GH Rohtak', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 18, 'Rohtak', 28, 'DTC_Rohtak', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 18, 'Rohtak', 29, 'PGIMS Rohtak', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 19, 'Sirsa', 30, 'DTC_Sirsa', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 20, 'Sonipat', 31, 'Ganaur', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 20, 'Sonipat', 32, 'Mudlana', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (2, 'Haryana', 20, 'Sonipat', 33, 'Gohana TU', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (3, 'Himachal Pradesh', 21, 'Bilaspur-HP', 34, 'Markand', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (3, 'Himachal Pradesh', 22, 'Sirmaur', 35, 'Rajpur', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (3, 'Himachal Pradesh', 22, 'Sirmaur', 36, 'Dhagera', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (3, 'Himachal Pradesh', 23, 'Kangra', 37, 'Tiara', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (3, 'Himachal Pradesh', 23, 'Kangra', 38, 'Nurpur', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (3, 'Himachal Pradesh', 24, 'Una-HP', 39, 'TU-Basdehra', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (3, 'Himachal Pradesh', 25, 'Mandi', 40, 'Ratti', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 26, 'Agar Malwa', 41, 'Agar', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 27, 'Ashoknagar', 42, 'Mungaoli', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 28, 'Barwani', 43, 'Barwani', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 29, 'Bhind', 44, 'Gohad', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 30, 'Bhopal', 45, 'DH Jaiprakash Hospital', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 30, 'Bhopal', 46, 'Jawaharlal Nehru Hospital (Gas Rahat)', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 30, 'Bhopal', 47, 'AIIMS Hospital', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 30, 'Bhopal', 48, 'Civil Hospital Bairagarh', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 30, 'Bhopal', 49, 'T. B. Hospital', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 31, 'Chhindwara', 50, 'Junnardeo', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 31, 'Chhindwara', 51, 'DTC Chhindwara', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 32, 'Damoh', 52, 'Damoh_DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 33, 'Dewas', 53, 'Dewas DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 34, 'Gwalior', 54, 'CH Gwalior', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 34, 'Gwalior', 55, 'Dabra', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 34, 'Gwalior', 56, 'Morar', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 34, 'Gwalior', 57, 'Medical College', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 34, 'Gwalior', 58, 'DTC-Gwalior', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 35, 'Harda', 59, 'Harda', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 36, 'Hoshangabad', 60, 'Pipariya', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 36, 'Hoshangabad', 61, 'Hoshangabad_DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 37, 'Katni', 62, 'Rithi', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 37, 'Katni', 63, 'Umaria Pan', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 37, 'Katni', 64, 'V_Garh', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 38, 'Khargone', 65, 'Khargone DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 39, 'Mandla', 66, 'DTC-Mandla', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 40, 'Morena', 67, 'TU-Kailaras', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 40, 'Morena', 68, 'TU-Sabalgarh', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 40, 'Morena', 69, 'TU Porsa', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 40, 'Morena', 70, 'TU-Joura', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 40, 'Morena', 71, 'TU-Morena DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 41, 'Narsinghpur', 72, 'Narsinghpur_DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 42, 'Raisen', 73, 'Raisen DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 43, 'Ratlam', 74, 'Jaora', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 44, 'Satna', 75, 'Majhgawan', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 44, 'Satna', 76, 'Satna', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 44, 'Satna', 77, 'Maihar', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 45, 'Singrauli', 78, 'DTC Singrauli', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 46, 'Tikamgarh', 79, 'Tikamgarh_DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (4, 'Madhya Pradesh', 47, 'Umaria', 80, 'Umaria_DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (5, 'Maharashtra', 48, 'Amravati', 81, 'Amravati', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (5, 'Maharashtra', 49, 'Kalyan Dombivli MC', 82, 'Bai Rukminibai Hospital TU', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (5, 'Maharashtra', 50, 'Latur', 83, 'Latur Urban', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (5, 'Maharashtra', 51, 'Mumbai_Andheri East', 84, 'Squatters Colony Health Post', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (5, 'Maharashtra', 52, 'Mumbai_Bandra East', 85, 'V.N. Desai Hospital', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (5, 'Maharashtra', 53, 'Mumbai_Chembur', 86, 'Maa Hospital', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (5, 'Maharashtra', 54, 'Mumbai_Dadar', 87, 'Urban Health Centre, Dharavi', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (5, 'Maharashtra', 55, 'Mumbai_Kurla', 88, 'K.B. Bhabha Hospital', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (5, 'Maharashtra', 56, 'Nagpur MC', 89, 'GMC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (5, 'Maharashtra', 56, 'Nagpur MC', 90, 'IGGMC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (5, 'Maharashtra', 57, 'Pimpri Chinchwad MC', 91, 'YCM Zone TB Unit', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (6, 'Odisha', 58, 'Balangir', 92, 'Balangir DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (6, 'Odisha', 59, 'Cuttack', 93, 'Urban_TU', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (6, 'Odisha', 60, 'Dhenkanal', 94, 'Dhenkanal_DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (6, 'Odisha', 61, 'Jharsuguda', 95, 'Jharsuguda', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (6, 'Odisha', 62, 'Kalahandi', 96, 'DTC Kalahandi', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (6, 'Odisha', 63, 'Mayurbhanj', 97, 'Baripada_DTC', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (6, 'Odisha', 63, 'Mayurbhanj', 98, 'Udala', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (6, 'Odisha', 64, 'Rayagada', 99, 'DTC Rayagada', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (6, 'Odisha', 65, 'Sundargarh', 100, 'Sadar Sundargarh', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (7, 'Tamil Nadu', 66, 'Chennai', 101, 'Chennai Central TU', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (7, 'Tamil Nadu', 66, 'Chennai', 102, 'TU1', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (7, 'Tamil Nadu', 67, 'Coimbatore', 103, 'TU3', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (7, 'Tamil Nadu', 68, 'Madurai', 104, 'TU2', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (7, 'Tamil Nadu', 69, 'Tiruvallur', 105, 'Tiruvallur TU', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();
INSERT INTO questions_studysite (state_id, state, district_id, district, tbu_id, tb_unit, launch_date, is_active, created_at, updated_at)
VALUES (99, 'Training State', 999, 'Training District', 999, 'Training TBU', CURRENT_DATE, TRUE, NOW(), NOW())
ON CONFLICT (tb_unit) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    state = EXCLUDED.state,
    district_id = EXCLUDED.district_id,
    district = EXCLUDED.district,
    tbu_id = EXCLUDED.tbu_id,
    is_active = TRUE,
    updated_at = NOW();

-- 4. Delete any remaining unmapped or test sites that have NULL state_id
DELETE FROM questions_studysite WHERE state_id IS NULL;

-- 5. Standardize & Backfill questions_participant (matches case-insensitively)
UPDATE questions_participant p
SET state_id = s.state_id, district_id = s.district_id, tbu_id = s.tbu_id, tb_unit = s.tb_unit, state = s.state, district = s.district
FROM questions_studysite s
WHERE LOWER(REPLACE(REPLACE(REPLACE(p.tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER(REPLACE(REPLACE(REPLACE(s.tb_unit, '_', ' '), '-', ' '), '.', ''));

-- 6. Standardize & Backfill questions_tptindividual
UPDATE questions_tptindividual t
SET state_id = s.state_id, district_id = s.district_id, tbu_id = s.tbu_id, tb_unit = s.tb_unit, state = s.state, district = s.district
FROM questions_studysite s
WHERE LOWER(REPLACE(REPLACE(REPLACE(t.tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER(REPLACE(REPLACE(REPLACE(s.tb_unit, '_', ' '), '-', ' '), '.', ''));

-- 7. Standardize & Backfill questions_ineligibleindividual
UPDATE questions_ineligibleindividual i
SET state_id = s.state_id, district_id = s.district_id, tbu_id = s.tbu_id, tb_unit = s.tb_unit, state = s.state, district = s.district
FROM questions_studysite s
WHERE LOWER(REPLACE(REPLACE(REPLACE(i.tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER(REPLACE(REPLACE(REPLACE(s.tb_unit, '_', ' '), '-', ' '), '.', ''));

-- 8. Standardize & Backfill questions_userprofile
UPDATE questions_userprofile u
SET state_id = s.state_id, district_id = s.district_id, tbu_id = s.tbu_id, tb_unit = s.tb_unit, state = s.state, district = s.district
FROM questions_studysite s
WHERE LOWER(REPLACE(REPLACE(REPLACE(u.tb_unit, '_', ' '), '-', ' '), '.', '')) = LOWER(REPLACE(REPLACE(REPLACE(s.tb_unit, '_', ' '), '-', ' '), '.', ''));

COMMIT;

-- Verification Queries (Run these to confirm zero NULLs):
-- SELECT COUNT(*) AS total_study_sites FROM questions_studysite;
-- SELECT COUNT(*) AS null_rows FROM questions_studysite WHERE state_id IS NULL OR district_id IS NULL OR tbu_id IS NULL;