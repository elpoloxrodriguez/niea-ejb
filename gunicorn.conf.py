"""
Configuración de Gunicorn para producción - NIEA-EJB
"""

import os
from config.production import ProductionConfig

config = ProductionConfig()

# Configuración del servidor
bind = f"{config.SERVER_HOST}:{config.SERVER_PORT}"
workers = config.GUNICORN_WORKERS
worker_class = config.GUNICORN_WORKER_CLASS
timeout = config.GUNICORN_TIMEOUT
keepalive = config.GUNICORN_KEEPALIVE

# Configuración de procesos
max_requests = 1000
max_requests_jitter = 100
preload_app = True
worker_connections = 1000

# Configuración de logging
accesslog = "/var/log/niea-ejb/gunicorn-access.log"
errorlog = "/var/log/niea-ejb/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de seguridad
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de SSL (si está habilitado)
if config.SSL_ENABLED:
    keyfile = config.SSL_KEY_PATH
    certfile = config.SSL_CERT_PATH
    ssl_version = 2  # TLSv1.2
    ciphers = "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"

# Configuración de monitoreo
def when_ready(server):
    """Callback ejecutado cuando el servidor está listo"""
    server.log.info("NIEA-EJB Server is ready. Listening on: %s", bind)

def worker_int(worker):
    """Callback ejecutado cuando un worker recibe SIGINT"""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Callback ejecutado antes de hacer fork de un worker"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Callback ejecutado después de hacer fork de un worker"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    """Callback ejecutado cuando un worker es abortado"""
    worker.log.info("Worker received SIGABRT signal")
