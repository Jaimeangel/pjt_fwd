"""
Utilidades para manejo de identificadores (NIT, RUT, etc).
"""

import re


def normalize_nit(nit: str | int) -> str:
    """
    Normaliza un NIT eliminando espacios, guiones y ceros a la izquierda.
    
    Args:
        nit: NIT en formato string o int
        
    Returns:
        NIT normalizado como string
        
    Examples:
        >>> normalize_nit("900.123.456-7")
        "9001234567"
        >>> normalize_nit("0000123456")
        "123456"
        >>> normalize_nit(900123456)
        "900123456"
    """
    s = str(nit).strip()
    # Eliminar espacios, puntos y guiones
    s = s.replace(" ", "").replace("-", "").replace(".", "")
    # Quitar ceros a la izquierda (si aplica)
    s = re.sub(r"^0+(?=\d)", "", s)
    return s

