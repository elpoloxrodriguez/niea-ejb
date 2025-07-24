#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para resetear la contraseña del usuario admin
Este script soluciona problemas de autenticación recreando el usuario admin
"""

import sys
import os
import logging
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).parent))

from config.database import get_db_connection, PostgreSQLConnection
from config.config import DB_CONFIG
from authentication import AuthManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def reset_admin_password():
    """Resetea la contraseña del usuario admin completamente"""
    conn = None
    cursor = None
    
    try:
        # Inicializar conexión
        PostgreSQLConnection.initialize(**DB_CONFIG)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.info("🔄 Eliminando usuario admin existente...")
        cursor.execute("DELETE FROM niea_ejb.users WHERE username = 'admin'")
        conn.commit()
        logger.info("✅ Usuario admin eliminado")
        
        # Crear nuevo hash para admin123
        new_password = "admin123"
        logger.info(f"🔐 Generando nuevo hash para contraseña: {new_password}")
        password_hash = AuthManager.hash_password(new_password)
        logger.info(f"✅ Hash generado (longitud: {len(password_hash)})")
        
        # Insertar nuevo usuario admin
        insert_sql = """
        INSERT INTO niea_ejb.users (username, email, password_hash, full_name, role, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        logger.info("📝 Insertando nuevo usuario admin...")
        cursor.execute(insert_sql, (
            'admin',
            'admin@niea-ejb.mil',
            password_hash,
            'Administrador Sistema',
            'admin',
            True
        ))
        
        conn.commit()
        logger.info("✅ Usuario admin recreado exitosamente")
        logger.info(f"   Username: admin")
        logger.info(f"   Password: {new_password}")
        logger.info(f"   Email: admin@niea-ejb.mil")
        
        # Verificar que el usuario existe
        cursor.execute("SELECT id, username, password_hash FROM niea_ejb.users WHERE username = 'admin'")
        user_data = cursor.fetchone()
        
        if not user_data:
            logger.error("❌ Usuario admin no se encontró después de crearlo")
            return False
            
        logger.info(f"✅ Usuario encontrado con ID: {user_data[0]}")
        stored_hash = user_data[2]
        
        # Verificar que la contraseña funciona
        logger.info("🔍 Verificando contraseña...")
        if AuthManager.verify_password(new_password, stored_hash):
            logger.info("✅ Verificación de contraseña exitosa")
            
            # Prueba adicional: simular autenticación completa
            logger.info("🧪 Probando autenticación completa...")
            try:
                user_auth_data = AuthManager.authenticate_user('admin', new_password)
                logger.info(f"✅ Autenticación completa exitosa para: {user_auth_data['username']}")
                return True
            except Exception as auth_error:
                logger.error(f"❌ Fallo en autenticación completa: {str(auth_error)}")
                return False
        else:
            logger.error("❌ Verificación de contraseña falló")
            return False
            
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error reseteando contraseña: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            PostgreSQLConnection.return_connection(conn)

if __name__ == '__main__':
    logger.info("🚀 Iniciando reset completo de contraseña admin...")
    logger.info("=" * 60)
    
    if reset_admin_password():
        logger.info("=" * 60)
        logger.info("🎉 RESET COMPLETADO EXITOSAMENTE")
        logger.info("🔐 Credenciales:")
        logger.info("   Username: admin")
        logger.info("   Password: admin123")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.info("=" * 60)
        logger.error("💥 RESET FALLÓ")
        logger.error("Revisa los logs anteriores para más detalles")
        logger.info("=" * 60)
        sys.exit(1)
