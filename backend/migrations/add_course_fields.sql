-- Migración: agregar campos nuevos a la tabla courses
-- Ejecutar una sola vez contra la DB de PostgreSQL

ALTER TABLE courses
    ADD COLUMN IF NOT EXISTS status      VARCHAR(20) NOT NULL DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS level       VARCHAR(20) NOT NULL DEFAULT 'basico',
    ADD COLUMN IF NOT EXISTS start_date  DATE,
    ADD COLUMN IF NOT EXISTS modules     JSONB       NOT NULL DEFAULT '[]';

-- Cursos existentes que ya estaban creados los marcamos como aprobados
-- para no romper datos actuales
UPDATE courses SET status = 'approved' WHERE status = 'pending';
