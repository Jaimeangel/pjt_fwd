"""
Ejemplo de integración del módulo Forward.
Muestra cómo conectar Model-View-Controller con servicios y señales.

NOTA: Este es un archivo de ejemplo/documentación. No es código ejecutable.
Todos los métodos están vacíos (pass) según los contratos definidos.
"""

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QObject
import sys

# Imports del módulo Forward
from src.models.forward_model import ForwardDataModel, SimulationsModel
from src.models.forward_table_models import OperationsTableModel, SimulationsTableModel
from src.views.forward_view import ForwardView
from src.controllers.forward_controller import ForwardController
from src.services.forward_pricing_service import ForwardPricingService
from src.services.exposure_service import ExposureService
from src.utils.signals import AppSignals


class ForwardModuleIntegrationExample:
    """
    Ejemplo de cómo integrar todos los componentes del módulo Forward.
    """
    
    def __init__(self):
        """
        Inicializa y conecta todos los componentes del módulo Forward.
        """
        # ================================================================
        # 1. CREAR SEÑALES GLOBALES
        # ================================================================
        self.signals = AppSignals()
        
        # ================================================================
        # 2. CREAR MODELOS DE DATOS
        # ================================================================
        
        # Modelo de datos del 415 y operaciones vigentes
        self.forward_data_model = ForwardDataModel()
        
        # Modelo de simulaciones en memoria
        self.simulations_model = SimulationsModel()
        
        # ================================================================
        # 3. CREAR MODELOS DE TABLA Qt
        # ================================================================
        
        # Modelo Qt para tabla de operaciones vigentes (solo lectura)
        self.operations_table_model = OperationsTableModel()
        
        # Modelo Qt para tabla de simulaciones (editable)
        # Se vincula al modelo de simulaciones
        self.simulations_table_model = SimulationsTableModel(
            simulations_model=self.simulations_model
        )
        
        # ================================================================
        # 4. CREAR SERVICIOS
        # ================================================================
        
        # Servicio de cálculos de pricing Forward
        self.pricing_service = ForwardPricingService()
        
        # Servicio de cálculos de exposición
        self.exposure_service = ExposureService()
        
        # ================================================================
        # 5. CREAR VISTA
        # ================================================================
        
        # Vista del módulo Forward (UI)
        self.forward_view = ForwardView()
        
        # Conectar modelos de tabla a la vista
        self.forward_view.set_operations_table(self.operations_table_model)
        self.forward_view.set_simulations_table(self.simulations_table_model)
        
        # ================================================================
        # 6. CREAR CONTROLADOR
        # ================================================================
        
        # Controlador que coordina todo
        self.forward_controller = ForwardController(
            data_model=self.forward_data_model,
            simulations_model=self.simulations_model,
            view=self.forward_view,
            pricing_service=self.pricing_service,
            exposure_service=self.exposure_service,
            signals=self.signals
        )
        
        # ================================================================
        # 7. CONECTAR SEÑALES GLOBALES (OPCIONAL)
        # ================================================================
        self._connect_global_signals()
    
    def _connect_global_signals(self):
        """
        Conecta señales globales para logging, notificaciones, etc.
        """
        # Ejemplo: Escuchar cuando se carga un 415
        self.signals.forward_415_loaded.connect(self._on_415_loaded)
        
        # Ejemplo: Escuchar cuando cambia la exposición
        self.signals.forward_exposure_updated.connect(self._on_exposure_updated)
        
        # Ejemplo: Escuchar errores
        self.signals.error_occurred.connect(self._on_error)
    
    # ================================================================
    # CALLBACKS DE SEÑALES GLOBALES (EJEMPLO)
    # ================================================================
    
    def _on_415_loaded(self, corte_415, estado_415):
        """
        Callback cuando se carga un archivo 415.
        
        Args:
            corte_415: Fecha de corte del 415
            estado_415: Estado del archivo
        """
        print(f"415 cargado - Corte: {corte_415}, Estado: {estado_415}")
        # Aquí podrías: guardar en log, actualizar otros módulos, etc.
    
    def _on_exposure_updated(self, outstanding, total_con_sim, disponibilidad):
        """
        Callback cuando se actualiza la exposición.
        
        Args:
            outstanding: Exposición actual
            total_con_sim: Exposición total con simulaciones
            disponibilidad: Disponibilidad del límite
        """
        print(f"Exposición actualizada - Outstanding: {outstanding:,.2f}")
        # Aquí podrías: enviar alertas, actualizar dashboard general, etc.
    
    def _on_error(self, title, message):
        """
        Callback para errores globales.
        
        Args:
            title: Título del error
            message: Mensaje del error
        """
        print(f"ERROR: {title} - {message}")
        # Aquí podrías: escribir a log, enviar notificación, etc.
    
    def show(self):
        """
        Muestra la vista del módulo Forward.
        """
        self.forward_view.show()


