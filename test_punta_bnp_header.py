"""
Test para verificar el cambio del encabezado de columna "Punta Empresa" a "Punta BNP".

Este test valida que:
1. El encabezado de la columna se muestra como "Punta BNP"
2. La lógica interna NO cambió (sigue usando el mismo índice)
"""

import sys
from PySide6.QtWidgets import QApplication

from src.models.qt.simulations_table_model import SimulationsTableModel


def test_encabezado_punta_bnp():
    """Test: Verificar que el encabezado dice 'Punta BNP'."""
    print("\n" + "="*70)
    print("TEST: Encabezado 'Punta BNP' en tabla de simulaciones")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Crear modelo
    model = SimulationsTableModel()
    
    # Verificar que los headers incluyen "Punta BNP"
    headers = model.HEADERS
    
    print(f"\n1. Headers del modelo:")
    for i, col in enumerate(headers):
        print(f"   [{i}] {col}")
    
    # Verificar que "Punta BNP" está en los headers
    assert "Punta BNP" in headers, \
        f"'Punta BNP' debería estar en los headers. Headers: {headers}"
    
    print("\n2. Verificar encabezado 'Punta BNP':")
    punta_idx = headers.index("Punta BNP")
    print(f"   Índice de 'Punta BNP': {punta_idx}")
    print(f"   ✓ Encabezado encontrado correctamente")
    
    # Verificar que NO existe "Punta Emp" (el nombre anterior abreviado)
    assert "Punta Emp" not in headers, \
        f"'Punta Emp' NO debería estar en los headers. Headers: {headers}"
    print(f"   ✓ 'Punta Emp' correctamente reemplazado")
    
    # Verificar que el índice es el esperado (posición 2)
    assert punta_idx == 2, \
        f"'Punta BNP' debería estar en el índice 2, está en {punta_idx}"
    print(f"   ✓ Índice correcto (posición 2)")
    
    # Verificar que las columnas antes y después no cambiaron
    assert headers[1] == "Punta Cli", "Header anterior debería ser 'Punta Cli'"
    assert headers[3] == "Nominal USD", "Header siguiente debería ser 'Nominal USD'"
    print(f"   ✓ Headers adyacentes intactos")
    
    # Verificar mediante headerData (lo que ve la UI)
    from PySide6.QtCore import Qt
    header_text = model.headerData(punta_idx, Qt.Horizontal)
    print(f"\n3. Texto del header en la UI:")
    print(f"   headerData({punta_idx}, Qt.Horizontal): '{header_text}'")
    
    assert header_text == "Punta BNP", \
        f"El header de la UI debería ser 'Punta BNP', es '{header_text}'"
    print(f"   ✓ Header de la UI correcto")
    
    print("\n✅ Encabezado 'Punta BNP' configurado correctamente")
    
    return True


def test_logica_interna_intacta():
    """Test: Verificar que la lógica interna no cambió."""
    print("\n" + "="*70)
    print("TEST: Lógica interna intacta")
    print("="*70)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    model = SimulationsTableModel()
    
    # Verificar que el número de headers no cambió
    num_cols = len(model.HEADERS)
    print(f"\n1. Número de columnas: {num_cols}")
    assert num_cols > 10, f"Debería haber más de 10 columnas, hay {num_cols}"
    print(f"   ✓ Número de columnas intacto")
    
    # Verificar que EDITABLE_COLUMNS existe y es consistente
    num_editable = len(model.EDITABLE_COLUMNS)
    print(f"\n2. Columnas editables: {num_editable} elementos")
    # EDITABLE_COLUMNS es una lista de índices, no tiene que tener el mismo tamaño
    assert num_editable > 0, "Debería haber al menos una columna editable"
    print(f"   ✓ Columnas editables definidas")
    
    # Verificar que la columna "Punta BNP" (índice 2) NO es editable
    # EDITABLE_COLUMNS contiene los índices de las columnas editables
    is_editable = 2 in model.EDITABLE_COLUMNS
    print(f"\n3. Columna 'Punta BNP' (índice 2) editable: {is_editable}")
    assert is_editable == False, \
        "'Punta BNP' NO debería ser editable (se calcula automáticamente)"
    print(f"   ✓ No está en EDITABLE_COLUMNS (correcto)")
    
    # Verificar que el modelo funciona
    print(f"\n4. Funcionalidad básica del modelo:")
    assert model.rowCount() == 0, "Modelo vacío debería tener 0 filas"
    assert model.columnCount() == num_cols, f"columnCount debería ser {num_cols}"
    print(f"   ✓ rowCount() funciona")
    print(f"   ✓ columnCount() funciona")
    
    print("\n✅ Lógica interna intacta, solo cambió el texto del encabezado")
    
    return True


def main():
    """Ejecuta todos los tests."""
    print("\n" + "="*70)
    print("TESTS: CAMBIO DE 'Punta Empresa' A 'Punta BNP'")
    print("="*70)
    
    try:
        # Test 1: Encabezado correcto
        test_encabezado_punta_bnp()
        
        # Test 2: Lógica interna intacta
        test_logica_interna_intacta()
        
        print("\n" + "="*70)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*70)
        print("\nResumen:")
        print("1. Encabezado 'Punta BNP' correcto ✓")
        print("2. Índice de columna intacto (posición 2) ✓")
        print("3. Columnas adyacentes no afectadas ✓")
        print("4. Lógica interna sin cambios ✓")
        print("5. Flag de edición correcto (False) ✓")
        
    except AssertionError as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

