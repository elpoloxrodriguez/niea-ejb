from psycopg2 import sql
from database import get_db_connection, PostgreSQLConnection
from datetime import datetime

CATEGORIAS = {
    'T': 'TECNICO',
    'C': 'COMANDO',
    'S': 'TROPA PROFESIONAL',
    'A': 'ASIMILADO',
    'W': 'ASIMILADO TECNICO'
}

def obtener_candidatos_ascenso(fecha, grado, categoria):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = sql.SQL("""
            SELECT
                A.CCEDULA,
                TRIM(A.XNOMBRE1) AS xnombre1,
                TRIM(A.XNOMBRE2) AS xnombre2,
                TRIM(A.XAPELLIDO1) AS xapellido1,
                TRIM(A.XAPELLIDO2) AS xapellido2,
                A.FULT_ASCENSO,
                A.CGRADO,
                D.XDES_GRADO_A,
                TRIM(D.XDES_GRADO_C),
                A.FINGRESO,
                A.FINGRESO_FAC,
                B.CCATEGORIA,
                B.XOFICIAL,
                E.QTIEMPO,
                TRUNC((%(fecha)s::date - A.FULT_ASCENSO::date) / 365.0) AS ANOS_GRADO
            FROM
                EJERCITO.PMIPERBASD A
            JOIN EJERCITO.PMIPERSOND B ON A.CCEDULA = B.CCEDULA
            JOIN EJERCITO.EJEGRADOSM D ON A.CGRADO = D.COD_GRADO
            JOIN EJERCITO.PMIMINJUNM E ON B.CGRADO = E.CGRADO AND B.CCATEGORIA = E.CCATEGORIA
            WHERE
                TRUNC((%(fecha)s::date - A.FULT_ASCENSO::date) / 365.0) >= E.QTIEMPO
                AND A.CGRADO = %(grado)s
                AND B.xoficial = %(categoria)s
            ORDER BY
                ANOS_GRADO, CCEDULA ASC
        """)

        params = {'fecha': fecha, 'grado': grado, 'categoria': categoria}
        cursor.execute(query, params)
        resultados = cursor.fetchall()

        candidatos = []
        for row in resultados:
            # Función auxiliar para manejar fechas (puede ser datetime o string)
            def format_date(date_value):
                if date_value is None:
                    return None
                if isinstance(date_value, str):
                    return date_value[:10]  # Si ya es string, tomamos los primeros 10 caracteres
                return date_value.strftime('%Y-%m-%d')  # Si es datetime, lo formateamos

            candidato = {
                'cedula': row[0],
                'nombre_completo': f"{row[1]} {row[2] or ''} {row[3]} {row[4]}".strip(),
                'ultimo_ascenso': format_date(row[5]),
                'grado_actual': row[6],
                'descripcion_grado': row[7],
                'descripcion_grado_c': row[8],
                'fecha_ingreso': format_date(row[9]),
                'fecha_ingreso_facultad': format_date(row[10]),
                'categoria': row[11],  # B.CCATEGORIA (numérico)
                'xoficial': row[12],   # B.XOFICIAL (T, C, S, A, W)
                'tiempo_requerido': row[13],
                'anos_en_grado': float(row[14]) if row[14] is not None else 0.0,
                'categoria_descripcion': CATEGORIAS.get(row[12], 'DESCONOCIDO')
            }
            candidatos.append(candidato)

        return candidatos

    except Exception as e:
        print(f"Error al ejecutar consulta: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            PostgreSQLConnection.return_connection(conn)


import logging
from typing import List, Dict, Any

def guardar_candidatos_en_db(
    candidatos: List[Dict[str, Any]],
    fecha_consulta: str,
    grado: str,
    categoria: str
) -> bool:
    """
    Elimina todos los registros de la tabla niea_ejb.candidatos y luego inserta los nuevos candidatos.
    """
    insert_query = sql.SQL("""
        INSERT INTO niea_ejb.candidatos (
            cedula, nombre_completo, ultimo_ascenso, grado_actual, 
            descripcion_grado, descripcion_grado_c, fecha_ingreso, 
            fecha_ingreso_facultad, categoria, categoria_descripcion,
            tiempo_requerido, anos_en_grado, fecha_consulta, grado,
            categoria_original, fecha_registro
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """)
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE niea_ejb.candidatos RESTART IDENTITY")
                for candidato in candidatos:
                    cursor.execute(insert_query, (
                        str(candidato['cedula'])[:20],
                        str(candidato['nombre_completo'])[:100],
                        candidato['ultimo_ascenso'],
                        str(candidato['grado_actual'])[:10],
                        str(candidato['descripcion_grado'])[:50],
                        str(candidato['descripcion_grado_c'])[:50],
                        candidato['fecha_ingreso'],
                        candidato['fecha_ingreso_facultad'],
                        candidato['xoficial'],
                        candidato['categoria_descripcion'],
                        int(candidato['tiempo_requerido']),
                        float(candidato['anos_en_grado']),
                        fecha_consulta,
                        str(grado)[:10],
                        candidato['xoficial'],
                        datetime.now()
                    ))
                conn.commit()
        return True
    except Exception as e:
        logging.exception("Error al guardar candidatos en la base de datos")
        return False