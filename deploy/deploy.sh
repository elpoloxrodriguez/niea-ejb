#!/bin/bash

# ========================================
# SCRIPT DE DESPLIEGUE NIEA-EJB
# ========================================

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuración
APP_NAME="niea-ejb"
APP_USER="niea-ejb"
APP_DIR="/opt/niea-ejb"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="niea-ejb.service"
NGINX_CONF="/etc/nginx/sites-available/niea-ejb"
LOG_DIR="/var/log/niea-ejb"
BACKUP_DIR="/var/backups/niea-ejb"

# Función para imprimir mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que se ejecuta como root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Este script debe ejecutarse como root"
        exit 1
    fi
}

# Crear usuario del sistema
create_system_user() {
    print_status "Creando usuario del sistema..."
    if ! id "$APP_USER" &>/dev/null; then
        useradd --system --shell /bin/bash --home-dir $APP_DIR --create-home $APP_USER
        print_success "Usuario $APP_USER creado"
    else
        print_warning "Usuario $APP_USER ya existe"
    fi
}

# Instalar dependencias del sistema
install_system_dependencies() {
    print_status "Instalando dependencias del sistema..."
    apt-get update
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        postgresql-client \
        redis-tools \
        nginx \
        supervisor \
        logrotate \
        fail2ban \
        ufw
    print_success "Dependencias del sistema instaladas"
}

# Crear directorios necesarios
create_directories() {
    print_status "Creando directorios..."
    mkdir -p $APP_DIR
    mkdir -p $LOG_DIR
    mkdir -p $BACKUP_DIR
    mkdir -p /etc/ssl/certs
    mkdir -p /etc/ssl/private
    
    chown -R $APP_USER:$APP_USER $APP_DIR
    chown -R $APP_USER:$APP_USER $LOG_DIR
    chown -R $APP_USER:$APP_USER $BACKUP_DIR
    
    print_success "Directorios creados"
}

# Copiar archivos de la aplicación
deploy_application() {
    print_status "Desplegando aplicación..."
    
    # Copiar archivos
    cp -r . $APP_DIR/
    chown -R $APP_USER:$APP_USER $APP_DIR
    
    # Crear entorno virtual
    sudo -u $APP_USER python3 -m venv $VENV_DIR
    
    # Instalar dependencias Python
    sudo -u $APP_USER $VENV_DIR/bin/pip install --upgrade pip
    sudo -u $APP_USER $VENV_DIR/bin/pip install -r $APP_DIR/requirements.txt
    sudo -u $APP_USER $VENV_DIR/bin/pip install gunicorn
    
    print_success "Aplicación desplegada"
}

# Configurar variables de entorno
setup_environment() {
    print_status "Configurando variables de entorno..."
    
    if [[ ! -f "$APP_DIR/.env.production" ]]; then
        print_error "Archivo .env.production no encontrado"
        exit 1
    fi
    
    # Verificar configuración
    sudo -u $APP_USER $VENV_DIR/bin/python -c "
from config.production import validate_production_config
try:
    validate_production_config()
    print('✅ Configuración válida')
except Exception as e:
    print(f'❌ Error de configuración: {e}')
    exit(1)
"
    
    print_success "Variables de entorno configuradas"
}

# Configurar base de datos
setup_database() {
    print_status "Configurando base de datos..."
    
    # Ejecutar instalación
    sudo -u $APP_USER $VENV_DIR/bin/python -c "
import sys
sys.path.append('$APP_DIR')
from setup_database import main
main()
"
    
    print_success "Base de datos configurada"
}

# Configurar servicio systemd
setup_systemd_service() {
    print_status "Configurando servicio systemd..."
    
    cp $APP_DIR/deploy/niea-ejb.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    
    print_success "Servicio systemd configurado"
}

# Configurar Nginx
setup_nginx() {
    print_status "Configurando Nginx..."
    
    cp $APP_DIR/deploy/nginx.conf $NGINX_CONF
    ln -sf $NGINX_CONF /etc/nginx/sites-enabled/niea-ejb
    
    # Remover configuración por defecto
    rm -f /etc/nginx/sites-enabled/default
    
    # Verificar configuración
    nginx -t
    
    print_success "Nginx configurado"
}

# Configurar firewall
setup_firewall() {
    print_status "Configurando firewall..."
    
    ufw --force enable
    ufw allow ssh
    ufw allow 'Nginx Full'
    ufw allow from 10.110.100.0/24 to any port 5432  # PostgreSQL desde red interna
    
    print_success "Firewall configurado"
}

# Configurar logrotate
setup_logrotate() {
    print_status "Configurando rotación de logs..."
    
    cat > /etc/logrotate.d/niea-ejb << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF
    
    print_success "Logrotate configurado"
}

# Configurar fail2ban
setup_fail2ban() {
    print_status "Configurando fail2ban..."
    
    cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/niea-ejb-error.log

[sshd]
enabled = true
EOF
    
    systemctl enable fail2ban
    systemctl restart fail2ban
    
    print_success "Fail2ban configurado"
}

# Iniciar servicios
start_services() {
    print_status "Iniciando servicios..."
    
    systemctl start $SERVICE_NAME
    systemctl restart nginx
    
    # Verificar estado
    sleep 5
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_success "Servicio NIEA-EJB iniciado correctamente"
    else
        print_error "Error al iniciar servicio NIEA-EJB"
        systemctl status $SERVICE_NAME
        exit 1
    fi
    
    if systemctl is-active --quiet nginx; then
        print_success "Nginx iniciado correctamente"
    else
        print_error "Error al iniciar Nginx"
        systemctl status nginx
        exit 1
    fi
}

# Verificar despliegue
verify_deployment() {
    print_status "Verificando despliegue..."
    
    # Verificar health check
    sleep 10
    if curl -f http://localhost:5001/v1/api/install/health > /dev/null 2>&1; then
        print_success "Health check OK"
    else
        print_error "Health check falló"
        exit 1
    fi
    
    # Verificar autenticación
    response=$(curl -s -X POST http://localhost:5001/v1/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "admin123"}')
    
    if echo "$response" | grep -q "success"; then
        print_success "Autenticación funcional"
    else
        print_error "Error en autenticación"
        echo "$response"
        exit 1
    fi
}

# Función principal
main() {
    print_status "Iniciando despliegue de NIEA-EJB..."
    
    check_root
    create_system_user
    install_system_dependencies
    create_directories
    deploy_application
    setup_environment
    setup_database
    setup_systemd_service
    setup_nginx
    setup_firewall
    setup_logrotate
    setup_fail2ban
    start_services
    verify_deployment
    
    print_success "¡Despliegue completado exitosamente!"
    print_status "La aplicación está disponible en: https://$(hostname -f)"
    print_status "Logs disponibles en: $LOG_DIR"
    print_status "Para verificar estado: systemctl status $SERVICE_NAME"
}

# Ejecutar función principal
main "$@"
