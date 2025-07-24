#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIEA-EJB Authentication Module
==============================

Módulo de autenticación JWT para el sistema NIEA-EJB.
Maneja login, generación de tokens, validación y decoradores de protección.

Autor: Sistema NIEA-EJB
Versión: 1.0.0
"""

import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from psycopg2 import sql
from config.database import get_db_connection, PostgreSQLConnection

# Configuración del logger
logger = logging.getLogger(__name__)

# Configuración JWT
JWT_SECRET_KEY = "niea-ejb-secret-key-2024"  # En producción, usar variable de entorno
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Timestamp de inicio del servidor para invalidar tokens en reinicio
SERVER_START_TIME = datetime.utcnow()

def get_server_info() -> dict:
    """
    Obtiene información sobre el estado del servidor
    
    Returns:
        dict: Información del servidor incluyendo tiempo de inicio
    """
    return {
        'server_start_time': SERVER_START_TIME.isoformat(),
        'server_start_timestamp': SERVER_START_TIME.timestamp(),
        'uptime_seconds': (datetime.utcnow() - SERVER_START_TIME).total_seconds(),
        'status': 'running'
    }

class AuthenticationError(Exception):
    """Excepción personalizada para errores de autenticación"""
    pass

class AuthManager:
    """Clase para gestionar la autenticación JWT"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera un hash seguro de la contraseña usando bcrypt
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        try:
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            result = password_hash.decode('utf-8')
            logger.debug(f"Hash generado para contraseña (longitud: {len(result)})")
            return result
        except Exception as e:
            logger.error(f"Error generando hash de contraseña: {str(e)}")
            raise
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash
        
        Args:
            password (str): Contraseña en texto plano
            password_hash (str): Hash almacenado (puede ser str o bytes)
            
        Returns:
            bool: True si la contraseña es correcta
        """
        try:
            # Si password_hash es string, convertir a bytes
            if isinstance(password_hash, str):
                hash_bytes = password_hash.encode('utf-8')
            else:
                hash_bytes = password_hash
            
            return bcrypt.checkpw(password.encode('utf-8'), hash_bytes)
        except Exception as e:
            logger.error(f"Error en verificación de contraseña: {str(e)}")
            return False
    
    @staticmethod
    def generate_token(user_data: dict) -> str:
        """
        Genera un token JWT para el usuario
        
        Args:
            user_data (dict): Datos del usuario (id, username, role, etc.)
            
        Returns:
            str: Token JWT
        """
        payload = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'email': user_data['email'],
            'role': user_data['role'],
            'full_name': user_data['full_name'],
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow(),
            'iss': 'niea-ejb-system',
            'server_start': SERVER_START_TIME.timestamp()  # Timestamp de inicio del servidor
        }
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verifica y decodifica un token JWT
        
        Args:
            token (str): Token JWT
            
        Returns:
            dict: Datos del usuario decodificados
            
        Raises:
            AuthenticationError: Si el token es inválido o expirado
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Verificar si el token fue generado antes del reinicio del servidor
            token_server_start = payload.get('server_start')
            if token_server_start is None:
                # Token antiguo sin server_start, invalidar
                raise AuthenticationError("Token inválido, requiere nueva autenticación")
            
            current_server_start = SERVER_START_TIME.timestamp()
            if token_server_start < current_server_start:
                # Token generado antes del reinicio del servidor
                logger.info(f"Token invalidado por reinicio del servidor. Token: {token_server_start}, Servidor: {current_server_start}")
                raise AuthenticationError("Token inválido, requiere nueva autenticación")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token inválido, requiere nueva autenticación")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Token inválido, requiere nueva autenticación")
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> dict:
        """
        Autentica un usuario con username y password
        
        Args:
            username (str): Nombre de usuario o email
            password (str): Contraseña
            
        Returns:
            dict: Datos del usuario si la autenticación es exitosa
            
        Raises:
            AuthenticationError: Si las credenciales son incorrectas
        """
        conn = None
        cursor = None
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Buscar usuario por username o email
            query = sql.SQL("""
                SELECT id, username, email, password_hash, full_name, role, is_active
                FROM niea_ejb.users 
                WHERE (username = %s OR email = %s) AND is_active = true
            """)
            
            cursor.execute(query, (username, username))
            user_row = cursor.fetchone()
            
            if not user_row:
                raise AuthenticationError("Usuario no encontrado o inactivo")
            
            # Verificar contraseña
            user_data = {
                'id': user_row[0],
                'username': user_row[1],
                'email': user_row[2],
                'password_hash': user_row[3],
                'full_name': user_row[4],
                'role': user_row[5],
                'is_active': user_row[6]
            }
            
            # Debug logging
            logger.debug(f"Usuario encontrado: {user_data['username']}")
            logger.debug(f"Hash almacenado (tipo: {type(user_data['password_hash'])}, longitud: {len(str(user_data['password_hash']))}")
            logger.debug(f"Contraseña recibida: {password}")
            
            if not AuthManager.verify_password(password, user_data['password_hash']):
                logger.error(f"Fallo verificación de contraseña para usuario: {user_data['username']}")
                raise AuthenticationError("Contraseña incorrecta")
            
            # Actualizar último login
            update_query = sql.SQL("""
                UPDATE niea_ejb.users 
                SET last_login = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """)
            cursor.execute(update_query, (user_data['id'],))
            conn.commit()
            
            # Remover password_hash de los datos retornados
            del user_data['password_hash']
            
            return user_data
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en autenticación: {str(e)}")
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError("Error interno del servidor")
        finally:
            if cursor:
                cursor.close()
            if conn:
                PostgreSQLConnection.return_connection(conn)

def token_required(f):
    """
    Decorador para proteger endpoints que requieren autenticación JWT
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_endpoint(current_user):
            return jsonify({'message': f'Hola {current_user["username"]}'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar token en headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    'status': 'error',
                    'message': 'Formato de token inválido. Use: Bearer <token>'
                }), 401
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token de acceso requerido'
            }), 401
        
        try:
            current_user = AuthManager.verify_token(token)
            return f(current_user, *args, **kwargs)
        except AuthenticationError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 401
        except Exception as e:
            logger.error(f"Error en validación de token: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor'
            }), 500
    
    return decorated

