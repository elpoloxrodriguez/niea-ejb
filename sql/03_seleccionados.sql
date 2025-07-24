-- =====================================================
-- NIEA-EJB: Tabla de Seleccionados
-- =====================================================
-- Descripción: Tabla para gestionar candidatos seleccionados
-- Autor: Sistema NIEA-EJB
-- Versión: 1.0.0
-- =====================================================

-- Crear tabla de seleccionados
CREATE TABLE IF NOT EXISTS niea_ejb.seleccionados (
    id SERIAL PRIMARY KEY,
    candidato_id INTEGER REFERENCES niea_ejb.candidatos(id) ON DELETE CASCADE,
    proceso_seleccion VARCHAR(100) NOT NULL,
    fecha_seleccion DATE DEFAULT CURRENT_DATE,
    grado_destino VARCHAR(50),
    puntaje_total DECIMAL(10,2),
    puntaje_evaluacion DECIMAL(10,2),
    puntaje_cursos DECIMAL(10,2),
    puntaje_experiencia DECIMAL(10,2),
    observaciones_seleccion TEXT,
    estado_seleccion VARCHAR(20) DEFAULT 'seleccionado' CHECK (estado_seleccion IN ('seleccionado', 'confirmado', 'rechazado', 'pendiente')),
    fecha_confirmacion DATE,
    unidad_destino VARCHAR(100),
    fecha_ascenso_programada DATE,
    documentos_adjuntos JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES niea_ejb.users(id),
    updated_by INTEGER REFERENCES niea_ejb.users(id)
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_seleccionados_candidato ON niea_ejb.seleccionados(candidato_id);
CREATE INDEX IF NOT EXISTS idx_seleccionados_proceso ON niea_ejb.seleccionados(proceso_seleccion);
CREATE INDEX IF NOT EXISTS idx_seleccionados_estado ON niea_ejb.seleccionados(estado_seleccion);
CREATE INDEX IF NOT EXISTS idx_seleccionados_fecha ON niea_ejb.seleccionados(fecha_seleccion);
CREATE INDEX IF NOT EXISTS idx_seleccionados_grado_destino ON niea_ejb.seleccionados(grado_destino);

-- Comentarios en las columnas
COMMENT ON TABLE niea_ejb.seleccionados IS 'Tabla de candidatos seleccionados para ascensos';
COMMENT ON COLUMN niea_ejb.seleccionados.candidato_id IS 'Referencia al candidato seleccionado';
COMMENT ON COLUMN niea_ejb.seleccionados.proceso_seleccion IS 'Nombre del proceso de selección';
COMMENT ON COLUMN niea_ejb.seleccionados.puntaje_total IS 'Puntaje total obtenido en la evaluación';
COMMENT ON COLUMN niea_ejb.seleccionados.documentos_adjuntos IS 'Documentos relacionados con la selección en formato JSON';

-- Trigger para actualizar updated_at automáticamente
CREATE TRIGGER update_seleccionados_updated_at 
    BEFORE UPDATE ON niea_ejb.seleccionados 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
