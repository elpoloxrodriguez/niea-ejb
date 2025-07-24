-- =====================================================
-- NIEA-EJB: Tabla de Estructura Organizacional
-- =====================================================
-- Descripción: Tabla para gestionar la estructura organizacional del ejército
-- Autor: Sistema NIEA-EJB
-- Versión: 1.0.0
-- =====================================================

-- Crear tabla de estructura organizacional
CREATE TABLE IF NOT EXISTS niea_ejb.estructura (
    id SERIAL PRIMARY KEY,
    codigo_unidad VARCHAR(20) UNIQUE NOT NULL,
    nombre_unidad VARCHAR(200) NOT NULL,
    tipo_unidad VARCHAR(50), -- Batallón, Compañía, Pelotón, etc.
    unidad_padre_id INTEGER REFERENCES niea_ejb.estructura(id),
    nivel_jerarquico INTEGER DEFAULT 1,
    comandante_cedula VARCHAR(20),
    comandante_nombre VARCHAR(100),
    comandante_grado VARCHAR(50),
    ubicacion_geografica VARCHAR(200),
    telefono VARCHAR(20),
    email VARCHAR(100),
    capacidad_personal INTEGER,
    personal_actual INTEGER DEFAULT 0,
    mision TEXT,
    funciones TEXT,
    equipamiento JSONB,
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'disuelto')),
    fecha_creacion DATE,
    fecha_disolucion DATE,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES niea_ejb.users(id),
    updated_by INTEGER REFERENCES niea_ejb.users(id)
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_estructura_codigo ON niea_ejb.estructura(codigo_unidad);
CREATE INDEX IF NOT EXISTS idx_estructura_nombre ON niea_ejb.estructura(nombre_unidad);
CREATE INDEX IF NOT EXISTS idx_estructura_tipo ON niea_ejb.estructura(tipo_unidad);
CREATE INDEX IF NOT EXISTS idx_estructura_padre ON niea_ejb.estructura(unidad_padre_id);
CREATE INDEX IF NOT EXISTS idx_estructura_nivel ON niea_ejb.estructura(nivel_jerarquico);
CREATE INDEX IF NOT EXISTS idx_estructura_comandante ON niea_ejb.estructura(comandante_cedula);
CREATE INDEX IF NOT EXISTS idx_estructura_estado ON niea_ejb.estructura(estado);

-- Comentarios en las columnas
COMMENT ON TABLE niea_ejb.estructura IS 'Tabla de estructura organizacional del ejército';
COMMENT ON COLUMN niea_ejb.estructura.codigo_unidad IS 'Código único de la unidad militar';
COMMENT ON COLUMN niea_ejb.estructura.unidad_padre_id IS 'Referencia a la unidad superior en la jerarquía';
COMMENT ON COLUMN niea_ejb.estructura.nivel_jerarquico IS 'Nivel en la jerarquía organizacional (1=más alto)';
COMMENT ON COLUMN niea_ejb.estructura.equipamiento IS 'Equipamiento asignado a la unidad en formato JSON';

-- Trigger para actualizar updated_at automáticamente
CREATE TRIGGER update_estructura_updated_at 
    BEFORE UPDATE ON niea_ejb.estructura 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
