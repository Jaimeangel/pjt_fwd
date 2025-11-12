"""
Modelo de datos para operaciones Forward y archivo 415.
"""

from typing import Optional, Dict, Any, List
from datetime import date
from src.utils.ids import normalize_nit


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
        
        # Exposición del cliente actual (COP reales)
        self._outstanding_cop: Optional[float] = None
        self._outstanding_with_sim_cop: Optional[float] = None
        
        # Mapeos NIT <-> Nombre de contraparte
        self.nit_to_nombre: Dict[str, str] = {}
        self.nombre_to_nit: Dict[str, str] = {}
        self.operaciones_por_nit: Dict[str, List[Dict[str, Any]]] = {}
        
        # Cliente actual seleccionado
        self.current_nit: Optional[str] = None
        self.current_nombre: Optional[str] = None
        
        # Factor de conversión global (si no hay específico por cliente)
        self.fc_global: float = 0.0
        
        # Factores de conversión por cliente (si aplica)
        self.fc_por_nit: Dict[str, float] = {}
        
        # Curva IBR
        self.ibr_curve: Dict[int, float] = {}  # {dias: tasa_decimal}
        self.ibr_loaded: bool = False
        self.ibr_file_path: Optional[str] = None
        
        # Metadatos del archivo IBR
        self.ibr_nombre: Optional[str] = None
        self.ibr_tamano_kb: Optional[float] = None
        self.ibr_timestamp: Optional[str] = None
        self.ibr_estado: str = "—"
    
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
        - Operaciones por NIT (normalizado)
        - Exposición por NIT (normalizado)
        - Mapeos NIT <-> nombre de contraparte
        
        Args:
            operaciones: Lista de operaciones procesadas con todas las columnas
            exp_por_nit: Diccionario con NIT -> exposición crediticia
        """
        # Normalizar NITs en el diccionario de exposiciones
        self.outstanding_por_cliente = {
            normalize_nit(nit): exposicion 
            for nit, exposicion in (exp_por_nit or {}).items()
        }
        
        # Agrupar operaciones por NIT normalizado y construir mapeos
        ops_por_nit: Dict[str, List[Dict[str, Any]]] = {}
        nit_to_nombre: Dict[str, str] = {}
        
        for op in operaciones:
            nit = str(op.get("nit", "")).strip()
            nit_norm = normalize_nit(nit)  # Normalizar NIT
            nombre = str(op.get("contraparte", "")).strip()  # 14Nom_Cont
            
            if not nit_norm:
                continue
                
            # Agrupar operaciones por NIT normalizado
            ops_por_nit.setdefault(nit_norm, []).append(op)
            
            # Guardar nombre de la contraparte
            if nombre:
                nit_to_nombre[nit_norm] = nombre
        
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
    
    def get_current_client_nit(self) -> Optional[str]:
        """
        Obtiene el NIT del cliente actualmente seleccionado.
        
        Returns:
            NIT del cliente actual o None
        """
        return self.current_nit
    
    def get_current_client_name(self) -> Optional[str]:
        """
        Obtiene el nombre del cliente actualmente seleccionado.
        
        Returns:
            Nombre del cliente actual o None
        """
        return self.current_nombre
    
    def set_current_client(self, nit: str, nombre: Optional[str] = None) -> None:
        """
        Establece el cliente actualmente seleccionado.
        
        Args:
            nit: NIT del cliente
            nombre: Nombre del cliente (opcional, se resuelve si no se proporciona)
        """
        self.current_nit = nit
        if nombre:
            self.current_nombre = nombre
        else:
            self.current_nombre = self.get_nombre_by_nit(nit)
    
    def get_fc_for_nit(self, nit: str) -> float:
        """
        Obtiene el factor de conversión (82FC) aplicable a una contraparte.
        
        Si no existe un fc específico para el NIT, devuelve el fc global.
        Si no hay fc global, devuelve 0.0.
        
        Args:
            nit: NIT del cliente
            
        Returns:
            Factor de conversión (fc)
        """
        return self.fc_por_nit.get(nit, self.fc_global)
    
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
    
    def set_ibr_curve(self, curve: Dict[int, float], file_path: Optional[str] = None) -> None:
        """
        Establece la curva IBR en memoria.
        
        Args:
            curve: Diccionario {dias: tasa_decimal}
            file_path: Ruta del archivo IBR (opcional)
        """
        self.ibr_curve = curve
        self.ibr_loaded = True
        self.ibr_file_path = file_path
    
    def set_ibr_metadata(self, nombre: str, tamano_kb: float, timestamp: str, estado: str) -> None:
        """
        Establece los metadatos del archivo IBR.
        
        Args:
            nombre: Nombre del archivo
            tamano_kb: Tamaño en KB
            timestamp: Fecha/hora de cargue (string)
            estado: Estado del archivo ("Cargado" o "Inválido")
        """
        self.ibr_nombre = nombre
        self.ibr_tamano_kb = tamano_kb
        self.ibr_timestamp = timestamp
        self.ibr_estado = estado
    
    def get_ibr_for_days(self, days: int) -> float:
        """
        Obtiene la tasa IBR para un plazo específico.
        
        La tasa se devuelve en PORCENTAJE (0-100), no en decimal.
        Si el plazo no existe en la curva, retorna 0.0.
        
        Args:
            days: Número de días (plazo)
            
        Returns:
            Tasa IBR en porcentaje (ej. 4.5 para 4.5%)
        """
        if not self.ibr_loaded or days not in self.ibr_curve:
            return 0.0
        
        # Convertir de decimal a porcentaje
        tasa_decimal = self.ibr_curve[days]
        return tasa_decimal * 100.0
    
    def get_ibr_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado de la curva IBR.
        
        Returns:
            Diccionario con información del IBR
        """
        return {
            "loaded": self.ibr_loaded,
            "file_path": self.ibr_file_path,
            "points_count": len(self.ibr_curve) if self.ibr_loaded else 0
        }
    
    def clear_ibr_data(self) -> None:
        """Limpia los datos de la curva IBR y sus metadatos."""
        self.ibr_curve = {}
        self.ibr_loaded = False
        self.ibr_file_path = None
        self.ibr_nombre = None
        self.ibr_tamano_kb = None
        self.ibr_timestamp = None
        self.ibr_estado = "—"
    
    def reset_simulation_state(self) -> None:
        """
        Resetea el estado de simulación.
        
        Este método limpia el valor de 'Outstanding + simulación', dejando
        solo el Outstanding actual. Útil cuando se cambia de contraparte.
        """
        self._outstanding_with_sim_cop = None
        print(f"[ForwardDataModel] Estado de simulación reseteado")
    
    # Métodos para exposición del cliente actual
    def outstanding_cop(self) -> Optional[float]:
        """
        Obtiene el outstanding del cliente actual en COP reales.
        
        Returns:
            Outstanding en COP o None si no hay datos
        """
        return self._outstanding_cop
    
    def set_outstanding_cop(self, value: Optional[float]) -> None:
        """
        Establece el outstanding del cliente actual en COP reales.
        
        Args:
            value: Outstanding en COP o None
        """
        self._outstanding_cop = value
    
    def outstanding_with_sim_cop(self) -> Optional[float]:
        """
        Obtiene el outstanding + simulación del cliente actual en COP reales.
        
        Returns:
            Outstanding con simulación en COP o None si no hay simulación
        """
        return self._outstanding_with_sim_cop
    
    def set_outstanding_with_sim_cop(self, value: Optional[float]) -> None:
        """
        Establece el outstanding + simulación del cliente actual en COP reales.
        
        Args:
            value: Outstanding con simulación en COP o None
        """
        self._outstanding_with_sim_cop = value
    
    def current_client_nit(self) -> Optional[str]:
        """
        Obtiene el NIT del cliente actualmente seleccionado.
        
        Returns:
            NIT del cliente actual o None
        """
        return self.current_nit

