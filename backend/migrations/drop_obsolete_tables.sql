-- Elimina tablas obsoletas (módulos de mentoría, cursos, contenido educativo)
-- CTech ya no usa estos módulos.
-- Orden: primero las tablas con FK salientes, luego las referenciadas.

DROP TABLE IF EXISTS mentoring_sessions CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS educational_content CASCADE;
DROP TABLE IF EXISTS specialties CASCADE;
DROP TABLE IF EXISTS technologies CASCADE;
DROP TABLE IF EXISTS thematic_areas CASCADE;
DROP TABLE IF EXISTS learning_levels CASCADE;
DROP TABLE IF EXISTS invitation_codes CASCADE;
DROP TABLE IF EXISTS password_reset_tokens CASCADE;
DROP TABLE IF EXISTS system_config CASCADE;
