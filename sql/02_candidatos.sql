-- =====================================================
-- NIEA-EJB: Tabla de Candidatos
-- =====================================================
-- Descripción: Tabla para gestionar candidatos del sistema NIEA-EJB
-- Autor: Sistema NIEA-EJB
-- Versión: 1.0.0
-- =====================================================

-- Crear tabla de candidatos
CREATE TABLE IF NOT EXISTS niea_ejb.candidatos (
    id SERIAL PRIMARY KEY,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nombres VARCHAR(100),
    apellidos VARCHAR(100),
    grado_actual VARCHAR(50),
    categoria VARCHAR(50),
    fecha_ingreso_ejercito DATE,
    unidad_actual VARCHAR(100),
    especialidad VARCHAR(100),
    tiempo_servicio INTEGER, -- en meses
    observaciones TEXT,
    -- Campos adicionales para compatibilidad
    fecha_nacimiento DATE,
    lugar_nacimiento VARCHAR(100),
    estado_civil VARCHAR(20),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    evaluaciones_desempeno JSONB,
    cursos_realizados JSONB,
    condecoraciones JSONB,
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'retirado')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES niea_ejb.users(id),
    updated_by INTEGER REFERENCES niea_ejb.users(id)
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_candidatos_cedula ON niea_ejb.candidatos(cedula);
CREATE INDEX IF NOT EXISTS idx_candidatos_grado ON niea_ejb.candidatos(grado_actual);
CREATE INDEX IF NOT EXISTS idx_candidatos_categoria ON niea_ejb.candidatos(categoria);
CREATE INDEX IF NOT EXISTS idx_candidatos_estado ON niea_ejb.candidatos(estado);
CREATE INDEX IF NOT EXISTS idx_candidatos_unidad ON niea_ejb.candidatos(unidad_actual);
CREATE INDEX IF NOT EXISTS idx_candidatos_nombres ON niea_ejb.candidatos(nombres, apellidos);

-- Comentarios en las columnas
COMMENT ON TABLE niea_ejb.candidatos IS 'Tabla de candidatos para ascensos y selecciones del sistema NIEA-EJB';
COMMENT ON COLUMN niea_ejb.candidatos.cedula IS 'Cédula de identidad del candidato (único)';
COMMENT ON COLUMN niea_ejb.candidatos.grado_actual IS 'Grado militar actual del candidato';
COMMENT ON COLUMN niea_ejb.candidatos.categoria IS 'Categoría militar del candidato';
COMMENT ON COLUMN niea_ejb.candidatos.tiempo_servicio IS 'Tiempo de servicio en meses';
COMMENT ON COLUMN niea_ejb.candidatos.evaluaciones_desempeno IS 'Evaluaciones de desempeño en formato JSON';
COMMENT ON COLUMN niea_ejb.candidatos.cursos_realizados IS 'Cursos realizados por el candidato en formato JSON';
COMMENT ON COLUMN niea_ejb.candidatos.condecoraciones IS 'Condecoraciones y reconocimientos en formato JSON';

-- Trigger para actualizar updated_at automáticamente
CREATE TRIGGER update_candidatos_updated_at 
    BEFORE UPDATE ON niea_ejb.candidatos 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