def admin_required(f):
    """
    Decorador para endpoints que requieren rol de administrador
    
    Usage:
        @app.route('/admin-only')
        @admin_required
        def admin_endpoint(current_user):
            return jsonify({'message': 'Solo administradores'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar token en headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({
                    'status': 'error',
                    'message': 'Formato de token inválido'
                }), 401
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token de acceso requerido'
            }), 401
        
        try:
            current_user = AuthManager.verify_token(token)
            
            if current_user.get('role') != 'admin':
                return jsonify({
                    'status': 'error',
                    'message': 'Acceso denegado. Se requieren privilegios de administrador'
                }), 403
            
            return f(current_user, *args, **kwargs)
        except AuthenticationError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 401
        except Exception as e:
            logger.error(f"Error en validación de admin: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor'
            }), 500
    
    return decorated

# Funciones de utilidad para crear usuarios
def create_user(username: str, email: str, password: str, full_name: str = None, role: str = 'user') -> dict:
    """
    Crea un nuevo usuario en la base de datos
    
    Args:
        username (str): Nombre de usuario único
        email (str): Email único
        password (str): Contraseña en texto plano
        full_name (str): Nombre completo (opcional)
        role (str): Rol del usuario (default: 'user')
        
    Returns:
        dict: Datos del usuario creado
        
    Raises:
        Exception: Si hay error en la creación
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hash de la contraseña
        password_hash = AuthManager.hash_password(password)
        
        # Insertar usuario
        query = sql.SQL("""
            INSERT INTO niea_ejb.users (username, email, password_hash, full_name, role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, username, email, full_name, role, is_active, created_at
        """)
        
        cursor.execute(query, (username, email, password_hash, full_name, role))
        user_row = cursor.fetchone()
        conn.commit()
        
        return {
            'id': user_row[0],
            'username': user_row[1],
            'email': user_row[2],
            'full_name': user_row[3],
            'role': user_row[4],
            'is_active': user_row[5],
            'created_at': user_row[6]
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creando usuario: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            PostgreSQLConnection.return_connection(conn)
