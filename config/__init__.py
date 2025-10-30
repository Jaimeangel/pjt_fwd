"""
Módulo de configuración del Simulador Forward.
Gestiona las configuraciones y parámetros del sistema.
"""

# Configuraciones por defecto
DEFAULT_DATABASE_PATH = "data/simulador_forward.db"
DEFAULT_WINDOW_TITLE = "Simulador de Negociación Forward"
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800

# Configuraciones de formato
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DECIMAL_PLACES = 2
CURRENCY_DECIMAL_PLACES = 4

# Configuraciones de negocio
DEFAULT_DAYS_YEAR = 360
DEFAULT_SPREAD = 0.0010  # 10 pips
MAX_FORWARD_DAYS = 360

# Límites por defecto
DEFAULT_LENDING_LIMIT_PERCENTAGE = 0.10  # 10% del patrimonio técnico
DEFAULT_MAX_EXPOSURE_WARNING = 0.80  # 80% del límite

__all__ = [
    'DEFAULT_DATABASE_PATH',
    'DEFAULT_WINDOW_TITLE',
    'DEFAULT_WINDOW_WIDTH',
    'DEFAULT_WINDOW_HEIGHT',
    'DATE_FORMAT',
    'DATETIME_FORMAT',
    'DECIMAL_PLACES',
    'CURRENCY_DECIMAL_PLACES',
    'DEFAULT_DAYS_YEAR',
    'DEFAULT_SPREAD',
    'MAX_FORWARD_DAYS',
    'DEFAULT_LENDING_LIMIT_PERCENTAGE',
    'DEFAULT_MAX_EXPOSURE_WARNING'
]

