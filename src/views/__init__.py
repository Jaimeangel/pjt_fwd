"""
Módulo de vistas del Simulador Forward.
Contiene las interfaces de usuario siguiendo el patrón MVC.
"""

from .main_window import MainWindow
from .forward_view import ForwardView

__all__ = [
    'MainWindow',
    'ForwardView'
]
