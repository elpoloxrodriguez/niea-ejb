# ========================================
# SCRIPT DE DESPLIEGUE NIEA-EJB - WINDOWS
# ========================================

param(
    [string]$InstallPath = "C:\niea-ejb",
    [string]$ServiceName = "NIEA-EJB",
    [switch]$SkipIIS = $false
)

# Configuración de colores
$Host.UI.RawUI.ForegroundColor = "White"

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Verificar permisos de administrador
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Instalar Chocolatey si no existe
function Install-Chocolatey {
    Write-Status "Verificando Chocolatey..."
    if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Status "Instalando Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Success "Chocolatey instalado"
    } else {
        Write-Success "Chocolatey ya está instalado"
    }
}

# Instalar dependencias del sistema
function Install-SystemDependencies {
    Write-Status "Instalando dependencias del sistema..."
    
    # Instalar Python
    choco install python3 -y
    
    # Instalar PostgreSQL client
    choco install postgresql -y --params '/Password:admin123'
    
    # Instalar Redis
    choco install redis-64 -y
    
    # Instalar Git
    choco install git -y
    
    # Instalar Visual C++ Build Tools
    choco install visualstudio2019buildtools -y
    choco install visualstudio2019-workload-vctools -y
    
    # Refrescar variables de entorno
    refreshenv
    
    Write-Success "Dependencias del sistema instaladas"
}

