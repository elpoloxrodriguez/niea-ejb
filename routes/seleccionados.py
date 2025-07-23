from flask import Blueprint, jsonify, request
from datetime import datetime
from candidatos_ascenso import (
    obtener_candidatos_ascenso, 
    guardar_candidatos_en_db,
    CATEGORIAS
)
from database import get_db_connection, PostgreSQLConnection

seleccionados_bp = Blueprint('seleccionados', __name__, url_prefix='/v1/api')

@seleccionados_bp.route('/seleccionados', methods=['POST'])
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