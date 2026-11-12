-- Joint group permutation test.
-- ORM metadata creates the tables. This file documents the added structure only;
-- no production migration runner is claimed.

-- traverse_groups(name UNIQUE, protocol, permutations, seed, created_by, created_at)
--   Pre-registered traverse group with its own B and seed.

-- traverse_group_members(group_id, study_id, plan_id, ordinal, label,
--   study_snapshot JSON, plan_snapshot JSON, source_fingerprint, created_at)
--   UNIQUE(group_id, ordinal); UNIQUE(group_id, study_id)
--   Snapshot of each member's study and frozen frequency plan at registration time.
--   If the source points or plan change, source_fingerprint no longer matches and
--   the old registration is stale: recompute into a new group and a new group run.

-- traverse_group_runs(group_id, name UNIQUE, group_snapshot JSON,
--   source_snapshot JSON, source_fingerprints JSON, group_fingerprint,
--   status, result JSON, error,
--   observed_max_power, global_p,
--   winning_member_ordinal, winning_study_id, winning_frequency,
--   created_by, created_at)
--   Full group snapshot, member-level spectra and the complete joint null distribution.

-- Existing spectrum_runs and weave_notes keep their single-traverse results and
-- approved snapshots unchanged. Group results live only in these new tables.
