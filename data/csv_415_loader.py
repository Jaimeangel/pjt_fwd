"""
Cargador de archivos CSV formato 415.
"""

from typing import Union, Dict, Any
import pandas as pd
from pathlib import Path


class Csv415Loader:
    """
    Cargador y parser de archivos CSV en formato 415.
    
    Responsabilidades:
    - Leer archivos CSV con separador ';'
    - Filtrar operaciones vigentes (UCaptura == 1)
    - Mapear columnas a nombres internos
    - Validar estructura del archivo
    """
    
    # Mapeo de columnas del 415 a nombres internos
    COLUMN_MAPPING = {
        "14Nom_Cont": "contraparte",
        "13Nro_Cont": "nit",
        "04Num_Cont": "deal",
        "71Oper": "tipo_operacion",
        "49Vlr_DerP": "vr_derecho",
        "50Vlr_OblP": "vr_obligacion",
        "82FC": "fc",
        "23Nomi_Der": "nomin_der",
        "25Nomi_Obl": "nomin_obl",
        "85TRM": "trm",
        "89FVcto": "fecha_liquidacion",
        "90FCorte": "fecha_corte",
        "UCaptura": "u_captura"
    }
    
    def __init__(self):
        """Inicializa el cargador de archivos 415."""
        pass
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        Carga el archivo 415 y retorna los datos procesados (stub).
        
        Args:
            file_path: Ruta al archivo CSV 415
            
        Returns:
            Diccionario con datos procesados
        """
        # Llamar a la función específica para operaciones
        df = self.load_operations_from_415(file_path)
        
        # Retornar como diccionario con metadatos
        return {
            "operations": df,
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    
    def load_operations_from_415(self, file_path: str) -> pd.DataFrame:
        """
        Carga operaciones vigentes del archivo 415.
        
        Lee el CSV con separador ';', filtra las filas donde UCaptura == 1,
        y mapea las columnas a nombres internos.
        
        Args:
            file_path: Ruta al archivo CSV 415
            
        Returns:
            DataFrame con operaciones vigentes y columnas renombradas
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el archivo tiene formato inválido
        """
        file_obj = Path(file_path)
        
        # Validar que el archivo existe
        if not file_obj.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        print(f"\n[Csv415Loader] Cargando archivo: {file_obj.name}")
        
        # Intentar leer con diferentes encodings
        df = None
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                print(f"   Intentando encoding: {encoding}")
                df = pd.read_csv(
                    file_path,
                    sep=';',
                    encoding=encoding,
                    dtype=str,  # Leer todo como string primero
                    na_values=['', 'NA', 'N/A', 'null', 'NULL']
                )
                print(f"   ✓ Archivo leído exitosamente con encoding {encoding}")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"   ❌ Error con encoding {encoding}: {e}")
                continue
        
        if df is None:
            raise ValueError(
                f"No se pudo leer el archivo con los encodings probados: {encodings}"
            )
        
        print(f"   ✓ Total de filas leídas: {len(df)}")
        print(f"   ✓ Total de columnas: {len(df.columns)}")
        
        # Limpiar encabezados (espacios y BOM)
        print(f"\n   Limpiando encabezados...")
        print(f"   ✓ Encabezados originales: {list(df.columns[:5])}")
        df.columns = [
            col.strip().lstrip("\ufeff") for col in df.columns
        ]
        print(f"   ✓ Encabezados después de limpiar: {list(df.columns[:5])}")
        
        # Validar que existe la columna UCaptura
        if 'UCaptura' not in df.columns:
            raise ValueError(
                f"Columna 'UCaptura' no encontrada. "
                f"Columnas disponibles: {list(df.columns[:10])}..."
            )
        
        # Filtrar solo operaciones vigentes (UCaptura == 1)
        print(f"\n   Filtrando operaciones vigentes (UCaptura == 1)...")
        
        # Convertir UCaptura a numérico para filtrar
        df['UCaptura'] = pd.to_numeric(df['UCaptura'], errors='coerce')
        
        # Contar cuántas tienen UCaptura == 1
        vigentes_count = (df['UCaptura'] == 1).sum()
        print(f"   ✓ Operaciones vigentes encontradas: {vigentes_count}")
        
        # Filtrar
        df_vigentes = df[df['UCaptura'] == 1].copy()
        
        if len(df_vigentes) == 0:
            print(f"   ⚠️  Advertencia: No se encontraron operaciones vigentes")
            # Retornar DataFrame vacío con columnas mapeadas
            empty_df = pd.DataFrame(columns=list(self.COLUMN_MAPPING.values()))
            return empty_df
        
        # Mapear columnas a nombres internos
        print(f"\n   Mapeando columnas a nombres internos...")
        
        # Verificar qué columnas del mapeo existen en el DataFrame
        columnas_disponibles = []
        columnas_faltantes = []
        
        for col_415, col_interno in self.COLUMN_MAPPING.items():
            if col_415 in df_vigentes.columns:
                columnas_disponibles.append(col_415)
            else:
                columnas_faltantes.append(col_415)
        
        print(f"   ✓ Columnas disponibles para mapear: {len(columnas_disponibles)}/{len(self.COLUMN_MAPPING)}")
        
        if columnas_faltantes:
            print(f"   ⚠️  Columnas no encontradas en el archivo:")
            for col in columnas_faltantes[:5]:  # Mostrar solo las primeras 5
                print(f"      - {col}")
        
        # Seleccionar solo las columnas que existen y renombrarlas
        columnas_a_mapear = {
            col_415: col_interno
            for col_415, col_interno in self.COLUMN_MAPPING.items()
            if col_415 in df_vigentes.columns
        }
        
        df_result = df_vigentes[list(columnas_a_mapear.keys())].copy()
        df_result = df_result.rename(columns=columnas_a_mapear)
        
        print(f"   ✓ Columnas mapeadas exitosamente")
        print(f"   ✓ Columnas finales: {list(df_result.columns)}")
        
        # Limpiar datos básicos (strip whitespace en strings)
        print(f"\n   Limpiando datos...")
        for col in df_result.columns:
            if df_result[col].dtype == 'object':
                df_result[col] = df_result[col].str.strip()
        
        print(f"   ✓ Datos limpios")
        
        # Convertir tipos de datos comunes
        print(f"\n   Convirtiendo tipos de datos...")
        
        # Columnas numéricas
        numeric_cols = ['vr_derecho', 'vr_obligacion', 'fc', 'nomin_der', 'nomin_obl', 'trm']
        for col in numeric_cols:
            if col in df_result.columns:
                df_result[col] = pd.to_numeric(df_result[col], errors='coerce')
        
        # Columnas de fecha
        date_cols = ['fecha_liquidacion', 'fecha_corte']
        for col in date_cols:
            if col in df_result.columns:
                df_result[col] = pd.to_datetime(df_result[col], errors='coerce')
        
        print(f"   ✓ Tipos de datos convertidos")
        
        print(f"\n✅ Carga completada:")
        print(f"   Total de operaciones vigentes: {len(df_result)}")
        print(f"   Columnas disponibles: {len(df_result.columns)}")
        
        return df_result
    
    def validate(self, data: Any) -> bool:
        """
        Valida que los datos cargados son correctos (stub).
        
        Args:
            data: Datos a validar
            
        Returns:
            True si los datos son válidos
        """
        if isinstance(data, pd.DataFrame):
            # Validar que tiene al menos algunas columnas requeridas
            required_cols = ['nit', 'deal', 'contraparte']
            available = [col for col in required_cols if col in data.columns]
            
            if len(available) < 2:
                print(f"   ⚠️  Advertencia: Faltan columnas requeridas")
                return False
            
            return True
        
        return False
    
    def get_column_mapping(self) -> Dict[str, str]:
        """
        Retorna el mapeo de columnas 415 → nombres internos.
        
        Returns:
            Diccionario con mapeo de columnas
        """
        return self.COLUMN_MAPPING.copy()
    
    def get_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Obtiene estadísticas básicas del DataFrame cargado.
        
        Args:
            df: DataFrame con operaciones
            
        Returns:
            Diccionario con estadísticas
        """
        if df.empty:
            return {
                "total_operaciones": 0,
                "clientes_unicos": 0,
                "tipos_operacion": []
            }
        
        stats = {
            "total_operaciones": len(df),
            "clientes_unicos": df['nit'].nunique() if 'nit' in df.columns else 0,
            "tipos_operacion": df['tipo_operacion'].unique().tolist() if 'tipo_operacion' in df.columns else [],
            "columnas_disponibles": list(df.columns),
            "valores_nulos": df.isnull().sum().to_dict()
        }
        
        return stats
