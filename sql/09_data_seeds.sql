-- =====================================================
-- NIEA-EJB: Estructura Principal del Sistema de Evaluación
-- =====================================================
-- Descripción: Estructura completa del sistema NIEA-EJB con tablas:
-- aspectos, variables, indicadores, especificidades, subespecificidades
-- Autor: Sistema NIEA-EJB
-- Versión: 1.0.0
-- =====================================================

-- Primero elimina las tablas existentes (si ya las creaste)
DROP TABLE IF EXISTS niea_ejb.subespecificidades;
DROP TABLE IF EXISTS niea_ejb.especificidades;
DROP TABLE IF EXISTS niea_ejb.indicadores;
DROP TABLE IF EXISTS niea_ejb.variables;
DROP TABLE IF EXISTS niea_ejb.aspectos;

-- Luego recrea las tablas con mayor precisión decimal
CREATE TABLE niea_ejb.aspectos (
    aspecto_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    porcentaje NUMERIC(6,3) NOT NULL,  -- Cambiado a 3 decimales
    puntaje_maximo NUMERIC(6,3) NOT NULL
);

CREATE TABLE niea_ejb.variables (
    variable_id SERIAL PRIMARY KEY,
    aspecto_id INTEGER REFERENCES niea_ejb.aspectos(aspecto_id),
    nombre VARCHAR(100) NOT NULL,
    porcentaje NUMERIC(6,3) NOT NULL,
    puntaje_maximo NUMERIC(6,3) NOT NULL
);

CREATE TABLE niea_ejb.indicadores (
    indicador_id SERIAL PRIMARY KEY,
    variable_id INTEGER REFERENCES niea_ejb.variables(variable_id),
    nombre VARCHAR(100) NOT NULL,
    porcentaje NUMERIC(6,3) NOT NULL,
    puntaje_maximo NUMERIC(6,3) NOT NULL
);

CREATE TABLE niea_ejb.especificidades (
    especificidad_id SERIAL PRIMARY KEY,
    indicador_id INTEGER REFERENCES niea_ejb.indicadores(indicador_id),
    nombre VARCHAR(100) NOT NULL,
    porcentaje NUMERIC(6,3) NOT NULL,
    puntaje_maximo NUMERIC(8,4) NOT NULL  -- Cambiado a 4 decimales
);

CREATE TABLE niea_ejb.subespecificidades (
    subespecificidad_id SERIAL PRIMARY KEY,
    especificidad_id INTEGER REFERENCES niea_ejb.especificidades(especificidad_id),
    nombre VARCHAR(100) NOT NULL,
    porcentaje NUMERIC(6,3) NOT NULL,
    puntaje_maximo NUMERIC(8,4) NOT NULL  -- Cambiado a 4 decimales
);

-- Insertar datos de aspectos
INSERT INTO niea_ejb.aspectos (nombre, porcentaje, puntaje_maximo)
VALUES 
	('Calificaciones de Servicio', 40.00, 40.00),
	('Historial', 60.00, 60.00);

-- Insertar variables del segundo aspecto
INSERT INTO niea_ejb.variables (aspecto_id, nombre, porcentaje, puntaje_maximo)
VALUES 
	(1, 'Grado Actual', 60.00, 24.00),
    (1, 'Grados Anteriores', 40.00, 16.00),
    (2, 'Condiciones Intelectuales', 20.00, 12.00),
    (2, 'Condiciones Profesionales', 35.00, 21.00),
    (2, 'Condiciones Morales', 25.00, 15.00),
    (2, 'Condiciones Fisicas', 10.00, 06.00),
    (2, 'Otros Aspectos', 10.00, 06.00);

