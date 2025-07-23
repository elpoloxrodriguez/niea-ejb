import logging
from flask import Flask
from config.database import PostgreSQLConnection
from config.config import DB_CONFIG
from routes.candidatos import candidatos_bp
from routes.seleccionados import seleccionados_bp
from routes.estructura import estructura_bp
from routes.cursos_militares import cursos_militares_bp
from routes.cursos_civiles import cursos_civiles_bp
from routes.idiomas import idiomas_bp
from routes.trabajo_institucional import trabajo_institucional_bp

# Configuración del logger para una salida profesional
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Crear la instancia principal de la aplicación Flask
app = Flask(__name__)

# Inicializar la conexión a la base de datos PostgreSQL usando la configuración
PostgreSQLConnection.initialize(**DB_CONFIG)
# logger.info("✅ Pool de conexiones a PostgreSQL inicializado correctamente.")

# Lista de blueprints a registrar
blueprints = [
    candidatos_bp,
    seleccionados_bp,
    estructura_bp,
    cursos_militares_bp,
    cursos_civiles_bp,
    idiomas_bp,
    trabajo_institucional_bp
]

# Registrar todos los blueprints de manera más limpia y escalable
for bp in blueprints:
    app.register_blueprint(bp)
    logger.info(f"🔗 Blueprint registrado: {bp.name}")

# Punto de entrada de la aplicación
if __name__ == '__main__':
    logger.info("🚀 Iniciando aplicación NIEA-EJB en modo desarrollo")
    logger.info("🌐 Acceso local:     http://127.0.0.1:5001")
    logger.info("🌐 Acceso en red:   http://192.168.137.144:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)