-- ============================================================
-- Student Record Management System
-- Master Setup Script
-- Run this file once to initialise the entire database.
--
-- Usage:
--   mysql -u root -p < database/setup.sql
-- ============================================================

SOURCE database/schema.sql;
SOURCE database/stored_procedures.sql;
SOURCE database/sample_data.sql;

-- Verify setup
SELECT 'Setup complete!' AS Status;
SELECT TABLE_NAME, TABLE_ROWS
FROM   information_schema.TABLES
WHERE  TABLE_SCHEMA = 'student_management_db'
ORDER BY TABLE_NAME;
