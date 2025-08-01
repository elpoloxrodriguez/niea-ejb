from flask import Blueprint, jsonify
from datetime import datetime
from config.database import PostgreSQLConnection
from authentication import token_required
import json

cursos_militares_bp = Blueprint('cursos_militares', __name__, url_prefix='/v1/api')

@cursos_militares_bp.route('/cursos-militares', methods=['GET'])
@token_required
def cursos_militares(current_user):  # Añadido el parámetro current_user
    try:
        # Definición de cursos militares con tipos
        cursos_militares = [
            {"grado_actual": 9, "categoria": "A", "grado_inmediato": 8, "curso": "R", "tipo": "obligatorio"},
            {"grado_actual": 8, "categoria": "", "grado_inmediato": 7, "curso": "S", "tipo": "obligatorio"},
            {"grado_actual": 7, "categoria": "", "grado_inmediato": 6, "curso": "T", "tipo": "obligatorio"},
            {"grado_actual": 6, "categoria": "", "grado_inmediato": 5, "curso": "U", "tipo": "obligatorio"},
            {"grado_actual": 5, "categoria": "", "grado_inmediato": 4, "curso": "V", "tipo": "obligatorio"},
            {"grado_actual": 4, "categoria": "", "grado_inmediato": 3, "curso": "M", "tipo": "obligatorio"},
            {"grado_actual": 24, "categoria": "", "grado_inmediato": 23, "curso": "R", "tipo": "obligatorio"},
            {"grado_actual": 23, "categoria": "", "grado_inmediato": 2, "curso": "S", "tipo": "obligatorio"},
            {"curso": "F", "tipo": "otros"}  # Curso adicional
        ]

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

        # Función para calcular puntos según los nuevos parámetros
        def calcular_puntos(candidato, curso):
            puntos = 0
            tipo_curso = curso.get('tipo', '')
            
            # Convertir a enteros para comparación
            grado_candidato = int(candidato['grado_actual'])
            
            if tipo_curso == 'obligatorio':
                # Puntos por grado actual (70% = 4.2 puntos)
                if 'grado_actual' in curso and grado_candidato == curso['grado_actual']:
                    puntos += 4.2
                
                # Puntos adicionales por categoría si aplica
                if curso.get('categoria') and candidato['categoria'] == curso['categoria']:
                    puntos += 0.5  # Pequeño bonus por categoría exacta
                    
            elif tipo_curso == 'otros' and curso['curso'] == 'F':
                # Puntos por otros cursos (30% = 1.8 puntos)
                puntos += 1.8
                
            return round(puntos, 2)  # Redondear a 2 decimales

        # Evaluar cada candidato
        resultados = []
        for candidato in candidatos_data:
            total_puntos = 0
            detalle_cursos = []
            
            for curso in cursos_militares:
                puntos_curso = calcular_puntos(candidato, curso)
                
                if puntos_curso > 0:
                    detalle_cursos.append({
                        "curso": curso['curso'],
                        "tipo": curso.get('tipo', ''),
                        "puntos": puntos_curso,
                        "cumple": puntos_curso > 0
                    })
                    total_puntos += puntos_curso
            
            # Asegurar que no supere el máximo de 6 puntos
            total_puntos = min(total_puntos, 6.0)
            
            resultados.append({
                "cedula": candidato['cedula'],
                "grado_actual": candidato['grado_actual'],
                "categoria": candidato['categoria'],
                "puntos_totales": round(total_puntos, 2),
                "desglose_puntos": {
                    "obligatorios": round(sum(c['puntos'] for c in detalle_cursos if c['tipo'] == 'obligatorio'), 2),
                    "otros": round(sum(c['puntos'] for c in detalle_cursos if c['tipo'] == 'otros'), 2)
                }
            })

        # Ordenar resultados de mayor a menor puntos
        resultados_ordenados = sorted(resultados, key=lambda x: x['puntos_totales'], reverse=True)

        # Guardar resultados en la base de datos
        db = PostgreSQLConnection()
        connection = None
        count_inserted = 0
        try:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                # Eliminar registros existentes
                delete_query = "TRUNCATE TABLE niea_ejb.cursos_militares RESTART IDENTITY"
                cursor.execute(delete_query)

                # Preparar datos para insertar
                datos_guardar = []
                for resultado in resultados_ordenados:
                    datos_guardar.append((
                        resultado['cedula'],
                        resultado['grado_actual'],
                        resultado['categoria'],
                        resultado['puntos_totales'],
                        json.dumps(resultado['desglose_puntos'])
                    ))

                # Insertar nuevos registros
                if datos_guardar:
                    insert_query = """
                        INSERT INTO niea_ejb.cursos_militares 
                        (cedula, grado_actual, categoria, puntos_totales, desglose_puntos)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.executemany(insert_query, datos_guardar)
                
                connection.commit()

                # Verificar cuántos registros se insertaron
                cedulas_list = [resultado['cedula'] for resultado in resultados_ordenados]
                cursor.execute("SELECT COUNT(*) FROM niea_ejb.cursos_militares WHERE cedula IN %s", (tuple(cedulas_list),))
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

        return jsonify({
            "status": "success",
            "count": len(resultados_ordenados),
            "data": resultados_ordenados,
            "metadata": {
                "esquema_puntos": {
                    "total": 6,
                    "obligatorios": {
                        "maximo": 4.2,
                        "descripcion": "Cursos requeridos por grado (70%)"
                    },
                    "otros": {
                        "maximo": 1.8,
                        "descripcion": "Otros cursos (30%)"
                    }
                },
                "fecha_consulta": datetime.now().isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Error interno al procesar la solicitud",
            "details": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500