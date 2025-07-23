from flask import Blueprint, jsonify
from datetime import datetime
from config.database import PostgreSQLConnection

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
def parametros_trabajo_valor():
    try:
        # Obtener candidatos
        from app import app
        with app.test_client() as client:
            response = client.get('/v1/api/candidatos')
            if response.status_code != 200:
                return jsonify({
                    "status": "error",
                    "message": "No se pudo obtener los candidatos"
                }), 500
            candidatos_data = response.get_json()['data']

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
                "fecha_consulta": datetime.now().isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Error interno",
            "details": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500