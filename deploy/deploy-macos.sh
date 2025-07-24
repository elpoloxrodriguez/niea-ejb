#!/bin/bash

# ========================================
# SCRIPT DE DESPLIEGUE NIEA-EJB - macOS
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
APP_USER="$(whoami)"
APP_DIR="/opt/niea-ejb"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="com.ejercito.niea-ejb"
LOG_DIR="/var/log/niea-ejb"
BACKUP_DIR="/var/backups/niea-ejb"
ARCH=$(uname -m)

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

# Detectar arquitectura
detect_architecture() {
    print_status "Detectando arquitectura del sistema..."
    
    if [[ "$ARCH" == "arm64" ]]; then
        print_status "Detectado: Apple Silicon (M1/M2/M3)"
        HOMEBREW_PREFIX="/opt/homebrew"
    elif [[ "$ARCH" == "x86_64" ]]; then
        print_status "Detectado: Intel x86_64"
        HOMEBREW_PREFIX="/usr/local"
    else
        print_error "Arquitectura no soportada: $ARCH"
        exit 1
    fi
    
    print_success "Arquitectura detectada: $ARCH"
}

# Verificar permisos
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        print_error "No ejecutar este script como root en macOS"
        exit 1
    fi
    
    print_status "Verificando permisos sudo..."
    sudo -v
}

# Instalar Homebrew si no existe
install_homebrew() {
    print_status "Verificando Homebrew..."
    
    if ! command -v brew &> /dev/null; then
        print_status "Instalando Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Configurar PATH para la sesión actual
        if [[ "$ARCH" == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        else
            echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        
        print_success "Homebrew instalado"
    else
        print_success "Homebrew ya está instalado"
    fi
}

# Instalar dependencias del sistema
install_system_dependencies() {
    print_status "Instalando dependencias del sistema..."
    
    # Actualizar Homebrew
    brew update
    
    # Instalar dependencias
    brew install python@3.11 postgresql redis nginx openssl
    
    # Instalar herramientas adicionales
    brew install --cask docker  # Para contenedores opcionales
    
    # Configurar Python
    if [[ "$ARCH" == "arm64" ]]; then
        # Apple Silicon
        export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"
        echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zprofile
    else
        # Intel
        export PATH="/usr/local/opt/python@3.11/bin:$PATH"
        echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.zprofile
    fi
    
    print_success "Dependencias del sistema instaladas"
}

# Crear directorios necesarios
create_directories() {
    print_status "Creando directorios..."
    
    sudo mkdir -p $APP_DIR
    sudo mkdir -p $LOG_DIR
    sudo mkdir -p $BACKUP_DIR
    sudo mkdir -p /etc/ssl/certs
    sudo mkdir -p /etc/ssl/private
    
    # Cambiar propietario
    sudo chown -R $APP_USER:staff $APP_DIR
    sudo chown -R $APP_USER:staff $LOG_DIR
    sudo chown -R $APP_USER:staff $BACKUP_DIR
    
    print_success "Directorios creados"
}

# Desplegar aplicación
deploy_application() {
    print_status "Desplegando aplicación..."
    
    # Copiar archivos
    sudo cp -r . $APP_DIR/
    sudo chown -R $APP_USER:staff $APP_DIR
    
    # Crear entorno virtual
    cd $APP_DIR
    python3.11 -m venv $VENV_DIR
    
    # Instalar dependencias Python
    source $VENV_DIR/bin/activate
    pip install --upgrade pip
    
    # Configurar variables de entorno para compilación en Apple Silicon
    if [[ "$ARCH" == "arm64" ]]; then
        export LDFLAGS="-L/opt/homebrew/opt/openssl/lib -L/opt/homebrew/opt/postgresql/lib"
        export CPPFLAGS="-I/opt/homebrew/opt/openssl/include -I/opt/homebrew/opt/postgresql/include"
        export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl/lib/pkgconfig:/opt/homebrew/opt/postgresql/lib/pkgconfig"
    else
        export LDFLAGS="-L/usr/local/opt/openssl/lib -L/usr/local/opt/postgresql/lib"
        export CPPFLAGS="-I/usr/local/opt/openssl/include -I/usr/local/opt/postgresql/include"
        export PKG_CONFIG_PATH="/usr/local/opt/openssl/lib/pkgconfig:/usr/local/opt/postgresql/lib/pkgconfig"
    fi
    
    pip install -r requirements.txt
    pip install gunicorn
    
    deactivate
    
    print_success "Aplicación desplegada"
}

# Configurar variables de entorno
setup_environment() {
    print_status "Configurando variables de entorno..."
    
    if [[ ! -f "$APP_DIR/.env.production" ]]; then
        print_error "Archivo .env.production no encontrado"
        exit 1
    fi
    
    # Crear archivo de configuración específico para macOS
    cat > $APP_DIR/.env.macos << EOF
# Configuración específica para macOS
HOMEBREW_PREFIX=$HOMEBREW_PREFIX
ARCH=$ARCH
SSL_CERT_PATH=/etc/ssl/certs/niea-ejb.crt
SSL_KEY_PATH=/etc/ssl/private/niea-ejb.key
LOG_FILE=$LOG_DIR/app.log
EOF
    
    print_success "Variables de entorno configuradas"
}

# Configurar base de datos
setup_database() {
    print_status "Configurando base de datos..."
    
    # Iniciar PostgreSQL
    brew services start postgresql
    
    cd $APP_DIR
    source $VENV_DIR/bin/activate
    python setup_database.py
    deactivate
    
    print_success "Base de datos configurada"
}

# Crear servicio LaunchDaemon
create_launchd_service() {
    print_status "Creando servicio LaunchDaemon..."
    
    # Crear plist para LaunchDaemon
    sudo tee /Library/LaunchDaemons/$SERVICE_NAME.plist > /dev/null << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$SERVICE_NAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV_DIR/bin/gunicorn</string>
        <string>--config</string>
        <string>$APP_DIR/gunicorn.conf.py</string>
        <string>app:app</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$APP_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$LOG_DIR/service.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/service-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$HOMEBREW_PREFIX/bin:/usr/bin:/bin</string>
        <key>PYTHONPATH</key>
        <string>$APP_DIR</string>
    </dict>
</dict>
</plist>
EOF
    
    # Configurar permisos
    sudo chown root:wheel /Library/LaunchDaemons/$SERVICE_NAME.plist
    sudo chmod 644 /Library/LaunchDaemons/$SERVICE_NAME.plist
    
    print_success "Servicio LaunchDaemon creado"
}

# Configurar Nginx
setup_nginx() {
    print_status "Configurando Nginx..."
    
    # Crear configuración de Nginx para macOS
    sudo tee $HOMEBREW_PREFIX/etc/nginx/servers/niea-ejb.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name localhost niea.ejercito.mil.co;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name localhost niea.ejercito.mil.co;

    # Configuración SSL
    ssl_certificate /etc/ssl/certs/niea-ejb.crt;
    ssl_certificate_key /etc/ssl/private/niea-ejb.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    # Configuración de proxy
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:5001/v1/api/install/health;
    }
}
EOF
    
    # Verificar configuración
    sudo nginx -t
    
    print_success "Nginx configurado"
}

