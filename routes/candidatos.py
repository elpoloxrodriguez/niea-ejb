from flask import Blueprint, jsonify
from psycopg2 import sql
from config.database import get_db_connection, PostgreSQLConnection
from datetime import datetime
from authentication import token_required

candidatos_bp = Blueprint('candidatos', __name__, url_prefix='/v1/api')

@candidatos_bp.route('/candidatos', methods=['GET'])
@token_required
def obtener_cedulas_candidatos(current_user):
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