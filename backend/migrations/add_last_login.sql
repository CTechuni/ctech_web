-- Agrega campo last_login a la tabla users
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP NULL;
