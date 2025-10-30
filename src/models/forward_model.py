"""
Modelo para operaciones Forward.
Gestiona los datos y la lógica de negocio relacionada con las transacciones Forward.
"""

from typing import Optional, Dict, Any, List
from datetime import date
import pandas as pd


class ForwardDataModel:
    """
    Modelo de datos para el estado del 415 y exposiciones.
    
    Responsabilidades:
    - Almacenar dataset del archivo 415
    - Gestionar información de corte y estado del 415
    - Calcular outstanding por cliente
    - Gestionar operaciones vigentes por cliente
    
    Estados contemplados:
    - 415 no cargado
    - Headers inválidos
    - CSV mal formateado
    """
    
    def __init__(self):
        """
        Inicializa el modelo de datos Forward.
        
        Estado inicial:
        - dataset_415: None (no cargado)
        - corte_415: None
        - estado_415: "no_cargado"
        - outstanding_por_cliente: dict vacío
        - ops_vigentes_por_cliente: dict vacío
        """
        self.dataset_415: Optional[pd.DataFrame] = None
        self.corte_415: Optional[date] = None
        self.estado_415: str = "no_cargado"  # valores: "no_cargado", "valido", "headers_invalidos", "formato_invalido"
        self.outstanding_por_cliente: Dict[str, float] = {}
        self.ops_vigentes_por_cliente: Dict[str, List[Dict[str, Any]]] = {}
    
    def load_415(self, file_path: str) -> tuple[bool, str]:
        """
        Carga el archivo 415 desde la ruta especificada.
        
        Valida:
        - Existencia del archivo
        - Formato CSV válido
        - Headers requeridos
        - Tipos de datos esperados
        
        Args:
            file_path: Ruta al archivo CSV formato 415
            
        Returns:
            Tupla (exito: bool, mensaje: str)
            - Si éxito: actualiza dataset_415, corte_415, estado_415="valido"
            - Si falla: estado_415="headers_invalidos" o "formato_invalido"
        
        Side effects:
            - Actualiza self.dataset_415
            - Actualiza self.corte_415 (extraído del archivo)
            - Actualiza self.estado_415
            - Recalcula outstanding_por_cliente
            - Recalcula ops_vigentes_por_cliente
        """
        pass
    
    def get_outstanding(self, nit: str) -> float:
        """
        Obtiene el outstanding (exposición vigente) de un cliente.
        
        Args:
            nit: NIT del cliente
            
        Returns:
            Monto del outstanding en COP. Retorna 0.0 si:
            - 415 no está cargado
            - Cliente no existe
            - Cliente no tiene operaciones vigentes
        """
        pass
    
    def get_ops_vigentes(self, nit: str) -> List[Dict[str, Any]]:
        """
        Obtiene las operaciones vigentes de un cliente.
        
        Estructura de cada operación:
        {
            'id_operacion': str,
            'fecha_inicio': date,
            'fecha_vencimiento': date,
            'nominal_usd': float,
            'tasa_forward': float,
            'punta_cliente': str,  # 'compra' o 'venta'
            'fair_value': float,
            'derecho': float,
            'obligacion': float,
            ...otros campos del 415
        }
        
        Args:
            nit: NIT del cliente
            
        Returns:
            Lista de operaciones vigentes. Lista vacía si:
            - 415 no cargado
            - Cliente no existe
            - Cliente sin operaciones vigentes
        """
        pass
    
    def get_all_clients(self) -> List[str]:
        """
        Obtiene lista de todos los NITs con operaciones en el 415.
        
        Returns:
            Lista de NITs (strings). Lista vacía si 415 no cargado.
        """
        pass
    
    def get_corte_415(self) -> Optional[date]:
        """
        Obtiene la fecha de corte del archivo 415.
        
        Returns:
            Fecha de corte o None si no hay 415 cargado.
        """
        pass
    
    def get_estado_415(self) -> str:
        """
        Obtiene el estado actual del archivo 415.
        
        Returns:
            Estado: "no_cargado", "valido", "headers_invalidos", "formato_invalido"
        """
        pass
    
    def is_415_loaded(self) -> bool:
        """
        Verifica si hay un archivo 415 válido cargado.
        
        Returns:
            True si estado_415 == "valido", False en caso contrario
        """
        pass
    
    def clear_415_data(self) -> None:
        """
        Limpia todos los datos del 415 cargado.
        
        Side effects:
            - dataset_415 = None
            - corte_415 = None
            - estado_415 = "no_cargado"
            - outstanding_por_cliente = {}
            - ops_vigentes_por_cliente = {}
        """
        pass


