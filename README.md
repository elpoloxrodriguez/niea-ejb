# 🇻🇪 SISTEMA NIEA-EJB

<div align="center">

![Badge](https://img.shields.io/badge/Ejército_Bolivariano-Sistema_NIEA--EJB-red?style=for-the-badge)
![Badge](https://img.shields.io/badge/Python-Backend-blue?style=for-the-badge&logo=python)
![Badge](https://img.shields.io/badge/Flask-Framework-green?style=for-the-badge&logo=flask)
![Badge](https://img.shields.io/badge/PostgreSQL-Database-blue?style=for-the-badge&logo=postgresql)
![Badge](https://img.shields.io/badge/JWT-Authentication-orange?style=for-the-badge)

**Sistema de Gestión Militar Integrado con Autenticación JWT**

</div>

---

## 📋 Descripción

**SISTEMA NIEA-EJB** es una solución informática robusta y especializada, diseñada para facilitar y optimizar la evaluación integral de los profesionales militares que son candidatos para ascenso en el Ejército Bolivariano. Este sistema proporciona herramientas avanzadas para la recopilación, procesamiento y análisis de datos, garantizando un proceso de evaluación eficaz, eficiente y estandarizado según los protocolos militares.

### ✨ Características Principales
- 🔐 **Autenticación JWT**: Sistema de autenticación seguro con tokens JWT
- 🛠️ **Instalación Automatizada**: API REST para instalación completa del sistema
- 📊 **Estructura de Evaluación**: Sistema completo de aspectos, variables, indicadores, especificidades y subespecificidades
- 🔒 **APIs Protegidas**: Todas las APIs requieren autenticación JWT
- 📁 **Instalación Modular**: Scripts SQL organizados por tabla

## 🚀 Tecnologías Utilizadas

### Backend
- **🐍 Python 3.8+**: Lenguaje de programación principal
- **🌐 Flask**: Framework web ligero y potente
- **🔐 PyJWT**: Manejo de tokens JWT para autenticación
- **🔒 bcrypt**: Hashing seguro de contraseñas
- **🌐 API RESTful**: Arquitectura de comunicación entre servicios

### Base de Datos
- **🐘 PostgreSQL 12+**: Sistema de gestión de base de datos relacional
- **📊 Estructura NIEA**: Tablas especializadas para evaluación militar

## 🛠️ Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/elpoloxrodriguez/niea-ejb
   cd NIEA-EJB
   ```

2. **Configurar entorno virtual**
   ```bash
   # Crear entorno virtual
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar PostgreSQL**
   ```bash
   # Crear base de datos
   psql -U postgres -c "CREATE DATABASE niea_db;"
   
   # Configurar variables de entorno (opcional)
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=niea_db
   export DB_USER=postgres
   export DB_PASSWORD=tu_password
   export SECRET_KEY=tu_clave_secreta_jwt
   ```

5. **Iniciar el servidor**
   ```bash
   python3 app.py
   ```
   *El servidor estará disponible en: `http://localhost:5001`*

## 🚀 Instalación Automática del Sistema

### Método 1: API REST (Recomendado)

```bash
# Instalar todas las tablas y datos iniciales
curl -X POST http://localhost:5001/v1/api/install \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Respuesta exitosa:**
```json
{
  "status": "success",
  "message": "Sistema instalado correctamente",
  "data": {
    "installation_completed": true,
    "details": [
      "✅ Todas las tablas instaladas correctamente",
      "✅ Usuario administrador creado",
      "✅ Datos iniciales cargados"
    ]
  }
}
```

### Método 2: Script Python

```bash
# Ejecutar instalación desde línea de comandos
python3 setup_database.py
```

### Verificar Instalación

```bash
# Verificar estado de la instalación
curl http://localhost:5001/v1/api/install/status
```

```bash
# Verificar salud del sistema
curl http://localhost:5001/v1/api/install/health
```

## API Endpoints

### Autenticación

#### POST /v1/api/auth/login
Autenticación de usuario y obtención de token JWT.

```bash
curl -X POST http://localhost:5001/v1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Respuesta exitosa:**
```json
{
  "status": "success",
  "count": 150,
  "data": [
    {
      "cedula": "12345678",
      "grado_actual": "TTE",
      "categoria": "OFICIAL"
    }
  ],
  "metadata": {
    "tabla_origen": "niea_ejb.candidatos",
    "orden": "ASC",
    "campos_consulta": ["cedula", "grado_actual", "categoria"]
  }
}
```

### Seleccionados

#### POST /v1/api/seleccionados
Obtener y procesar candidatos para ascenso según criterios específicos.

```bash
curl -X POST http://localhost:5001/v1/api/seleccionados \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2025-01-15",
    "grado": "TTE",
    "categoria": "OFICIAL"
  }'
```

**Parámetros requeridos:**
- `fecha`: Fecha de consulta (YYYY-MM-DD)
- `grado`: Código del grado militar
- `categoria`: Categoría (OFICIAL, SUBOFICIAL, etc.)

**Respuesta exitosa:**
```json
{
  "metadata": {
    "fecha_consulta": "2025-01-15",
    "grado_solicitado": "TTE",
    "categoria_solicitada": {
      "codigo": "OFICIAL",
      "descripcion": "Oficiales del Ejército"
    },
    "total_candidatos": 25,
    "guardado_db": true,
    "estructura_tabla": {
      "nombre": "niea_ejb.candidatos",
      "registros_nuevos": 25
    }
  },
  "candidatos": [
    {
      "cedula": "12345678",
      "nombre_completo": "Juan Pérez",
      "grado_actual": "TTE",
      "anos_en_grado": 3.5
    }
  ]
}
```

### Estructura de Evaluación

#### GET /v1/api/estructura-evaluacion
Obtener la estructura completa de evaluación NIEA.

```bash
curl -X GET http://localhost:5001/v1/api/estructura-evaluacion
```

**Respuesta exitosa:**
```json
{
  "status": "success",
  "data": {
    "aspectos": [
      {
        "id": 1,
        "nombre": "Liderazgo",
        "descripcion": "Capacidad de liderazgo militar",
        "peso": 25
      }
    ],
    "variables": [
      {
        "id": 1,
        "aspecto_id": 1,
        "nombre": "Iniciativa",
        "descripcion": "Capacidad de tomar iniciativa"
      }
    ]
  },
  "timestamp": "2025-07-23T22:45:00"
}
```

#### POST /v1/api/actualizar-estructura
Actualizar cache de estructura de evaluación.

```bash
curl -X POST http://localhost:5001/v1/api/actualizar-estructura
```

### Instalación del Sistema

#### POST /v1/api/install
Instalación completa del sistema NIEA-EJB.

```bash
curl -X POST http://localhost:5001/v1/api/install \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### GET /v1/api/install/status
Verificar estado de instalación del sistema.

```bash
curl -X GET http://localhost:5001/v1/api/install/status
```

#### GET /v1/api/install/health
Verificar salud del sistema.

```bash
curl -X GET http://localhost:5001/v1/api/install/health
```

#### POST /v1/api/install/reset
Reset completo del sistema (requiere confirmación).

```bash
curl -X POST http://localhost:5001/v1/api/install/reset \
  -H "Content-Type: application/json" \
  -d '{
    "confirm_reset": true,
    "reset_password": "MIA_INTELLIGENCE_NIEA_2025"
  }'
```

### Resumen de Endpoints

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/v1/api/auth/login` | POST | Iniciar sesión | No |
| `/v1/api/auth/verify` | POST | Verificar token | Sí |
| `/v1/api/auth/profile` | GET | Perfil del usuario | Sí |
| `/v1/api/auth/create-user` | POST | Crear usuario | Sí (Admin) |
| `/v1/api/auth/logout` | POST | Cerrar sesión | Sí |
| `/v1/api/candidatos` | GET | Obtener candidatos | Sí |
| `/v1/api/seleccionados` | POST | Procesar candidatos | Sí |
| `/v1/api/estructura-evaluacion` | GET | Estructura NIEA | No |
| `/v1/api/actualizar-estructura` | POST | Actualizar cache | No |
| `/v1/api/install` | POST | Instalar sistema | No |
| `/v1/api/install/status` | GET | Estado instalación | No |
| `/v1/api/install/health` | GET | Salud del sistema | No |
| `/v1/api/install/reset` | POST | Reset sistema | No |

## 🚀 Despliegue a Producción

### Requisitos del Sistema

#### Hardware Mínimo
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disco**: 50 GB SSD
- **Red**: Conexión estable a base de datos PostgreSQL

#### Software Requerido
- **OS**: Ubuntu 20.04 LTS o superior
- **Python**: 3.8+
- **PostgreSQL**: 12+
- **Redis**: 6.0+ (opcional, para cache)
- **Nginx**: 1.18+
- **Certificados SSL**: Para HTTPS

### Preparación del Entorno

#### 1. Configurar Variables de Entorno

Editar el archivo `.env.production` con los valores específicos de producción:

```bash
# Copiar archivo de ejemplo
cp .env.production .env.production.local

# Editar configuración
nano .env.production.local
```

**Variables críticas a configurar:**
```bash
# Base de datos
DB_HOST=127.0.0.1
DB_NAME=ejercito
DB_USER=ejercito
DB_PASSWORD=TU_PASSWORD_SEGURO

# JWT (CAMBIAR OBLIGATORIAMENTE)
JWT_SECRET_KEY=TU_CLAVE_SECRETA_SUPER_SEGURA_2025

# SSL
SSL_CERT_PATH=/etc/ssl/certs/niea-ejb.crt
SSL_KEY_PATH=/etc/ssl/private/niea-ejb.key

# Email (opcional)
SMTP_PASSWORD=tu_password_smtp
```

#### 2. Preparar Certificados SSL

```bash
# Generar certificados autofirmados (desarrollo)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/niea-ejb.key \
  -out /etc/ssl/certs/niea-ejb.crt

# O usar certificados de CA válida (recomendado)
sudo cp tu-certificado.crt /etc/ssl/certs/niea-ejb.crt
sudo cp tu-clave-privada.key /etc/ssl/private/niea-ejb.key
sudo chmod 600 /etc/ssl/private/niea-ejb.key
```

### Despliegue Automatizado

#### Opción 1: Script de Despliegue Completo

```bash
# Ejecutar como root
sudo ./deploy/deploy.sh
```

Este script realiza:
- ✅ Instalación de dependencias del sistema
- ✅ Creación de usuario del sistema
- ✅ Configuración de entorno virtual Python
- ✅ Instalación de la aplicación
- ✅ Configuración de base de datos
- ✅ Configuración de servicios systemd
- ✅ Configuración de Nginx
- ✅ Configuración de firewall
- ✅ Configuración de logs y monitoreo
- ✅ Verificación del despliegue

### APIs de Instalación (No requieren JWT)

| Endpoint | Método | Descripción |
|----------|--------|-----------|
| `/v1/api/install` | POST | Instalar sistema completo |
| `/v1/api/install/status` | GET | Estado de instalación |
| `/v1/api/install/health` | GET | Salud del sistema |
| `/v1/api/install/reset` | POST | Resetear sistema (placeholder) |

## 📊 Estructura de Base de Datos

### Tablas del Sistema NIEA

1. **users** - Usuarios del sistema
2. **candidatos** - Información de candidatos
3. **seleccionados** - Personal seleccionado
4. **estructura** - Estructura organizacional
5. **cursos_militares** - Cursos de formación militar
6. **cursos_civiles** - Cursos de formación civil
7. **idiomas** - Competencias en idiomas
8. **trabajo_institucional** - Trabajo institucional
9. **aspectos** - Aspectos de evaluación
10. **variables** - Variables de medición
11. **indicadores** - Indicadores de evaluación
12. **especificidades** - Especificidades de evaluación
13. **subespecificidades** - Subespecificidades detalladas

### Estructura de Evaluación NIEA

```
Aspectos
├── Variables
│   ├── Indicadores
│   │   ├── Especificidades
│   │   │   └── Subespecificidades
```

## 🔧 Funcionalidades Principales

- 🔐 **Autenticación JWT**: Sistema de autenticación seguro con tokens de 24 horas
- 🛠️ **Instalación Automatizada**: API REST para instalación completa del sistema
- 📊 **Estructura de Evaluación**: Sistema jerárquico completo de evaluación militar
- 🔒 **APIs Protegidas**: Todas las APIs principales requieren autenticación JWT
- 📁 **Instalación Modular**: Scripts SQL organizados por tabla para fácil mantenimiento
- 👤 **Gestión de Usuarios**: Creación y gestión de usuarios con roles
- 🔍 **Verificación de Sistema**: Endpoints para verificar estado y salud del sistema
- 🔄 **Reset de Contraseña**: Script automatizado para solucionar problemas de autenticación

## 🛠️ Mantenimiento del Sistema

### Resetear Contraseña de Administrador

Si no puedes hacer login con las credenciales por defecto:

```bash
python3 reset_admin_password.py
```

**Salida esperada:**
```
🚀 Iniciando reset completo de contraseña admin...
============================================================
🔄 Eliminando usuario admin existente...
✅ Usuario admin eliminado
🔐 Generando nuevo hash para contraseña: admin123
✅ Hash generado (longitud: 60)
📝 Insertando nuevo usuario admin...
✅ Usuario admin recreado exitosamente
✅ Usuario encontrado con ID: X
🔍 Verificando contraseña...
✅ Verificación de contraseña exitosa
🧪 Probando autenticación completa...
✅ Autenticación completa exitosa para: admin
============================================================
🎉 RESET COMPLETADO EXITOSAMENTE
🔐 Credenciales:
   Username: admin
   Password: admin123
============================================================
```

### Verificación de Funcionamiento

Después del reset, verifica que la autenticación funcione:

```bash
# Probar login
curl -X POST http://localhost:5001/v1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Respuesta esperada:**
```json
{
  "status": "success",
  "message": "Login exitoso",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
      "id": 4,
      "username": "admin",
      "email": "admin@niea-ejb.mil",
      "full_name": "Administrador Sistema",
      "role": "admin"
    }
  }
}
```

#### 📁 Archivos Clave
- `authentication.py` - Módulo de autenticación JWT
- `routes/auth.py` - Endpoints de autenticación
- `routes/install.py` - API de instalación
- `setup_database.py` - Lógica de instalación
- `reset_admin_password.py` - Script de reset de contraseña
- `sql/` - Scripts SQL modulares (13 archivos)

#### 🔐 Estado Actual
- **Sistema**: Completamente funcional
- **Autenticación**: Operativa con JWT
- **Base de Datos**: 13 tablas instaladas
- **APIs**: Todas protegidas y funcionales
- **Documentación**: Completa y actualizada

### Comandos de Verificación Rápida

```bash
# 1. Verificar instalación
curl http://localhost:5001/v1/api/install/status

# 2. Verificar salud del sistema
curl http://localhost:5001/v1/api/install/health

# 3. Login admin
curl -X POST http://localhost:5001/v1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 4. Probar API protegida (usar token del paso 3)
curl -X GET http://localhost:5001/v1/api/candidatos \
  -H "Authorization: Bearer TU_TOKEN_JWT"
```

## 🤝 Contribución

Las contribuciones son bienvenidas y valoradas. Para contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 👨‍💼 Autor

**Mayor Andrés Ricardo Rodríguez Durán**
- 📧 Email: [elpoloxrodriguez@gmail.com](mailto:elpoloxrodriguez@gmail.com)
- 📱 Teléfono: +58 412-996-7096
- 🏛️ Ejército Bolivariano de Venezuela

## 🏢 Colaboración Empresarial

Este proyecto ha sido desarrollado en colaboración con:

**BUNKER TECHNOLOGIES SOLUTIONS C.A**
- Empresa especializada en soluciones tecnológicas
- Soporte técnico y desarrollo de sistemas

---

## 📜 Licencia

Este proyecto está desarrollado para uso exclusivo del Ejército Bolivariano de Venezuela.

---

<div align="center">

**Desarrollado para la Patria Grande**

*"Independencia y Patria Socialista. Viviremos y Venceremos"*

</div>
