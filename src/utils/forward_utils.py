"""
Utilidades para cálculos de operaciones Forward.
"""


def delta_from_punta_empresa(punta_empresa: str) -> int:
    """
    Devuelve el signo (delta) para la exposición desde la perspectiva de la EMPRESA.
    
    Este delta se usa en todos los cálculos de exposición crediticia:
    - VNA (Valor Nominal Ajustado)
    - VNE (Valor Nominal Equivalente) = vna × trm × delta × t
    - EPFp (Exposición Potencial Futura) = fc × |VNE|
    - Y todos los cálculos derivados de exposición
    
    Regla de negocio:
    - Si EMPRESA COMPRA → delta = +1
    - Si EMPRESA VENDE → delta = -1
    
    Args:
        punta_empresa: "Compra" o "Venta" (desde perspectiva de la empresa)
    
    Returns:
        +1 si empresa compra, -1 si empresa vende, 0 si valor inválido
    
    Ejemplos:
        >>> delta_from_punta_empresa("Compra")
        1
        >>> delta_from_punta_empresa("Venta")
        -1
        >>> delta_from_punta_empresa("COMPRA")
        1
        >>> delta_from_punta_empresa("")
        0
    """
    if not isinstance(punta_empresa, str):
        return 0
    
    punta = punta_empresa.strip().upper()
    
    if punta == "COMPRA":
        return 1
    elif punta == "VENTA":
        return -1
    else:
        return 0


def get_punta_opuesta(punta: str) -> str:
    """
    Devuelve la punta opuesta.
    
    Regla: La punta empresa SIEMPRE es opuesta a la punta cliente:
    - Si cliente = "Compra" → empresa = "Venta"
    - Si cliente = "Venta" → empresa = "Compra"
    
    Args:
        punta: "Compra" o "Venta"
    
    Returns:
        La punta opuesta, manteniendo el case original
    
    Ejemplos:
        >>> get_punta_opuesta("Compra")
        "Venta"
        >>> get_punta_opuesta("Venta")
        "Compra"
        >>> get_punta_opuesta("COMPRA")
        "VENTA"
    """
    if not isinstance(punta, str):
        return ""
    
    punta_stripped = punta.strip()
    if not punta_stripped:
        return ""
    
    punta_upper = punta_stripped.upper()
    
    if punta_upper == "COMPRA":
        # Mantener el case original (detectar si es todo mayúsculas o capitalizado)
        if punta_stripped.isupper():
            return "VENTA"
        elif punta_stripped[0].isupper():
            return "Venta"
        else:
            return "venta"
    elif punta_upper == "VENTA":
        # Mantener el case original (detectar si es todo mayúsculas o capitalizado)
        if punta_stripped.isupper():
            return "COMPRA"
        elif punta_stripped[0].isupper():
            return "Compra"
        else:
            return "compra"
    else:
        return ""

