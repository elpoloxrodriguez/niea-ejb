from flask import Blueprint, render_template_string, current_app
import markdown
import os
from pathlib import Path

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    """Sirve el README.md como HTML formateado en la ruta raíz."""
    
    # Intentar encontrar el README.md en varias ubicaciones posibles
    possible_paths = [
        # 1. En el directorio raíz de la aplicación (junto a app.py)
        Path(current_app.root_path).parent / 'README.md',
        # 2. En el directorio actual de la aplicación
        Path(current_app.root_path) / 'README.md',
        # 3. En el directorio del blueprint
        Path(__file__).parent.parent / 'README.md',
        # 4. En el directorio del script actual
        Path(__file__).parent / 'README.md',
    ]
    
    readme_content = None
    readme_path = None
    
    # Buscar el archivo en las ubicaciones posibles
    for path in possible_paths:
        if path.exists():
            readme_path = path
            break
    
    if readme_path:
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        except UnicodeDecodeError:
            # Fallback para diferentes codificaciones
            try:
                with open(readme_path, 'r', encoding='latin-1') as f:
                    readme_content = f.read()
            except Exception as e:
                current_app.logger.error(f"No se pudo leer el README.md: {str(e)}")
                readme_content = "Error al leer el archivo README.md"
    else:
        readme_content = "No se encontró el archivo README.md en ninguna ubicación estándar"
    
    # Configurar markdown con extensiones
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.attr_list',
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'css_class': 'highlight',
                'use_pygments': True
            }
        }
    )
    
    # Convertir markdown a HTML
    html_content = md.convert(readme_content) if readme_content else "<p>No hay contenido para mostrar</p>"
    
    # Plantilla HTML con estilos (igual que antes)
    html_template = '''<!DOCTYPE html>
<html lang="es">
<head>
       <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISTEMA NIEA-EJB - Documentación</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism-tomorrow.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #24292e;
            background-color: #ffffff;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            margin-bottom: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .content {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .content h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.5rem;
            margin: 2rem 0 1rem 0;
        }
        
        .content h2 {
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 1rem;
            margin: 1.5rem 0 1rem 0;
        }
        
        .content h3 {
            color: #7f8c8d;
            margin: 1.5rem 0 1rem 0;
        }
        
        .content p {
            margin-bottom: 1rem;
            text-align: justify;
        }
        
        .content ul, .content ol {
            margin-left: 2rem;
            margin-bottom: 1rem;
        }
        
        .content li {
            margin-bottom: 0.5rem;
        }
        
        .content code {
            background-color: #f6f8fa;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .content pre {
            background-color: #2d3748;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 5px;
            overflow-x: auto;
            margin: 1rem 0;
        }
        
        .content pre code {
            background-color: transparent;
            color: inherit;
            padding: 0;
        }
        
        .content table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        
        .content th, .content td {
            border: 1px solid #ddd;
            padding: 0.75rem;
            text-align: left;
        }
        
        .content th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        
        .badge-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
            margin: 1rem 0;
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            font-size: 0.75rem;
            font-weight: bold;
            border-radius: 0.25rem;
            text-decoration: none;
            color: white;
        }
        
        .badge-success { background-color: #28a745; }
        .badge-info { background-color: #17a2b8; }
        .badge-warning { background-color: #ffc107; color: #212529; }
        .badge-danger { background-color: #dc3545; }
        
        .footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 10px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .content {
                padding: 1rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎖️ SISTEMA NIEA-EJB</h1>
            <p>Sistema de Gestión Militar Integrado</p>
            <div class="badge-container">
                <span class="badge badge-success">Ejército Bolivariano</span>
                <span class="badge badge-info">Python Backend</span>
                <span class="badge badge-warning">PostgreSQL</span>
                <span class="badge badge-danger">JWT Auth</span>
            </div>
        </div>
        
        <div class="content">
            {{ content|safe }}
        </div>
        
        <div class="footer">
            <p><strong>Desarrollado para la Patria Grande</strong></p>
            <p>"Independencia y Patria Socialista. Viviremos y Venceremos"</p>
            <p>Mayor Andrés Ricardo Rodríguez Durán - Ejército Bolivariano de Venezuela</p>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-bash.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-json.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-python.min.js"></script>
</body>
</html>'''
    
    return render_template_string(html_template, content=html_content)