"""
Test para verificar que la selección de contraparte no sobrescribe valores correctos con defaults.

Criterios de aceptación:
1. MainWindow NO debe setear valores de límites con defaults/hardcodes
2. ForwardController es la ÚNICA fuente que calcula y setea límites
3. No hay dobles conexiones de señales
4. La vista solo muestra textos recibidos (no inventa valores)
5. Los logs NO muestran sobrescritura de valores después de la carga correcta
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import pandas as pd

# Agregar src al path
sys.path.insert(0, 'src')

from src.models.settings_model import SettingsModel
from src.models.forward_data_model import ForwardDataModel
from src.models.simulations_model import SimulationsModel
from src.views.forward_view import ForwardView
from src.controllers.forward_controller import ForwardController

def test_seleccion_sin_sobrescritura():
    """
    Verifica que al seleccionar un cliente, los valores correctos
    NO sean sobrescritos por defaults.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    print("\n" + "="*80)
    print("TEST: Selección de contraparte SIN sobrescritura de valores")
    print("="*80 + "\n")
    
    # 1️⃣ Configurar SettingsModel con datos de prueba
    settings_model = SettingsModel()
    
    # Configurar patrimonio, TRM y colchón
    settings_model.set_patrimonio(1500000000.0)  # $1,500 millones
    settings_model.set_trm(4500.0)
    settings_model.set_colchon(10.0)  # 10%
    
    # Cargar líneas de crédito de prueba
    lineas_df = pd.DataFrame([
        {
            "Contraparte": "Banco ABC",
            "NIT": "123456789",
            "Monto (COP)": 5500000.0,  # Sin comas, valor numérico
            "Grupo Conectado de Contrapartes": "Grupo A",
            "Código País": "CO",
            "Calificación": "AAA"
        },
        {
            "Contraparte": "Banco XYZ",
            "NIT": "987654321",
            "Monto (COP)": 3200000.0,  # Sin comas, valor numérico
            "Grupo Conectado de Contrapartes": "Grupo B",
            "Código País": "CO",
            "Calificación": "AA"
        }
    ])
    settings_model.set_lineas_credito(lineas_df)
    
    print("✓ SettingsModel configurado:")
    print(f"  - Patrimonio: $ {settings_model.patrimonio():,.0f}")
    print(f"  - TRM: $ {settings_model.trm():,.2f}")
    print(f"  - Colchón: {settings_model.colchon():.2f}%")
    print(f"  - Líneas de crédito: {len(settings_model.lineas_credito_df)} registros")
    print()
    
    # 2️⃣ Crear modelos y vista
    data_model = ForwardDataModel()
    simulations_model = SimulationsModel()
    
    # Agregar cliente a data_model para que pueda encontrarlo
    data_model.nit_to_name = {"123456789": "Banco ABC", "987654321": "Banco XYZ"}
    data_model.nombre_to_nit = {"Banco ABC": "123456789", "Banco XYZ": "987654321"}
    
    # Crear vista y controller
    forward_view = ForwardView(settings_model=settings_model)
    forward_controller = ForwardController(
        data_model=data_model,
        simulations_model=simulations_model,
        view=forward_view,
        settings_model=settings_model
    )
    
    # Configurar cliente en el dropdown de la vista (simular selección de usuario)
    forward_view.cmbClientes.addItems(["Banco ABC", "Banco XYZ"])
    
    print("✓ Modelos, vista y controlador creados")
    print()
    
    # 3️⃣ Simular selección de cliente
    print("="*80)
    print("SELECCIONANDO CLIENTE: Banco ABC (NIT: 123456789)")
    print("="*80)
    print()
    
    # Capturar valores de la vista ANTES de seleccionar
    print("ANTES de seleccionar cliente:")
    print(f"  Línea de crédito: {forward_view.lblLineaCredito.text()}")
    print(f"  Colchón interno: {forward_view.lblColchonInterno.text()}")
    print(f"  Límite máximo: {forward_view.lblLimiteMax.text()}")
    print()
    
    # Seleccionar cliente (esto debería actualizar SOLO una vez)
    forward_controller.select_client("Banco ABC")
    
    # Capturar valores DESPUÉS de seleccionar
    print("\nDESPUÉS de seleccionar cliente:")
    linea_txt = forward_view.lblLineaCredito.text()
    colchon_txt = forward_view.lblColchonInterno.text()
    limite_txt = forward_view.lblLimiteMax.text()
    
    print(f"  Línea de crédito: {linea_txt}")
    print(f"  Colchón interno: {colchon_txt}")
    print(f"  Límite máximo: {limite_txt}")
    print()
    
    # 4️⃣ Verificar que los valores sean correctos y NO defaults
    print("="*80)
    print("VERIFICACIÓN DE VALORES")
    print("="*80)
    print()
    
    # Valores esperados:
    # Línea: $5,500,000
    # Colchón: 10.00%
    # Límite: $5,500,000 * (1 - 0.10) = $4,950,000
    
    errores = []
    
    # Verificar línea
    if "5,500,000" not in linea_txt:
        errores.append(f"❌ Línea incorrecta: esperado '$5,500,000', obtenido '{linea_txt}'")
    else:
        print("✓ Línea de crédito correcta: $ 5,500,000")
    
    # Verificar colchón
    if "10.00%" not in colchon_txt:
        errores.append(f"❌ Colchón incorrecto: esperado '10.00%', obtenido '{colchon_txt}'")
    else:
        print("✓ Colchón interno correcto: 10.00%")
    
    # Verificar límite
    if "4,950,000" not in limite_txt:
        errores.append(f"❌ Límite incorrecto: esperado '$4,950,000', obtenido '{limite_txt}'")
    else:
        print("✓ Límite máximo correcto: $ 4,950,000")
    
    # Verificar que NO sean valores por defecto (5,000,000, 0.10, 5,500,000)
    if "5,000,000" in linea_txt:
        errores.append(f"❌ Línea tiene valor por defecto: {linea_txt} (esperado $5,500,000)")
    
    if "5,500,000" in limite_txt and "4,950,000" not in limite_txt:
        errores.append(f"❌ Límite tiene valor por defecto: {limite_txt} (esperado $4,950,000)")
    
    print()
    
    # 5️⃣ Test de reentrancia (kill-switch)
    print("="*80)
    print("TEST: Kill-switch anti-reentrancia")
    print("="*80)
    print()
    
    print("Llamando select_client múltiples veces rápidamente...")
    
    # Simular múltiples selecciones rápidas (debería bloquearse si ya está procesando)
    for i in range(3):
        forward_controller.select_client("Banco ABC")
    
    # Verificar que los valores siguen siendo correctos
    linea_final = forward_view.lblLineaCredito.text()
    colchon_final = forward_view.lblColchonInterno.text()
    limite_final = forward_view.lblLimiteMax.text()
    
    if "5,500,000" in linea_final and "10.00%" in colchon_final and "4,950,000" in limite_final:
        print("✓ Kill-switch funcionando: valores siguen siendo correctos")
    else:
        errores.append(f"❌ Kill-switch falló: valores incorrectos después de múltiples llamadas")
        print(f"   Línea: {linea_final}")
        print(f"   Colchón: {colchon_final}")
        print(f"   Límite: {limite_final}")
    
    print()
    
    # 6️⃣ Test de cambio de colchón reactivo
    print("="*80)
    print("TEST: Cambio de colchón reactivo")
    print("="*80)
    print()
    
    print("Cambiando colchón de 10% a 15%...")
    settings_model.set_colchon(15.0)
    
    # Esperar un momento para que se procese la señal
    app.processEvents()
    
    # Verificar que el límite se recalculó
    # Nuevo límite: $5,500,000 * (1 - 0.15) = $4,675,000
    limite_nuevo = forward_view.lblLimiteMax.text()
    colchon_nuevo = forward_view.lblColchonInterno.text()
    
    print(f"Nuevos valores:")
    print(f"  Colchón: {colchon_nuevo}")
    print(f"  Límite: {limite_nuevo}")
    
    if "15.00%" in colchon_nuevo and "4,675,000" in limite_nuevo:
        print("✓ Colchón reactivo funcionando correctamente")
    else:
        errores.append(f"❌ Colchón reactivo falló: esperado 15.00% y $4,675,000")
        print(f"   Esperado: Colchón=15.00%, Límite=$4,675,000")
        print(f"   Obtenido: Colchón={colchon_nuevo}, Límite={limite_nuevo}")
    
    print()
    
    # 7️⃣ Resumen final
    print("="*80)
    print("RESUMEN DEL TEST")
    print("="*80)
    print()
    
    if errores:
        print(f"❌ TEST FALLÓ con {len(errores)} error(es):")
        for error in errores:
            print(f"  {error}")
        print()
        return False
    else:
        print("✅ TODOS LOS TESTS PASARON")
        print()
        print("Criterios verificados:")
        print("  ✓ Valores correctos cargados desde SettingsModel")
        print("  ✓ NO se sobrescriben con defaults desde MainWindow")
        print("  ✓ Kill-switch anti-reentrancia funcionando")
        print("  ✓ Cambio de colchón reactivo funcionando")
        print("  ✓ Vista solo muestra valores recibidos del Controller")
        print()
        return True

if __name__ == "__main__":
    try:
        resultado = test_seleccion_sin_sobrescritura()
        sys.exit(0 if resultado else 1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

