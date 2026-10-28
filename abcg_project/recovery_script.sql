-- ==============================================================================
-- aBCG PARTICIPANT LOCATION RECOVERY TRANSACTION SCRIPT
-- ==============================================================================
-- Purpose: Safely and reversibly restore participant State, District, and TB Unit
--          corrupted by questionnaire update bug (overwritten with GLOBAL scope).
--
-- Execution Guidelines:
-- 1. Create a physical database backup prior to running:
--      copy db.sqlite3 db.sqlite3.pre_recovery_backup
-- 2. Run inside an explicit database transaction.
-- 3. Only records with explicit high-confidence verification and approved IDs are updated.
-- 4. Review change count before issuing COMMIT.
-- ==============================================================================

BEGIN TRANSACTION;

-- Step 1: Pre-Condition Check
-- Verify target records currently hold generic/corrupted values before altering
-- Example verification query:
-- SELECT id, study_id, state, district, tb_unit FROM questions_participant
-- WHERE state = 'GLOBAL' OR district = 'ALL DISTRICTS' OR tb_unit = 'ALL TB UNITS';

-- Step 2: Parameterized / Verified Target Updates (Template)
-- Ensure updates are bound strictly to exact Primary Keys (id) and verified Study IDs

/*
UPDATE questions_participant
SET state = 'Tamil Nadu',
    district = 'Tiruvallur',
    tb_unit = 'Tiruvallur TU'
WHERE id = :target_id 
  AND study_id = :target_study_id
  AND (state = 'GLOBAL' OR district = 'ALL DISTRICTS' OR tb_unit = 'ALL TB UNITS');
*/

-- Step 3: Insert Audit Trail Entry
/*
INSERT INTO questions_auditlog (actor_id, action, timestamp, target_user_id)
VALUES (
    1, 
    'RECOVERY: Restored State, District, TB Unit for participant ' || :target_study_id,
    DATETIME('now'),
    NULL
);
*/

-- Step 4: Verification Check
-- Ensure no records in target batch still retain generic location values
-- SELECT COUNT(*) FROM questions_participant 
-- WHERE id IN (:approved_id_list) 
--   AND (state = 'GLOBAL' OR district = 'ALL DISTRICTS' OR tb_unit = 'ALL TB UNITS');
-- Expected result: 0

-- If all checks match expected verification counts:
COMMIT;

-- If any discrepancy is observed:
-- ROLLBACK;
