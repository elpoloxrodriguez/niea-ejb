#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIEA-EJB Database Setup Script
==============================

Script completo para instalar todas las tablas del sistema NIEA-EJB.
Incluye instalación modular por archivos SQL y API REST para instalación remota.

Autor: Sistema NIEA-EJB
Versión: 2.0.0
"""

import sys
import os
import logging
import glob
from pathlib import Path
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

def execute_sql_file(file_path: str, description: str = None) -> bool:
    """Ejecuta un archivo SQL específico"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Leer el archivo SQL
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Ejecutar el SQL
        cursor.execute(sql_content)
        conn.commit()
        
        file_name = os.path.basename(file_path)
        desc = description or file_name
        logger.info(f"✅ {desc} ejecutado correctamente")
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error ejecutando {file_path}: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            PostgreSQLConnection.return_connection(conn)

def install_all_tables() -> bool:
    """Instala todas las tablas del sistema ejecutando archivos SQL en orden"""
    try:
        # Inicializar conexión a la base de datos
        PostgreSQLConnection.initialize(**DB_CONFIG)
        
        # Obtener la ruta del directorio SQL
        sql_dir = Path(__file__).parent / 'sql'
        
        if not sql_dir.exists():
            logger.error(f"❌ Directorio SQL no encontrado: {sql_dir}")
            return False
        
        # Obtener todos los archivos SQL ordenados
        sql_files = sorted(glob.glob(str(sql_dir / '*.sql')))
        
        if not sql_files:
            logger.error("❌ No se encontraron archivos SQL en el directorio")
            return False
        
        logger.info(f"📁 Encontrados {len(sql_files)} archivos SQL para ejecutar")
        
        # Ejecutar cada archivo SQL en orden
        for sql_file in sql_files:
            file_name = os.path.basename(sql_file)
            logger.info(f"🔄 Ejecutando: {file_name}")
            
            if not execute_sql_file(sql_file, f"Script {file_name}"):
                logger.error(f"❌ Falló la ejecución de {file_name}")
                return False
        
        logger.info("✅ Todas las tablas instaladas correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en instalación completa: {str(e)}")
        return False

def create_users_table():
    """Crea la tabla de usuarios (método legacy - usar install_all_tables)"""
    logger.info("⚠️  Usando método legacy. Se recomienda usar install_all_tables()")
    sql_file = Path(__file__).parent / 'sql' / '01_users.sql'
    return execute_sql_file(str(sql_file), "Tabla de usuarios")

def create_admin_user():
    """Crea el usuario administrador por defecto"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Primero eliminar usuario admin si existe (para recrearlo con hash correcto)
        cursor.execute("DELETE FROM niea_ejb.users WHERE username = %s", ('admin',))
        
        # Crear hash de la contraseña "admin123"
        password_hash = AuthManager.hash_password("admin123")
        
        # Insertar usuario admin
        insert_sql = """
        INSERT INTO niea_ejb.users (username, email, password_hash, full_name, role)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_sql, (
            'admin',
            'admin@niea-ejb.mil',
            password_hash,
            'Administrador Sistema',
            'admin'
        ))
        
        conn.commit()
        logger.info("✅ Usuario admin creado exitosamente")
        logger.info("   Username: admin")
        logger.info("   Password: admin123")
        logger.info("   Email: admin@niea-ejb.mil")
        
        # Verificar que el usuario se creó correctamente
        cursor.execute("SELECT username, role FROM niea_ejb.users WHERE username = %s", ('admin',))
        verify_user = cursor.fetchone()
        if verify_user:
            logger.info(f"✅ Verificación: Usuario {verify_user[0]} con rol {verify_user[1]}")
        else:
            logger.error("❌ Error: Usuario admin no se encontró después de crearlo")
            return False
        
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error creando usuario admin: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            PostgreSQLConnection.return_connection(conn)

