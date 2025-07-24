#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIEA-EJB Installation API Routes
================================

API REST para instalación y configuración del sistema NIEA-EJB.

Autor: Sistema NIEA-EJB
Versión: 1.0.0
"""

from flask import Blueprint, jsonify, request
from setup_database import install_complete_system, get_installation_status
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Crear blueprint
install_bp = Blueprint('install', __name__, url_prefix='/v1/api')

@install_bp.route('/install', methods=['POST'])
def install_system():
    """
    Endpoint para instalar el sistema completo NIEA-EJB
    
    POST /v1/api/install
    
    Body JSON (opcional):
    {
        "force_reinstall": false,
        "skip_verification": false
    }
    
    Returns:
        JSON con resultado de la instalación
    """
    try:
        # Obtener parámetros opcionales (manejar tanto JSON como peticiones vacías)
        data = {}
        if request.is_json:
            data = request.get_json() or {}
        force_reinstall = data.get('force_reinstall', False)
        skip_verification = data.get('skip_verification', False)
        
        logger.info("🚀 Iniciando instalación del sistema NIEA-EJB via API")
        
        # Verificar si ya está instalado (a menos que se fuerce la reinstalación)
        if not force_reinstall:
            status = get_installation_status()
            if status.get('installed', False):
                return jsonify({
                    'status': 'success',
                    'message': 'Sistema ya está instalado',
                    'data': {
                        'already_installed': True,
                        'installation_status': status,
                        'credentials': {
                            'username': 'admin',
                            'password': 'admin123'
                        }
                    }
                }), 200
        
        # Ejecutar instalación completa
        result = install_complete_system()
        
        if result['success']:
            response = {
                'status': 'success',
                'message': result['message'],
                'data': {
                    'installation_completed': True,
                    'details': result['details'],
                    'credentials': {
                        'username': 'admin',
                        'password': 'admin123'
                    },
                    'next_steps': [
                        'Hacer login en POST /v1/api/auth/login',
                        'Usar el token JWT para acceder a las APIs protegidas',
                        'Comenzar a cargar datos en el sistema'
                    ]
                }
            }
            
            logger.info("✅ Instalación completada exitosamente via API")
            return jsonify(response), 201
        else:
            response = {
                'status': 'error',
                'message': result['message'],
                'data': {
                    'installation_completed': False,
                    'errors': result['errors'],
                    'details': result['details']
                }
            }
            
            logger.error("❌ Instalación falló via API")
            return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"❌ Error crítico en instalación via API: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor durante la instalación',
            'data': {
                'error_details': str(e)
            }
        }), 500

@install_bp.route('/install/status', methods=['GET'])
def get_install_status():
    """
    Endpoint para verificar el estado de instalación del sistema
    
    GET /v1/api/install/status
    
    Returns:
        JSON con estado actual de la instalación
    """
    try:
        status = get_installation_status()
        
        if 'error' in status:
            return jsonify({
                'status': 'error',
                'message': 'Error verificando estado de instalación',
                'data': status
            }), 500
        
        response = {
            'status': 'success',
            'message': 'Estado de instalación obtenido correctamente',
            'data': {
                'system_installed': status['installed'],
                'tables_status': {
                    'installed': status['tables_installed'],
                    'expected': status['tables_expected'],
                    'existing_tables': status['existing_tables'],
                    'missing_tables': status['missing_tables']
                },
                'admin_user_exists': status['admin_user_exists'],
                'installation_complete': status['installed'] and status['admin_user_exists']
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado de instalación: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor',
            'data': {
                'error_details': str(e)
            }
        }), 500

@install_bp.route('/install/reset', methods=['POST'])
def reset_system():
    """
    Endpoint para resetear el sistema (PELIGROSO - solo para desarrollo)
    
    POST /v1/api/install/reset
    
    Body JSON:
    {
        "confirm_reset": true,
        "reset_password": "MIA_INTELLIGENCE_NIEA_2025"
    }
    
    Returns:
        JSON con resultado del reseteo
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos JSON requeridos para reseteo'
            }), 400
        
        # Verificar confirmación y password de seguridad
        if not data.get('confirm_reset', False):
            return jsonify({
                'status': 'error',
                'message': 'Debe confirmar el reseteo con confirm_reset: true'
            }), 400
        
        if data.get('reset_password') != 'MIA_INTELLIGENCE_NIEA_2025':
            return jsonify({
                'status': 'error',
                'message': 'Password de reseteo incorrecto'
            }), 403
        
        logger.warning("⚠️ INICIANDO RESETEO DEL SISTEMA - OPERACIÓN PELIGROSA")
        
        # Aquí iría la lógica de reseteo (eliminar tablas, etc.)
        # Por seguridad, solo retornamos un mensaje informativo
        
        return jsonify({
            'status': 'info',
            'message': 'Función de reseteo no implementada por seguridad',
            'data': {
                'note': 'Para resetear el sistema, ejecute manualmente los comandos SQL de eliminación de tablas'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error en reseteo del sistema: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor',
            'data': {
                'error_details': str(e)
            }
        }), 500

@install_bp.route('/install/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check para verificar conectividad
    
    GET /v1/api/install/health
    
    Returns:
        JSON con estado de salud del sistema
    """
    try:
        from config.database import PostgreSQLConnection
        from config.config import DB_CONFIG
        
        # Verificar conexión a base de datos
        try:
            PostgreSQLConnection.initialize(**DB_CONFIG)
            conn = PostgreSQLConnection.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            PostgreSQLConnection.return_connection(conn)
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        response = {
            'status': 'success',
            'message': 'Health check completado',
            'data': {
                'api_status': 'running',
                'database_status': db_status,
                'timestamp': '2024-01-01T00:00:00Z'  # Se actualizaría con datetime real
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Error en health check',
            'data': {
                'error_details': str(e)
            }
        }), 500
