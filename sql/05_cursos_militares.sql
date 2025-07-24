-- NIEA-EJB: Tabla de Resultados de Cursos Militares
-- =====================================================
-- Descripción: Tabla para almacenar resultados calculados de puntuación por cursos militares
-- Autor: Sistema NIEA-EJB
-- Versión: 2.0.0
-- =====================================================

-- Crear tabla de resultados de cursos militares
CREATE TABLE IF NOT EXISTS niea_ejb.cursos_militares (
    id SERIAL PRIMARY KEY,
    cedula VARCHAR(50) NOT NULL,
    grado_actual VARCHAR(50),
    categoria VARCHAR(50),
    puntos_totales DECIMAL(5,2) DEFAULT 0.00,
    desglose_puntos JSONB,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_cursos_militares_cedula ON niea_ejb.cursos_militares(cedula);
CREATE INDEX IF NOT EXISTS idx_cursos_militares_grado ON niea_ejb.cursos_militares(grado_actual);
CREATE INDEX IF NOT EXISTS idx_cursos_militares_categoria ON niea_ejb.cursos_militares(categoria);
CREATE INDEX IF NOT EXISTS idx_cursos_militares_puntos ON niea_ejb.cursos_militares(puntos_totales);

-- Comentarios en las columnas
COMMENT ON TABLE niea_ejb.cursos_militares IS 'Tabla de resultados calculados de puntuación por cursos militares';
COMMENT ON COLUMN niea_ejb.cursos_militares.cedula IS 'Cédula del candidato';
COMMENT ON COLUMN niea_ejb.cursos_militares.puntos_totales IS 'Puntos totales obtenidos por cursos militares (máximo 6.0)';
COMMENT ON COLUMN niea_ejb.cursos_militares.desglose_puntos IS 'Desglose de puntos obtenidos en formato JSON';

-- Trigger para actualizar fecha_actualizacion automáticamente
CREATE OR REPLACE FUNCTION update_cursos_militares_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_cursos_militares_timestamp_trigger
    BEFORE UPDATE ON niea_ejb.cursos_militares 
    FOR EACH ROW EXECUTE FUNCTION update_cursos_militares_timestamp();
