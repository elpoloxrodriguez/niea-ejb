import psycopg2
from psycopg2 import pool
import threading

class PostgreSQLConnection:
    _connection_pool = None
    _lock = threading.Lock()
    
    @classmethod
    def initialize(cls, **kwargs):
        with cls._lock:
            if cls._connection_pool is None:
                try:
                    cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                        minconn=1,
                        maxconn=10,
                        **kwargs
                    )
                    print("Pool de conexiones inicializado correctamente")
                except Exception as e:
                    print(f"Error al inicializar pool: {str(e)}")
                    raise

    @classmethod
    def get_connection(cls):
        if cls._connection_pool is None:
            raise Exception("Pool de conexiones no inicializado. Llama a initialize() primero")
        return cls._connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        if cls._connection_pool and connection:
            cls._connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        if cls._connection_pool:
            cls._connection_pool.closeall()
            cls._connection_pool = None

def get_db_connection():
    return PostgreSQLConnection.get_connection()