def verify_setup():
    """Verifica que la configuración sea correcta"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar tabla y usuarios
        cursor.execute("SELECT COUNT(*) FROM niea_ejb.users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT username, email, role FROM niea_ejb.users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        logger.info("=" * 60)
        logger.info("📊 VERIFICACIÓN DE CONFIGURACIÓN")
        logger.info("=" * 60)
        logger.info(f"👥 Total de usuarios: {user_count}")
        
        if admin_user:
            logger.info(f"👤 Usuario admin encontrado:")
            logger.info(f"   - Username: {admin_user[0]}")
            logger.info(f"   - Email: {admin_user[1]}")
            logger.info(f"   - Role: {admin_user[2]}")
        else:
            logger.warning("⚠️  Usuario admin no encontrado")
        
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en verificación: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            PostgreSQLConnection.return_connection(conn)

def test_admin_authentication() -> bool:
    """Prueba la autenticación del usuario admin para verificar que funciona"""
    try:
        # Simular el proceso de autenticación
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener el hash de contraseña del usuario admin
        cursor.execute("SELECT password_hash FROM niea_ejb.users WHERE username = %s", ('admin',))
        result = cursor.fetchone()
        
        if not result:
            logger.error("❌ Usuario admin no encontrado en la base de datos")
            return False
        
        password_hash = result[0]
        
        # Verificar que la contraseña "admin123" coincida con el hash
        if AuthManager.verify_password("admin123", password_hash):
            logger.info("✅ Autenticación admin verificada correctamente")
            return True
        else:
            logger.error("❌ Fallo en verificación de contraseña admin")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en prueba de autenticación: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            PostgreSQLConnection.return_connection(conn)

def get_installation_status() -> dict:
    """Obtiene el estado actual de la instalación"""
    try:
        PostgreSQLConnection.initialize(**DB_CONFIG)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar qué tablas existen
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'niea_ejb'
            ORDER BY table_name
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        # Tablas esperadas (incluyendo todas las tablas del sistema NIEA)
        expected_tables = [
            'users', 'candidatos', 'seleccionados', 'estructura',
            'cursos_militares', 'cursos_civiles', 'idiomas', 'trabajo_institucional',
            'aspectos', 'variables', 'indicadores', 'especificidades', 'subespecificidades'
        ]
        
        # Verificar usuario admin
        admin_exists = False
        if 'users' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM niea_ejb.users WHERE username = 'admin'")
            admin_exists = cursor.fetchone()[0] > 0
        
        status = {
            'installed': len(existing_tables) == len(expected_tables),
            'tables_installed': len(existing_tables),
            'tables_expected': len(expected_tables),
            'existing_tables': existing_tables,
            'missing_tables': [t for t in expected_tables if t not in existing_tables],
            'admin_user_exists': admin_exists
        }
        
        return status
        
    except Exception as e:
        return {
            'error': str(e),
            'installed': False,
            'tables_installed': 0,
            'tables_expected': 8
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            PostgreSQLConnection.return_connection(conn)

def install_complete_system() -> dict:
    """Instala el sistema completo y retorna el resultado"""
    result = {
        'success': False,
        'message': '',
        'details': [],
        'errors': []
    }
    
    try:
        logger.info("🚀 INICIANDO INSTALACIÓN COMPLETA DEL SISTEMA NIEA-EJB")
        logger.info("=" * 70)
        
        # Paso 1: Instalar todas las tablas
        logger.info("📊 Paso 1: Instalando todas las tablas del sistema...")
        if not install_all_tables():
            result['errors'].append("Falló la instalación de las tablas")
            result['message'] = "Error en la instalación de tablas"
            return result
        
        result['details'].append("✅ Todas las tablas instaladas correctamente")
        
        # Paso 2: Crear usuario admin
        logger.info("👤 Paso 2: Creando usuario administrador...")
        if not create_admin_user():
            result['errors'].append("Falló la creación del usuario admin")
            result['message'] = "Error creando usuario administrador"
            return result
        
        result['details'].append("✅ Usuario administrador creado")
        
        # Paso 3: Verificar instalación
        logger.info("🔍 Paso 3: Verificando instalación...")
        status = get_installation_status()
        
        # Paso 4: Verificar autenticación
        logger.info("🔐 Paso 4: Verificando autenticación...")
        auth_test = test_admin_authentication()
        
        if status.get('installed', False) and auth_test:
            result['success'] = True
            result['message'] = "Sistema NIEA-EJB instalado exitosamente"
            result['details'].append(f"✅ {status['tables_installed']} tablas instaladas")
            result['details'].append("✅ Usuario admin configurado")
            result['details'].append("✅ Autenticación verificada")
            result['details'].append("🔐 Credenciales: admin / admin123")
        else:
            if not status.get('installed', False):
                result['errors'].append(f"Faltan tablas: {status.get('missing_tables', [])}")
            if not auth_test:
                result['errors'].append("Fallo en verificación de autenticación")
            result['message'] = "Instalación incompleta"
        
        logger.info("=" * 70)
        if result['success']:
            logger.info("✅ INSTALACIÓN COMPLETADA EXITOSAMENTE")
            logger.info("🔐 Credenciales de acceso:")
            logger.info("   Username: admin")
            logger.info("   Password: admin123")
        else:
            logger.error("❌ INSTALACIÓN FALLÓ")
        
        return result
        
    except Exception as e:
        result['errors'].append(str(e))
        result['message'] = f"Error crítico: {str(e)}"
        logger.error(f"❌ Error crítico en instalación: {str(e)}")
        return result
    finally:
        # NO cerrar las conexiones aquí para que sigan disponibles para la aplicación
        # PostgreSQLConnection.close_all_connections()
        pass

def main():
    """Función principal del script de configuración"""
    result = install_complete_system()
    
    if not result['success']:
        logger.error("❌ INSTALACIÓN FALLÓ")
        for error in result['errors']:
            logger.error(f"   - {error}")
        sys.exit(1)
    
    logger.info("=" * 60)

if __name__ == '__main__':
    main()
