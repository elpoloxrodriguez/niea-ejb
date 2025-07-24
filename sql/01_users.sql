-- =====================================================
-- NIEA-EJB: Tabla de Usuarios para Autenticación JWT
-- =====================================================
-- Descripción: Tabla principal para gestionar usuarios del sistema
-- Autor: Sistema NIEA-EJB
-- Versión: 1.0.0
-- =====================================================

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS niea_ejb.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'moderator')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_users_username ON niea_ejb.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON niea_ejb.users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON niea_ejb.users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_role ON niea_ejb.users(role);

-- Comentarios en las columnas
COMMENT ON TABLE niea_ejb.users IS 'Tabla de usuarios para autenticación JWT del sistema NIEA-EJB';
COMMENT ON COLUMN niea_ejb.users.id IS 'Identificador único del usuario';
COMMENT ON COLUMN niea_ejb.users.username IS 'Nombre de usuario único para login';
COMMENT ON COLUMN niea_ejb.users.email IS 'Correo electrónico único del usuario';
COMMENT ON COLUMN niea_ejb.users.password_hash IS 'Hash bcrypt de la contraseña';
COMMENT ON COLUMN niea_ejb.users.full_name IS 'Nombre completo del usuario';
COMMENT ON COLUMN niea_ejb.users.role IS 'Rol del usuario (admin, user, moderator)';
COMMENT ON COLUMN niea_ejb.users.is_active IS 'Estado activo/inactivo del usuario';
COMMENT ON COLUMN niea_ejb.users.created_at IS 'Fecha y hora de creación del registro';
COMMENT ON COLUMN niea_ejb.users.updated_at IS 'Fecha y hora de última actualización';
COMMENT ON COLUMN niea_ejb.users.last_login IS 'Fecha y hora del último login exitoso';

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON niea_ejb.users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
