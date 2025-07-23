from flask import Blueprint, jsonify
from datetime import datetime
from estructura_evaluacion import obtener_estructura_completa, actualizar_estructura_cache

estructura_bp = Blueprint('estructura', __name__, url_prefix='/v1/api')

@estructura_bp.route('/estructura-evaluacion', methods=['GET'])
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

@estructura_bp.route('/actualizar-estructura', methods=['POST'])
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