# Generar certificados SSL
generate_ssl_certificates() {
    print_status "Generando certificados SSL..."
    
    # Generar certificados autofirmados
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/ssl/private/niea-ejb.key \
        -out /etc/ssl/certs/niea-ejb.crt \
        -subj "/C=CO/ST=Bogota/L=Bogota/O=Ejercito Nacional/OU=NIEA/CN=niea.ejercito.mil.co"
    
    sudo chmod 600 /etc/ssl/private/niea-ejb.key
    
    print_success "Certificados SSL generados"
}

# Configurar firewall (pfctl)
setup_firewall() {
    print_status "Configurando firewall..."
    
    # Crear reglas de firewall
    sudo tee /etc/pf.anchors/niea-ejb > /dev/null << 'EOF'
# Reglas para NIEA-EJB
pass in proto tcp from any to any port 80
pass in proto tcp from any to any port 443
pass in proto tcp from any to any port 5001
EOF
    
    # Cargar reglas
    sudo pfctl -f /etc/pf.conf
    
    print_success "Firewall configurado"
}

# Iniciar servicios
start_services() {
    print_status "Iniciando servicios..."
    
    # Iniciar Redis
    brew services start redis
    
    # Iniciar PostgreSQL
    brew services start postgresql
    
    # Cargar servicio NIEA-EJB
    sudo launchctl load /Library/LaunchDaemons/$SERVICE_NAME.plist
    
    # Iniciar Nginx
    brew services start nginx
    
    # Verificar estado
    sleep 10
    if sudo launchctl list | grep -q $SERVICE_NAME; then
        print_success "Servicio NIEA-EJB iniciado correctamente"
    else
        print_error "Error al iniciar servicio NIEA-EJB"
        exit 1
    fi
    
    print_success "Servicios iniciados"
}

# Verificar despliegue
verify_deployment() {
    print_status "Verificando despliegue..."
    
    # Verificar health check
    sleep 15
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
    print_status "Iniciando despliegue de NIEA-EJB en macOS..."
    
    detect_architecture
    check_permissions
    install_homebrew
    install_system_dependencies
    create_directories
    deploy_application
    setup_environment
    setup_database
    create_launchd_service
    setup_nginx
    generate_ssl_certificates
    setup_firewall
    start_services
    verify_deployment
    
    print_success "¡Despliegue en macOS completado exitosamente!"
    print_status "Arquitectura: $ARCH"
    print_status "La aplicación está disponible en: https://localhost"
    print_status "Logs disponibles en: $LOG_DIR"
    print_status "Para verificar estado: sudo launchctl list | grep $SERVICE_NAME"
    
    # Comandos útiles
    echo ""
    print_status "Comandos útiles:"
    echo "  Reiniciar servicio: sudo launchctl unload /Library/LaunchDaemons/$SERVICE_NAME.plist && sudo launchctl load /Library/LaunchDaemons/$SERVICE_NAME.plist"
    echo "  Ver logs: tail -f $LOG_DIR/service.log"
    echo "  Estado de servicios: brew services list"
}

# Ejecutar función principal
main "$@"
