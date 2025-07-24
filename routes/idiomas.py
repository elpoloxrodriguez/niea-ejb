from flask import Blueprint, jsonify
from datetime import datetime
from config.database import PostgreSQLConnection
from authentication import token_required

# Definición de la función primero
def obtener_puntuacion_idiomas(cantidad):
    """Calcula la puntuación de idiomas según la cantidad"""
    if cantidad == 1:
        return 0.54  # 25% de 1.8 (1.8 * 0.25 = 0.45)
    elif cantidad == 2:
        return 1.08  # 35% de 1.8 (1.8 * 0.35 = 0.63)
    elif cantidad >= 3:
        return 1.8   # 100% de 1.8 (máximo)
    return 0.0

# Creación del Blueprint
idiomas_bp = Blueprint('idiomas', __name__, url_prefix='/v1/api')

@idiomas_bp.route('/idiomas', methods=['GET'])
@token_required
def parametros_idiomas(current_user):  # Añadido el parámetro current_user
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

        # Extraer cédulas
        try:
            cedulas = [int(c['cedula']) for c in candidatos_data]
        except (ValueError, KeyError) as e:
            return jsonify({
                "status": "error",
                "message": "Formato inválido de cédula",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }), 400

        if not cedulas:
            return jsonify({
                "status": "success",
                "count": 0,
                "data": [],
                "metadata": {"message": "No hay candidatos para evaluar"}
            }), 200

        # Consultar cantidad de idiomas por candidato
        db = PostgreSQLConnection()
        connection = None
        try:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                # Consulta para obtener idiomas
                query = """
                    SELECT ccedula, COUNT(*) as cantidad 
                    FROM ejercito.pmiidiomad 
                    WHERE ccedula IN %s
                    GROUP BY ccedula
                """
                cursor.execute(query, (tuple(cedulas),))
                resultados = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                resultados_idiomas = [dict(zip(column_names, row)) for row in resultados]

                # Procesar resultados
                puntuaciones = {}
                for item in resultados_idiomas:
                    cedula = item['ccedula']
                    cantidad = item['cantidad']
                    puntuaciones[cedula] = {
                        "puntos": obtener_puntuacion_idiomas(cantidad),
                        "cantidad_idiomas": cantidad,
                        "porcentaje": round((obtener_puntuacion_idiomas(cantidad) / 1.8 * 15), 2)
                    }

                # Preparar datos para insertar/actualizar
                datos_guardar = []
                for candidato in candidatos_data:
                    cedula = int(candidato['cedula'])
                    info = puntuaciones.get(cedula, {
                        "puntos": 0.0,
                        "cantidad_idiomas": 0,
                        "porcentaje": 0.0
                    })
                    
                    datos_guardar.append((
                        candidato['cedula'],
                        candidato['grado_actual'],
                        candidato['categoria'],
                        round(info['puntos'], 2),
                        info['cantidad_idiomas'],
                        info['porcentaje']
                    ))

                # Eliminar registros existentes para estas cédulas
                delete_query = "TRUNCATE TABLE niea_ejb.idiomas RESTART IDENTITY"
                cursor.execute(delete_query)

                # Insertar nuevos registros
                if datos_guardar:
                    insert_query = """
                        INSERT INTO niea_ejb.idiomas 
                        (cedula, grado_actual, categoria, puntos_totales, cantidad_idiomas, porcentaje)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.executemany(insert_query, datos_guardar)
                
                connection.commit()

                # Verificar cuántos registros se insertaron
                cursor.execute("SELECT COUNT(*) FROM niea_ejb.idiomas WHERE cedula::integer IN %s", (tuple(cedulas),))
                count_inserted = cursor.fetchone()[0]

        except Exception as e:
            if connection:
                connection.rollback()
            return jsonify({
                "status": "error",
                "message": "Error en la base de datos",
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
                "cantidad_idiomas": 0,
                "porcentaje": 0.0
            })
            
            resultados.append({
                "cedula": candidato['cedula'],
                "grado_actual": candidato['grado_actual'],
                "categoria": candidato['categoria'],
                "puntos_totales": round(info['puntos'], 2),
                "cantidad_idiomas": info['cantidad_idiomas'],
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
                    "descripcion": "Conocimiento de idiomas (15% del total general)",
                    "especificidad": {
                        "1_idioma": "0.54 puntos (25%)",
                        "2_idiomas": "1.08 puntos (35%)",
                        "3+_idiomas": "1.8 puntos (100%)"
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