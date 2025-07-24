-- =====================================================
-- NIEA-EJB: Tabla de Resultados de Trabajo Institucional
-- =====================================================
-- Descripción: Tabla para almacenar resultados calculados de puntuación por trabajo institucional
-- Autor: Sistema NIEA-EJB
-- Versión: 2.0.0
-- =====================================================

-- Crear tabla de resultados de trabajo institucional
CREATE TABLE IF NOT EXISTS niea_ejb.trabajo_institucional (
    id SERIAL PRIMARY KEY,
    cedula INTEGER NOT NULL,
    grado_actual VARCHAR(50),
    categoria VARCHAR(50),
    puntos_totales DECIMAL(5,2) DEFAULT 0.00,
    cantidad_trabajos_valor INTEGER DEFAULT 0,
    porcentaje DECIMAL(5,2) DEFAULT 0.00,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_trabajo_institucional_cedula ON niea_ejb.trabajo_institucional(cedula);
CREATE INDEX IF NOT EXISTS idx_trabajo_institucional_grado ON niea_ejb.trabajo_institucional(grado_actual);
CREATE INDEX IF NOT EXISTS idx_trabajo_institucional_categoria ON niea_ejb.trabajo_institucional(categoria);
CREATE INDEX IF NOT EXISTS idx_trabajo_institucional_puntos ON niea_ejb.trabajo_institucional(puntos_totales);
CREATE INDEX IF NOT EXISTS idx_trabajo_institucional_cantidad ON niea_ejb.trabajo_institucional(cantidad_trabajos_valor);

-- Comentarios en las columnas
COMMENT ON TABLE niea_ejb.trabajo_institucional IS 'Tabla de resultados calculados de puntuación por trabajo institucional';
COMMENT ON COLUMN niea_ejb.trabajo_institucional.cedula IS 'Cédula del candidato';
COMMENT ON COLUMN niea_ejb.trabajo_institucional.puntos_totales IS 'Puntos totales obtenidos por trabajo institucional (máximo 1.8)';
COMMENT ON COLUMN niea_ejb.trabajo_institucional.cantidad_trabajos_valor IS 'Cantidad de trabajos de valor institucional realizados';
COMMENT ON COLUMN niea_ejb.trabajo_institucional.porcentaje IS 'Porcentaje de puntuación obtenida respecto al máximo';

-- Trigger para actualizar fecha_actualizacion automáticamente
CREATE OR REPLACE FUNCTION update_trabajo_institucional_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_trabajo_institucional_timestamp_trigger
    BEFORE UPDATE ON niea_ejb.trabajo_institucional 
    FOR EACH ROW EXECUTE FUNCTION update_trabajo_institucional_timestamp();

-- Trigger para actualizar updated_at automáticamente
CREATE TRIGGER update_trabajo_institucional_updated_at 
    BEFORE UPDATE ON niea_ejb.trabajo_institucional 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
