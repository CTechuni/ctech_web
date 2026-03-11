-- Migration: synchronize database schema with current models
-- 1. Add missing `last_login` column to users table (required by User model)
-- 2. Ensure the 'admin' role exists and assign it to the correct user(s)

-- Add columns if they don't already exist (PostgreSQL syntax)
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS last_login DateTime NULL;

-- new in models: email verification flag
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS is_email_verified BOOLEAN DEFAULT FALSE;

-- session management fields used by auth logic
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS last_valid_token VARCHAR(500) NULL;
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS last_token_issued_at DateTime NULL;

-- Ensure roles table contains all expected names (admin, leader, mentor, user)
INSERT INTO roles (name_rol, description)
SELECT v.name, v.role_desc
FROM (VALUES
    ('admin','Administrador'),
    ('leader','Leader role'),
    ('user','Usuario estándar')
) AS v(name, role_desc)
ON CONFLICT (name_rol) DO NOTHING;

-- If there is a known administrator account, make sure its rol_id is correct
-- Replace the email below with any admin emails you have in the system.
UPDATE users
SET rol_id = (SELECT id_rol FROM roles WHERE name_rol = 'admin')
WHERE email IN ('ctech.uni@gmail.com');

-- You can extend the WHERE clause to assign the admin role to other accounts as needed.

-- Optionally, you may backfill last_login for existing users (NULL is fine);
-- for example, set it equal to registration_date:
-- UPDATE users SET last_login = registration_date WHERE last_login IS NULL;
