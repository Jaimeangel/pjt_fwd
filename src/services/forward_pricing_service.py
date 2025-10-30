"""
Servicio de pricing para operaciones Forward.
"""

from typing import Dict


class ForwardPricingService:
    """
    Servicio de cálculo de precios Forward.
    
    Responsabilidades:
    - Calcular tasa forward
    - Calcular puntos forward
    - Calcular fair value de operaciones
    
    Nota: Esta es una implementación MOCK para testing.
    En producción, conectar con fuentes de datos reales.
    """
    
    def calc_forward(
        self,
        spot: float,
        tasa_dom: float,
        tasa_ext: float,
        plazo_dias: int
    ) -> Dict[str, float]:
        """
        Calcula tasa forward, puntos y fair value (MOCK).
        
        Fórmula simplificada:
        tasa_fwd = spot * (1 + tasa_dom * plazo_dias / 360) / (1 + tasa_ext * plazo_dias / 360)
        puntos = tasa_fwd - spot
        
        Args:
            spot: Tasa spot actual
            tasa_dom: Tasa doméstica (Colombia)
            tasa_ext: Tasa extranjera (USD)
            plazo_dias: Plazo en días
            
        Returns:
            Diccionario con tasa_fwd, puntos, fair_value
        """
        # Validaciones básicas
        if spot <= 0:
            spot = 4250.0  # Default mock
        
        if tasa_dom <= 0:
            tasa_dom = 0.12  # 12% mock
        
        if tasa_ext <= 0:
            tasa_ext = 0.05  # 5% mock
        
        if plazo_dias <= 0:
            plazo_dias = 30  # 30 días mock
        
        # Cálculo de tasa forward (fórmula de paridad de tasas de interés)
        factor_dom = 1 + (tasa_dom * plazo_dias / 360)
        factor_ext = 1 + (tasa_ext * plazo_dias / 360)
        tasa_fwd = spot * (factor_dom / factor_ext)
        
        # Puntos forward
        puntos = tasa_fwd - spot
        
        # Fair value (mock simplificado)
        # En realidad, sería el valor presente de flujos futuros
        # Por ahora, usamos una aproximación simple
        fair_value = puntos * 1000  # Mock: cada punto vale $1000
        
        return {
            "tasa_fwd": round(tasa_fwd, 6),
            "puntos": round(puntos, 6),
            "fair_value": round(fair_value, 2)
        }
    
    def calc_forward_from_simulation(self, fila_sim: Dict) -> Dict[str, float]:
        """
        Calcula forward desde una fila de simulación.
        
        Args:
            fila_sim: Diccionario con datos de simulación
                Debe contener: spot, tasa_ibr, fec_sim, fec_venc
                
        Returns:
            Diccionario con tasa_fwd, puntos, fair_value
        """
        spot = float(fila_sim.get("spot", 4250.0))
        tasa_ibr = float(fila_sim.get("tasa_ibr", 0.11))  # Tasa doméstica
        
        # Calcular plazo en días (mock: asumimos fechas o usamos default)
        # En producción, calcular fecha_venc - fecha_sim
        plazo_dias = 90  # Mock: 90 días
        
        # Tasa extranjera mock (USD)
        tasa_ext = 0.05  # 5% anual
        
        return self.calc_forward(spot, tasa_ibr, tasa_ext, plazo_dias)
