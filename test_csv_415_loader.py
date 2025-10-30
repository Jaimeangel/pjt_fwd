"""
Script de prueba para Csv415Loader.
"""

import sys
from pathlib import Path

# Agregar el directorio data al path
sys.path.insert(0, str(Path(__file__).parent))

# Configurar encoding para Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from data.csv_415_loader import Csv415Loader


def test_csv_415_loader():
    """Prueba el cargador de archivos 415."""
    print("\n" + "="*60)
    print("PRUEBA: Csv415Loader")
    print("="*60)
    
    loader = Csv415Loader()
    
    # Test 1: Cargar archivo de prueba
    print("\nTest 1: Cargar archivo de prueba")
    print("-" * 60)
    
    try:
        df = loader.load_operations_from_415("test_415_completo.csv")
        
        print(f"\n[OK] Archivo cargado exitosamente")
        print(f"   Total de filas: {len(df)}")
        print(f"   Columnas: {list(df.columns)}")
        
        if len(df) > 0:
            print(f"\n   Primera fila:")
            for col in df.columns:
                print(f"      {col}: {df[col].iloc[0]}")
        
        # Validar
        is_valid = loader.validate(df)
        print(f"\n   Validación: {'[OK]' if is_valid else '[FAIL]'}")
        
        # Estadísticas
        stats = loader.get_stats(df)
        print(f"\n   Estadísticas:")
        print(f"      Total operaciones: {stats['total_operaciones']}")
        print(f"      Clientes únicos: {stats['clientes_unicos']}")
        print(f"      Tipos de operación: {stats['tipos_operacion']}")
        
        print("\n✅ Test 1: PASADO")
        
    except FileNotFoundError as e:
        print(f"\n⚠️  Archivo de prueba no encontrado: {e}")
        print(f"   Creando archivo de prueba...")
        crear_archivo_prueba_completo()
        print(f"   Archivo creado. Por favor ejecutar de nuevo.")
        return False
    
    except Exception as e:
        print(f"\n❌ Test 1: FALLIDO - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def crear_archivo_prueba_completo():
    """Crea un archivo de prueba con formato 415 completo."""
    contenido = """14Nom_Cont;13Nro_Cont;04Num_Cont;71Oper;49Vlr_DerP;50Vlr_OblP;82FC;23Nomi_Der;25Nomi_Obl;85TRM;89FVcto;90FCorte;UCaptura
Cliente Ejemplo S.A.;123456789;FWD001;FWD;425050000;427625000;1.006;100000;100000;4250.50;2025-12-15;2025-10-28;1
Corporación ABC Ltda.;987654321;FWD002;FWD;1051250000;1064400000;1.012;250000;250000;4250.50;2025-11-30;2025-10-28;1
Empresa XYZ S.A.S.;555444333;FWD003;FWD;315375000;319931250;1.014;75000;75000;4250.50;2026-01-20;2025-10-28;1
Cliente Ejemplo S.A.;123456789;FWD004;FWD;630750000;637687500;1.011;150000;150000;4250.50;2025-12-31;2025-10-28;0
Corporación ABC Ltda.;987654321;FWD005;FWD;210250000;212525000;1.011;50000;50000;4250.50;2026-02-10;2025-10-28;0
"""
    
    with open("test_415_completo.csv", "w", encoding="utf-8") as f:
        f.write(contenido)
    
    print(f"   Archivo 'test_415_completo.csv' creado con 5 filas (3 vigentes)")


def test_con_archivo_completo():
    """Prueba con archivo completo."""
    print("\n" + "="*60)
    print("PRUEBA: Con archivo completo (3 vigentes + 2 no vigentes)")
    print("="*60)
    
    loader = Csv415Loader()
    
    try:
        df = loader.load_operations_from_415("test_415_completo.csv")
        
        print(f"\n✅ Archivo cargado")
        print(f"   Operaciones vigentes (UCaptura=1): {len(df)}")
        print(f"   Esperado: 3")
        
        if len(df) == 3:
            print(f"   [OK] Filtrado correcto")
        else:
            print(f"   [FAIL] Se esperaban 3 operaciones vigentes, se obtuvieron {len(df)}")
        
        # Mostrar deals
        if 'deal' in df.columns:
            print(f"\n   Deals vigentes:")
            for deal in df['deal'].values:
                print(f"      - {deal}")
        
        return True
        
    except FileNotFoundError:
        print(f"\n⚠️  Creando archivo de prueba...")
        crear_archivo_prueba_completo()
        print(f"   Archivo creado. Ejecutar de nuevo.")
        return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mapeo_columnas():
    """Prueba el mapeo de columnas."""
    print("\n" + "="*60)
    print("PRUEBA: Mapeo de columnas")
    print("="*60)
    
    loader = Csv415Loader()
    
    mapeo = loader.get_column_mapping()
    
    print(f"\nMapeo de columnas 415 → nombres internos:")
    print(f"{'Columna 415':<20} → {'Nombre interno':<20}")
    print("-" * 45)
    
    for col_415, col_interno in mapeo.items():
        print(f"{col_415:<20} → {col_interno:<20}")
    
    print(f"\n✅ Total de columnas mapeadas: {len(mapeo)}")
    
    return True


def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "="*60)
    print("PRUEBAS DE CSV 415 LOADER")
    print("="*60)
    
    tests_passed = 0
    tests_total = 3
    
    # Test 1: Mapeo de columnas
    if test_mapeo_columnas():
        tests_passed += 1
    
    # Test 2: Cargar archivo completo
    if test_con_archivo_completo():
        tests_passed += 1
    
    # Test 3: Validación
    if test_csv_415_loader():
        tests_passed += 1
    
    # Resumen
    print("\n" + "="*60)
    print(f"RESUMEN: {tests_passed}/{tests_total} pruebas pasadas")
    print("="*60 + "\n")
    
    return 0 if tests_passed == tests_total else 1


if __name__ == "__main__":
    sys.exit(main())

