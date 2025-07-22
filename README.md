# 🇻🇪 SISTEMA NIEA

<div align="center">

![Badge](https://img.shields.io/badge/Ejército_Bolivariano-Sistema_NIEA-red?style=for-the-badge)
![Badge](https://img.shields.io/badge/Python-Backend-blue?style=for-the-badge&logo=python)
![Badge](https://img.shields.io/badge/Angular-Frontend-red?style=for-the-badge&logo=angular)
![Badge](https://img.shields.io/badge/PostgreSQL-Database-blue?style=for-the-badge&logo=postgresql)

**Matriz de Evaluación Integral (MEI) del Ejército Bolivariano**

</div>

---

## 📋 Descripción

**SISTEMA NIEA** es una solución informática robusta y especializada, diseñada para facilitar y optimizar la evaluación integral de las unidades del Ejército Bolivariano. Este sistema proporciona herramientas avanzadas para la recopilación, procesamiento y análisis de datos, garantizando un proceso de evaluación eficaz, eficiente y estandarizado según los protocolos militares.

## 🚀 Tecnologías Utilizadas

### Backend
- **🐍 Python**: Lenguaje de programación principal para el desarrollo del servidor
- **🌐 API RESTful**: Arquitectura de comunicación entre servicios con endpoints especializados
- **🐘 PostgreSQL**: Sistema de gestión de base de datos relacional potente y escalable

### Frontend
- **🅰️ Angular**: Framework moderno para interfaces de usuario interactivas y dinámicas

## 🛠️ Instalación

### Prerrequisitos
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Angular CLI

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/elpoloxrodriguez/niea-ejb
   cd NIEA-EJB
   ```

2. **Configuración del Backend**
   ```bash
   # Crear entorno virtual
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   
   # Instalar dependencias
   pip install -r requirements.txt
   
   # Configurar base de datos
   psql -U postgres -c "CREATE DATABASE niea_db;"
   ```

3. **Configuración del Frontend**
   ```bash
   # Navegar al directorio del frontend
   cd frontend
   
   # Instalar dependencias
   npm install
   ```

## 🚦 Uso del Sistema

### Iniciar el Backend
```bash
# Desde el directorio raíz del proyecto
python3 api.py
```
*El servidor estará disponible en: `http://localhost:5000`*

### Iniciar el Frontend
```bash
# Desde el directorio del frontend
ng serve
```
*La aplicación estará disponible en: `http://localhost:4200`*

## 📊 Funcionalidades Principales

- ✅ **Evaluación Integral**: Sistema completo de matriz de evaluación
- 📈 **Análisis de Datos**: Herramientas avanzadas de análisis y reportes
- 🔒 **Seguridad**: Autenticación y autorización robusta
- 📱 **Interfaz Responsive**: Compatible con dispositivos móviles y desktop
- 📄 **Generación de Reportes**: Exportación de datos en múltiples formatos

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
