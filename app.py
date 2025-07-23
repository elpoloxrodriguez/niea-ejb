from flask import Flask
from database import PostgreSQLConnection
from config import DB_CONFIG
from routes.candidatos import candidatos_bp
from routes.seleccionados import seleccionados_bp
from routes.estructura import estructura_bp
from routes.cursos_militares import cursos_militares_bp
from routes.cursos_civiles import cursos_civiles_bp

app = Flask(__name__)

# Inicializar la conexión a la base de datos
PostgreSQLConnection.initialize(**DB_CONFIG)

# Registrar blueprints (rutas)
app.register_blueprint(candidatos_bp)
app.register_blueprint(seleccionados_bp)
app.register_blueprint(estructura_bp)
app.register_blueprint(cursos_militares_bp)
app.register_blueprint(cursos_civiles_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)