-- Insertar indicadores de 'Condiciones intelectuales'
INSERT INTO niea_ejb.indicadores (variable_id, nombre, porcentaje, puntaje_maximo)
VALUES 
    (3, 'Cursos Militares', 50.00, 6.00),
    (3, 'Estudios Civiles', 20.00, 2.40),
    (3, 'Idiomas', 15.00, 1.80),
    (3, 'Trabajo de Valor Institucional', 15.00, 1.80),
	(4, 'Clases Impartidas', 20.00, 4.2),
	(4, 'Complejidad del Cargo', 30.00, 6.3),
	(4, 'Actividad Operacional y Logistica', 50.00, 10.5),
	(5, 'Calificacion de Conducta', 100.00, 15.00),
	(6, 'Prueba Fisica', 70.00, 4.2),
	(6, 'Reposos Medicos', 10.00, 0.6),
	(6, 'Juegos Deportivos', 20.00, 1.2),
	(7, 'Reconocimientos', 20.00, 1.2),
	(7, 'Comisiones Especiales', 20.00, 1.2),
	(7, 'Condecoraciones', 20.00, 1.2),
	(7, 'Consideraciones para Ascensos', 20.00, 1.2);

-- Insertar especificidades para 'cursos militares'
INSERT INTO niea_ejb.especificidades (indicador_id, nombre, porcentaje, puntaje_maximo)
VALUES 
    (1, 'Obligatorios del Grado', 70.00, 4.20),
    (1, 'Otros Cursos', 30.00, 1.80),
    (2, 'Doctorados', 30.00, 0.72),
    (2, 'Maestrias', 25.00, 0.60),
    (2, 'Especializaciones', 20.00, 0.48),
    (2, 'Pregrados', 15.00, 0.36),
    (2, 'Otros', 10.00, 0.24),
    (3, 'Un Idioma', 30.00, 0.54),
    (3, 'Dos Idiomas', 30.00, 0.54),
    (3, 'Tres Idiomas', 40.00, 0.72),
    (4, 'Un Trabajo', 25.00, 0.45),
    (4, 'Dos Trabajos', 35.00, 0.63),
    (4, 'Tres Trabajos', 40.00, 0.72),
    (5, 'Postgrados', 40.00, 1.68),
    (5, 'Pregrado', 35.00, 1.47),
    (5, 'Educacion Basica', 25.00, 1.05),
	(6, 'Grado Actual', 60.00, 3.78),
    (6, 'Grado Anteriores', 40.00, 2.52),
    (7, 'Horas de Vuelo', 15.00, 1.575),
    (7, 'Millas Navegadas', 15.00, 1.575),
    (7, 'Horas Operacionales', 20.00, 2.1),
    (7, 'Logistica Operacional', 20.00, 2.1),
    (7, 'Horas de Inmersion', 15.00, 1.575),
    (7, 'Saltos en Paracaidas', 15.00, 1.575),
    (8, 'Grado Actual', 60.00, 9.00),
    (8, 'Grado Anterior', 40.00, 6.00),
    (9, 'Para Ascenso', 60.00, 2.52),
    (9, 'Promedio Anterior', 40.00, 1.68),
    (10, 'Ningun Reposo', 100.00, 0.6),
    (11, 'Internacionales', 30.00, 0.36),
    (11, 'Nacionales', 25.00, 0.3),
    (11, 'Nacionales Militares', 20.00, 0.24),
    (11, 'Regionales Militares', 15.00, 0.18),
    (11, 'Unidades Militares', 10.00, 0.12),
    (12, 'Exaltaciones de Merito', 30.00, 0.18),
    (12, 'Barras', 25.00, 0.15),
    (12, 'Placas', 20.00, 0.12),
    (12, 'Diplomas', 15.00, 0.09),
    (12, 'Felicitaciones', 10.00, 0.06),
	(13, 'Presidencial', 45.00, 0.135),
	(13, 'Internacional', 35.00, 0.105),
	(13, 'Otras', 20.00, 0.06),
	(14, 'Extra Componente', 40.00, 0.24),
	(14, 'Componente', 35.00, 0.21),
	(14, 'No Militares', 10.00, 0.06),
	(14, 'Internacionales', 15.00, 0.09),
	(15, 'Opinion de Comando', 20.00, 0.9),
	(15, 'Examen de Conocimiento', 20.00, 0.9),
	(15, 'Calificacion de Tiro', 20.00, 0.9),
	(15, 'Considereciones Componente', 40.00, 1.8);

