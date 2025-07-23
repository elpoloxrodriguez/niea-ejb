import psycopg2
from psycopg2 import pool
import threading

class PostgreSQLConnection:
    """
    Clase para gestionar un pool de conexiones a PostgreSQL de forma segura y eficiente.
    Utiliza un pool de conexiones para optimizar el acceso concurrente a la base de datos.
    """
    _connection_pool = None  # Pool de conexiones compartido por toda la aplicación
    _lock = threading.Lock() # Lock para asegurar inicialización thread-safe

    @classmethod
    def initialize(cls, **kwargs):
        """
        Inicializa el pool de conexiones si aún no ha sido creado.
        Recibe los parámetros de conexión como argumentos clave-valor.
        """
        with cls._lock:
            if cls._connection_pool is None:
                try:
                    cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                        minconn=1,      # Número mínimo de conexiones abiertas
                        maxconn=10,     # Número máximo de conexiones abiertas
                        **kwargs
                    )
                    print("✅ Pool de conexiones a PostgreSQL inicializado correctamente.")
                except Exception as e:
                    print(f"❌ Error al inicializar pool: {str(e)}")
                    raise

    @classmethod
    def get_connection(cls):
        """
        Obtiene una conexión del pool.
        Lanza una excepción si el pool no ha sido inicializado.
        """
        if cls._connection_pool is None:
            raise Exception("Pool de conexiones no inicializado. Llama a initialize() primero.")
        return cls._connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        """
        Devuelve una conexión al pool para que pueda ser reutilizada.
        """
        if cls._connection_pool and connection:
            cls._connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        """
        Cierra todas las conexiones del pool y libera los recursos.
        """
        if cls._connection_pool:
            cls._connection_pool.closeall()
            cls._connection_pool = None

def get_db_connection():
    """
    Función de ayuda para obtener una conexión a la base de datos.
    """
    return PostgreSQLConnection.get_connection()