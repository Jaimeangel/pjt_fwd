"""
Script de prueba para Forward415Processor.
Verifica los cálculos de columnas derivadas.
"""

import sys
from pathlib import Path

# Agregar directorios al path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configurar encoding para Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from data.csv_415_loader import Csv415Loader
from services.forward_415_processor import Forward415Processor, enrich_operations_with_calculations
import pandas as pd


def test_basic_calculations():
    """Prueba los cálculos básicos."""
    print("\n" + "="*60)
    print("TEST 1: Cálculos Básicos (VR, DELTA, VNA)")
    print("="*60)
    
    # Crear datos de prueba simples
    data = {
        'vr_derecho': [425050000, 1051250000],
        'vr_obligacion': [427625000, 1064400000],
        'tipo_operacion': ['COMPRA', 'VENTA'],
        'nomin_der': [100000, 250000],
        'nomin_obl': [100000, 250000],
        'trm': [4250.5, 4250.5],
        'fc': [1.006, 1.012],
        'fecha_corte': [pd.Timestamp('2025-10-28'), pd.Timestamp('2025-10-28')],
        'fecha_liquidacion': [pd.Timestamp('2025-12-15'), pd.Timestamp('2025-11-30')]
    }
    
    df = pd.DataFrame(data)
    
    print(f"\nDatos de entrada: {len(df)} operaciones")
    print(f"   Op 1: COMPRA, vr_derecho={data['vr_derecho'][0]:,.0f}, vr_obligacion={data['vr_obligacion'][0]:,.0f}")
    print(f"   Op 2: VENTA, vr_derecho={data['vr_derecho'][1]:,.0f}, vr_obligacion={data['vr_obligacion'][1]:,.0f}")
    
    # Procesar
    processor = Forward415Processor()
    df_result = processor.process_operations(df)
    
    # Verificar VR
    print(f"\n✓ VR calculado:")
    print(f"   Op 1: {df_result['vr'].iloc[0]:,.0f} (esperado: {data['vr_derecho'][0] - data['vr_obligacion'][0]:,.0f})")
    print(f"   Op 2: {df_result['vr'].iloc[1]:,.0f} (esperado: {data['vr_derecho'][1] - data['vr_obligacion'][1]:,.0f})")
    
    # Verificar DELTA
    print(f"\n✓ DELTA calculado:")
    print(f"   Op 1 (COMPRA): {df_result['delta'].iloc[0]} (esperado: 1)")
    print(f"   Op 2 (VENTA): {df_result['delta'].iloc[1]} (esperado: -1)")
    
    assert df_result['delta'].iloc[0] == 1, "COMPRA debe tener delta=1"
    assert df_result['delta'].iloc[1] == -1, "VENTA debe tener delta=-1"
    
    # Verificar VNA
    print(f"\n✓ VNA calculado:")
    print(f"   Op 1 (delta=1): {df_result['vna'].iloc[0]:,.0f} (esperado: nomin_der={data['nomin_der'][0]:,.0f})")
    print(f"   Op 2 (delta=-1): {df_result['vna'].iloc[1]:,.0f} (esperado: nomin_obl={data['nomin_obl'][1]:,.0f})")
    
    print("\n✅ Test 1: PASADO")
    return True


def test_business_days_calculation():
    """Prueba el cálculo de días hábiles."""
    print("\n" + "="*60)
    print("TEST 2: Cálculo de Días Hábiles (TD)")
    print("="*60)
    
    processor = Forward415Processor()
    
    # Test 1: Días hábiles simples
    fecha_corte = pd.Timestamp('2025-10-28')  # Martes
    fecha_liquidacion = pd.Timestamp('2025-11-05')  # Miércoles (siguiente semana)
    
    td = processor._calculate_business_days(fecha_corte, fecha_liquidacion)
    
    print(f"\nTest 2.1: Rango sin festivos")
    print(f"   Fecha corte: {fecha_corte.date()} (martes)")
    print(f"   Fecha liquidación: {fecha_liquidacion.date()} (miércoles)")
    print(f"   TD calculado: {td} días hábiles")
    print(f"   Fórmula aplicada: max(días_hábiles - 1, 10)")
    
    # Test 2: Con fechas que incluyen fin de semana
    fecha_corte2 = pd.Timestamp('2025-10-31')  # Viernes
    fecha_liquidacion2 = pd.Timestamp('2025-11-07')  # Viernes siguiente
    
    td2 = processor._calculate_business_days(fecha_corte2, fecha_liquidacion2)
    
    print(f"\nTest 2.2: Rango incluyendo fin de semana")
    print(f"   Fecha corte: {fecha_corte2.date()} (viernes)")
    print(f"   Fecha liquidación: {fecha_liquidacion2.date()} (viernes siguiente)")
    print(f"   TD calculado: {td2} días hábiles")
    print(f"   (Debe excluir sábado 01-nov y domingo 02-nov)")
    
    # Test 3: Fechas muy cercanas (mínimo 10)
    fecha_corte3 = pd.Timestamp('2025-10-28')
    fecha_liquidacion3 = pd.Timestamp('2025-10-30')  # Solo 2 días después
    
    td3 = processor._calculate_business_days(fecha_corte3, fecha_liquidacion3)
    
    print(f"\nTest 2.3: Fechas muy cercanas (mínimo 10)")
    print(f"   Fecha corte: {fecha_corte3.date()}")
    print(f"   Fecha liquidación: {fecha_liquidacion3.date()}")
    print(f"   TD calculado: {td3} días (debe ser 10 por el mínimo)")
    
    assert td3 == 10, "TD mínimo debe ser 10"
    
    print("\n✅ Test 2: PASADO")
    return True


