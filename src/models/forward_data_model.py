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
        
        # Datos de exposición y operaciones
        self.outstanding_por_cliente: Dict[str, float] = {}
        self.ops_vigentes_por_cliente: Dict[str, List[Dict[str, Any]]] = {}
        
        # Mapeos NIT <-> Nombre de contraparte
        self.nit_to_nombre: Dict[str, str] = {}
        self.nombre_to_nit: Dict[str, str] = {}
        self.operaciones_por_nit: Dict[str, List[Dict[str, Any]]] = {}
    
    def load_415(self, file_path: str) -> None:
        """
        Carga el archivo 415 desde la ruta especificada.
        
        Args:
            file_path: Ruta al archivo CSV formato 415
        """
        pass
    
    def set_datos_415(self, operaciones: List[Dict[str, Any]], exp_por_nit: Dict[str, float]) -> None:
        """
        Guarda la información procesada del 415:
        - Operaciones por NIT
        - Exposición por NIT
        - Mapeos NIT <-> nombre de contraparte
        
        Args:
            operaciones: Lista de operaciones procesadas con todas las columnas
            exp_por_nit: Diccionario con NIT -> exposición crediticia
        """
        self.outstanding_por_cliente = exp_por_nit or {}
        
        # Agrupar operaciones por NIT y construir mapeos
        ops_por_nit: Dict[str, List[Dict[str, Any]]] = {}
        nit_to_nombre: Dict[str, str] = {}
        
        for op in operaciones:
            nit = str(op.get("nit", "")).strip()
            nombre = str(op.get("contraparte", "")).strip()  # 14Nom_Cont
            
            if not nit:
                continue
                
            # Agrupar operaciones por NIT
            ops_por_nit.setdefault(nit, []).append(op)
            
            # Guardar nombre de la contraparte
            if nombre:
                nit_to_nombre[nit] = nombre
        
        # Construir mapeo inverso nombre -> NIT
        nombre_to_nit = {v: k for k, v in nit_to_nombre.items()}
        
        self.operaciones_por_nit = ops_por_nit
        self.nit_to_nombre = nit_to_nombre
        self.nombre_to_nit = nombre_to_nit
        
        print(f"[ForwardDataModel] Datos 415 guardados:")
        print(f"   - {len(self.outstanding_por_cliente)} clientes con exposición")
        print(f"   - {len(self.operaciones_por_nit)} clientes con operaciones")
        print(f"   - {len(self.nit_to_nombre)} mapeos NIT->Nombre")
    
    def set_outstanding_por_nit(self, data: Dict[str, float]) -> None:
        """
        Guarda el resultado del cálculo de exposición por contraparte.
        
        Args:
            data: Diccionario con NIT -> exposición crediticia
        """
        self.outstanding_por_cliente = data or {}
        print(f"[ForwardDataModel] Outstanding guardado para {len(self.outstanding_por_cliente)} clientes")
    
    def get_outstanding_por_nit(self, nit: str) -> float:
        """
        Devuelve la exposición (Outstanding) del NIT o 0.0 si no existe.
        
        Args:
            nit: NIT del cliente
            
        Returns:
            Monto del outstanding en COP
        """
        return float(self.outstanding_por_cliente.get(nit, 0.0))
    
    def get_clientes_disponibles(self) -> List[str]:
        """
        Obtiene lista de todos los NITs con operaciones.
        
        Returns:
            Lista de NITs
        """
        return list(self.outstanding_por_cliente.keys())
    
    def get_client_names(self) -> List[str]:
        """
        Devuelve la lista de nombres de contrapartes para mostrar en el combo.
        
        Returns:
            Lista de nombres ordenados alfabéticamente
        """
        return sorted(self.nombre_to_nit.keys())
    
    def get_nit_by_name(self, nombre: str) -> Optional[str]:
        """
        Obtiene el NIT a partir del nombre de la contraparte.
        
        Args:
            nombre: Nombre de la contraparte
            
        Returns:
            NIT o None si no existe
        """
        return self.nombre_to_nit.get(nombre)
    
    def get_nombre_by_nit(self, nit: str) -> Optional[str]:
        """
        Obtiene el nombre de la contraparte a partir del NIT.
        
        Args:
            nit: NIT del cliente
            
        Returns:
            Nombre de la contraparte o None
        """
        return self.nit_to_nombre.get(nit)
    
    def get_operaciones_por_nit(self, nit: str) -> List[Dict[str, Any]]:
        """
        Obtiene las operaciones vigentes de un cliente por NIT.
        
        Args:
            nit: NIT del cliente
            
        Returns:
            Lista de operaciones del cliente
        """
        return self.operaciones_por_nit.get(nit, [])
    
    def get_outstanding(self, nit: str) -> float:
        """
        Obtiene el outstanding de un cliente (alias de get_outstanding_por_nit).
        
        Args:
            nit: NIT del cliente
            
        Returns:
            Monto del outstanding en COP
        """
        return self.get_outstanding_por_nit(nit)
    
    def get_ops_vigentes(self, nit: str) -> List[Dict[str, Any]]:
        """
        Obtiene las operaciones vigentes de un cliente.
        
        Args:
            nit: NIT del cliente
            
        Returns:
            Lista de operaciones vigentes
        """
        return self.ops_vigentes_por_cliente.get(nit, [])
    
    def get_all_clients(self) -> List[str]:
        """
        Obtiene lista de todos los NITs con operaciones.
        
        Returns:
            Lista de NITs
        """
        return self.get_clientes_disponibles()
    
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