# Crear directorios necesarios
function New-Directories {
    Write-Status "Creando directorios..."
    
    $directories = @(
        $InstallPath,
        "$InstallPath\logs",
        "$InstallPath\backups",
        "$InstallPath\ssl"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "Directorios creados"
}

# Desplegar aplicación
function Deploy-Application {
    Write-Status "Desplegando aplicación..."
    
    # Copiar archivos
    Copy-Item -Path ".\*" -Destination $InstallPath -Recurse -Force -Exclude @(".git", "__pycache__", "*.pyc")
    
    # Crear entorno virtual
    Set-Location $InstallPath
    python -m venv venv
    
    # Activar entorno virtual e instalar dependencias
    & ".\venv\Scripts\Activate.ps1"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install waitress
    
    Write-Success "Aplicación desplegada"
}

# Configurar variables de entorno
function Set-EnvironmentVariables {
    Write-Status "Configurando variables de entorno..."
    
    if (!(Test-Path "$InstallPath\.env.production")) {
        Write-Error "Archivo .env.production no encontrado"
        exit 1
    }
    
    # Leer variables de entorno y configurarlas para Windows
    $envContent = Get-Content "$InstallPath\.env.production"
    foreach ($line in $envContent) {
        if ($line -match "^([^=]+)=(.*)$") {
            $name = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($name, $value, "Machine")
        }
    }
    
    # Configurar rutas específicas de Windows
    [Environment]::SetEnvironmentVariable("SSL_CERT_PATH", "$InstallPath\ssl\niea-ejb.crt", "Machine")
    [Environment]::SetEnvironmentVariable("SSL_KEY_PATH", "$InstallPath\ssl\niea-ejb.key", "Machine")
    [Environment]::SetEnvironmentVariable("LOG_FILE", "$InstallPath\logs\app.log", "Machine")
    
    Write-Success "Variables de entorno configuradas"
}

# Configurar base de datos
function Initialize-Database {
    Write-Status "Configurando base de datos..."
    
    Set-Location $InstallPath
    & ".\venv\Scripts\python.exe" setup_database.py
    
    Write-Success "Base de datos configurada"
}

# Crear servicio de Windows
function New-WindowsService {
    Write-Status "Creando servicio de Windows..."
    
    # Crear script de inicio
    $startScript = @"
@echo off
cd /d $InstallPath
call venv\Scripts\activate.bat
python -m waitress --host=0.0.0.0 --port=5001 app:app
"@
    
    $startScript | Out-File -FilePath "$InstallPath\start.bat" -Encoding ASCII
    
    # Instalar NSSM (Non-Sucking Service Manager)
    choco install nssm -y
    
    # Crear servicio
    nssm install $ServiceName "$InstallPath\start.bat"
    nssm set $ServiceName DisplayName "NIEA-EJB Sistema de Evaluación Militar"
    nssm set $ServiceName Description "Sistema de Evaluación NIEA para el Ejército"
    nssm set $ServiceName Start SERVICE_AUTO_START
    nssm set $ServiceName AppDirectory $InstallPath
    nssm set $ServiceName AppStdout "$InstallPath\logs\service.log"
    nssm set $ServiceName AppStderr "$InstallPath\logs\service-error.log"
    
    Write-Success "Servicio de Windows creado"
}

# Configurar IIS (opcional)
function Configure-IIS {
    if ($SkipIIS) {
        Write-Warning "Saltando configuración de IIS"
        return
    }
    
    Write-Status "Configurando IIS..."
    
    # Habilitar IIS
    Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole, IIS-WebServer, IIS-CommonHttpFeatures, IIS-HttpErrors, IIS-HttpLogging, IIS-RequestFiltering, IIS-StaticContent, IIS-DefaultDocument, IIS-DirectoryBrowsing -All
    
    # Instalar URL Rewrite Module
    choco install urlrewrite -y
    
    # Crear configuración de IIS
    $webConfig = @"
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="NIEA-EJB Proxy" stopProcessing="true">
          <match url="(.*)" />
          <action type="Rewrite" url="http://localhost:5001/{R:1}" />
        </rule>
      </rules>
    </rewrite>
    <httpErrors errorMode="Detailed" />
  </system.webServer>
</configuration>
"@
    
    $webConfig | Out-File -FilePath "C:\inetpub\wwwroot\web.config" -Encoding UTF8
    
    Write-Success "IIS configurado"
}

# Configurar firewall
function Configure-Firewall {
    Write-Status "Configurando firewall..."
    
    # Permitir puerto 5001
    New-NetFirewallRule -DisplayName "NIEA-EJB HTTP" -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow
    
    # Permitir puerto 443 si se usa SSL
    New-NetFirewallRule -DisplayName "NIEA-EJB HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
    
    Write-Success "Firewall configurado"
}

# Generar certificados SSL autofirmados
function New-SelfSignedCertificates {
    Write-Status "Generando certificados SSL..."
    
    $cert = New-SelfSignedCertificate -DnsName "localhost", "niea.ejercito.mil.co" -CertStoreLocation "cert:\LocalMachine\My" -KeyUsage DigitalSignature, KeyEncipherment -Type SSLServerAuthentication
    
    # Exportar certificado
    $certPath = "$InstallPath\ssl\niea-ejb.crt"
    $keyPath = "$InstallPath\ssl\niea-ejb.key"
    
    Export-Certificate -Cert $cert -FilePath $certPath -Type CERT
    
    Write-Success "Certificados SSL generados"
}

# Iniciar servicios
function Start-Services {
    Write-Status "Iniciando servicios..."
    
    # Iniciar Redis
    Start-Service redis
    
    # Iniciar servicio NIEA-EJB
    Start-Service $ServiceName
    
    # Verificar estado
    Start-Sleep -Seconds 10
    $service = Get-Service $ServiceName
    if ($service.Status -eq "Running") {
        Write-Success "Servicio NIEA-EJB iniciado correctamente"
    } else {
        Write-Error "Error al iniciar servicio NIEA-EJB"
        exit 1
    }
    
    Write-Success "Servicios iniciados"
}

# Verificar despliegue
function Test-Deployment {
    Write-Status "Verificando despliegue..."
    
    # Esperar a que el servicio esté listo
    Start-Sleep -Seconds 15
    
    try {
        # Verificar health check
        $healthResponse = Invoke-RestMethod -Uri "http://localhost:5001/v1/api/install/health" -Method Get
        if ($healthResponse.status -eq "healthy") {
            Write-Success "Health check OK"
        } else {
            Write-Error "Health check falló"
            exit 1
        }
        
        # Verificar autenticación
        $loginBody = @{
            username = "admin"
            password = "admin123"
        } | ConvertTo-Json
        
        $loginResponse = Invoke-RestMethod -Uri "http://localhost:5001/v1/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
        
        if ($loginResponse.status -eq "success") {
            Write-Success "Autenticación funcional"
        } else {
            Write-Error "Error en autenticación"
            exit 1
        }
        
    } catch {
        Write-Error "Error en verificación: $($_.Exception.Message)"
        exit 1
    }
}

# Función principal
function Main {
    Write-Status "Iniciando despliegue de NIEA-EJB en Windows..."
    
    if (!(Test-Administrator)) {
        Write-Error "Este script debe ejecutarse como Administrador"
        exit 1
    }
    
    Install-Chocolatey
    Install-SystemDependencies
    New-Directories
    Deploy-Application
    Set-EnvironmentVariables
    Initialize-Database
    New-WindowsService
    Configure-IIS
    Configure-Firewall
    New-SelfSignedCertificates
    Start-Services
    Test-Deployment
    
    Write-Success "¡Despliegue en Windows completado exitosamente!"
    Write-Status "La aplicación está disponible en: http://localhost:5001"
    Write-Status "Logs disponibles en: $InstallPath\logs"
    Write-Status "Para verificar estado: Get-Service $ServiceName"
}

# Ejecutar función principal
Main
