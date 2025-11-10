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
    
    # Señales para cambios en tiempo real (pueden emitir float o None)
    patrimonioChanged = Signal(object)  # float | None
    trmChanged = Signal(object)         # float | None
    colchonChanged = Signal(object)     # float | None
    lineasCreditoChanged = Signal()     # Aviso de cambios en DataFrame
    
    def __init__(self):
        """
        Inicializa el modelo de configuración SIN valores por defecto.
        Todos los parámetros inician en None hasta que el usuario los configure.
        """
        super().__init__()
        
        # Parámetros Generales (sin defaults)
        self._patrimonio_cop: Optional[float] = None
        self._trm: Optional[float] = None
        
        # Parámetros Normativos (sin defaults)
        self._lim_endeud: Optional[float] = None
        self._lim_entfin: Optional[float] = None
        self.colchon_seguridad: Optional[float] = None  # Sin valor por defecto
        
        # Líneas de Crédito Vigentes
        self.lineas_credito_df = pd.DataFrame()  # DataFrame con líneas de crédito cargadas
        
        print("[SettingsModel] Inicializado SIN valores por defecto (todos en None)")
    
    # === Parámetros Generales ===
    
    def set_patrimonio(self, v) -> None:
        """
        Establece el Patrimonio Técnico Vigente y emite señal si cambió.
        Acepta None o float.
        
        Args:
            v: Nuevo valor de patrimonio en COP (float o None)
        """
        v = None if v is None else float(v)
        if v != self._patrimonio_cop:
            self._patrimonio_cop = v
            self.patrimonioChanged.emit(v)
            if v is not None:
                print(f"[SettingsModel] Patrimonio actualizado: $ {v:,.2f} COP")
            else:
                print("[SettingsModel] Patrimonio limpiado (None)")
    
    def patrimonio(self) -> Optional[float]:
        """
        Obtiene el Patrimonio Técnico Vigente.
        
        Returns:
            Valor de patrimonio en COP o None si no está configurado
        """
        return self._patrimonio_cop
    
    def set_trm(self, v) -> None:
        """
        Establece la TRM vigente y emite señal si cambió.
        Acepta None o float.
        
        Args:
            v: Nuevo valor de TRM en COP/USD (float o None)
        """
        v = None if v is None else float(v)
        if v != self._trm:
            self._trm = v
            self.trmChanged.emit(v)
            if v is not None:
                print(f"[SettingsModel] TRM actualizada: $ {v:,.2f}")
            else:
                print("[SettingsModel] TRM limpiada (None)")
    
    def trm(self) -> Optional[float]:
        """
        Obtiene la TRM vigente.
        
        Returns:
            Valor de TRM en COP/USD o None si no está configurado
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
    
    def set_colchon(self, v) -> None:
        """
        Establece el colchón de seguridad (%) y emite señal si cambió.
        Acepta None o float.
        
        Args:
            v: Nuevo valor de colchón en porcentaje (float o None)
        """
        v = None if v is None else float(v)
        if v != self.colchon_seguridad:
            self.colchon_seguridad = v
            self.colchonChanged.emit(v)
            if v is not None:
                print(f"[SettingsModel] Colchón actualizado: {v}%")
            else:
                print("[SettingsModel] Colchón limpiado (None)")
    
    def colchon(self) -> Optional[float]:
        """
        Obtiene el colchón de seguridad (%).
        
        Returns:
            Valor de colchón en porcentaje o None si no está configurado
        """
        return self.colchon_seguridad
    
    # === Líneas de Crédito ===
    
    def set_lineas_credito(self, df: pd.DataFrame) -> None:
        """
        Establece el DataFrame de líneas de crédito vigentes.
        Normaliza el NIT (elimina guiones) antes de almacenar.
        
        Args:
            df: DataFrame con columnas NIT, Contraparte, Grupo Conectado de Contrapartes, Monto (COP)
        """
        # Normalizar NIT sin guiones
        df = df.copy()
        df["NIT"] = df["NIT"].astype(str).str.replace("-", "", regex=False).str.strip()
        self.lineas_credito_df = df
        self.lineasCreditoChanged.emit()
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
            "colchon": self.colchon_seguridad
        }