-- Insertar subespecificidades para 'otros' en estudios civiles
INSERT INTO niea_ejb.subespecificidades (especificidad_id, nombre, porcentaje, puntaje_maximo)
VALUES 
    (7, 'Tecnico Superior Universitario', 55.00, 0.132),
    (7, 'Diplomados', 25.00, 0.060),
    (7, 'Otros Estudios', 20.00, 0.048),
	(19, 'Tacticas', 50.00, 0.7875),
	(19, 'Administrativas', 20.00, 0.315),
	(19, 'Instruccion', 30.00, 0.4725),
	(20, 'Tripulante', 60.00, 0.945),
	(20, 'Combatiente', 30.00, 0.4725),
	(20, 'Instruccion', 10.00, 0.1575),
	(21, 'Tacticas', 50.00, 1.05),
	(21, 'Seguridad', 30.00, 0.63),
	(21, 'Destacamentos', 20.00, 0.42),
	(22, 'Bases Logisticas en Operaciones', 50.00, 1.05),
	(22, 'Sostenimiento Logistico', 30.00, 0.63),
	(22, 'Operaciones de Abastecimiento', 20.00, 0.42),
	(23, 'Tacticas', 60.00, 0.945),
	(23, 'Instruccion', 30.00, 0.4725),
	(23, 'Administrativas', 10.00, 0.1575),
	(24, 'Tacticos', 50.00, 0.7875),
	(24, 'Instruccion', 30.00, 0.4725),
	(24, 'Administrativos', 20.00, 0.315),
	(36, 'Extra Componente', 40.00, 0.06),
	(36, 'Ministerial', 33.33, 0.05),
	(36, 'Comando General', 20.00, 0.03),
	(36, 'Instituciones Militares', 5.33, 0.008),
	(36, 'Instituciones Civiles', 1.33, 0.002),
	(37, 'Extra Componente', 23.33, 0.028),
	(37, 'Ministerial', 22.50, 0.027),
	(37, 'Comando General', 20.83, 0.025),
	(37, 'Instituciones Militares', 17.50, 0.021),
	(37, 'Instituciones Civiles', 15.83, 0.019),
	(38, 'Extra Componente', 22.22, 0.02),
	(38, 'Ministerial', 21.11, 0.019),
	(38, 'Comando General', 20.00, 0.018),
	(38, 'Instituciones Militares', 18.88, 0.017),
	(38, 'Instituciones Civiles', 17.77, 0.016),
	(39, 'Extra Componente', 23.33, 0.014),
	(39, 'Ministerial', 21.66, 0.013),
	(39, 'Comando General', 20.00, 0.012),
	(39, 'Instituciones Militares', 18.33, 0.011),
	(39, 'Instituciones Civiles', 16.66, 0.001),
	(40, 'Fuera del Pais', 57.40, 0.0775),
	(40, 'Dentro del Pais', 42.59, 0.0575);

-- Insertar usuario administrador por defecto
-- Password: admin123 (hash generado con bcrypt)
INSERT INTO niea_ejb.users (username, email, password_hash, full_name, role) 
VALUES (
    'admin', 
    'admin@niea-ejb.mil', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVjHUxHlW', 
    'Administrador Sistema', 
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- Insertar usuario de prueba
INSERT INTO niea_ejb.users (username, email, password_hash, full_name, role) 
VALUES (
    'usuario_test', 
    'test@niea-ejb.mil', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVjHUxHlW', 
    'Usuario de Prueba', 
    'user'
) ON CONFLICT (username) DO NOTHING;

-- Mensaje de confirmación
SELECT 'Estructura NIEA-EJB instalada correctamente' as status;