# ================================================================
# EJEMPLO DE FLUJO DE TRABAJO
# ================================================================

def ejemplo_flujo_trabajo():
    """
    Ejemplo paso a paso del flujo de trabajo típico.
    
    NOTA: Este es código de ejemplo. Los métodos están vacíos (pass).
    """
    
    # Crear instancia de integración
    forward_module = ForwardModuleIntegrationExample()
    
    # ----------------------------------------------------------------
    # PASO 1: CARGAR ARCHIVO 415
    # ----------------------------------------------------------------
    print("\n=== PASO 1: Cargar 415 ===")
    
    # Usuario hace clic en "Cargar 415" y selecciona archivo
    file_path = "/ruta/al/archivo/415.csv"
    
    # La vista emite señal: load_415_clicked(file_path)
    # El controlador recibe: forward_controller.load_415(file_path)
    forward_module.forward_controller.load_415(file_path)
    
    # Resultado esperado:
    # - Modelo actualizado con datos del 415
    # - Vista muestra: patrimonio, TRM, corte, estado
    # - Vista puebla combo de clientes
    # - Señal emitida: forward_415_loaded
    # - Controles habilitados
    
    # ----------------------------------------------------------------
    # PASO 2: SELECCIONAR CLIENTE
    # ----------------------------------------------------------------
    print("\n=== PASO 2: Seleccionar cliente ===")
    
    # Usuario selecciona cliente del dropdown
    nit_cliente = "123456789"
    
    # La vista emite señal: client_selected(nit_cliente)
    # El controlador recibe: forward_controller.select_client(nit)
    forward_module.forward_controller.select_client(nit_cliente)
    
    # Resultado esperado:
    # - Vista muestra límites del cliente
    # - Vista muestra exposición actual (outstanding)
    # - Tabla de operaciones vigentes actualizada
    # - Gráfico de exposición actualizado
    # - Señal emitida: forward_client_changed
    # - Controles de simulación habilitados
    
    # ----------------------------------------------------------------
    # PASO 3: AGREGAR SIMULACIÓN
    # ----------------------------------------------------------------
    print("\n=== PASO 3: Agregar simulación ===")
    
    # Usuario hace clic en "Agregar Fila"
    # La vista emite señal: add_simulation_row_clicked()
    # El controlador recibe: forward_controller.add_simulation()
    forward_module.forward_controller.add_simulation()
    
    # Resultado esperado:
    # - Nueva fila agregada a tabla de simulaciones
    # - Fila tiene valores por defecto (NIT, fecha_sim=hoy, spot=TRM)
    # - Señal emitida: forward_simulations_changed
    
    # ----------------------------------------------------------------
    # PASO 4: EDITAR SIMULACIÓN
    # ----------------------------------------------------------------
    print("\n=== PASO 4: Editar simulación ===")
    
    # Usuario edita celdas en la tabla
    # La tabla emite: setData() en SimulationsTableModel
    # El modelo de tabla actualiza: SimulationsModel.update(row, field, value)
    
    # Ejemplo: Usuario edita nominal_usd
    row = 0
    field = "nominal_usd"
    value = 100000.0
    
    forward_module.simulations_model.update(row, field, value)
    
    # Resultado esperado:
    # - Celda actualizada en memoria
    # - Señal emitida: forward_simulations_changed
    
    # ----------------------------------------------------------------
    # PASO 5: EJECUTAR SIMULACIONES
    # ----------------------------------------------------------------
    print("\n=== PASO 5: Ejecutar simulaciones ===")
    
    # Usuario hace clic en "Ejecutar Simulaciones"
    # La vista emite señal: run_simulations_clicked()
    # El controlador recibe: forward_controller.run_simulations()
    forward_module.forward_controller.run_simulations()
    
    # Resultado esperado:
    # - Para cada simulación completa:
    #   * Calcula tasa_fwd, puntos, fair_value (via ForwardPricingService)
    #   * Calcula exposición (via ExposureService)
    #   * Actualiza campos calculados en SimulationsModel
    # - Vista muestra:
    #   * Tabla actualizada con valores calculados
    #   * Exposición total incluyendo simulaciones
    #   * Gráfico actualizado
    # - Señales emitidas: forward_simulations_changed, forward_exposure_updated
    # - Notificación: "X simulaciones calculadas, Y incompletas"
    
    # ----------------------------------------------------------------
    # PASO 6: GUARDAR SIMULACIONES
    # ----------------------------------------------------------------
    print("\n=== PASO 6: Guardar simulaciones ===")
    
    # Usuario selecciona filas y hace clic en "Guardar Seleccionadas"
    rows_to_save = [0, 1]  # Índices de filas seleccionadas
    
    # La vista emite señal: save_selected_simulations_clicked(rows)
    # El controlador recibe: forward_controller.save_simulations(rows)
    forward_module.forward_controller.save_simulations(rows_to_save)
    
    # Resultado esperado:
    # - Valida que filas estén completas y calculadas
    # - Muestra diálogo de confirmación
    # - Convierte simulaciones a operaciones vigentes
    # - Persiste en base de datos
    # - Actualiza ForwardDataModel (agrega a ops_vigentes)
    # - Elimina de SimulationsModel
    # - Vista muestra:
    #   * Tabla de vigentes actualizada (incluye nuevas)
    #   * Tabla de simulaciones sin las guardadas
    #   * Outstanding actualizado
    # - Señales emitidas: forward_operation_created, forward_simulations_changed
    # - Notificación: "X operaciones guardadas correctamente"


