-- =====================================================
-- NIEA-EJB: Tabla de Resultados de Idiomas
-- =====================================================
-- Descripción: Tabla para almacenar resultados calculados de puntuación por idiomas
-- Autor: Sistema NIEA-EJB
-- Versión: 2.0.0
-- =====================================================

-- Crear tabla de resultados de idiomas
CREATE TABLE IF NOT EXISTS niea_ejb.idiomas (
    id SERIAL PRIMARY KEY,
    cedula INTEGER NOT NULL,
    grado_actual VARCHAR(50),
    categoria VARCHAR(50),
    puntos_totales DECIMAL(5,2) DEFAULT 0.00,
    cantidad_idiomas INTEGER DEFAULT 0,
    porcentaje DECIMAL(5,2) DEFAULT 0.00,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_idiomas_cedula ON niea_ejb.idiomas(cedula);
CREATE INDEX IF NOT EXISTS idx_idiomas_grado ON niea_ejb.idiomas(grado_actual);
CREATE INDEX IF NOT EXISTS idx_idiomas_categoria ON niea_ejb.idiomas(categoria);
CREATE INDEX IF NOT EXISTS idx_idiomas_puntos ON niea_ejb.idiomas(puntos_totales);
CREATE INDEX IF NOT EXISTS idx_idiomas_cantidad ON niea_ejb.idiomas(cantidad_idiomas);

-- Comentarios en las columnas
COMMENT ON TABLE niea_ejb.idiomas IS 'Tabla de resultados calculados de puntuación por idiomas';
COMMENT ON COLUMN niea_ejb.idiomas.cedula IS 'Cédula del candidato';
COMMENT ON COLUMN niea_ejb.idiomas.puntos_totales IS 'Puntos totales obtenidos por idiomas (máximo 1.8)';
COMMENT ON COLUMN niea_ejb.idiomas.cantidad_idiomas IS 'Cantidad de idiomas que maneja el candidato';
COMMENT ON COLUMN niea_ejb.idiomas.porcentaje IS 'Porcentaje de puntuación obtenida respecto al máximo';

-- Trigger para actualizar fecha_actualizacion automáticamente
CREATE OR REPLACE FUNCTION update_idiomas_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_idiomas_timestamp_trigger
    BEFORE UPDATE ON niea_ejb.idiomas 
    FOR EACH ROW EXECUTE FUNCTION update_idiomas_timestamp();
