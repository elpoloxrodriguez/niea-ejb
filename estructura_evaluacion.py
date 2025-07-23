# estructura_evaluacion.py
from config.database import get_db_connection, PostgreSQLConnection
from psycopg2 import sql
from functools import lru_cache
from datetime import datetime

# Asegúrate de usar el esquema correcto (ej: 'public.' o 'esquema_negocio.')
ESQUEMA = 'niea_ejb.'  # Cambia esto por tu esquema o déjalo vacío si no usas esquemas

ESTRUCTURA_QUERY = sql.SQL(f"""
    SELECT 
        a.nombre AS aspecto, a.porcentaje AS porcentaje_aspecto,
        v.nombre AS variable, v.porcentaje AS porcentaje_variable, v.puntaje_maximo AS puntaje_maximo_variable,
        i.nombre AS indicador, i.porcentaje AS porcentaje_indicador, i.puntaje_maximo AS puntaje_maximo_indicador,
        e.nombre AS especificidad, e.porcentaje AS porcentaje_especificidad, e.puntaje_maximo AS puntaje_maximo_especificidad,
        s.nombre AS subespecificidad, s.porcentaje AS porcentaje_subespecificidad, s.puntaje_maximo AS puntaje_maximo_subespecificidad
    FROM {ESQUEMA}aspectos a
    LEFT JOIN {ESQUEMA}variables v ON a.aspecto_id = v.aspecto_id
    LEFT JOIN {ESQUEMA}indicadores i ON v.variable_id = i.variable_id
    LEFT JOIN {ESQUEMA}especificidades e ON i.indicador_id = e.indicador_id
    LEFT JOIN {ESQUEMA}subespecificidades s ON e.especificidad_id = s.especificidad_id
    ORDER BY a.aspecto_id, v.variable_id, i.indicador_id, e.especificidad_id, s.subespecificidad_id;
""")

@lru_cache(maxsize=1)
def obtener_estructura_completa():
    """Obtiene y cachea la estructura completa de evaluación"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(ESTRUCTURA_QUERY)
        column_names = [desc[0] for desc in cursor.description]
        resultados = cursor.fetchall()
        
        estructura = []
        for row in resultados:
            estructura.append(dict(zip(column_names, row)))
            
        return {
            'status': 'success',
            'data': estructura,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"Error al obtener estructura: {str(e)}")
        return {
            'status': 'error',
            'message': 'Error al obtener estructura',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            PostgreSQLConnection.return_connection(conn)

def actualizar_estructura_cache():
    """Limpia la caché para forzar recarga"""
    obtener_estructura_completa.cache_clear()
    return {
        'status': 'success',
        'message': 'Caché limpiado',
        'timestamp': datetime.now().isoformat()
    }