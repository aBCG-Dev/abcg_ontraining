-- ==============================================================================
-- aBCG NEON POSTGRESQL PARTICIPANT LOCATION AUDIT & RECOVERY SCRIPT
-- ==============================================================================
-- Target Records Verified:
-- 1. ABCG-AN-NEL-% (Facility: ACSR Medical college)
--    -> State: 'Andhra Pradesh', District: 'Sri Potti Sriramulu Nellore', TB Unit: 'NELLORE-1'
-- 2. ABCG-AN-GUN-% (Facility: Guntur DTC)
--    -> State: 'Andhra Pradesh', District: 'Guntur', TB Unit: 'Guntur DTC'
-- 3. ABCG-OD-BAR-% (Facility: District TB Centre Mayurbhanj)
--    -> State: 'Odisha', District: 'Mayurbhanj', TB Unit: 'Baripada_DTC'
-- 4. ABCG-OD-URB-% (Facility: SCB MCH)
--    -> State: 'Odisha', District: 'Cuttack', TB Unit: 'Urban_TU'
-- 5. ABCG-TN-TIR-% (Facility: Avadi PHC / Tiruvallur)
--    -> State: 'Tamil Nadu', District: 'Tiruvallur', TB Unit: 'Tiruvallur TU'
-- 6. ABCG-KA-BEN-% (Facility: Bengaluru)
--    -> State: 'Karnataka', District: 'Bengaluru', TB Unit: 'Bengaluru TU'
-- ==============================================================================

BEGIN;

-- 1. Andhra Pradesh - Nellore (ACSR Medical college)
UPDATE questions_participant
SET state = 'Andhra Pradesh',
    district = 'Sri Potti Sriramulu Nellore',
    tb_unit = 'NELLORE-1'
WHERE (study_id LIKE 'ABCG-AN-NEL-%' OR facility = 'ACSR Medical college')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_tptindividual
SET state = 'Andhra Pradesh',
    district = 'Sri Potti Sriramulu Nellore',
    tb_unit = 'NELLORE-1'
WHERE (study_id LIKE 'ABCG-AN-NEL-%' OR facility = 'ACSR Medical college')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_ineligibleindividual
SET state = 'Andhra Pradesh',
    district = 'Sri Potti Sriramulu Nellore',
    tb_unit = 'NELLORE-1'
WHERE (study_id LIKE 'ABCG-AN-NEL-%' OR facility = 'ACSR Medical college')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));


-- 2. Andhra Pradesh - Guntur (Guntur DTC)
UPDATE questions_participant
SET state = 'Andhra Pradesh',
    district = 'Guntur',
    tb_unit = 'Guntur DTC'
WHERE (study_id LIKE 'ABCG-AN-GUN-%' OR facility = 'Guntur DTC')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_tptindividual
SET state = 'Andhra Pradesh',
    district = 'Guntur',
    tb_unit = 'Guntur DTC'
WHERE (study_id LIKE 'ABCG-AN-GUN-%' OR facility = 'Guntur DTC')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_ineligibleindividual
SET state = 'Andhra Pradesh',
    district = 'Guntur',
    tb_unit = 'Guntur DTC'
WHERE (study_id LIKE 'ABCG-AN-GUN-%' OR facility = 'Guntur DTC')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));


-- 3. Odisha - Mayurbhanj (District TB Centre Mayurbhanj / Baripada_DTC)
UPDATE questions_participant
SET state = 'Odisha',
    district = 'Mayurbhanj',
    tb_unit = 'Baripada_DTC'
WHERE (study_id LIKE 'ABCG-OD-BAR-%' OR facility = 'District TB Centre Mayurbhanj')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_tptindividual
SET state = 'Odisha',
    district = 'Mayurbhanj',
    tb_unit = 'Baripada_DTC'
WHERE (study_id LIKE 'ABCG-OD-BAR-%' OR facility = 'District TB Centre Mayurbhanj')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_ineligibleindividual
SET state = 'Odisha',
    district = 'Mayurbhanj',
    tb_unit = 'Baripada_DTC'
WHERE (study_id LIKE 'ABCG-OD-BAR-%' OR facility = 'District TB Centre Mayurbhanj')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));


-- 4. Odisha - Cuttack (SCB MCH / Urban_TU)
UPDATE questions_participant
SET state = 'Odisha',
    district = 'Cuttack',
    tb_unit = 'Urban_TU'
WHERE (study_id LIKE 'ABCG-OD-URB-%' OR facility = 'SCB MCH')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_tptindividual
SET state = 'Odisha',
    district = 'Cuttack',
    tb_unit = 'Urban_TU'
WHERE (study_id LIKE 'ABCG-OD-URB-%' OR facility = 'SCB MCH')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_ineligibleindividual
SET state = 'Odisha',
    district = 'Cuttack',
    tb_unit = 'Urban_TU'
WHERE (study_id LIKE 'ABCG-OD-URB-%' OR facility = 'SCB MCH')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));


-- 5. Tamil Nadu - Tiruvallur (Avadi PHC / Tiruvallur TU)
UPDATE questions_participant
SET state = 'Tamil Nadu',
    district = 'Tiruvallur',
    tb_unit = 'Tiruvallur TU'
WHERE (study_id LIKE 'ABCG-TN-TIR-%' OR facility ILIKE '%Avadi%' OR public_phi ILIKE '%Avadi%')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_tptindividual
SET state = 'Tamil Nadu',
    district = 'Tiruvallur',
    tb_unit = 'Tiruvallur TU'
WHERE (study_id LIKE 'ABCG-TN-TIR-%' OR facility ILIKE '%Avadi%' OR public_phi ILIKE '%Avadi%')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_ineligibleindividual
SET state = 'Tamil Nadu',
    district = 'Tiruvallur',
    tb_unit = 'Tiruvallur TU'
WHERE (study_id LIKE 'ABCG-TN-TIR-%' OR facility ILIKE '%Avadi%' OR public_phi ILIKE '%Avadi%')
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));


-- 6. Karnataka - Bengaluru (Bengaluru TU)
UPDATE questions_participant
SET state = 'Karnataka',
    district = 'Bengaluru',
    tb_unit = 'Bengaluru TU'
WHERE study_id LIKE 'ABCG-KA-BEN-%'
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_tptindividual
SET state = 'Karnataka',
    district = 'Bengaluru',
    tb_unit = 'Bengaluru TU'
WHERE study_id LIKE 'ABCG-KA-BEN-%'
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));

UPDATE questions_ineligibleindividual
SET state = 'Karnataka',
    district = 'Bengaluru',
    tb_unit = 'Bengaluru TU'
WHERE study_id LIKE 'ABCG-KA-BEN-%'
  AND (UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL'));


-- ------------------------------------------------------------------------------
-- VERIFICATION CHECK
-- ------------------------------------------------------------------------------
-- Expected remaining count: 0
SELECT COUNT(*) AS remaining_generic_count
FROM (
    SELECT id FROM questions_participant WHERE UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL')
    UNION ALL
    SELECT id FROM questions_tptindividual WHERE UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL')
    UNION ALL
    SELECT id FROM questions_ineligibleindividual WHERE UPPER(state) = 'GLOBAL' OR UPPER(district) = 'ALL DISTRICTS' OR UPPER(tb_unit) IN ('ALL TB UNITS', 'GLOBAL')
) AS remaining;

-- Issue COMMIT to permanently apply all updates:
COMMIT;
