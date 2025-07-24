-- =====================================================
-- NIEA-EJB: Tabla de Resultados de Cursos Civiles
-- =====================================================
-- Descripción: Tabla para almacenar resultados calculados de puntuación por cursos civiles
-- Autor: Sistema NIEA-EJB
-- Versión: 2.0.0
-- =====================================================

-- Crear tabla de resultados de cursos civiles
CREATE TABLE IF NOT EXISTS niea_ejb.cursos_civiles (
    id SERIAL PRIMARY KEY,
    cedula INTEGER NOT NULL,
    grado_actual VARCHAR(50),
    puntos_totales DECIMAL(5,2) DEFAULT 0.00,
    desglose_puntos JSONB,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_cursos_civiles_cedula ON niea_ejb.cursos_civiles(cedula);
CREATE INDEX IF NOT EXISTS idx_cursos_civiles_grado ON niea_ejb.cursos_civiles(grado_actual);
CREATE INDEX IF NOT EXISTS idx_cursos_civiles_puntos ON niea_ejb.cursos_civiles(puntos_totales);

-- Comentarios en las columnas
COMMENT ON TABLE niea_ejb.cursos_civiles IS 'Tabla de resultados calculados de puntuación por cursos civiles';
COMMENT ON COLUMN niea_ejb.cursos_civiles.cedula IS 'Cédula del candidato';
COMMENT ON COLUMN niea_ejb.cursos_civiles.puntos_totales IS 'Puntos totales obtenidos por cursos civiles (máximo 2.4)';
COMMENT ON COLUMN niea_ejb.cursos_civiles.desglose_puntos IS 'Desglose de puntos obtenidos en formato JSON';

-- Trigger para actualizar fecha_actualizacion automáticamente
CREATE OR REPLACE FUNCTION update_cursos_civiles_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_cursos_civiles_timestamp_trigger
    BEFORE UPDATE ON niea_ejb.cursos_civiles 
    FOR EACH ROW EXECUTE FUNCTION update_cursos_civiles_timestamp();
