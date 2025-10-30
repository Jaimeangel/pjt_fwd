"""
Servicio de cálculo de exposición crediticia.
"""

from typing import Dict, Any


class ExposureService:
    """
    Servicio de cálculo de exposición y límites.
    
    Responsabilidades:
    - Calcular exposición de operaciones vigentes
    - Calcular exposición de simulaciones
    - Calcular disponibilidad de línea de crédito
    
    Nota: Esta es una implementación MOCK para testing.
    En producción, usar modelos de riesgo reales.
    """
    
    def calc_simulated_exposure(self, fila_sim: Dict[str, Any]) -> float:
        """
        Calcula la exposición crediticia de una simulación (MOCK).
        
        Fórmula simplificada:
        exposicion = nominal_usd * factor_exposicion
        
        En realidad, dependería de:
        - Fair value de la operación
        - Probabilidad de default
        - Tiempo al vencimiento
        - Colaterales
        
        Args:
            fila_sim: Diccionario con datos de simulación
                Debe contener al menos: nominal_usd
                
        Returns:
            Exposición en pesos colombianos
        """
        nominal_usd = float(fila_sim.get("nominal_usd", 0))
        spot = float(fila_sim.get("spot", 4250.0))
        
        # Factor de exposición mock: 15% del nominal
        # En producción, usar modelo de CVA (Credit Value Adjustment)
        factor_exposicion = 0.15
        
        # Exposición en COP
        exposicion_cop = nominal_usd * spot * factor_exposicion
        
        return round(exposicion_cop, 2)
    
    def calc_outstanding_exposure(
        self,
        operaciones: list,
        spot: float = 4250.0
    ) -> float:
        """
        Calcula la exposición total de operaciones vigentes (MOCK).
        
        Args:
            operaciones: Lista de operaciones vigentes
            spot: Tasa spot actual
            
        Returns:
            Exposición total en COP
        """
        if not operaciones:
            return 0.0
        
        total_exposure = 0.0
        
        for op in operaciones:
            nominal = float(op.get("nominal", 0))
            # Mock: cada operación tiene una exposición del 20% del nominal
            exposure = nominal * spot * 0.20
            total_exposure += exposure
        
        return round(total_exposure, 2)
    
    def calc_disponibilidad(
        self,
        outstanding: float,
        exposicion_simulada: float,
        linea_credito: float,
        colchon_pct: float
    ) -> Dict[str, float]:
        """
        Calcula la disponibilidad de línea de crédito.
        
        Args:
            outstanding: Exposición actual
            exposicion_simulada: Exposición de simulaciones
            linea_credito: Línea de crédito total
            colchon_pct: Colchón interno (% de la línea)
            
        Returns:
            Diccionario con métricas de disponibilidad
        """
        # Límite máximo = línea - colchón
        limite_max = linea_credito * (1 - colchon_pct)
        
        # Total con simulación
        total_con_simulacion = outstanding + exposicion_simulada
        
        # Disponibilidad
        disponibilidad = limite_max - total_con_simulacion
        
        # Utilización (%)
        utilizacion_pct = (total_con_simulacion / limite_max * 100) if limite_max > 0 else 0
        
        return {
            "outstanding": round(outstanding, 2),
            "exposicion_simulada": round(exposicion_simulada, 2),
            "total_con_simulacion": round(total_con_simulacion, 2),
            "limite_max": round(limite_max, 2),
            "disponibilidad": round(disponibilidad, 2),
            "utilizacion_pct": round(utilizacion_pct, 2)
        }
