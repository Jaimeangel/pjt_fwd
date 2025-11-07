"""
Modelo para Settings (Configuración del Sistema).
Gestiona la configuración y parámetros de la aplicación con señales Qt para actualización en tiempo real.
"""

from PySide6.QtCore import QObject, Signal
from typing import Optional, Dict, Any
import pandas as pd


class SettingsModel(QObject):
    """
    Modelo de datos para la configuración del sistema.
    
    Usa señales Qt para notificar cambios en tiempo real a todas las vistas conectadas.
    
    Responsabilidades:
    - Gestionar Patrimonio Técnico Vigente (COP)
    - Gestionar TRM vigente
    - Gestionar parámetros normativos
    - Gestionar líneas de crédito vigentes
    - Notificar cambios en tiempo real mediante señales
    """
    
    # Señales para cambios en tiempo real
    patrimonioChanged = Signal(float)
    trmChanged = Signal(float)
    colchonChanged = Signal(float)
    
    def __init__(self):
        """
        Inicializa el modelo de configuración con valores por defecto.
        """
        super().__init__()
        
        # Parámetros Generales
        self._patrimonio_cop: float = 50_000_000_000.00  # Default: 50 mil millones COP
        self._trm: float = 4200.50                        # Default: 4200.50 COP/USD
        
        # Parámetros Normativos
        self._lim_endeud: float = 10.0  # %
        self._lim_entfin: float = 30.0  # %
        self._colchon: float = 5.0      # %
        
        # Líneas de Crédito Vigentes
        self.lineas_credito_df = pd.DataFrame()  # DataFrame con líneas de crédito cargadas
        
        print("[SettingsModel] Inicializado con valores por defecto")
        print(f"   Patrimonio: $ {self._patrimonio_cop:,.2f} COP")
        print(f"   TRM: $ {self._trm:,.2f}")
        print(f"   Colchón de seguridad: {self._colchon}%")
    
    # === Parámetros Generales ===
    
    def set_patrimonio(self, v: float) -> None:
        """
        Establece el Patrimonio Técnico Vigente y emite señal si cambió.
        
        Args:
            v: Nuevo valor de patrimonio en COP
        """
        if v != self._patrimonio_cop:
            self._patrimonio_cop = v
            self.patrimonioChanged.emit(v)
            print(f"[SettingsModel] Patrimonio actualizado: $ {v:,.2f} COP")
    
    def patrimonio(self) -> float:
        """
        Obtiene el Patrimonio Técnico Vigente.
        
        Returns:
            Valor de patrimonio en COP
        """
        return self._patrimonio_cop
    
    def set_trm(self, v: float) -> None:
        """
        Establece la TRM vigente y emite señal si cambió.
        
        Args:
            v: Nuevo valor de TRM en COP/USD
        """
        if v != self._trm:
            self._trm = v
            self.trmChanged.emit(v)
            print(f"[SettingsModel] TRM actualizada: $ {v:,.2f}")
    
    def trm(self) -> float:
        """
        Obtiene la TRM vigente.
        
        Returns:
            Valor de TRM en COP/USD
        """
        return self._trm
    
    # === Parámetros Normativos ===
    
    def set_lim_endeud(self, v: float) -> None:
        """Establece el límite máximo de endeudamiento individual (%)."""
        self._lim_endeud = v
    
    def lim_endeud(self) -> float:
        """Obtiene el límite máximo de endeudamiento individual (%)."""
        return self._lim_endeud
    
    def set_lim_entfin(self, v: float) -> None:
        """Establece el límite máximo de concentración con entidades financieras (%)."""
        self._lim_entfin = v
    
    def lim_entfin(self) -> float:
        """Obtiene el límite máximo de concentración con entidades financieras (%)."""
        return self._lim_entfin
    
    def set_colchon(self, v: float) -> None:
        """
        Establece el colchón de seguridad (%) y emite señal si cambió.
        
        Args:
            v: Nuevo valor de colchón en porcentaje
        """
        if v != self._colchon:
            self._colchon = v
            self.colchonChanged.emit(v)
            print(f"[SettingsModel] Colchón actualizado: {v}%")
    
    def colchon(self) -> float:
        """Obtiene el colchón de seguridad (%)."""
        return self._colchon
    
    # === Líneas de Crédito ===
    
    def set_lineas_credito(self, df: pd.DataFrame) -> None:
        """
        Establece el DataFrame de líneas de crédito vigentes.
        
        Args:
            df: DataFrame con columnas NIT, Contraparte, Grupo Conectado de Contrapartes, Monto (COP)
        """
        self.lineas_credito_df = df
        print(f"[SettingsModel] Líneas de crédito actualizadas: {len(df)} registros")
    
    def get_linea_credito_por_nit(self, nit: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la línea de crédito para un NIT específico.
        
        Args:
            nit: NIT del cliente (sin guiones)
            
        Returns:
            Diccionario con datos del cliente o None si no se encuentra
        """
        if self.lineas_credito_df.empty:
            return None
        
        # Buscar cliente por NIT
        cliente_info = self.lineas_credito_df[self.lineas_credito_df["NIT"] == nit]
        
        if cliente_info.empty:
            return None
        
        # Retornar primera coincidencia como diccionario
        return {
            "nit": str(cliente_info["NIT"].iloc[0]),
            "contraparte": str(cliente_info["Contraparte"].iloc[0]),
            "grupo": str(cliente_info["Grupo Conectado de Contrapartes"].iloc[0]),
            "monto_cop": float(cliente_info["Monto (COP)"].iloc[0])
        }
    
    # === Métodos de utilidad ===
    
    def get_all_params(self) -> Dict[str, Any]:
        """
        Obtiene todos los parámetros como diccionario.
        
        Returns:
            Diccionario con todos los parámetros
        """
        return {
            "patrimonio_cop": self._patrimonio_cop,
            "trm": self._trm,
            "lim_endeud": self._lim_endeud,
            "lim_entfin": self._lim_entfin,
            "colchon": self._colchon
        }

