import requests
from flask import Flask, request, jsonify
from datetime import datetime
from candidatos_ascenso import (
    obtener_candidatos_ascenso, 
    guardar_candidatos_en_db,
    CATEGORIAS
)
from database import PostgreSQLConnection, get_db_connection
from config import DB_CONFIG
from psycopg2 import sql
from estructura_evaluacion import obtener_estructura_completa, actualizar_estructura_cache

app = Flask(__name__)

# Solución 1: Inicializar la conexión directamente (solución simple)
PostgreSQLConnection.initialize(**DB_CONFIG)

# Solución 2: Alternativa moderna con @app.before_first_request (para Flask >= 2.3.0)
@app.before_request
def initialize_database():
    if not hasattr(app, 'db_initialized'):
        PostgreSQLConnection.initialize(**DB_CONFIG)
        app.db_initialized = True

@app.route('/v1/api/seleccionados', methods=['POST'])
def obtener_candidatos_api():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        data = request.get_json()
        
        # Validación de parámetros básicos
        if not data or 'fecha' not in data or 'grado' not in data or 'categoria' not in data:
            return jsonify({
                'error': 'Parámetros faltantes',
                'requeridos': {
                    'fecha': 'YYYY-MM-DD',
                    'grado': 'Código de grado',
                    'categoria': list(CATEGORIAS.keys())
                }
            }), 400
        
        # Normalización de la categoría
        categoria = data['categoria'].upper()
        
        # Validación de categoría
        if categoria not in CATEGORIAS:
            return jsonify({
                'error': 'Categoría no válida',
                'categorias_validas': CATEGORIAS,
                'recibido': data['categoria']
            }), 400
        
        # Obtener candidatos
        candidatos = obtener_candidatos_ascenso(
            fecha=data['fecha'],
            grado=data['grado'],
            categoria=categoria
        )
        
        # Guardar en DB
        guardar_exitoso = guardar_candidatos_en_db(
            candidatos=candidatos,
            fecha_consulta=data['fecha'],
            grado=data['grado'],
            categoria=categoria
        )
        
        if not guardar_exitoso:
            return jsonify({
                'error': 'Error al guardar en base de datos',
                'detalle': 'Ver logs del servidor'
            }), 500
        
        # Preparar respuesta
        response = {
            'metadata': {
                'fecha_consulta': data['fecha'],
                'grado_solicitado': data['grado'],
                'categoria_solicitada': {
                    'codigo': categoria,
                    'descripcion': CATEGORIAS[categoria]
                },
                'total_candidatos': len(candidatos),
                'guardado_db': guardar_exitoso,
                'estructura_tabla': {
                    'nombre': 'niea_ejb.candidatos',
                    'registros_nuevos': len(candidatos)
                }
            },
            'candidatos': candidatos
        }
        
        return jsonify(response), 200

    except Exception as e:
        print(f"Error en endpoint /seleccionados: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor',
            'details': str(e)
        }), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            PostgreSQLConnection.return_connection(conn)

@app.route('/v1/api/candidatos', methods=['GET'])
def obtener_cedulas_candidatos():
    conn = None
    cursor = None
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
        
        # Crear una lista de objetos con todos los campos
        candidatos = [{
            "cedula": row[0], 
            "grado_actual": row[1],
            "categoria": row[2]
        } for row in resultados]

        response = {
            "status": "success",
            "count": len(candidatos),
            "data": candidatos,
            "metadata": {
                "tabla_origen": "niea_ejb.candidatos",
                "orden": "ASC",
                "campos_consulta": ["cedula", "grado_actual", "categoria"]
            }
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"Error en endpoint /candidatos: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Error al consultar la base de datos",
            "details": str(e)
        }), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            PostgreSQLConnection.return_connection(conn)

@app.route('/v1/api/estructura-evaluacion', methods=['GET'])
def obtener_estructura():
    try:
        resultado = obtener_estructura_completa()
        if resultado['status'] == 'error':
            return jsonify(resultado), 500
            
        return jsonify({
            'status': 'success',
            'data': resultado['data'],
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Error interno al procesar la solicitud',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/v1/api/actualizar-estructura', methods=['POST'])
def actualizar_estructura():
    try:
        actualizar_estructura_cache()
        return jsonify({
            'status': 'success',
            'message': 'Cache de estructura limpiado',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Error al actualizar estructura',
            'details': str(e)
        }), 500

@app.route('/v1/api/parametros-cursos-militares', methods=['GET'])
def parametros_cursos_militares():
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

        # Obtener candidatos de la API usando el sistema interno de Flask
        with app.test_client() as client:
            response = client.get('http://localhost:5001/v1/api/candidatos')
            if response.status_code != 200:
                return jsonify({
                    "status": "error",
                    "message": "No se pudo obtener los candidatos",
                    "details": response.json
                }), 500

            candidatos_data = response.get_json()['data']

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
                "detalle_cursos": detalle_cursos,
                "desglose_puntos": {
                    "obligatorios": round(sum(c['puntos'] for c in detalle_cursos if c['tipo'] == 'obligatorio'), 2),
                    "otros": round(sum(c['puntos'] for c in detalle_cursos if c['tipo'] == 'otros'), 2)
                }
            })

        # Ordenar resultados de mayor a menor puntos
        resultados_ordenados = sorted(resultados, key=lambda x: x['puntos_totales'], reverse=True)

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
                "cursos_disponibles": cursos_militares,
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
    


    
if __name__ == '__main__':
    # Inicialización explícita para asegurar que la conexión esté lista
    PostgreSQLConnection.initialize(**DB_CONFIG)
    app.run(host='0.0.0.0', port=5001, debug=True)