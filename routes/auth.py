#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIEA-EJB Authentication Routes
==============================

Rutas de autenticación para login, logout y gestión de usuarios.

Autor: Sistema NIEA-EJB
Versión: 1.0.0
"""

from flask import Blueprint, request, jsonify
from authentication import AuthManager, AuthenticationError, token_required, admin_required, create_user, get_server_info
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Crear blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/v1/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint para autenticación de usuarios
    
    Body JSON:
    {
        "username": "admin",
        "password": "admin123"
    }
    
    Returns:
        JSON con token JWT y datos del usuario
    """
    try:
        # Validar datos de entrada
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos JSON requeridos'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'status': 'error',
                'message': 'Username y password son requeridos'
            }), 400
        
        # Autenticar usuario
        user_data = AuthManager.authenticate_user(username, password)
        
        # Generar token JWT
        token = AuthManager.generate_token(user_data)
        
        response = {
            'status': 'success',
            'message': 'Login exitoso',
            'data': {
                'token': token,
                'token_type': 'Bearer',
                'expires_in': 86400,  # 24 horas en segundos
                'user': {
                    'id': user_data['id'],
                    'username': user_data['username'],
                    'email': user_data['email'],
                    'full_name': user_data['full_name'],
                    'role': user_data['role']
                }
            }
        }
        
        logger.info(f"Login exitoso para usuario: {username}")
        return jsonify(response), 200
        
    except AuthenticationError as e:
        logger.warning(f"Intento de login fallido: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 401
        
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/verify', methods=['POST'])
@token_required
def verify_token(current_user):
    """
    Endpoint para verificar si un token es válido
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON con datos del usuario actual
    """
    try:
        response = {
            'status': 'success',
            'message': 'Token válido',
            'data': {
                'user': {
                    'id': current_user['user_id'],
                    'username': current_user['username'],
                    'email': current_user['email'],
                    'full_name': current_user['full_name'],
                    'role': current_user['role']
                },
                'token_info': {
                    'issued_at': current_user['iat'],
                    'expires_at': current_user['exp'],
                    'issuer': current_user['iss']
                }
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error en verificación de token: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    Endpoint para obtener el perfil del usuario actual
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON con perfil completo del usuario
    """
    try:
        response = {
            'status': 'success',
            'data': {
                'id': current_user['user_id'],
                'username': current_user['username'],
                'email': current_user['email'],
                'full_name': current_user['full_name'],
                'role': current_user['role']
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo perfil: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@auth_bp.route('/users', methods=['POST'])
@admin_required
def create_new_user(current_user):
    """
    Endpoint para crear nuevos usuarios (solo administradores)
    
    Headers:
        Authorization: Bearer <admin_token>
    
    Body JSON:
    {
        "username": "nuevo_usuario",
        "email": "usuario@niea-ejb.mil",
        "password": "password123",
        "full_name": "Nombre Completo",
        "role": "user"
    }
    
    Returns:
        JSON con datos del usuario creado
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'Campo {field} es requerido'
                }), 400
        
        # Crear usuario
        new_user = create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name'),
            role=data.get('role', 'user')
        )
        
        response = {
            'status': 'success',
            'message': 'Usuario creado exitosamente',
            'data': new_user
        }
        
        logger.info(f"Usuario creado por admin {current_user['username']}: {new_user['username']}")
        return jsonify(response), 201
        
    except Exception as e:
        logger.error(f"Error creando usuario: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error creando usuario',
            'details': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    Endpoint para logout (informativo, el token expira automáticamente)
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON confirmando logout
    """
    try:
        response = {
            'status': 'success',
            'message': 'Logout exitoso',
            'data': {
                'username': current_user['username'],
                'logout_time': 'now'
            }
        }
        
        logger.info(f"Logout para usuario: {current_user['username']}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500
