from flask import Blueprint, jsonify
from datetime import datetime
from config.database import PostgreSQLConnection
from authentication import token_required
import json

cursos_civiles_bp = Blueprint('cursos_civiles', __name__, url_prefix='/v1/api')

@cursos_civiles_bp.route('/cursos-civiles', methods=['GET'])
@token_required
def cursos_civiles(current_user):  # Añadido el parámetro current_user
    try:
        # 1. Definición de tipos de cursos con sus parámetros
        tipos_cursos = [
            {"tipo": "Doctorados", "codigo": 19, "porcentaje": 30, "puntos": 0.72},
            {"tipo": "Maestrias", "codigo": 18, "porcentaje": 23, "puntos": 0.60},
            {"tipo": "Especializaciones", "codigo": 17, "porcentaje": 20, "puntos": 0.48},
            {"tipo": "Pregrados", "codigo": 16, "porcentaje": 15, "puntos": 0.36},
            {"tipo": "Otros", "codigo": 20, "porcentaje": 10, "puntos": 0.24,
             "subtipos": [
                 {"tipo": "Tecnico Superior Universitario", "codigo": 15, "porcentaje": 55, "puntos": 0.132},
                 {"tipo": "Diplomados", "codigo": 24, "porcentaje": 25, "puntos": 0.060},
                 {"tipo": "Otros Estudios", "codigo": 20, "porcentaje": 20, "puntos": 0.048}
             ]}
        ]

        # 2. Obtener lista de candidatos directamente de la base de datos
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
            
            cedulas = [int(c['cedula']) for c in candidatos_data]
            
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

        # 3. Consultar cursos desde la base de datos
        conn = None
        cursor = None
        try:
            conn = PostgreSQLConnection.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *, cgrado::integer, cnivel_inst::integer 
                FROM ejercito.pmipostgrd 
                WHERE ccedula = ANY(%s::integer[])
            """, (cedulas,))
            
            cursos_data = [dict(zip([col[0] for col in cursor.description], row)) 
                          for row in cursor.fetchall()]
            
            # Debug: Distribución de cnivel_inst
            distribucion = {nivel: sum(1 for c in cursos_data if c['cnivel_inst'] == nivel) 
                           for nivel in {c['cnivel_inst'] for c in cursos_data}}
            
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error en BD: {str(e)}"}), 500
        finally:
            if cursor: cursor.close()
            if conn: PostgreSQLConnection.return_connection(conn)

        # 4. Organizar cursos por cédula
        cursos_por_cedula = {}
        for curso in cursos_data:
            cedula = curso['ccedula']
            cursos_por_cedula.setdefault(cedula, []).append(curso)

        # 5. Función para calcular puntos corregida según especificaciones
        def calcular_puntos(candidato, cursos):
            puntos_totales = 0
            detalle_cursos = []
            grado_candidato = int(candidato['grado_actual'])
            
            # Variables para controlar los tipos principales aplicados
            tipos_principales_aplicados = {
                "Doctorados": False,
                "Maestrias": False,
                "Especializaciones": False,
                "Pregrados": False,
                "Otros": False
            }
            
            # Variables para controlar subtipos de "Otros"
            subtipos_otros = {
                "Tecnico Superior Universitario": False,
                "Diplomados": False,
                "Otros Estudios": False
            }
            
            # Primero procesamos los cursos principales (no Otros)
            for curso in cursos:
                cgrado = int(curso.get('cgrado', 0))
                cnivel_inst = int(curso.get('cnivel_inst', 0))
                
                # Validar coincidencia de grado
                if cgrado != grado_candidato:
                    continue
                
                # Buscar en tipos principales (excluyendo Otros)
                tipo_principal = next((t for t in tipos_cursos[:-1] if t['codigo'] == cnivel_inst), None)
                
                if tipo_principal and not tipos_principales_aplicados[tipo_principal['tipo']]:
                    detalle_cursos.append({
                        "tipo": tipo_principal['tipo'],
                        "codigo": tipo_principal['codigo'],
                        "nombre_curso": curso.get('cdescripcion', ''),
                        "puntos": tipo_principal['puntos'],
                        "cgrado": cgrado,
                        "cnivel_inst": cnivel_inst
                    })
                    puntos_totales += tipo_principal['puntos']
                    tipos_principales_aplicados[tipo_principal['tipo']] = True
            
            # Luego procesamos los cursos de tipo "Otros"
            for curso in cursos:
                cgrado = int(curso.get('cgrado', 0))
                cnivel_inst = int(curso.get('cnivel_inst', 0))
                
                # Validar coincidencia de grado
                if cgrado != grado_candidato:
                    continue
                
                # Solo procesar si es un subtipo de "Otros" y no hemos alcanzado el máximo
                if puntos_totales >= 2.4:
                    break
                    
                # Buscar en subtipos de "Otros"
                for subtipo in tipos_cursos[-1]['subtipos']:
                    if cnivel_inst == subtipo['codigo'] and not subtipos_otros[subtipo['tipo']]:
                        # Verificar que no excedamos el máximo de 0.24 para Otros
                        puntos_otros_actual = sum(c['puntos'] for c in detalle_cursos if "Otros" in c.get('tipo', ''))
                        if puntos_otros_actual + subtipo['puntos'] > 0.24:
                            continue
                            
                        detalle_cursos.append({
                            "tipo": f"Otros - {subtipo['tipo']}",
                            "codigo": subtipo['codigo'],
                            "nombre_curso": curso.get('cdescripcion', ''),
                            "puntos": subtipo['puntos'],
                            "cgrado": cgrado,
                            "cnivel_inst": cnivel_inst
                        })
                        puntos_totales += subtipo['puntos']
                        subtipos_otros[subtipo['tipo']] = True
                        break
            
            # Asegurar máximo teórico (2.4)
            puntos_totales = min(puntos_totales, 2.4)
            
            return round(puntos_totales, 3), detalle_cursos

        # 6. Procesar todos los candidatos
        resultados = []
        for candidato in candidatos_data:
            cedula = int(candidato['cedula'])
            cursos = cursos_por_cedula.get(cedula, [])
            
            puntos, detalle = calcular_puntos(candidato, cursos)
            
            # Desglose de puntos
            desglose = {
                "Doctorados": round(sum(c['puntos'] for c in detalle if c['tipo'] == "Doctorados"), 3),
                "Maestrias": round(sum(c['puntos'] for c in detalle if c['tipo'] == "Maestrias"), 3),
                "Especializaciones": round(sum(c['puntos'] for c in detalle if c['tipo'] == "Especializaciones"), 3),
                "Pregrados": round(sum(c['puntos'] for c in detalle if c['tipo'] == "Pregrados"), 3),
                "Otros": round(sum(c['puntos'] for c in detalle if "Otros" in c['tipo']), 3),
                "Tecnicos Sup Univ": round(sum(c['puntos'] for c in detalle if "Tecnico" in c['tipo']), 3),
                "Diplomados": round(sum(c['puntos'] for c in detalle if "Diplomados" in c['tipo']), 3)
            }
            
            resultados.append({
                "cedula": cedula,
                "grado_actual": candidato['grado_actual'],
                "puntos_totales": puntos,
                "desglose_puntos": desglose
            })

        # 7. Ordenar resultados
        resultados_ordenados = sorted(resultados, key=lambda x: x['puntos_totales'], reverse=True)

        # 8. Guardar resultados en la base de datos
        db = PostgreSQLConnection()
        connection = None
        count_inserted = 0
        try:
            connection = db.get_connection()
            with connection.cursor() as cursor:
                # Eliminar registros existentes
                delete_query = "TRUNCATE TABLE niea_ejb.cursos_civiles RESTART IDENTITY"
                cursor.execute(delete_query)

                # Preparar datos para insertar
                datos_guardar = []
                for resultado in resultados_ordenados:
                    datos_guardar.append((
                        resultado['cedula'],
                        resultado['grado_actual'],
                        resultado['puntos_totales'],
                        json.dumps(resultado['desglose_puntos'])
                    ))

                # Insertar nuevos registros
                if datos_guardar:
                    insert_query = """
                        INSERT INTO niea_ejb.cursos_civiles 
                        (cedula, grado_actual, puntos_totales, desglose_puntos)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.executemany(insert_query, datos_guardar)
                
                connection.commit()

                # Verificar cuántos registros se insertaron
                cedulas_list = [resultado['cedula'] for resultado in resultados_ordenados]
                cursor.execute("SELECT COUNT(*) FROM niea_ejb.cursos_civiles WHERE cedula IN %s", (tuple(cedulas_list),))
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
                "maximo_teorico": 2.4,
                "distribucion_cnivel_inst": distribucion,
                "fecha_consulta": datetime.now().isoformat(),
                "esquema_puntos": {
                    tipo['tipo']: tipo['puntos'] for tipo in tipos_cursos if tipo['tipo'] != 'Otros'
                },
                "esquema_otros": {
                    "maximo": 0.24,
                    "subtipos": tipos_cursos[4]['subtipos']
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error interno: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500