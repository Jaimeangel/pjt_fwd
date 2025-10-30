"""
Servicio de gestión de clientes.
"""

from typing import Dict, List, Optional


class ClientService:
    """
    Servicio de consulta de información de clientes.
    
    Responsabilidades:
    - Obtener información básica de clientes
    - Consultar límites de crédito
    - Obtener parámetros de riesgo
    
    Nota: Esta es una implementación MOCK para testing.
    En producción, conectar con base de datos real.
    """
    
    # Datos mock de clientes
    _CLIENTS_MOCK = {
        "123456789": {
            "nit": "123456789",
            "nombre": "Cliente Ejemplo S.A.",
            "linea_credito": 5_000_000_000.0,  # $5,000 millones
            "colchon_interno": 0.10,  # 10%
            "rating": "AAA",
            "sector": "Financiero"
        },
        "987654321": {
            "nit": "987654321",
            "nombre": "Corporación ABC Ltda.",
            "linea_credito": 10_000_000_000.0,  # $10,000 millones
            "colchon_interno": 0.15,  # 15%
            "rating": "AA",
            "sector": "Industrial"
        },
        "555444333": {
            "nit": "555444333",
            "nombre": "Empresa XYZ S.A.S.",
            "linea_credito": 3_000_000_000.0,  # $3,000 millones
            "colchon_interno": 0.12,  # 12%
            "rating": "A",
            "sector": "Comercial"
        }
    }
    
    def get_client_by_nit(self, nit: str) -> Optional[Dict]:
        """
        Obtiene información completa de un cliente por NIT (MOCK).
        
        Args:
            nit: Número de identificación tributaria
            
        Returns:
            Diccionario con información del cliente o None si no existe
        """
        return self._CLIENTS_MOCK.get(nit)
    
    def get_linea_credito(self, nit: str) -> float:
        """
        Obtiene la línea de crédito de un cliente (MOCK).
        
        Args:
            nit: Número de identificación tributaria
            
        Returns:
            Línea de crédito en COP
        """
        client = self._CLIENTS_MOCK.get(nit)
        if client:
            return client["linea_credito"]
        
        # Default mock para clientes no encontrados
        return 1_000_000_000.0  # $1,000 millones
    
    def get_colchon_interno(self, nit: str) -> float:
        """
        Obtiene el colchón interno (%) de un cliente (MOCK).
        
        El colchón interno es un porcentaje de la línea de crédito
        que se reserva como buffer de seguridad.
        
        Args:
            nit: Número de identificación tributaria
            
        Returns:
            Colchón interno como decimal (ej: 0.10 = 10%)
        """
        client = self._CLIENTS_MOCK.get(nit)
        if client:
            return client["colchon_interno"]
        
        # Default mock
        return 0.10  # 10%
    
    def get_all_clients(self) -> List[Dict]:
        """
        Obtiene lista de todos los clientes (MOCK).
        
        Returns:
            Lista de diccionarios con información de clientes
        """
        return list(self._CLIENTS_MOCK.values())
    
    def get_client_limits(self, nit: str) -> Dict[str, float]:
        """
        Obtiene todos los límites y parámetros de crédito de un cliente (MOCK).
        
        Args:
            nit: Número de identificación tributaria
            
        Returns:
            Diccionario con linea_credito, colchon_interno, limite_max
        """
        linea = self.get_linea_credito(nit)
        colchon = self.get_colchon_interno(nit)
        limite_max = linea * (1 - colchon)
        
        return {
            "linea_credito": linea,
            "colchon_interno": colchon,
            "colchon_pct": colchon * 100,  # Como porcentaje
            "limite_max": limite_max
        }
