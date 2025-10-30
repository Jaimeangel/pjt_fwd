# Simulador de Negociación de Transacciones Forward

Sistema de simulación y gestión de operaciones Forward con interfaz gráfica desarrollado en Python y PySide6.

## 📋 Descripción

El Simulador Forward es una aplicación de escritorio que permite:
- Simular operaciones de compra/venta Forward
- Gestionar límites de crédito (Cop Lending)
- Controlar operaciones cambiarias
- Consultar archivo diario de operaciones
- Configurar parámetros del sistema

## 🏗️ Arquitectura

El proyecto sigue el patrón **Model-View-Controller (MVC)** con la siguiente estructura:

```
SimuladorForward/
│
├── config/                   # Configuraciones del sistema
├── data/                     # Datos y repositorios
│   ├── sqlite_repository.py
│   └── csv_415_loader.py
│
├── src/                      # Código fuente principal
│   ├── models/              # Modelos de datos (MVC)
│   │   ├── forward_model.py
│   │   ├── cop_lending_model.py
│   │   ├── control_cambios_model.py
│   │   ├── settings_model.py
│   │   └── archivo_diario_model.py
│   │
│   ├── views/               # Interfaces de usuario (MVC)
│   │   ├── main_window.py
│   │   ├── forward_view.py
│   │   ├── cop_lending_view.py
│   │   ├── control_cambios_view.py
│   │   ├── settings_view.py
│   │   └── archivo_diario_view.py
│   │
│   ├── controllers/         # Controladores (MVC)
│   │   ├── forward_controller.py
│   │   ├── cop_lending_controller.py
│   │   ├── control_cambios_controller.py
│   │   ├── settings_controller.py
│   │   └── archivo_diario_controller.py
│   │
│   ├── services/            # Servicios auxiliares
│   │   ├── forward_pricing_service.py
│   │   ├── exposure_service.py
│   │   └── client_service.py
│   │
│   ├── utils/               # Utilidades
│   │   └── signals.py
│   │
│   └── resources/           # Recursos (estilos, iconos)
│       ├── styles/
│       └── icons/
│
├── tests/                   # Pruebas unitarias
├── main.py                  # Punto de entrada
└── requirements.txt         # Dependencias
```

## 🚀 Instalación

### Requisitos previos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd SimuladorForward
```

2. Crear entorno virtual (recomendado):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 🎯 Uso

### Ejecutar la aplicación
```bash
python main.py
```

### Módulos principales

1. **Forward**: Simulación de operaciones Forward
   - Cálculo de tasas Forward
   - Registro de operaciones
   - Gestión de transacciones

2. **Cop Lending**: Gestión de límites de crédito
   - Control de límites legales
   - Cálculo de exposición
   - Alertas de límites

3. **Control de Cambios**: Monitoreo de operaciones cambiarias
   - Registro de operaciones
   - Declaraciones
   - Reportes de cumplimiento

4. **Archivo Diario**: Consulta de operaciones
   - Búsqueda y filtrado
   - Exportación de datos
   - Estadísticas diarias

5. **Settings**: Configuración del sistema
   - Parámetros generales
   - Preferencias de usuario
   - Configuración de base de datos

## 🧪 Testing

Ejecutar pruebas unitarias:
```bash
pytest tests/
```

Ejecutar con cobertura:
```bash
pytest --cov=src tests/
```

## 📚 Tecnologías

- **Python 3.9+**: Lenguaje de programación
- **PySide6**: Framework de interfaz gráfica (Qt for Python)
- **SQLite**: Base de datos local
- **Pandas**: Procesamiento de datos
- **pytest**: Framework de testing

## 🔧 Desarrollo

### Estructura de clases

Cada módulo principal sigue el patrón MVC:
- **Model**: Gestiona los datos y la lógica de negocio
- **View**: Presenta la interfaz de usuario
- **Controller**: Coordina entre Model y View

### Señales personalizadas

La aplicación utiliza señales Qt para comunicación entre componentes (ver `src/utils/signals.py`).

## 📝 Estado actual

Este es el **esqueleto inicial** del proyecto. Las clases contienen:
- Definiciones de clase con docstrings descriptivos
- Métodos vacíos con documentación
- Estructura preparada para implementación

## 🤝 Contribución

1. Implementar la lógica de los métodos vacíos
2. Agregar validaciones y manejo de errores
3. Crear pruebas unitarias
4. Diseñar la interfaz de usuario
5. Implementar estilos QSS

## 📄 Licencia

[Definir licencia del proyecto]

## 👥 Autores

[Definir autores del proyecto]