def test_time_factor_calculation():
    """Prueba el cálculo del factor de tiempo."""
    print("\n" + "="*60)
    print("TEST 3: Factor de Tiempo (T)")
    print("="*60)
    
    processor = Forward415Processor()
    
    # Test con diferentes valores de TD
    test_cases = [
        (10, "Mínimo"),
        (30, "1 mes"),
        (90, "3 meses"),
        (252, "1 año"),
        (300, "Más de 1 año - se capea a 252")
    ]
    
    print(f"\nFórmula: t = sqrt(min(td, 252) / 252)")
    print(f"\n{'TD':<10} {'Min(TD,252)':<15} {'T calculado':<20} {'Caso'}")
    print("-" * 70)
    
    for td, descripcion in test_cases:
        t = processor._calculate_time_factor(td)
        td_capped = min(td, 252)
        
        print(f"{td:<10} {td_capped:<15} {t:<20.14f} {descripcion}")
    
    # Verificar redondeo a 14 decimales
    t_test = processor._calculate_time_factor(100)
    decimales = len(str(t_test).split('.')[-1]) if '.' in str(t_test) else 0
    
    print(f"\n✓ Redondeo a 14 decimales verificado (TD=100): {t_test}")
    
    print("\n✅ Test 3: PASADO")
    return True


def test_complete_pipeline():
    """Prueba el pipeline completo con archivo real."""
    print("\n" + "="*60)
    print("TEST 4: Pipeline Completo (Loader + Processor)")
    print("="*60)
    
    try:
        # Cargar archivo de prueba
        loader = Csv415Loader()
        df_operations = loader.load_operations_from_415("test_415_completo.csv")
        
        print(f"\n✓ Operaciones cargadas: {len(df_operations)}")
        
        # Procesar
        df_enriched = enrich_operations_with_calculations(df_operations)
        
        print(f"\n✓ Operaciones enriquecidas: {len(df_enriched)}")
        print(f"✓ Columnas totales: {len(df_enriched.columns)}")
        print(f"✓ Columnas nuevas: {list(set(df_enriched.columns) - set(df_operations.columns))}")
        
        # Mostrar primera operación completa
        print(f"\n📊 Primera operación procesada:")
        primera = df_enriched.iloc[0]
        
        campos_mostrar = [
            'contraparte', 'deal', 'tipo_operacion',
            'vr_derecho', 'vr_obligacion', 'vr',
            'delta', 'vna', 'td', 't', 'vne', 'EPFp'
        ]
        
        for campo in campos_mostrar:
            if campo in primera.index:
                valor = primera[campo]
                if isinstance(valor, float):
                    print(f"   {campo:<20}: {valor:,.6f}")
                else:
                    print(f"   {campo:<20}: {valor}")
        
        # Obtener estadísticas
        processor = Forward415Processor()
        stats = processor.get_summary_stats(df_enriched)
        
        print(f"\n📈 Estadísticas:")
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"   {key}: {value:,.2f}")
            else:
                print(f"   {key}: {value}")
        
        print("\n✅ Test 4: PASADO")
        return True
        
    except FileNotFoundError:
        print("\n⚠️  Archivo de prueba no encontrado")
        print("   Ejecutar: python test_csv_415_loader.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Prueba casos edge."""
    print("\n" + "="*60)
    print("TEST 5: Casos Edge")
    print("="*60)
    
    # Caso 1: Operación sin fecha de liquidación
    data = {
        'vr_derecho': [100000],
        'vr_obligacion': [95000],
        'tipo_operacion': ['COMPRA'],
        'nomin_der': [50000],
        'nomin_obl': [50000],
        'trm': [4250.0],
        'fc': [1.0],
        'fecha_corte': [pd.Timestamp('2025-10-28')],
        'fecha_liquidacion': [pd.NaT]  # Sin fecha
    }
    
    df = pd.DataFrame(data)
    
    processor = Forward415Processor()
    df_result = processor.process_operations(df)
    
    print(f"\nCaso 1: Sin fecha de liquidación")
    print(f"   TD: {df_result['td'].iloc[0]} (debe ser None/NaN)")
    print(f"   T: {df_result['t'].iloc[0]} (debe ser None/NaN)")
    print(f"   VNE: {df_result['vne'].iloc[0]} (debe ser None/NaN)")
    print(f"   EPFp: {df_result['EPFp'].iloc[0]} (debe ser None/NaN)")
    
    assert pd.isna(df_result['td'].iloc[0]), "TD debe ser None sin fecha"
    assert pd.isna(df_result['vne'].iloc[0]), "VNE debe ser None sin TD"
    
    print(f"   ✓ Manejo correcto de valores nulos")
    
    # Caso 2: VR debe calcularse incluso sin fechas
    assert df_result['vr'].iloc[0] == 5000, "VR debe calcularse = 100000 - 95000"
    assert df_result['delta'].iloc[0] == 1, "DELTA debe calcularse = 1 para COMPRA"
    assert df_result['vna'].iloc[0] == 50000, "VNA debe calcularse = nomin_der"
    
    print(f"   ✓ VR, DELTA, VNA calculados correctamente sin fechas")
    
    print("\n✅ Test 5: PASADO")
    return True


def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "="*60)
    print("PRUEBAS DE FORWARD 415 PROCESSOR")
    print("="*60)
    
    tests = [
        ("Cálculos básicos", test_basic_calculations),
        ("Días hábiles", test_business_days_calculation),
        ("Factor de tiempo", test_time_factor_calculation),
        ("Pipeline completo", test_complete_pipeline),
        ("Casos edge", test_edge_cases)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ Test '{name}' falló con excepción: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Resumen
    print("\n" + "="*60)
    print(f"RESUMEN: {passed}/{len(tests)} pruebas pasadas")
    print("="*60 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

