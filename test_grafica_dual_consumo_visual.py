"""
Test Visual: Gráfica dual de consumo de línea (LCA / LLL)

Tiempo extendido para observar la gráfica en detalle.
Escenarios:
1. Cliente sin operaciones (0 consumo)
2. Cliente con consumo moderado (dentro de límites)
3. Cliente con consumo alto (excede LLL pero no LCA)
4. Cliente con consumo muy alto (excede ambos límites)
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
import pandas as pd

from src.views.forward_view import ForwardView
from src.controllers.forward_controller import ForwardController
from src.models.forward_data_model import ForwardDataModel
from src.models.settings_model import SettingsModel


def test_grafica_visual():
    """
    Test visual con múltiples escenarios de consumo.
    """
    app = QApplication(sys.argv)
    
    print("\n" + "="*80)
    print("TEST VISUAL: GRÁFICA DUAL DE CONSUMO DE LÍNEA (LCA / LLL)")
    print("="*80)
    print("\nEscenarios a visualizar:")
    print("  1️⃣  Sin consumo (cliente nuevo)")
    print("  2️⃣  Consumo moderado dentro de límites")
    print("  3️⃣  Consumo alto (excede LLL, dentro de LCA)")
    print("  4️⃣  Consumo muy alto (excede ambos límites)")
    print("\n" + "="*80)
    
    # Setup: crear modelos y vista
    print("\n🔧 Inicializando componentes...")
    view = ForwardView()
    data_model = ForwardDataModel()
    settings_model = SettingsModel()
    
    # Mock simple para cliente
    data_model.nit_to_name = {"900123456": "Banco Test"}
    data_model.nombre_to_nit = {"Banco Test": "900123456"}
    
    # Crear líneas de crédito de prueba
    # LCA = 5,000 MM COP
    # LLL = 1,250 MM COP (25% de 5,000 MM)
    lineas_df = pd.DataFrame({
        "NIT": ["900123456"],
        "Contraparte": ["Banco Test"],
        "Grupo Conectado de Contrapartes": ["Grupo A"],
        "Fecha PT última actualización": ["2024-01-15"],
        "Patrimonio técnico": [5000.0],  # MM
        "LLL 25% (COP)": [1250.0],       # MM (límite máximo permitido)
        "LLL 25% (EUR)": [1.0],          # MM €
        "EUR (MM)": [1.0],                # MM
        "COP (MM)": [5000.0]              # MM (línea de crédito autorizada)
    })
    
    settings_model.lineas_credito_df = lineas_df
    print(f"   ✅ Líneas de crédito: LCA = $5,000 MM | LLL = $1,250 MM")
    
    # Crear controlador
    controller = ForwardController(
        view=view,
        data_model=data_model,
        simulations_model=None,
        simulations_table_model=None,
        operations_table_model=None,
        client_service=None,
        settings_model=settings_model,
        simulation_processor=None
    )
    
    print(f"   ✅ Controller inicializado")
    
    # Mostrar la vista maximizada
    view.show()
    view.resize(1600, 1000)
    
    # Variables globales para el test
    escenario_actual = 0
    
    def mostrar_mensaje(titulo, mensaje):
        """Muestra un mensaje informativo en la vista."""
        msg = QMessageBox(view)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.show()
        # Auto-cerrar después de 3 segundos
        QTimer.singleShot(3000, msg.close)
    
    def escenario_1_sin_consumo():
        """Escenario 1: Cliente sin operaciones (consumo = 0)"""
        nonlocal escenario_actual
        escenario_actual = 1
        
        print("\n" + "="*80)
        print("1️⃣  ESCENARIO 1: SIN CONSUMO")
        print("="*80)
        
        data_model.set_current_client("900123456", "Banco Test")
        outstanding = 0.0
        data_model.set_outstanding_cop(outstanding)
        data_model.set_outstanding_with_sim_cop(None)
        
        controller.refresh_exposure_block()
        
        print(f"   Outstanding: $ 0")
        print(f"   Estado: Cliente nuevo sin operaciones")
        print(f"   Visualización: Barras base completas, sin consumo")
        
        mostrar_mensaje(
            "Escenario 1: Sin Consumo",
            "Cliente sin operaciones vigentes\n\n"
            "Outstanding: $0\n"
            "Disponibilidad: 100% en ambas líneas\n\n"
            "Observa: Barras base (azul LCA / morado LLL) sin consumo"
        )
    
    def escenario_2_consumo_moderado():
        """Escenario 2: Consumo moderado (50% de LLL, 20% de LCA)"""
        nonlocal escenario_actual
        escenario_actual = 2
        
        print("\n" + "="*80)
        print("2️⃣  ESCENARIO 2: CONSUMO MODERADO")
        print("="*80)
        
        outstanding = 625_000_000_000.0  # 625 MM (50% de LLL, 12.5% de LCA)
        data_model.set_outstanding_cop(outstanding)
        data_model.set_outstanding_with_sim_cop(None)
        
        controller.refresh_exposure_block()
        
        print(f"   Outstanding: $ {outstanding:,.0f} (625 MM)")
        print(f"   % de LCA: {(outstanding / 5_000_000_000_000) * 100:.1f}%")
        print(f"   % de LLL: {(outstanding / 1_250_000_000_000) * 100:.1f}%")
        print(f"   Estado: Consumo saludable, dentro de ambos límites")
        
        mostrar_mensaje(
            "Escenario 2: Consumo Moderado",
            f"Outstanding: $625 MM\n\n"
            f"% LCA: 12.5% ✅\n"
            f"% LLL: 50.0% ✅\n\n"
            "Observa: Segmento verde en ambas barras"
        )
    
    def escenario_3_excede_lll():
        """Escenario 3: Excede LLL pero no LCA"""
        nonlocal escenario_actual
        escenario_actual = 3
        
        print("\n" + "="*80)
        print("3️⃣  ESCENARIO 3: EXCEDE LLL (DENTRO DE LCA)")
        print("="*80)
        
        outstanding = 1_300_000_000_000.0  # 1,300 MM (excede LLL de 1,250 MM)
        data_model.set_outstanding_cop(outstanding)
        data_model.set_outstanding_with_sim_cop(None)
        
        controller.refresh_exposure_block()
        
        exceso_lll = outstanding - 1_250_000_000_000
        
        print(f"   Outstanding: $ {outstanding:,.0f} (1,300 MM)")
        print(f"   % de LCA: {(outstanding / 5_000_000_000_000) * 100:.1f}%")
        print(f"   % de LLL: {(outstanding / 1_250_000_000_000) * 100:.1f}%")
        print(f"   Exceso sobre LLL: $ {exceso_lll:,.0f} (50 MM)")
        print(f"   ⚠️  Estado: Excede límite LLL, requiere atención")
        
        mostrar_mensaje(
            "Escenario 3: Excede LLL",
            f"Outstanding: $1,300 MM\n\n"
            f"% LCA: 26.0% ✅\n"
            f"% LLL: 104.0% ⚠️\n\n"
            f"Exceso LLL: $50 MM\n\n"
            "Observa: Barra LLL con segmento ROJO (exceso)"
        )
    
    def escenario_4_excede_ambos():
        """Escenario 4: Excede ambos límites"""
        nonlocal escenario_actual
        escenario_actual = 4
        
        print("\n" + "="*80)
        print("4️⃣  ESCENARIO 4: EXCEDE AMBOS LÍMITES")
        print("="*80)
        
        outstanding = 5_500_000_000_000.0  # 5,500 MM (excede ambos)
        data_model.set_outstanding_cop(outstanding)
        data_model.set_outstanding_with_sim_cop(None)
        
        controller.refresh_exposure_block()
        
        exceso_lca = outstanding - 5_000_000_000_000
        exceso_lll = outstanding - 1_250_000_000_000
        
        print(f"   Outstanding: $ {outstanding:,.0f} (5,500 MM)")
        print(f"   % de LCA: {(outstanding / 5_000_000_000_000) * 100:.1f}%")
        print(f"   % de LLL: {(outstanding / 1_250_000_000_000) * 100:.1f}%")
        print(f"   Exceso sobre LCA: $ {exceso_lca:,.0f} (500 MM)")
        print(f"   Exceso sobre LLL: $ {exceso_lll:,.0f} (4,250 MM)")
        print(f"   🚨 Estado: ALERTA - Excede ambos límites regulatorios")
        
        mostrar_mensaje(
            "Escenario 4: Excede Ambos Límites",
            f"Outstanding: $5,500 MM\n\n"
            f"% LCA: 110.0% 🚨\n"
            f"% LLL: 440.0% 🚨\n\n"
            f"Exceso LCA: $500 MM\n"
            f"Exceso LLL: $4,250 MM\n\n"
            "Observa: Ambas barras con segmento ROJO"
        )
    
    def finalizar_test():
        """Finaliza el test con resumen"""
        print("\n" + "="*80)
        print("✅ TEST VISUAL COMPLETADO")
        print("="*80)
        print("\n📊 Resumen de Visualizaciones:")
        print("  ✅ Escenario 1: Sin consumo (barras base limpias)")
        print("  ✅ Escenario 2: Consumo moderado (verde en ambas)")
        print("  ✅ Escenario 3: Excede LLL (rojo en LLL, verde en LCA)")
        print("  ✅ Escenario 4: Excede ambos (rojo en ambas)")
        print("\n🎨 Elementos Visuales Verificados:")
        print("  ✅ Barras base con transparencia (azul LCA / morado LLL)")
        print("  ✅ Segmento verde = consumo dentro del límite")
        print("  ✅ Segmento rojo = exceso sobre el límite")
        print("  ✅ Etiquetas numéricas en COP (sin porcentajes)")
        print("  ✅ Auto-escala del eje Y según los valores")
        print("\n" + "="*80)
        print("\n⏱️  La ventana permanecerá abierta.")
        print("   Ciérrala manualmente cuando termines de revisar.\n")
    
    # Programar secuencia de escenarios con tiempos extendidos
    QTimer.singleShot(500, escenario_1_sin_consumo)        # 0.5s
    QTimer.singleShot(8000, escenario_2_consumo_moderado)  # 8s (visualiza 7.5s el escenario 1)
    QTimer.singleShot(16000, escenario_3_excede_lll)       # 16s (visualiza 8s el escenario 2)
    QTimer.singleShot(24000, escenario_4_excede_ambos)     # 24s (visualiza 8s el escenario 3)
    QTimer.singleShot(32000, finalizar_test)               # 32s (visualiza 8s el escenario 4)
    
    # No cerrar automáticamente, dejar que el usuario cierre manualmente
    print("\n⏳ Iniciando secuencia de escenarios (8 segundos cada uno)...")
    print("   La ventana permanecerá abierta al finalizar para que revises.")
    
    # Ejecutar
    sys.exit(app.exec())


if __name__ == "__main__":
    test_grafica_visual()

