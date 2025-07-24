from flask import Blueprint, jsonify
from datetime import datetime
from config.database import PostgreSQLConnection
from authentication import token_required

trabajo_institucional_bp = Blueprint('trabajo_institucional', __name__, url_prefix='/v1/api')

def obtener_puntuacion_trabajo_valor(cantidad):
    """Calcula la puntuación de trabajo valor institucional según la cantidad"""
    if cantidad == 1:
        return 0.45  # 25% de 3.6 (3.6 * 0.25 = 0.9)
    elif cantidad == 2:
        return 1.08  # 50% de 3.6 (3.6 * 0.5 = 1.8)
    elif cantidad >= 3:
        return 1.8   # 100% de 3.6 (máximo)
    return 0.0

@trabajo_institucional_bp.route('/trabajo_institucional', methods=['GET'])
@token_required
def parametros_trabajo_valor(current_user):  # Añadido el parámetro current_user
    try:
        # Obtener candidatos directamente de la base de datos
        from config.database import get_db_connection
        from psycopg2 import sql
        
        conn = None
        cursor = None
        candidatos_data = []
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = sql.SQL("""
                SELECT cedula, grado_actual, categoria
                FROM niea_ejb.candidatos 
                ORDER BY cedula ASC
            """)
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            # Crear lista de candidatos
            candidatos_data = [{
                "cedula": row[0], 
                "grado_actual": row[1],
                "categoria": row[2]
            } for row in resultados]
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al obtener candidatos: {str(e)}"
            }), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                PostgreSQLConnection.return_connection(conn)

        # Extraer cédulas y grados actuales
        try:
            cedulas_grados = [(int(c['cedula']), c['grado_actual']) for c in candidatos_data]
        except (ValueError, KeyError) as e:
            return jsonify({
                "status": "error",
                "message": "Formato inválido de datos de candidatos",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }), 400

        if not cedulas_grados:
            return jsonify({
                "status": "success",
                "count": 0,
                "data": [],
                "metadata": {"message": "No hay candidatos para evaluar"}
            }), 200

        # Consultar trabajos de valor institucional por candidato
        db = PostgreSQLConnection()
        connection = None
        try:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                query = """
                    SELECT ccedula, COUNT(*) as cantidad 
                    FROM ejercito.pmitraintd 
                    WHERE ccedula IN %s AND cgrado = %s
                    GROUP BY ccedula
                """
                # Ejecutar consulta para cada candidato con su grado actual
                resultados_trabajo_valor = []
                for cedula, grado_actual in cedulas_grados:
                    cursor.execute(query, (tuple([cedula]), grado_actual))
                    resultados = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    for row in resultados:
                        resultados_trabajo_valor.append(dict(zip(column_names, row)))

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": "Error en la base de datos",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
        finally:
            if connection:
                db.return_connection(connection)

        # Procesar resultados
        puntuaciones = {}
        for item in resultados_trabajo_valor:
            cedula = item['ccedula']
            cantidad = item['cantidad']
            puntuaciones[cedula] = {
                "puntos": obtener_puntuacion_trabajo_valor(cantidad),
                "cantidad_trabajos_valor": cantidad,
                "porcentaje": round((obtener_puntuacion_trabajo_valor(cantidad) / 1.8 * 15), 2)
            }

        # Preparar datos para insertar/actualizar en la tabla trabajo_institucional
        datos_guardar = []
        for candidato in candidatos_data:
            cedula = int(candidato['cedula'])
            info = puntuaciones.get(cedula, {
                "puntos": 0.0,
                "cantidad_trabajos_valor": 0,
                "porcentaje": 0.0
            })
            
            datos_guardar.append((
                candidato['cedula'],
                candidato['grado_actual'],
                candidato['categoria'],
                round(info['puntos'], 2),
                info['cantidad_trabajos_valor'],
                info['porcentaje']
            ))

        # Guardar resultados en la base de datos
        db = PostgreSQLConnection()
        connection = None
        count_inserted = 0
        try:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                # Eliminar registros existentes
                delete_query = "TRUNCATE TABLE niea_ejb.trabajo_institucional RESTART IDENTITY"
                cursor.execute(delete_query)

                # Insertar nuevos registros
                if datos_guardar:
                    insert_query = """
                        INSERT INTO niea_ejb.trabajo_institucional 
                        (cedula, grado_actual, categoria, puntos_totales, cantidad_trabajos_valor, porcentaje)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.executemany(insert_query, datos_guardar)
                
                connection.commit()

                # Verificar cuántos registros se insertaron
                cedulas_list = [int(c['cedula']) for c in candidatos_data]
                cursor.execute("SELECT COUNT(*) FROM niea_ejb.trabajo_institucional WHERE cedula IN %s", (tuple(cedulas_list),))
                count_inserted = cursor.fetchone()[0]

        except Exception as e:
            if connection:
                connection.rollback()
            return jsonify({
                "status": "error",
                "message": "Error al guardar en la base de datos",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
        finally:
            if connection:
                db.return_connection(connection)

        # Preparar respuesta
        resultados = []
        for candidato in candidatos_data:
            cedula = int(candidato['cedula'])
            info = puntuaciones.get(cedula, {
                "puntos": 0.0,
                "cantidad_trabajos_valor": 0,
                "porcentaje": 0.0
            })
            
            resultados.append({
                "cedula": candidato['cedula'],
                "grado_actual": candidato['grado_actual'],
                "categoria": candidato['categoria'],
                "puntos_totales": round(info['puntos'], 2),
                "cantidad_trabajos_valor": info['cantidad_trabajos_valor'],
                "porcentaje": info['porcentaje']
            })

        # Ordenar resultados
        resultados_ordenados = sorted(resultados, key=lambda x: x['puntos_totales'], reverse=True)

        return jsonify({
            "status": "success",
            "count": len(resultados_ordenados),
            "data": resultados_ordenados,
            "metadata": {
                "esquema_puntos": {
                    "total": 1.8,
                    "descripcion": "Trabajo de valor institucional (15% del total general)",
                    "especificidad": {
                        "1_trabajo": "0.45 puntos (25%)",
                        "2_trabajos": "0.63 puntos (35%)",
                        "3+_trabajos": "0.72 puntos (40%)"
                    }
                },
                "fecha_consulta": datetime.now().isoformat(),
                "registros_guardados": count_inserted
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Error interno",
            "details": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500