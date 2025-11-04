"""
Módulo para cargar archivos CSV con curvas IBR (Interbank Reference Rate).

Este módulo proporciona funciones para leer y validar archivos CSV
que contienen curvas de tasas IBR, mapeando días a tasas decimales.
"""

import pandas as pd
from typing import Dict


def load_ibr_csv(file_path: str) -> Dict[int, float]:
    """
    Lee un archivo CSV sin headers, delimitado por ';', con encoding UTF-8 (fallback a latin-1).
    La primera columna se interpreta como días (int) y la segunda como tasa en DECIMAL (float).
    Retorna un diccionario {dias: tasa_decimal}.
    
    Args:
        file_path: Ruta al archivo CSV
        
    Returns:
        Diccionario {dias: tasa_decimal}
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo no tiene el formato esperado
    """
    ibr_curve = {}
    
    try:
        # Intentar con utf-8
        df = pd.read_csv(file_path, sep=';', header=None, encoding='utf-8')
    except UnicodeDecodeError:
        # Fallback a latin-1
        df = pd.read_csv(file_path, sep=';', header=None, encoding='latin-1')
    
    # Verificar que el archivo tenga al menos 2 columnas
    if df.shape[1] < 2:
        return {}
    
    # Limpiar posibles BOM o espacios en blanco de los datos
    df[0] = df[0].astype(str).str.strip()
    df[1] = df[1].astype(str).str.strip()
    
    # Convertir la primera columna a int (días) y la segunda a float (tasa decimal)
    # Coerce errors will turn invalid parsing into NaN, then dropna will remove them
    df[0] = pd.to_numeric(df[0], errors='coerce').astype('Int64')  # Use Int64 to allow NaN
    df[1] = pd.to_numeric(df[1], errors='coerce')
    
    # Eliminar filas con valores NaN resultantes de la conversión
    df = df.dropna()
    
    # Asegurarse de que los días sean positivos
    df = df[df[0] >= 0]
    
    # Crear el diccionario {dias: tasa_decimal}
    # Convertir de Int64 a int estándar de Python
    ibr_curve = {int(row[0]): float(row[1]) for _, row in df.iterrows()}
    
    return ibr_curve


def validate_ibr_curve(curve: Dict[int, float]) -> bool:
    """
    Valida que la curva IBR contenga datos válidos.
    
    Criterios de validación:
    - Debe tener al menos un punto.
    - Todas las claves (días) deben ser enteros no negativos.
    - Todos los valores (tasas) deben ser floats no negativos.
    
    Args:
        curve: Diccionario {dias: tasa_decimal} a validar
        
    Returns:
        True si la curva es válida, False en caso contrario
    """
    if not curve:
        return False
    
    for days, rate in curve.items():
        # Validar tipo y valor de días
        if not isinstance(days, int) or days < 0:
            return False
        
        # Validar tipo y valor de tasa
        if not isinstance(rate, (int, float)) or rate < 0:
            return False
    
    return True
