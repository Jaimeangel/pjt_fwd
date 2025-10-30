"""
Procesador de operaciones Forward del informe 415.
Calcula columnas derivadas y métricas financieras.
"""

import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime, date
import holidays


class Forward415Processor:
    """
    Procesador de operaciones Forward del informe 415.
    
    Responsabilidades:
    - Calcular columnas derivadas financieras
    - Calcular días hábiles usando calendario de Colombia
    - Enriquecer operaciones con métricas calculadas
    """
    
    def __init__(self):
        """Inicializa el procesador."""
        # Calendario de festivos de Colombia
        self.colombia_holidays = holidays.Colombia()
    
    def process_operations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Procesa operaciones y calcula columnas derivadas.
        
        Columnas calculadas:
        - vr: Valor razonable (vr_derecho - vr_obligacion)
        - delta: Dirección (1 para COMPRA, -1 para otros)
        - vna: Valor nominal ajustado
        - td: Días al vencimiento (días hábiles - 1, mínimo 10)
        - t: Tiempo ajustado (sqrt(min(td, 252) / 252))
        - vne: Valor nominal equivalente
        - EPFp: Exposición potencial futura
        
        Args:
            df: DataFrame con operaciones vigentes del 415
            
        Returns:
            DataFrame enriquecido con columnas derivadas
        """
        if df.empty:
            print("[Forward415Processor] DataFrame vacío, no hay operaciones para procesar")
            return df
        
        print(f"\n[Forward415Processor] Procesando {len(df)} operaciones...")
        
        # Crear copia para no modificar el original
        df_result = df.copy()
        
        # 1. Calcular VR (Valor Razonable)
        print("   Calculando VR (vr_derecho - vr_obligacion)...")
        df_result['vr'] = df_result['vr_derecho'] - df_result['vr_obligacion']
        print(f"      ✓ VR calculado para {len(df_result)} operaciones")
        
        # 2. Calcular DELTA (dirección)
        print("   Calculando DELTA (1 si COMPRA, -1 si otro)...")
        df_result['delta'] = df_result['tipo_operacion'].apply(
            lambda x: 1 if str(x).upper() == 'COMPRA' else -1
        )
        compras = (df_result['delta'] == 1).sum()
        ventas = (df_result['delta'] == -1).sum()
        print(f"      ✓ COMPRAS: {compras}, VENTAS: {ventas}")
        
        # 3. Calcular VNA (Valor Nominal Ajustado)
        print("   Calculando VNA (nomin_der si delta=1, nomin_obl si delta=-1)...")
        df_result['vna'] = df_result.apply(
            lambda row: row['nomin_der'] if row['delta'] == 1 else row['nomin_obl'],
            axis=1
        )
        print(f"      ✓ VNA calculado")
        
        # 4. Calcular TD (Días al vencimiento en días hábiles)
        print("   Calculando TD (días hábiles al vencimiento)...")
        df_result['td'] = df_result.apply(
            lambda row: self._calculate_business_days(
                row.get('fecha_corte'),
                row.get('fecha_liquidacion')
            ),
            axis=1
        )
        
        # Contar cuántas tienen td válido
        td_validos = df_result['td'].notna().sum()
        td_nulos = df_result['td'].isna().sum()
        print(f"      ✓ TD calculado: {td_validos} válidos, {td_nulos} nulos")
        
        if td_validos > 0:
            td_min = df_result['td'].min()
            td_max = df_result['td'].max()
            td_mean = df_result['td'].mean()
            print(f"      ✓ Rango TD: mín={td_min:.0f}, máx={td_max:.0f}, media={td_mean:.1f} días")
        
        # 5. Calcular T (Tiempo ajustado)
        print("   Calculando T (sqrt(min(td, 252) / 252))...")
        df_result['t'] = df_result['td'].apply(self._calculate_time_factor)
        t_validos = df_result['t'].notna().sum()
        print(f"      ✓ T calculado para {t_validos} operaciones")
        
        # 6. Calcular VNE (Valor Nominal Equivalente)
        print("   Calculando VNE (vna * trm * delta * t)...")
        df_result['vne'] = df_result.apply(
            lambda row: self._calculate_vne(
                row.get('vna'),
                row.get('trm'),
                row.get('delta'),
                row.get('t')
            ),
            axis=1
        )
        vne_validos = df_result['vne'].notna().sum()
        print(f"      ✓ VNE calculado para {vne_validos} operaciones")
        
        # 7. Calcular EPFp (Exposición Potencial Futura)
        print("   Calculando EPFp (fc * vne)...")
        df_result['EPFp'] = df_result.apply(
            lambda row: self._calculate_epfp(
                row.get('fc'),
                row.get('vne')
            ),
            axis=1
        )
        epfp_validos = df_result['EPFp'].notna().sum()
        print(f"      ✓ EPFp calculado para {epfp_validos} operaciones")
        
        # Resumen
        print(f"\n✅ Procesamiento completado:")
        print(f"   Operaciones procesadas: {len(df_result)}")
        print(f"   Columnas originales: {len(df.columns)}")
        print(f"   Columnas finales: {len(df_result.columns)}")
        print(f"   Columnas añadidas: {len(df_result.columns) - len(df.columns)}")
        print(f"   Nuevas columnas: {list(set(df_result.columns) - set(df.columns))}")
        
        return df_result
    
    def _calculate_business_days(
        self,
        fecha_corte: Optional[pd.Timestamp],
        fecha_liquidacion: Optional[pd.Timestamp]
    ) -> Optional[int]:
        """
        Calcula días hábiles entre fecha_corte y fecha_liquidacion.
        
        Excluye:
        - Sábados
        - Domingos
        - Festivos de Colombia
        
        Args:
            fecha_corte: Fecha de corte del 415
            fecha_liquidacion: Fecha de vencimiento de la operación
            
        Returns:
            max(días_hábiles - 1, 10) o None si no hay fechas válidas
        """
        # Validar que ambas fechas existen y son válidas
        if pd.isna(fecha_corte) or pd.isna(fecha_liquidacion):
            return None
        
        try:
            # Convertir a datetime.date si es necesario
            if isinstance(fecha_corte, pd.Timestamp):
                fecha_corte = fecha_corte.date()
            if isinstance(fecha_liquidacion, pd.Timestamp):
                fecha_liquidacion = fecha_liquidacion.date()
            
            # Si la fecha de liquidación es anterior o igual al corte, retornar None
            if fecha_liquidacion <= fecha_corte:
                return None
            
            # Contar días hábiles
            dias_habiles = 0
            current_date = fecha_corte
            
            while current_date < fecha_liquidacion:
                current_date += pd.Timedelta(days=1)
                
                # Verificar si es día hábil (no sábado, no domingo, no festivo)
                if current_date.weekday() < 5:  # Lunes=0, Viernes=4
                    if current_date not in self.colombia_holidays:
                        dias_habiles += 1
            
            # Aplicar fórmula: max(dias_habiles - 1, 10)
            td = max(dias_habiles - 1, 10)
            
            return td
            
        except Exception as e:
            print(f"      ⚠️  Error calculando días hábiles: {e}")
            return None
    
    def _calculate_time_factor(self, td: Optional[float]) -> Optional[float]:
        """
        Calcula el factor de tiempo ajustado.
        
        Fórmula: t = sqrt(min(td, 252) / 252)
        
        Args:
            td: Días al vencimiento
            
        Returns:
            Factor de tiempo redondeado a 14 decimales, o None
        """
        if pd.isna(td) or td is None:
            return None
        
        try:
            # Aplicar fórmula: sqrt(min(td, 252) / 252)
            td_capped = min(td, 252)
            t = np.sqrt(td_capped / 252)
            
            # Redondear a 14 decimales
            t_rounded = round(t, 14)
            
            return t_rounded
            
        except Exception as e:
            print(f"      ⚠️  Error calculando factor de tiempo: {e}")
            return None
    
    def _calculate_vne(
        self,
        vna: Optional[float],
        trm: Optional[float],
        delta: Optional[int],
        t: Optional[float]
    ) -> Optional[float]:
        """
        Calcula el Valor Nominal Equivalente.
        
        Fórmula: vne = vna * trm * delta * t
        
        Args:
            vna: Valor nominal ajustado
            trm: Tasa representativa del mercado
            delta: Dirección (1 o -1)
            t: Factor de tiempo
            
        Returns:
            VNE redondeado a 6 decimales, o None
        """
        # Validar que todos los valores existen y son válidos
        if any(pd.isna(x) or x is None for x in [vna, trm, delta, t]):
            return None
        
        try:
            # Calcular VNE
            vne = vna * trm * delta * t
            
            # Redondear a 6 decimales
            vne_rounded = round(vne, 6)
            
            return vne_rounded
            
        except Exception as e:
            print(f"      ⚠️  Error calculando VNE: {e}")
            return None
    
    def _calculate_epfp(
        self,
        fc: Optional[float],
        vne: Optional[float]
    ) -> Optional[float]:
        """
        Calcula la Exposición Potencial Futura.
        
        Fórmula: EPFp = fc * vne
        
        Args:
            fc: Factor de conversión
            vne: Valor nominal equivalente
            
        Returns:
            EPFp (sin redondeo adicional específico), o None
        """
        # Validar que ambos valores existen
        if pd.isna(fc) or pd.isna(vne) or fc is None or vne is None:
            return None
        
        try:
            # Calcular EPFp
            epfp = fc * vne
            
            return epfp
            
        except Exception as e:
            print(f"      ⚠️  Error calculando EPFp: {e}")
            return None
    
    def get_summary_stats(self, df: pd.DataFrame) -> dict:
        """
        Obtiene estadísticas de resumen de las operaciones procesadas.
        
        Args:
            df: DataFrame con operaciones procesadas
            
        Returns:
            Diccionario con estadísticas
        """
        if df.empty:
            return {"total_operaciones": 0}
        
        stats = {
            "total_operaciones": len(df),
            "compras": (df['delta'] == 1).sum() if 'delta' in df.columns else 0,
            "ventas": (df['delta'] == -1).sum() if 'delta' in df.columns else 0,
        }
        
        # Estadísticas de VR
        if 'vr' in df.columns:
            stats['vr_total'] = df['vr'].sum()
            stats['vr_promedio'] = df['vr'].mean()
        
        # Estadísticas de TD
        if 'td' in df.columns:
            td_validos = df['td'].notna()
            if td_validos.any():
                stats['td_min'] = df.loc[td_validos, 'td'].min()
                stats['td_max'] = df.loc[td_validos, 'td'].max()
                stats['td_promedio'] = df.loc[td_validos, 'td'].mean()
        
        # Estadísticas de EPFp
        if 'EPFp' in df.columns:
            epfp_validos = df['EPFp'].notna()
            if epfp_validos.any():
                stats['EPFp_total'] = df.loc[epfp_validos, 'EPFp'].sum()
                stats['EPFp_promedio'] = df.loc[epfp_validos, 'EPFp'].mean()
        
        return stats


def enrich_operations_with_calculations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Función helper para enriquecer operaciones con cálculos derivados.
    
    Esta es una función conveniente que crea un procesador y aplica
    todos los cálculos de una vez.
    
    Args:
        df: DataFrame con operaciones vigentes del 415
        
    Returns:
        DataFrame enriquecido con columnas derivadas
    """
    processor = Forward415Processor()
    return processor.process_operations(df)

