"""
Configuración de producción para NIEA-EJB
Carga variables de entorno y configuraciones específicas de producción
"""

import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno desde .env.production
load_dotenv('.env.production')

class ProductionConfig:
    """Configuración de producción"""
    
    # Base de datos
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', '10.110.100.236'),
        'database': os.getenv('DB_NAME', 'ejercito'),
        'user': os.getenv('DB_USER', 'ejercito'),
        'password': os.getenv('DB_PASSWORD', 'Arrd18022023$'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    # Servidor
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 5001))
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'NIEA_EJB_PRODUCTION_SECRET_KEY_2025_MIA_INTELLIGENCE')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    
    # Seguridad
    BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', 12))
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/niea-ejb/app.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    CORS_METHODS = os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(',')
    CORS_HEADERS = os.getenv('CORS_HEADERS', 'Content-Type,Authorization').split(',')
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100 per hour')
    RATE_LIMIT_LOGIN = os.getenv('RATE_LIMIT_LOGIN', '10 per minute')
    
    # Cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'redis')
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    
    # Monitoreo
    MONITORING_ENABLED = os.getenv('MONITORING_ENABLED', 'True').lower() == 'true'
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', 60))
    METRICS_ENDPOINT = os.getenv('METRICS_ENDPOINT', '/metrics')
    
    # Backup
    BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'True').lower() == 'true'
    BACKUP_SCHEDULE = os.getenv('BACKUP_SCHEDULE', '0 2 * * *')
    BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
    BACKUP_PATH = os.getenv('BACKUP_PATH', '/var/backups/niea-ejb')
    
    # Email
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.ejercito.mil.co')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', 'niea-system@ejercito.mil.co')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@ejercito.mil.co')
    
    # SSL/TLS
    SSL_CERT_PATH = os.getenv('SSL_CERT_PATH', '/etc/ssl/certs/niea-ejb.crt')
    SSL_KEY_PATH = os.getenv('SSL_KEY_PATH', '/etc/ssl/private/niea-ejb.key')
    SSL_ENABLED = os.getenv('SSL_ENABLED', 'True').lower() == 'true'
    
    # Gunicorn
    GUNICORN_WORKERS = int(os.getenv('GUNICORN_WORKERS', 4))
    GUNICORN_WORKER_CLASS = os.getenv('GUNICORN_WORKER_CLASS', 'sync')
    GUNICORN_TIMEOUT = int(os.getenv('GUNICORN_TIMEOUT', 30))
    GUNICORN_KEEPALIVE = int(os.getenv('GUNICORN_KEEPALIVE', 2))
    
    # Proxy
    PROXY_FIX_ENABLED = os.getenv('PROXY_FIX_ENABLED', 'True').lower() == 'true'
    PROXY_FIX_X_FOR = int(os.getenv('PROXY_FIX_X_FOR', 1))
    PROXY_FIX_X_PROTO = int(os.getenv('PROXY_FIX_X_PROTO', 1))
    PROXY_FIX_X_HOST = int(os.getenv('PROXY_FIX_X_HOST', 1))
    PROXY_FIX_X_PREFIX = int(os.getenv('PROXY_FIX_X_PREFIX', 1))

def setup_production_logging():
    """Configurar logging para producción"""
    config = ProductionConfig()
    
    # Crear directorio de logs si no existe
    log_dir = os.path.dirname(config.LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def validate_production_config():
    """Validar configuración de producción"""
    config = ProductionConfig()
    errors = []
    
    # Validar configuración crítica
    if not config.JWT_SECRET_KEY or config.JWT_SECRET_KEY == 'your-secret-key':
        errors.append("JWT_SECRET_KEY debe ser configurado con un valor seguro")
    
    if not config.DB_CONFIG['password']:
        errors.append("DB_PASSWORD debe ser configurado")
    
    if config.SSL_ENABLED and not os.path.exists(config.SSL_CERT_PATH):
        errors.append(f"Certificado SSL no encontrado: {config.SSL_CERT_PATH}")
    
    if config.SSL_ENABLED and not os.path.exists(config.SSL_KEY_PATH):
        errors.append(f"Clave SSL no encontrada: {config.SSL_KEY_PATH}")
    
    if errors:
        raise ValueError("Errores de configuración de producción:\n" + "\n".join(errors))
    
    return True

# Instancia global de configuración
production_config = ProductionConfig()
