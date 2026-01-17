"""
Modelo para Settings (Configuración del Sistema).
Gestiona la configuración y parámetros de la aplicación con señales Qt para actualización en tiempo real.
"""

from PySide6.QtCore import QObject, Signal
from typing import Optional, Dict, Any, List
import pandas as pd
from src.utils.ids import normalize_nit


class SettingsModel(QObject):
    """
    Modelo de datos para la configuración del sistema.
    
    Usa señales Qt para notificar cambios en tiempo real a todas las vistas conectadas.
    
    Responsabilidades:
    - Gestionar TRM COP/USD vigente
    - Gestionar TRM EUR/USD vigente
    - Gestionar parámetros normativos
    - Gestionar información de contrapartes
    - Notificar cambios en tiempo real mediante señales
    """
    
    # Señales para cambios en tiempo real (pueden emitir float o None)
    trm_cop_usdChanged = Signal(object)  # float | None
    trm_cop_eurChanged = Signal(object)  # float | None
    patrimonioTecCopChanged = Signal(object)  # float | None
    colchonSeguridadChanged = Signal(object)  # float | None
    lineasCreditoChanged = Signal()      # Aviso de cambios en DataFrame
    counterpartiesChanged = Signal()     # Aviso de cambios en catálogo de contrapartes
    
    def __init__(self):
        """
        Inicializa el modelo de configuración SIN valores por defecto.
        Todos los parámetros inician en None hasta que el usuario los configure.
        """
        super().__init__()
        
        # Parámetros Generales (TRMs y Patrimonio)
        self._trm_cop_usd: Optional[float] = None  # TRM COP/USD
        self._trm_cop_eur: Optional[float] = None  # TRM COP/EUR
        self._patrimonio_tec_cop: Optional[float] = None  # Patrimonio técnico en COP
        
        # Parámetros Normativos
        self._lim_endeud: Optional[float] = None
        self._lim_entfin: Optional[float] = None
        self._colchon_seguridad: float = 0.10  # Colchón de seguridad (10% por defecto)
        self._lll_percent: float = 25.0  # LLL por defecto (25% del patrimonio)
        
        # Información de contrapartes
        self._lineas_credito_df = pd.DataFrame()  # DataFrame con contrapartes cargadas
        
        print("[SettingsModel] Inicializado SIN valores por defecto (todos en None)")
    
    # === Parámetros Generales ===
    
    def set_trm_cop_usd(self, v) -> None:
        """
        Establece la TRM COP/USD vigente y emite señal si cambió.
        Acepta None, float, o string.
        
        Args:
            v: Nuevo valor de TRM COP/USD (float, str o None)
        """
        try:
            val = float(v) if v not in (None, "") else None
        except (TypeError, ValueError):
            val = None
        
        if val != self._trm_cop_usd:
            self._trm_cop_usd = val
            self.trm_cop_usdChanged.emit(val)
            if val is not None:
                print(f"[SettingsModel] TRM COP/USD actualizada: {val:,.6f}")
            else:
                print("[SettingsModel] TRM COP/USD limpiada (None)")
    
    def trm_cop_usd(self) -> Optional[float]:
        """
        Obtiene la TRM COP/USD vigente.
        
        Returns:
            Valor de TRM COP/USD o None si no está configurado
        """
        return self._trm_cop_usd
    
    def set_trm_cop_eur(self, v) -> None:
        """
        Establece la TRM COP/EUR vigente y emite señal si cambió.
        Acepta None, float, o string.
        
        Args:
            v: Nuevo valor de TRM COP/EUR (float, str o None)
        """
        try:
            val = float(v) if v not in (None, "") else None
        except (TypeError, ValueError):
            val = None
        
        if val != self._trm_cop_eur:
            self._trm_cop_eur = val
            self.trm_cop_eurChanged.emit(val)
            if val is not None:
                print(f"[SettingsModel] TRM COP/EUR actualizada: {val:,.6f}")
            else:
                print("[SettingsModel] TRM COP/EUR limpiada (None)")
    
    def trm_cop_eur(self) -> Optional[float]:
        """
        Obtiene la TRM COP/EUR vigente.
        
        Returns:
            Valor de TRM COP/EUR o None si no está configurado
        """
        return self._trm_cop_eur
    
    def set_patrimonio_tec_cop(self, value) -> None:
        """
        Establece el Patrimonio técnico vigente en COP y emite señal si cambió.
        Acepta None, float, o string. Valida que no sea NaN ni infinito.
        
        Args:
            value: Nuevo valor de Patrimonio técnico en COP (float, str o None)
        """
        import math
        
        try:
            val = float(value) if value not in (None, "") else None
            if val is not None and (math.isnan(val) or math.isinf(val)):
                val = None
        except (TypeError, ValueError):
            val = None
        
        if val != self._patrimonio_tec_cop:
            self._patrimonio_tec_cop = val
            self.patrimonioTecCopChanged.emit(val)
            if val is not None:
                print(f"[SettingsModel] Patrimonio técnico vigente actualizado: $ {val:,.2f} COP")
            else:
                print("[SettingsModel] Patrimonio técnico vigente limpiado (None)")
    
    def patrimonio_tec_cop(self) -> Optional[float]:
        """
        Obtiene el Patrimonio técnico vigente en COP.
        
        Returns:
            Valor de Patrimonio técnico en COP o None si no está configurado
        """
        return self._patrimonio_tec_cop
    
    def get_patrimonio_tecnico(self) -> float:
        """Devuelve el patrimonio técnico vigente (0.0 si no está definido)."""
        return float(self._patrimonio_tec_cop or 0.0)
    
    def lll_cop(self) -> Optional[float]:
        """
        Calcula el LLL (Límite de Liquidez Legal) global en COP.
        LLL = 25% del Patrimonio técnico vigente × (1 - Colchón de seguridad).
        
        Ejemplo:
        - PT = 8,000,000,000,000 COP
        - Colchón = 10% (0.10)
        - LLL = 8,000,000,000,000 × 0.25 × (1 - 0.10) = 1,800,000,000,000 COP
        
        Returns:
            float: LLL en COP reales, o None si no hay patrimonio configurado
        """
        pt = self._patrimonio_tec_cop
        if pt is None:
            return None
        try:
            colchon = self._colchon_seguridad
            # LLL = 25% del PT × (1 - colchón)
            return 0.25 * float(pt) * (1 - colchon)
        except (TypeError, ValueError):
            return None
    
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
    
    def set_colchon_seguridad(self, v: float) -> None:
        """
        Establece el colchón de seguridad (%).
        
        Args:
            v: Colchón de seguridad en porcentaje (ej: 0.10 para 10%)
        """
        if v != self._colchon_seguridad:
            self._colchon_seguridad = v
            self.colchonSeguridadChanged.emit(v)
            print(f"[SettingsModel] Colchón de seguridad actualizado: {v * 100:.1f}%")
    
    def colchon_seguridad(self) -> float:
        """Obtiene el colchón de seguridad (%)."""
        return self._colchon_seguridad
    
    def get_lll_percent(self) -> float:
        """Devuelve el porcentaje de LLL configurado (por defecto 25%)."""
        return float(self._lll_percent or 25.0)
    
    # === Información de contrapartes ===
    
    @property
    def lineas_credito_df(self) -> pd.DataFrame:
        """Devuelve el DataFrame de contrapartes (solo lectura)."""
        return self._lineas_credito_df
    
    def set_lineas_credito(self, df: pd.DataFrame) -> None:
        """
        Establece el DataFrame de información de contrapartes.
        Normaliza el NIT (elimina guiones, espacios, ceros a la izquierda) antes de almacenar.
        
        Args:
            df: DataFrame con columnas NIT, Contraparte, Grupo Conectado de Contrapartes
        """
        df = df.copy()
        
        # Conservar solo columnas relevantes (ignorar extras)
        required_cols = ["NIT", "Contraparte", "Grupo Conectado de Contrapartes"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        df = df[required_cols].copy()
        
        # Normalizar NIT usando la función de utilidades (crear columna NIT_norm)
        if "NIT" in df.columns:
            df["NIT_norm"] = df["NIT"].map(normalize_nit)
        elif "NIT_norm" in df.columns:
            df["NIT_norm"] = df["NIT_norm"].map(normalize_nit)
        else:
            # Garantizar la existencia de la columna aunque venga sin identificador
            df["NIT_norm"] = ""
        
        # Asegurar que la columna de grupo exista (aunque venga vacía)
        if "Grupo Conectado de Contrapartes" not in df.columns:
            df["Grupo Conectado de Contrapartes"] = ""
        else:
            df["Grupo Conectado de Contrapartes"] = (
                df["Grupo Conectado de Contrapartes"].fillna("").astype(str)
            )
        
        self._lineas_credito_df = df
        self.lineasCreditoChanged.emit()
        self.counterpartiesChanged.emit()
        print(f"[SettingsModel] Contrapartes actualizadas: {len(df)} registros")
    
    def get_linea_credito_por_nit(self, nit: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la contraparte para un NIT específico.
        
        Args:
            nit: NIT del cliente (sin guiones)
            
        Returns:
            Diccionario con datos del cliente o None si no se encuentra
        """
        if self.lineas_credito_df.empty:
            return None
        
        # Buscar cliente por NIT
        nit_norm = normalize_nit(nit)
        cliente_info = self.lineas_credito_df[self.lineas_credito_df["NIT_norm"] == nit_norm]
        
        if cliente_info.empty:
            return None
        
        # Retornar primera coincidencia como diccionario
        result = {
            "nit": str(cliente_info["NIT"].iloc[0]),
            "contraparte": str(cliente_info["Contraparte"].iloc[0]),
            "grupo": str(cliente_info["Grupo Conectado de Contrapartes"].iloc[0])
        }
        
        return result
    
    # === Métodos de utilidad ===
    
    def get_all_params(self) -> Dict[str, Any]:
        """
        Obtiene todos los parámetros como diccionario.
        
        Returns:
            Diccionario con todos los parámetros
        """
        return {
            "trm_cop_usd": self._trm_cop_usd,
            "trm_cop_eur": self._trm_cop_eur,
            "lim_endeud": self._lim_endeud,
            "lim_entfin": self._lim_entfin
        }
    
    def get_counterparties(self) -> List[Dict[str, Any]]:
        """
        Devuelve el catálogo de contrapartes desde la tabla de información de contrapartes.
        
        Returns:
            Lista de diccionarios con estructura:
            [{nit, nombre, grupo}, ...]
            
        Notes:
            - Devuelve lista vacía si no hay contrapartes cargadas
            - Deduplicación por NIT normalizado (mantiene primer registro)
            - NITs normalizados (sin espacios, guiones, ceros a la izquierda)
        """
        if self.lineas_credito_df is None or self.lineas_credito_df.empty:
            return []
        
        df = self.lineas_credito_df
        cols = df.columns
        out = []
        
        for _, row in df.iterrows():
            # Usar NIT_norm si existe, sino normalizar NIT original
            nit_norm = row.get("NIT_norm") if "NIT_norm" in cols else normalize_nit(row.get("NIT", ""))
            
            out.append({
                "nit": nit_norm,
                "nombre": row.get("Contraparte", ""),
                "grupo": row.get("Grupo Conectado de Contrapartes", ""),
            })
        
        # Deduplicar por NIT (mantener primero)
        seen = set()
        dedup = []
        for c in out:
            if c["nit"] in seen:
                continue
            seen.add(c["nit"])
            dedup.append(c)
        
        print(f"[SettingsModel] Catálogo de contrapartes: {len(dedup)} registros")
        return dedup

    # === Grupos de contrapartes ===
    
    def get_group_for_nit(self, nit_norm: str) -> Optional[str]:
        """
        Devuelve el nombre del grupo conectado para un NIT normalizado.
        """
        df = getattr(self, "_lineas_credito_df", None)
        if df is None or df.empty or not nit_norm:
            return None
        
        rows = df[df["NIT_norm"] == nit_norm]
        if rows.empty:
            return None
        
        grupo = rows["Grupo Conectado de Contrapartes"].iloc[0]
        grupo = str(grupo).strip() if grupo is not None else ""
        return grupo or None
    
    def get_counterparties_by_group(self, grupo: str) -> List[Dict[str, str]]:
        """
        Devuelve lista de contrapartes pertenecientes a un grupo dado.
        """
        df = getattr(self, "_lineas_credito_df", None)
        if df is None or df.empty:
            return []
        
        if not grupo:
            return []
        
        grupo_normalizado = grupo.strip()
        if not grupo_normalizado:
            return []
        
        mask = df["Grupo Conectado de Contrapartes"].astype(str).str.strip() == grupo_normalizado
        sub = df[mask]
        if sub.empty:
            return []
        
        result: List[Dict[str, str]] = []
        for _, row in sub.iterrows():
            nit_norm = row.get("NIT_norm")
            if not nit_norm:
                nit_norm = normalize_nit(row.get("NIT", ""))
            result.append({
                "nit": nit_norm,
                "nombre": row.get("Contraparte", ""),
                "grupo": row.get("Grupo Conectado de Contrapartes", ""),
            })
        return result
    
    def get_group_members_by_nit(self, nit_norm: str) -> List[Dict[str, str]]:
        """
        Devuelve todas las contrapartes del mismo grupo al que pertenece el NIT dado,
        incluyendo la contraparte actual.
        
        Args:
            nit_norm: NIT normalizado de la contraparte
        
        Returns:
            Lista de dicts con 'nit', 'nombre', 'grupo' para cada miembro del grupo.
            Si no hay grupo o el grupo tiene solo 1 miembro, retorna lista vacía o
            lista con solo la contraparte actual.
        """
        # Obtener el grupo del NIT
        grupo = self.get_group_for_nit(nit_norm)
        
        if not grupo:
            # Sin grupo asignado, retornar lista vacía
            return []
        
        # Obtener todos los miembros del grupo
        members = self.get_counterparties_by_group(grupo)
        
        return members

