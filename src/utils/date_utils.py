"""
Utilidades para manejo de fechas y cálculo de días hábiles.

Este módulo proporciona funciones para trabajar con fechas en el contexto
de días hábiles en Colombia, excluyendo fines de semana y días festivos.
"""

from datetime import date, timedelta
import holidays


# Inicializar días festivos de Colombia
CO_HOLIDAYS = holidays.Colombia()


def dias_habiles_colombia(fecha_inicio: date, fecha_fin: date) -> int:
    """
    Cuenta los días hábiles entre dos fechas, excluyendo fines de semana y festivos colombianos.
    
    Los días hábiles son aquellos que NO son:
    - Sábados (weekday == 5)
    - Domingos (weekday == 6)
    - Festivos colombianos (según librería holidays)
    
    Args:
        fecha_inicio: Fecha de inicio (inclusive)
        fecha_fin: Fecha de fin (inclusive)
        
    Returns:
        Número de días hábiles entre las fechas (inclusive)
        Retorna 0 si alguna fecha es None o si fecha_fin < fecha_inicio
        
    Ejemplo:
        >>> from datetime import date
        >>> dias_habiles_colombia(date(2025, 1, 6), date(2025, 1, 10))
        5  # Lunes a viernes (sin festivos en ese rango)
    """
    # Validaciones
    if not fecha_inicio or not fecha_fin:
        return 0
    
    if fecha_fin < fecha_inicio:
        return 0
    
    # Contar días hábiles
    delta = timedelta(days=1)
    count = 0
    current = fecha_inicio
    
    while current <= fecha_fin:
        # Verificar que no sea fin de semana (lunes=0, ..., viernes=4, sábado=5, domingo=6)
        is_weekday = current.weekday() < 5
        
        # Verificar que no sea festivo colombiano
        is_not_holiday = current not in CO_HOLIDAYS
        
        # Contar si es día hábil
        if is_weekday and is_not_holiday:
            count += 1
        
        current += delta
    
    return count


def aplicar_reglas_plazo(td: int) -> int:
    """
    Aplica las reglas de ajuste de plazo según el informe 415.
    
    Reglas:
    1. Restar 1 al plazo calculado
    2. Aplicar piso mínimo de 10 días
    
    Args:
        td: Plazo en días hábiles calculado
        
    Returns:
        Plazo ajustado según reglas (td - 1, con mínimo de 10)
        
    Ejemplo:
        >>> aplicar_reglas_plazo(15)
        14  # 15 - 1 = 14
        >>> aplicar_reglas_plazo(5)
        10  # 5 - 1 = 4, pero piso es 10
        >>> aplicar_reglas_plazo(11)
        10  # 11 - 1 = 10
    """
    # Aplicar -1 y piso de 10
    td_ajustado = max(td - 1, 10)
    return td_ajustado

