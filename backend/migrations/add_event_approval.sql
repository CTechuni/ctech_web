-- Agrega columnas de visibilidad y mentor_id a la tabla events
-- Separa visibilidad (publico/privado) del estado de aprobación (draft/pending/approved/rejected)

ALTER TABLE events
    ADD COLUMN IF NOT EXISTS visibility VARCHAR(20) NOT NULL DEFAULT 'publico',
    ADD COLUMN IF NOT EXISTS mentor_id INTEGER;

-- Migrar datos existentes: el valor de status era 'publico' o 'privado'
UPDATE events SET visibility = status WHERE status IN ('publico', 'privado');

-- Todos los eventos existentes pasan a 'approved'
UPDATE events SET status = 'approved' WHERE status NOT IN ('draft', 'pending', 'approved', 'rejected');
