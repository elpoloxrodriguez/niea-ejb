#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIEA-EJB Flask Application
==========================

Aplicación web para la gestión del sistema NIEA-EJB.
Esta aplicación maneja candidatos, seleccionados, estructura organizacional,
cursos militares y civiles, idiomas y trabajo institucional.

Autor: Sistema NIEA-EJB
Versión: 1.0.0
"""

import os
import sys
import logging
import socket
import signal
import atexit
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


def setup_logging():
    """Configura el sistema de logging de manera profesional."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def create_app():
    """Factory function para crear y configurar la aplicación Flask."""
    app = Flask(__name__)
    
    # Configuración de la aplicación
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', os.urandom(24).hex()),  # Generar una clave secreta aleatoria
        'JSON_AS_ASCII': False,  # Soporte para caracteres UTF-8
        'JSONIFY_PRETTYPRINT_REGULAR': True
    })
    
    return app


def initialize_database(logger, show_message=True):
    """Inicializa la conexión a la base de datos PostgreSQL."""
    try:
        was_initialized = PostgreSQLConnection.initialize(**DB_CONFIG)
        if was_initialized and show_message:
            logger.info("✅ Pool de conexiones a PostgreSQL inicializado correctamente")
        # Si ya estaba inicializado, no mostramos mensaje para evitar duplicados
    except Exception as e:
        logger.error(f"❌ Error al inicializar la base de datos: {str(e)}")
        sys.exit(1)


def register_blueprints(app, logger, show_messages=True):
    """Registra todos los blueprints de la aplicación."""
    blueprints = [
        (candidatos_bp, "Candidatos"),
        (seleccionados_bp, "Seleccionados"),
        (estructura_bp, "Estructura"),
        (cursos_militares_bp, "Cursos Militares"),
        (cursos_civiles_bp, "Cursos Civiles"),
        (idiomas_bp, "Idiomas"),
        (trabajo_institucional_bp, "Trabajo Institucional")
    ]
    
    for blueprint, description in blueprints:
        try:
            app.register_blueprint(blueprint)
            if show_messages:
                logger.info(f"🔗 Blueprint registrado: {description} ({blueprint.name})")
        except Exception as e:
            logger.error(f"❌ Error registrando blueprint {description}: {str(e)}")


def setup_shutdown_handlers(logger):
    """Configura los manejadores para una salida limpia de la aplicación."""
    # Evitar registrar múltiples veces los manejadores
    if hasattr(setup_shutdown_handlers, 'already_setup'):
        return
    
    def signal_handler(signum, frame):
        # Solo mostrar en el proceso principal
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            logger.info("\n🛑 Aplicación detenida por el usuario")
            logger.info("👋 ¡Hasta luego!")
        sys.exit(0)
    
    # Registrar manejadores para diferentes señales
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Terminación
    
    # Marcar como configurado
    setup_shutdown_handlers.already_setup = True


def get_network_ip():
    """Obtiene la dirección IP de la red local dinámicamente."""
    try:
        # Crear un socket para conectarse a un servidor externo
        # Esto nos permite obtener la IP local sin hacer una conexión real
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Conectar a un servidor DNS público (no envía datos)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        # Si falla, intentar obtener el hostname
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            # Último recurso: usar localhost
            return "127.0.0.1"


def main():
    """Función principal de la aplicación."""
    # Configurar logging
    logger = setup_logging()
    
    # Solo mostrar mensajes en el proceso principal (no en el reloader)
    is_main_process = os.environ.get('WERKZEUG_RUN_MAIN') != 'true'
    
    if is_main_process:
        # Banner de inicio mejorado
        logger.info("🎆 " + "="*60 + " 🎆")
        logger.info("🚀 INICIANDO APLICACIÓN NIEA-EJB")
        logger.info("📋 Sistema de Gestión Militar Integrado")
        logger.info("" + "="*64)
    
    # Crear aplicación Flask
    app = create_app()
    
    # Inicializar base de datos SIEMPRE (necesario para que funcionen los endpoints)
    initialize_database(logger, show_message=is_main_process)
    
    # Registrar blueprints
    register_blueprints(app, logger, show_messages=is_main_process)
    
    # Mostrar información de acceso solo en el proceso principal
    if is_main_process:
        # Obtener IPs dinámicamente
        local_ip = "127.0.0.1"
        network_ip = get_network_ip()
        port = 5001
        
        logger.info("" + "="*64)
        logger.info("🌐 SERVIDOR DISPONIBLE EN:")
        logger.info(f"   💻 Local:    http://{local_ip}:{port}")
        logger.info(f"   🌍 Red:      http://{network_ip}:{port}")
        logger.info("" + "="*64)
        logger.info("💡 Presiona CTRL+C para detener el servidor")
        logger.info("🔄 Iniciando servidor Flask...")
        logger.info("" + "-"*64)
    
    return app


# Crear la aplicación solo cuando se ejecuta directamente
app = None


if __name__ == '__main__':
    # Configurar logging
    logger = setup_logging()
    
    # Configurar manejadores de señales para salida limpia
    setup_shutdown_handlers(logger)
    
    # Ejecutar la aplicación
    try:
        app = main()
        

        
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=True,
            use_reloader=True,
            threaded=True
        )
    except KeyboardInterrupt:
        # Fallback por si el signal handler no funciona
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            logger.info("\n🛑 Aplicación detenida por el usuario")
            logger.info("👋 ¡Hasta luego!")
    except Exception as e:
        logger.error(f"❌ Error crítico: {str(e)}")
        sys.exit(1)
else:
    # Cuando se importa como módulo, crear la aplicación básica sin mensajes
    app = create_app()
    logger = setup_logging()
    initialize_database(logger, show_message=False)
    register_blueprints(app, logger, show_messages=False)