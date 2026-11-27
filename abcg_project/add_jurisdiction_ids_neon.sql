-- ============================================================================
-- aBCG VE Study: Add state_id, district_id, tbu_id & Seed Jurisdiction Master
-- Target: Neon PostgreSQL (or Self-Hosted PostgreSQL)
-- Run this script in the Neon SQL Editor or via psql
-- ============================================================================
BEGIN;

-- 1. Add columns to questions_studysite
ALTER TABLE questions_studysite ADD COLUMN IF NOT EXISTS state_id INTEGER;
ALTER TABLE questions_studysite ADD COLUMN IF NOT EXISTS district_id INTEGER;
ALTER TABLE questions_studysite ADD COLUMN IF NOT EXISTS tbu_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_studysite_state_id ON questions_studysite(state_id);
CREATE INDEX IF NOT EXISTS idx_studysite_district_id ON questions_studysite(district_id);
CREATE INDEX IF NOT EXISTS idx_studysite_tbu_id ON questions_studysite(tbu_id);

-- 2. Add columns to questions_participant
ALTER TABLE questions_participant ADD COLUMN IF NOT EXISTS state_id INTEGER;
ALTER TABLE questions_participant ADD COLUMN IF NOT EXISTS district_id INTEGER;
ALTER TABLE questions_participant ADD COLUMN IF NOT EXISTS tbu_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_participant_state_id ON questions_participant(state_id);
CREATE INDEX IF NOT EXISTS idx_participant_district_id ON questions_participant(district_id);
CREATE INDEX IF NOT EXISTS idx_participant_tbu_id ON questions_participant(tbu_id);

-- 3. Add columns to questions_tptindividual
ALTER TABLE questions_tptindividual ADD COLUMN IF NOT EXISTS state_id INTEGER;
ALTER TABLE questions_tptindividual ADD COLUMN IF NOT EXISTS district_id INTEGER;
ALTER TABLE questions_tptindividual ADD COLUMN IF NOT EXISTS tbu_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_tpt_state_id ON questions_tptindividual(state_id);
CREATE INDEX IF NOT EXISTS idx_tpt_district_id ON questions_tptindividual(district_id);
CREATE INDEX IF NOT EXISTS idx_tpt_tbu_id ON questions_tptindividual(tbu_id);

-- 4. Add columns to questions_ineligibleindividual
ALTER TABLE questions_ineligibleindividual ADD COLUMN IF NOT EXISTS state_id INTEGER;
ALTER TABLE questions_ineligibleindividual ADD COLUMN IF NOT EXISTS district_id INTEGER;
ALTER TABLE questions_ineligibleindividual ADD COLUMN IF NOT EXISTS tbu_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_ineligible_state_id ON questions_ineligibleindividual(state_id);
CREATE INDEX IF NOT EXISTS idx_ineligible_district_id ON questions_ineligibleindividual(district_id);
CREATE INDEX IF NOT EXISTS idx_ineligible_tbu_id ON questions_ineligibleindividual(tbu_id);

-- 5. Add columns to questions_userprofile
ALTER TABLE questions_userprofile ADD COLUMN IF NOT EXISTS state_id INTEGER;
ALTER TABLE questions_userprofile ADD COLUMN IF NOT EXISTS district_id INTEGER;
ALTER TABLE questions_userprofile ADD COLUMN IF NOT EXISTS tbu_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_userprofile_state_id ON questions_userprofile(state_id);
CREATE INDEX IF NOT EXISTS idx_userprofile_district_id ON questions_userprofile(district_id);
CREATE INDEX IF NOT EXISTS idx_userprofile_tbu_id ON questions_userprofile(tbu_id);

-- 6. Deactivate legacy Karnataka sites if present
UPDATE questions_studysite SET is_active = FALSE WHERE LOWER(state) = 'karnataka';

-- 7. Upsert Master Study Sites (106 sites)
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

-- 8. Backfill questions_participant from questions_studysite
UPDATE questions_participant p
SET state_id = s.state_id, district_id = s.district_id, tbu_id = s.tbu_id
FROM questions_studysite s
WHERE LOWER(REPLACE(REPLACE(p.tb_unit, '_', ' '), '-', ' ')) = LOWER(REPLACE(REPLACE(s.tb_unit, '_', ' '), '-', ' '));

-- 9. Backfill questions_tptindividual from questions_studysite
UPDATE questions_tptindividual t
SET state_id = s.state_id, district_id = s.district_id, tbu_id = s.tbu_id
FROM questions_studysite s
WHERE LOWER(REPLACE(REPLACE(t.tb_unit, '_', ' '), '-', ' ')) = LOWER(REPLACE(REPLACE(s.tb_unit, '_', ' '), '-', ' '));

-- 10. Backfill questions_ineligibleindividual from questions_studysite
UPDATE questions_ineligibleindividual i
SET state_id = s.state_id, district_id = s.district_id, tbu_id = s.tbu_id
FROM questions_studysite s
WHERE LOWER(REPLACE(REPLACE(i.tb_unit, '_', ' '), '-', ' ')) = LOWER(REPLACE(REPLACE(s.tb_unit, '_', ' '), '-', ' '));

-- 11. Backfill questions_userprofile from questions_studysite
UPDATE questions_userprofile u
SET state_id = s.state_id, district_id = s.district_id, tbu_id = s.tbu_id
FROM questions_studysite s
WHERE LOWER(REPLACE(REPLACE(u.tb_unit, '_', ' '), '-', ' ')) = LOWER(REPLACE(REPLACE(s.tb_unit, '_', ' '), '-', ' '));

COMMIT;
-- ============================================================================
-- Execution Complete: All columns added, 106 study sites seeded, records backfilled.
-- ============================================================================