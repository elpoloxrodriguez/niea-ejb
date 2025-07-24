-- NIEA-EJB Users Table Setup
-- Execute this SQL in your PostgreSQL database

-- Create users table for JWT authentication
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

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON niea_ejb.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON niea_ejb.users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON niea_ejb.users(is_active);

-- Insert a default admin user (password: admin123)
INSERT INTO niea_ejb.users (username, email, password_hash, full_name, role) 
VALUES (
    'admin', 
    'admin@niea-ejb.mil', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVjHUxHlW', 
    'Administrador Sistema', 
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- Verify the table was created successfully
SELECT 'Users table created successfully' as status;
SELECT COUNT(*) as user_count FROM niea_ejb.users;
