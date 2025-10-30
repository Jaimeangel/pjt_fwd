"""
Modelo de datos para operaciones Forward y archivo 415.
"""

from typing import Optional, Dict, Any, List
from datetime import date


class ForwardDataModel:
    """
    Modelo de datos para el estado del 415 y exposiciones.
    
    Responsabilidades:
    - Almacenar dataset del archivo 415
    - Gestionar información de corte y estado del 415
    - Calcular outstanding por cliente
    - Gestionar operaciones vigentes por cliente
    """
    
    def __init__(self):
        """Inicializa el modelo de datos Forward."""
        self.dataset_415: Optional[Any] = None
        self.corte_415: Optional[date] = None
        self.estado_415: str = "no_cargado"
        
        # Metadatos del archivo 415
        self.ruta_415: Optional[str] = None
        self.nombre_415: Optional[str] = None
        self.tamano_415_kb: float = 0.0
        self.hash_415: Optional[str] = None
        self.timestamp_cargue: Optional[Any] = None  # datetime
        
        self.outstanding_por_cliente: Dict[str, float] = {}
        self.ops_vigentes_por_cliente: Dict[str, List[Dict[str, Any]]] = {}
    
    def load_415(self, file_path: str) -> None:
        """
        Carga el archivo 415 desde la ruta especificada.
        
        Args:
            file_path: Ruta al archivo CSV formato 415
        """
        pass
    
    def get_outstanding(self, nit: str) -> float:
        """
        Obtiene el outstanding de un cliente.
        
        Args:
            nit: NIT del cliente
            
        Returns:
            Monto del outstanding en COP
        """
        pass
    
    def get_ops_vigentes(self, nit: str) -> List[Dict[str, Any]]:
        """
        Obtiene las operaciones vigentes de un cliente.
        
        Args:
            nit: NIT del cliente
            
        Returns:
            Lista de operaciones vigentes
        """
        pass
    
    def get_all_clients(self) -> List[str]:
        """
        Obtiene lista de todos los NITs con operaciones.
        
        Returns:
            Lista de NITs
        """
        pass
    
    def is_415_loaded(self) -> bool:
        """
        Verifica si hay un archivo 415 válido cargado.
        
        Returns:
            True si estado_415 == "valido"
        """
        return self.estado_415 == "valido"
    
    def set_415_metadata(
        self,
        ruta: str,
        nombre: str,
        tamano_kb: float,
        hash_value: str,
        estado: str
    ) -> None:
        """
        Establece los metadatos del archivo 415.
        
        Args:
            ruta: Ruta completa del archivo
            nombre: Nombre del archivo
            tamano_kb: Tamaño del archivo en KB
            hash_value: Hash simple del archivo
            estado: Estado de validación ("valido", "invalido", "no_cargado")
        """
        from datetime import datetime
        
        self.ruta_415 = ruta
        self.nombre_415 = nombre
        self.tamano_415_kb = tamano_kb
        self.hash_415 = hash_value
        self.timestamp_cargue = datetime.now()
        self.estado_415 = estado
    
    def get_415_metadata(self) -> Dict[str, Any]:
        """
        Obtiene los metadatos del archivo 415.
        
        Returns:
            Diccionario con metadatos del archivo
        """
        return {
            "ruta": self.ruta_415,
            "nombre": self.nombre_415,
            "tamano_kb": self.tamano_415_kb,
            "hash": self.hash_415,
            "timestamp": self.timestamp_cargue,
            "estado": self.estado_415
        }
    
    def clear_415_data(self) -> None:
        """Limpia todos los datos del 415."""
        self.dataset_415 = None
        self.corte_415 = None
        self.estado_415 = "no_cargado"
        self.ruta_415 = None
        self.nombre_415 = None
        self.tamano_415_kb = 0.0
        self.hash_415 = None
        self.timestamp_cargue = None
        self.outstanding_por_cliente.clear()
        self.ops_vigentes_por_cliente.clear()