# ================================================================
# EJEMPLO DE MANEJO DE ERRORES
# ================================================================

def ejemplo_manejo_errores():
    """
    Ejemplo de cómo se manejan diferentes errores.
    """
    
    forward_module = ForwardModuleIntegrationExample()
    
    # ----------------------------------------------------------------
    # ERROR 1: Cargar 415 con headers inválidos
    # ----------------------------------------------------------------
    print("\n=== ERROR 1: Headers inválidos ===")
    
    file_path = "/ruta/archivo/invalido.csv"
    forward_module.forward_controller.load_415(file_path)
    
    # Resultado esperado:
    # - forward_data_model.estado_415 = "headers_invalidos"
    # - Vista muestra: estado en rojo "Headers inválidos"
    # - Notificación error: "Error al cargar 415: Headers inválidos. Campos requeridos: [...]"
    # - Controles permanecen deshabilitados
    
    # ----------------------------------------------------------------
    # ERROR 2: Intentar simular sin cliente seleccionado
    # ----------------------------------------------------------------
    print("\n=== ERROR 2: Sin cliente seleccionado ===")
    
    # Usuario intenta agregar simulación sin seleccionar cliente
    # (Este control debería estar deshabilitado, pero por si acaso)
    forward_module.forward_controller.add_simulation()
    
    # Resultado esperado:
    # - Validación falla en controller
    # - Notificación warning: "Debe seleccionar un cliente primero"
    # - No se agrega simulación
    
    # ----------------------------------------------------------------
    # ERROR 3: Guardar simulación incompleta
    # ----------------------------------------------------------------
    print("\n=== ERROR 3: Simulación incompleta ===")
    
    # Usuario intenta guardar simulación sin todos los campos
    rows = [0]
    forward_module.forward_controller.save_simulations(rows)
    
    # Resultado esperado:
    # - Validación falla: simulations_model.validate_simulation() retorna errores
    # - Notificación error: "Simulación incompleta: faltan campos obligatorios [lista]"
    # - No se guarda
    
    # ----------------------------------------------------------------
    # ERROR 4: Guardar excediendo límite
    # ----------------------------------------------------------------
    print("\n=== ERROR 4: Excede límite ===")
    
    # Simulación completa pero excede límite de exposición
    rows = [0]
    forward_module.forward_controller.save_simulations(rows)
    
    # Resultado esperado:
    # - Cálculo de exposición total > límite_max
    # - Notificación error: "No se puede guardar: excede límite de exposición"
    # - No se guarda


# ================================================================
# MAIN (EJEMPLO)
# ================================================================

def main():
    """
    Función principal de ejemplo.
    """
    app = QApplication(sys.argv)
    
    # Crear e inicializar módulo Forward
    forward_module = ForwardModuleIntegrationExample()
    
    # Mostrar vista
    forward_module.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    # Descomentar para ejecutar (una vez implementados los métodos)
    # main()
    
    # Por ahora, solo mostrar ejemplos de flujo
    print("=" * 60)
    print("EJEMPLO DE INTEGRACIÓN DEL MÓDULO FORWARD")
    print("=" * 60)
    
    ejemplo_flujo_trabajo()
    ejemplo_manejo_errores()
    
    print("\n" + "=" * 60)
    print("FIN DE EJEMPLOS")
    print("=" * 60)