class SimulationsModel:
    """
    Modelo para simulaciones de operaciones Forward en memoria.
    
    Responsabilidades:
    - Gestionar lista de simulaciones (no persistidas)
    - Agregar, duplicar, eliminar simulaciones
    - Actualizar campos de simulaciones
    - Validar completitud de simulaciones
    
    Estructura de fila de simulación:
    {
        'nit': str,
        'punta_cliente': str,  # 'compra' o 'venta'
        'punta_empresa': str,  # 'venta' o 'compra' (inverso de punta_cliente)
        'nominal_usd': float,
        'fecha_sim': date,
        'fecha_venc': date,
        'spot': float,
        'puntos': float,
        'tasa_fwd': float,
        'tasa_ibr': float,
        'derecho': float,
        'obligacion': float,
        'fair_value': float
    }
    
    Estados contemplados:
    - Fila incompleta (campos obligatorios faltantes)
    - Cliente sin vigentes (warning, no error)
    """
    
    def __init__(self):
        """
        Inicializa el modelo de simulaciones.
        
        Estado inicial:
        - _simulations: lista vacía
        """
        self._simulations: List[Dict[str, Any]] = []
    
    def add(self, simulation_data: Optional[Dict[str, Any]] = None) -> int:
        """
        Agrega una nueva simulación.
        
        Args:
            simulation_data: Datos iniciales de la simulación.
                           Si es None, crea fila con valores por defecto/vacíos.
        
        Returns:
            Índice de la simulación agregada (0-based)
            
        Side effects:
            - Agrega fila a _simulations
            - Emite señal simulations_changed (via controller)
        """
        pass
    
    def duplicate(self, idx: int) -> Optional[int]:
        """
        Duplica una simulación existente.
        
        Args:
            idx: Índice de la simulación a duplicar (0-based)
            
        Returns:
            Índice de la nueva simulación o None si idx inválido
            
        Side effects:
            - Agrega copia de la fila a _simulations
            - Emite señal simulations_changed
        """
        pass
    
    def remove(self, indices: List[int]) -> bool:
        """
        Elimina múltiples simulaciones.
        
        Args:
            indices: Lista de índices a eliminar (0-based)
            
        Returns:
            True si se eliminó al menos una, False si todos los índices inválidos
            
        Side effects:
            - Elimina filas de _simulations
            - Reordena índices
            - Emite señal simulations_changed
        """
        pass
    
    def all(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las simulaciones.
        
        Returns:
            Lista de diccionarios con todas las simulaciones.
            Lista vacía si no hay simulaciones.
        """
        pass
    
    def get(self, idx: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una simulación específica.
        
        Args:
            idx: Índice de la simulación (0-based)
            
        Returns:
            Diccionario con datos de la simulación o None si índice inválido
        """
        pass
    
    def update(self, idx: int, field: str, value: Any) -> bool:
        """
        Actualiza un campo específico de una simulación.
        
        Args:
            idx: Índice de la simulación (0-based)
            field: Nombre del campo a actualizar
            value: Nuevo valor
            
        Returns:
            True si se actualizó correctamente, False si índice o campo inválido
            
        Side effects:
            - Modifica fila en _simulations
            - Emite señal simulations_changed
        """
        pass
    
    def count(self) -> int:
        """
        Obtiene el número de simulaciones.
        
        Returns:
            Cantidad de simulaciones en memoria
        """
        pass
    
    def clear(self) -> None:
        """
        Elimina todas las simulaciones.
        
        Side effects:
            - Vacía _simulations
            - Emite señal simulations_changed
        """
        pass
    
    def validate_simulation(self, idx: int) -> tuple[bool, List[str]]:
        """
        Valida completitud de una simulación.
        
        Campos obligatorios:
        - nit (no vacío)
        - punta_cliente ('compra' o 'venta')
        - nominal_usd (> 0)
        - fecha_venc (válida y futura)
        - spot (> 0)
        - tasa_ibr (>= 0)
        
        Args:
            idx: Índice de la simulación a validar
            
        Returns:
            Tupla (es_valida: bool, errores: List[str])
            - es_valida: True si pasa todas las validaciones
            - errores: Lista de mensajes de error (vacía si es_valida=True)
        """
        pass
    
    def get_simulations_by_nit(self, nit: str) -> List[int]:
        """
        Obtiene índices de simulaciones para un NIT específico.
        
        Args:
            nit: NIT del cliente
            
        Returns:
            Lista de índices (0-based) de simulaciones del cliente
        """
        pass

