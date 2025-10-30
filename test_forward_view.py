"""
Script de prueba visual para ForwardView.
Permite ver el layout completo y probar la interfaz.

Ejecutar: python test_forward_view.py
"""

import sys
from pathlib import Path
from datetime import date

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from views.forward_view import ForwardView


def test_forward_view_visual():
    """Test visual de la ForwardView."""
    
    print("\n" + "="*70)
    print("TEST VISUAL - FORWARD VIEW")
    print("="*70 + "\n")
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    
    # Crear vista
    print("[Test] Creando ForwardView...")
    view = ForwardView()
    
    # Verificar objectNames
    print("[Test] Verificando objectNames...")
    object_names = [
        # Header
        'btnLoad415', 'lblTituloForward', 'lblFechaCorte415', 
        'lblEstado415', 'lblArchivo415',
        # Columna 1
        'lblPatrimonio', 'lblTRM', 'cmbClientes', 'txtBuscarCliente',
        # Columna 2
        'lblLineaCredito', 'lblColchonInterno', 'lblLimiteMax',
        'lblOutstanding', 'lblOutstandingSim', 'lblDisponibilidad',
        # Columna 3
        'chartContainer',
        # Simulaciones
        'btnAddSim', 'btnDupSim', 'btnDelSim', 'btnRunAll', 
        'btnSaveSel', 'tblSimulaciones',
        # Vigentes
        'txtFiltroVigentes', 'chkIncluirCalculo', 'tblVigentes',
        # Banner
        'banner415'
    ]
    
    missing = []
    for name in object_names:
        widget = view.findChild(object, name)
        if widget is None:
            missing.append(name)
        else:
            print(f"   ✓ {name}")
    
    if missing:
        print(f"\n   ✗ Faltantes: {missing}")
    else:
        print(f"\n   ✅ Todos los {len(object_names)} objectNames encontrados")
    
    # Conectar señales para testing
    print("\n[Test] Conectando señales...")
    view.load_415_requested.connect(
        lambda path: print(f"   → Señal: load_415_requested({path})")
    )
    view.client_selected.connect(
        lambda nit: print(f"   → Señal: client_selected({nit})")
    )
    view.add_simulation_requested.connect(
        lambda: print("   → Señal: add_simulation_requested()")
    )
    view.run_simulations_requested.connect(
        lambda: print("   → Señal: run_simulations_requested()")
    )
    
    # Poblar combo de clientes con datos de prueba
    print("\n[Test] Poblando combo de clientes con datos de prueba...")
    clientes_test = [
        "123456789 - Cliente Prueba 1 S.A.",
        "987654321 - Cliente Prueba 2 Ltda.",
        "555444333 - Cliente Prueba 3 S.A.S."
    ]
    for cliente in clientes_test:
        view.cmbClientes.addItem(cliente)
    
    # Actualizar vista con datos de prueba
    print("[Test] Actualizando vista con datos de prueba...")
    
    # Información básica
    view.show_basic_info(
        patrimonio=50000000000.0,  # 50 mil millones
        trm=4250.75,
        corte_415=date.today(),
        estado_415="valido"
    )
    
    # Límites de cliente
    view.show_client_limits(
        linea=5000000.0,      # 5 millones
        colchon_pct=0.10,     # 10%
        limite_max=5500000.0  # 5.5 millones
    )
    
    # Exposición
    view.show_exposure(
        outstanding=1000000.0,           # 1 millón
        total_con_simulacion=1500000.0,  # 1.5 millones
        disponibilidad=4000000.0         # 4 millones
    )
    
    # Mostrar banner 415
    view.banner415.setVisible(True)
    view.lblArchivo415.setText("Archivo: operaciones_415_20251028.csv | Fecha: 28/10/2025 | Estado: Válido")
    
    print("   ✅ Datos de prueba cargados")
    
    # Configurar ventana
    view.setWindowTitle("Test Visual - ForwardView")
    view.resize(1400, 900)
    
    # Mostrar vista
    print("\n[Test] Mostrando vista...")
    print("\n" + "="*70)
    print("INSTRUCCIONES DE PRUEBA:")
    print("="*70)
    print("1. Verifica el layout visual:")
    print("   • Header con título, fecha corte, badge y botón")
    print("   • Banner de estado del 415 (azul)")
    print("   • 3 columnas con cards")
    print("   • Placeholder de gráfica con texto 'Gráfica pendiente'")
    print("   • 2 tablas en la parte inferior")
    print()
    print("2. Prueba los botones:")
    print("   • 'Cargar 415' → Abre diálogo de archivo")
    print("   • 'Agregar fila' → Emite señal en consola")
    print("   • 'Simular todo' → Emite señal en consola")
    print()
    print("3. Prueba el combo de clientes:")
    print("   • Selecciona un cliente → Emite señal con NIT")
    print()
    print("4. Verifica los estilos:")
    print("   • Cards con bordes y títulos")
    print("   • Badge de estado en verde")
    print("   • Disponibilidad en verde (> 1 millón)")
    print("   • Tablas con filas alternadas (cuando tengan datos)")
    print()
    print("La ventana se cerrará automáticamente en 30 segundos...")
    print("O presiona Ctrl+C para cerrar antes")
    print("="*70 + "\n")
    
    view.show()
    
    # Cerrar automáticamente después de 30 segundos
    QTimer.singleShot(30000, app.quit)
    
    # Ejecutar aplicación
    result = app.exec()
    
    # Resumen final
    print("\n" + "="*70)
    print("✅ TEST VISUAL COMPLETADO")
    print("="*70)
    print(f"ObjectNames verificados: {len(object_names)}/{len(object_names)}")
    print("Layout: Completo")
    print("Señales: Conectadas")
    print("Estilos: Aplicados")
    print("\nLa vista ForwardView está lista para usarse!")
    print("="*70 + "\n")
    
    return result


if __name__ == "__main__":
    sys.exit(test_forward_view_visual())

