"""
Vista para el módulo de operaciones Forward.
Layout visual completo con cards, tablas y toolbar.
"""

from typing import Optional, List, Dict, Any
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QComboBox, QTableView,
    QGroupBox, QFrame, QSplitter, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class ForwardView(QWidget):
    """
    Vista del módulo Forward con layout visual completo.
    
    Responsabilidades:
    - Mostrar formulario de captura de datos
    - Visualizar cálculos y resultados en cards
    - Mostrar tablas de operaciones vigentes y simulaciones
    - Emitir señales de acciones del usuario
    """
    
    # Señales que emite la vista (events que van al controller)
    load_415_requested = Signal(str)           # file_path
    load_ibr_requested = Signal(str)           # file_path
    client_selected = Signal(str)              # nit
    add_simulation_requested = Signal()
    delete_simulations_requested = Signal(list)       # rows
    simulate_selected_requested = Signal()            # simular fila seleccionada
    save_simulations_requested = Signal(list)         # rows
    
    def __init__(self, parent=None, settings_model=None):
        """
        Inicializa la vista Forward.
        
        Args:
            parent: Widget padre
            settings_model: Modelo compartido de configuración (para Patrimonio y TRM)
        """
        super().__init__(parent)
        
        # Referencia al modelo de configuración compartido
        self._settings_model = settings_model
        
        # Referencias a widgets principales (se crean en _setup_ui)
        self.btnLoad415 = None
        self.btnLoadIBR = None
        self.lblTituloForward = None
        self.lblFechaCorte415 = None
        self.lblEstado415 = None
        self.lblArchivo415 = None
        
        # Referencias para banner IBR
        self.lblArchivoIBR = None
        self.lblTamanoIBR = None
        self.lblFechaIBR = None
        self.lblEstadoIBR = None
        
        self.lblPatrimonio = None
        self.lblTRM = None
        self.cmbClientes = None
        
        self.lblLineaCredito = None
        self.lblColchonInterno = None
        self.lblLimiteMax = None
        self.lblOutstanding = None
        self.lblOutstandingSim = None
        self.lblDisponibilidad = None
        
        self.chartContainer = None
        
        self.btnAddSim = None
        self.btnDelSim = None
        self.btnRun = None
        self.btnSaveSel = None
        self.tblSimulaciones = None
        
        self.tblVigentes = None
        
        self.banner415 = None
        self.bannerIBR = None
        
        self._setup_ui()
        self._connect_settings_model()
    
    def _connect_settings_model(self):
        """
        Conecta las señales del SettingsModel para actualización en tiempo real.
        
        Nota: Patrimonio, TRM y Colchón fueron eliminados del modelo global.
        Ahora estos valores son por contraparte y vienen del CSV de líneas de crédito.
        """
        if self._settings_model:
            # Suscribirse a cambios en las líneas de crédito (para futuras actualizaciones)
            # self._settings_model.lineasCreditoChanged.connect(...)
            
            print("[ForwardView] Conectado a SettingsModel")
        else:
            print("[ForwardView] SettingsModel no proporcionado")
    
    def _setup_ui(self):
        """Configura la interfaz de usuario completa."""
        # Layout principal vertical
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 1. Header
        main_layout.addWidget(self._create_header())
        
        # 2. Banner estado 415
        self.banner415 = self._create_banner_415()
        main_layout.addWidget(self.banner415)
        
        # 2b. Banner estado IBR
        self.bannerIBR = self._create_banner_ibr()
        main_layout.addWidget(self.bannerIBR)
        
        # 3. Panel superior con 3 columnas
        main_layout.addWidget(self._create_upper_panel())
        
        # 4. Panel inferior con tablas
        main_layout.addWidget(self._create_lower_panel())
    
    def _create_header(self) -> QWidget:
        """Crea el header con título y botón de carga."""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        self.lblTituloForward = QLabel("Forward")
        self.lblTituloForward.setObjectName("lblTituloForward")
        font_title = QFont()
        font_title.setPointSize(16)
        font_title.setBold(True)
        self.lblTituloForward.setFont(font_title)
        header_layout.addWidget(self.lblTituloForward)
        
        header_layout.addSpacing(30)
        
        # Fecha corte 415
        self.lblFechaCorte415 = QLabel("Fecha corte 415: --")
        self.lblFechaCorte415.setObjectName("lblFechaCorte415")
        header_layout.addWidget(self.lblFechaCorte415)
        
        header_layout.addSpacing(20)
        
        # Estado (badge)
        self.lblEstado415 = QLabel("No cargado")
        self.lblEstado415.setObjectName("lblEstado415")
        self.lblEstado415.setStyleSheet(
            "QLabel { background-color: #999; color: white; "
            "padding: 4px 12px; border-radius: 3px; }"
        )
        header_layout.addWidget(self.lblEstado415)
        
        header_layout.addStretch()
        
        # Botón Cargar IBR
        self.btnLoadIBR = QPushButton("Cargar IBR")
        self.btnLoadIBR.setObjectName("btnLoadIBR")
        self.btnLoadIBR.setMinimumWidth(120)
        self.btnLoadIBR.clicked.connect(self._on_load_ibr_button_clicked)
        header_layout.addWidget(self.btnLoadIBR)
        
        # Botón Cargar 415
        self.btnLoad415 = QPushButton("Cargar 415")
        self.btnLoad415.setObjectName("btnLoad415")
        self.btnLoad415.setMinimumWidth(120)
        self.btnLoad415.clicked.connect(self._on_load_415_button_clicked)
        header_layout.addWidget(self.btnLoad415)
        
        return header_widget
    
    def _create_banner_415(self) -> QFrame:
        """Crea el banner de estado del archivo 415."""
        banner = QFrame()
        banner.setObjectName("banner415")
        banner.setFrameShape(QFrame.StyledPanel)
        banner.setStyleSheet(
            "QFrame#banner415 { background-color: #f0f4f8; border: 1px solid #d1d9e0; "
            "border-radius: 4px; padding: 8px; }"
        )
        
        banner_layout = QHBoxLayout(banner)
        
        # Label de archivo
        self.lblArchivo415 = QLabel("Archivo: Ninguno cargado")
        self.lblArchivo415.setObjectName("lblArchivo415")
        banner_layout.addWidget(self.lblArchivo415)
        
        banner_layout.addStretch()
        
        # Inicialmente oculto
        banner.setVisible(False)
        
        return banner
    
    def _create_banner_ibr(self) -> QFrame:
        """Crea el banner de estado del archivo IBR."""
        banner = QFrame()
        banner.setObjectName("bannerIBR")
        banner.setFrameShape(QFrame.StyledPanel)
        banner.setStyleSheet(
            "QFrame#bannerIBR { background-color: #f0f4f8; border: 1px solid #d1d9e0; "
            "border-radius: 4px; padding: 8px; }"
        )
        
        banner_layout = QHBoxLayout(banner)
        banner_layout.setSpacing(15)
        
        # Label de archivo
        self.lblArchivoIBR = QLabel("Archivo: —")
        self.lblArchivoIBR.setObjectName("lblArchivoIBR")
        banner_layout.addWidget(self.lblArchivoIBR)
        
        # Label de tamaño
        self.lblTamanoIBR = QLabel("Tamaño: —")
        self.lblTamanoIBR.setObjectName("lblTamanoIBR")
        banner_layout.addWidget(self.lblTamanoIBR)
        
        # Label de fecha
        self.lblFechaIBR = QLabel("Fecha: —")
        self.lblFechaIBR.setObjectName("lblFechaIBR")
        banner_layout.addWidget(self.lblFechaIBR)
        
        banner_layout.addStretch()
        
        # Badge de estado
        self.lblEstadoIBR = QLabel("—")
        self.lblEstadoIBR.setObjectName("lblEstadoIBR")
        self.lblEstadoIBR.setStyleSheet(
            "QLabel { background-color: #999; color: white; "
            "padding: 4px 12px; border-radius: 3px; }"
        )
        banner_layout.addWidget(self.lblEstadoIBR)
        
        # Inicialmente oculto
        banner.setVisible(False)
        
        return banner
    
    def _create_upper_panel(self) -> QWidget:
        """Crea el panel superior con 3 columnas de cards."""
        panel_widget = QWidget()
        panel_layout = QHBoxLayout(panel_widget)
        panel_layout.setSpacing(15)
        panel_layout.setContentsMargins(0, 0, 0, 6)
        
        # Columna 1: Contexto
        panel_layout.addWidget(self._create_column_1(), stretch=1)
        
        # Columna 2: Detalle cliente
        panel_layout.addWidget(self._create_column_2(), stretch=1)
        
        # Columna 3: Visualización
        panel_layout.addWidget(self._create_column_3(), stretch=1)
        
        return panel_widget
    
    def _create_column_1(self) -> QWidget:
        """Columna 1: Información básica y Cliente."""
        column = QWidget()
        column_layout = QVBoxLayout(column)
        column_layout.setSpacing(10)
        column_layout.setContentsMargins(0, 0, 0, 0)
        
        # Card A: Información básica
        card_a = self._create_card("Información básica")
        card_a_layout = QGridLayout()
        card_a_layout.setSpacing(8)
        card_a_layout.setContentsMargins(10, 10, 10, 10)
        
        font_value = QFont()
        font_value.setBold(True)
        
        # Patrimonio técnico (columna 0)
        lbl_pat_title = QLabel("Patrimonio técnico vigente")
        lbl_pat_title.setAlignment(Qt.AlignCenter)
        self.lblPatrimonio = QLabel("$ 0.00")
        self.lblPatrimonio.setObjectName("lblPatrimonio")
        self.lblPatrimonio.setFont(font_value)
        self.lblPatrimonio.setAlignment(Qt.AlignCenter)
        card_a_layout.addWidget(lbl_pat_title, 0, 0)
        card_a_layout.addWidget(self.lblPatrimonio, 1, 0)
        
        # TRM vigente (columna 1)
        lbl_trm_title = QLabel("TRM vigente")
        lbl_trm_title.setAlignment(Qt.AlignCenter)
        self.lblTRM = QLabel("$ 0.00")
        self.lblTRM.setObjectName("lblTRM")
        self.lblTRM.setFont(font_value)
        self.lblTRM.setAlignment(Qt.AlignCenter)
        card_a_layout.addWidget(lbl_trm_title, 0, 1)
        card_a_layout.addWidget(self.lblTRM, 1, 1)
        
        card_a.setLayout(card_a_layout)
        card_a.setMaximumHeight(120)
        column_layout.addWidget(card_a)
        
        # Card B: Cliente
        card_b = self._create_card("Cliente")
        card_b_layout = QVBoxLayout()
        card_b_layout.setSpacing(8)
        card_b_layout.setContentsMargins(10, 10, 10, 10)
        
        # ComboBox de clientes (sin campo de búsqueda)
        lbl_cliente = QLabel("Seleccionar contraparte:")
        self.cmbClientes = QComboBox()
        self.cmbClientes.setObjectName("cmbClientes")
        # Iniciar vacío, sin selección
        self.cmbClientes.setCurrentIndex(-1)
        self.cmbClientes.currentTextChanged.connect(self._on_client_combo_changed)
        card_b_layout.addWidget(lbl_cliente)
        card_b_layout.addWidget(self.cmbClientes)
        
        card_b.setLayout(card_b_layout)
        column_layout.addWidget(card_b)
        
        column_layout.addStretch()
        
        return column
    
    def _create_column_2(self) -> QWidget:
        """Columna 2: Parámetros de crédito y Exposición."""
        column = QWidget()
        column_layout = QVBoxLayout(column)
        column_layout.setSpacing(10)
        column_layout.setContentsMargins(0, 0, 0, 0)
        
        # Card C: Parámetros de crédito
        card_c = self._create_card("Parámetros de crédito")
        card_c_layout = QGridLayout()
        card_c_layout.setSpacing(8)
        card_c_layout.setContentsMargins(10, 10, 10, 10)
        
        font_value = QFont()
        font_value.setBold(True)
        
        # Línea de crédito (columna 0)
        lbl_linea_title = QLabel("Línea de crédito")
        lbl_linea_title.setAlignment(Qt.AlignCenter)
        self.lblLineaCredito = QLabel("—")  # Sin valor por defecto
        self.lblLineaCredito.setObjectName("lblLineaCredito")
        self.lblLineaCredito.setFont(font_value)
        self.lblLineaCredito.setAlignment(Qt.AlignCenter)
        card_c_layout.addWidget(lbl_linea_title, 0, 0)
        card_c_layout.addWidget(self.lblLineaCredito, 1, 0)
        
        # Colchón interno (columna 1)
        lbl_colchon_title = QLabel("Colchón interno")
        lbl_colchon_title.setAlignment(Qt.AlignCenter)
        self.lblColchonInterno = QLabel("—")  # Sin valor por defecto
        self.lblColchonInterno.setObjectName("lblColchonInterno")
        self.lblColchonInterno.setFont(font_value)
        self.lblColchonInterno.setAlignment(Qt.AlignCenter)
        card_c_layout.addWidget(lbl_colchon_title, 0, 1)
        card_c_layout.addWidget(self.lblColchonInterno, 1, 1)
        
        # Límite máximo (columna 2)
        lbl_limite_title = QLabel("Límite máximo permitido")
        lbl_limite_title.setAlignment(Qt.AlignCenter)
        self.lblLimiteMax = QLabel("—")  # Sin valor por defecto
        self.lblLimiteMax.setObjectName("lblLimiteMax")
        self.lblLimiteMax.setFont(font_value)
        self.lblLimiteMax.setAlignment(Qt.AlignCenter)
        card_c_layout.addWidget(lbl_limite_title, 0, 2)
        card_c_layout.addWidget(self.lblLimiteMax, 1, 2)
        
        card_c.setLayout(card_c_layout)
        card_c.setMaximumHeight(120)
        column_layout.addWidget(card_c)
        
        # Card D: Exposición
        card_d = self._create_card("Exposición")
        card_d_layout = QGridLayout()
        card_d_layout.setSpacing(8)
        card_d_layout.setContentsMargins(10, 10, 10, 10)
        
        # Outstanding (columna 0)
        lbl_out_title = QLabel("Outstanding")
        lbl_out_title.setAlignment(Qt.AlignCenter)
        self.lblOutstanding = QLabel("—")  # Iniciar sin valor
        self.lblOutstanding.setObjectName("lblOutstanding")
        self.lblOutstanding.setFont(font_value)
        self.lblOutstanding.setAlignment(Qt.AlignCenter)
        card_d_layout.addWidget(lbl_out_title, 0, 0)
        card_d_layout.addWidget(self.lblOutstanding, 1, 0)
        
        # Outstanding + simulación (columna 1)
        lbl_outsim_title = QLabel("Outst. + simulación")
        lbl_outsim_title.setAlignment(Qt.AlignCenter)
        self.lblOutstandingSim = QLabel("—")  # Iniciar sin valor
        self.lblOutstandingSim.setObjectName("lblOutstandingSim")
        self.lblOutstandingSim.setFont(font_value)
        self.lblOutstandingSim.setAlignment(Qt.AlignCenter)
        card_d_layout.addWidget(lbl_outsim_title, 0, 1)
        card_d_layout.addWidget(self.lblOutstandingSim, 1, 1)
        
        # Disponibilidad (columna 2)
        lbl_disp_title = QLabel("Disponibilidad de línea")
        lbl_disp_title.setAlignment(Qt.AlignCenter)
        self.lblDisponibilidad = QLabel("—")  # Iniciar sin valor
        self.lblDisponibilidad.setObjectName("lblDisponibilidad")
        self.lblDisponibilidad.setFont(font_value)
        self.lblDisponibilidad.setAlignment(Qt.AlignCenter)
        self.lblDisponibilidad.setStyleSheet("QLabel { color: #2e7d32; font-weight: bold; }")
        card_d_layout.addWidget(lbl_disp_title, 0, 2)
        card_d_layout.addWidget(self.lblDisponibilidad, 1, 2)
        
        card_d.setLayout(card_d_layout)
        card_d.setMaximumHeight(120)
        column_layout.addWidget(card_d)
        
        column_layout.addStretch()
        
        return column
    
    def _create_column_3(self) -> QWidget:
        """Columna 3: Visualización (gráfica)."""
        column = QWidget()
        column_layout = QVBoxLayout(column)
        column_layout.setSpacing(10)
        column_layout.setContentsMargins(0, 0, 0, 0)
        
        # Card E: Consumo de línea
        card_e = self._create_card("Consumo de línea")
        card_e_layout = QVBoxLayout()
        
        # Placeholder de gráfica
        self.chartContainer = QWidget()
        self.chartContainer.setObjectName("chartContainer")
        self.chartContainer.setMinimumHeight(250)
        self.chartContainer.setStyleSheet(
            "QWidget#chartContainer { background-color: #fafafa; "
            "border: 2px dashed #ccc; border-radius: 4px; }"
        )
        
        # Label placeholder
        chart_placeholder_layout = QVBoxLayout(self.chartContainer)
        lbl_placeholder = QLabel("Gráfica pendiente")
        lbl_placeholder.setAlignment(Qt.AlignCenter)
        lbl_placeholder.setStyleSheet("QLabel { color: #999; font-size: 14px; }")
        chart_placeholder_layout.addWidget(lbl_placeholder)
        
        card_e_layout.addWidget(self.chartContainer)
        
        card_e.setLayout(card_e_layout)
        column_layout.addWidget(card_e)
        
        column_layout.addStretch()
        
        return column
    
    def _create_lower_panel(self) -> QWidget:
        """Crea el panel inferior con tablas de simulaciones y vigentes."""
        # Usar QSplitter para permitir redimensionar
        splitter = QSplitter(Qt.Vertical)
        
        # Sección de simulaciones
        splitter.addWidget(self._create_simulations_section())
        
        # Sección de operaciones vigentes
        splitter.addWidget(self._create_operations_section())
        
        # Distribución inicial 50/50
        splitter.setSizes([400, 300])
        
        return splitter
    
    def _create_simulations_section(self) -> QWidget:
        """Crea la sección de simulaciones con título y botones en la misma línea."""
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(6)
        section_layout.setContentsMargins(0, 2, 0, 5)
        
        # Barra de título con botones (en la misma línea)
        title_bar = QHBoxLayout()
        title_bar.setSpacing(12)
        
        # Título a la izquierda
        lbl_title = QLabel("Simulaciones Forward")
        font_title = QFont()
        font_title.setPointSize(11)
        font_title.setBold(True)
        lbl_title.setFont(font_title)
        title_bar.addWidget(lbl_title)
        
        # Separador vertical
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        title_bar.addWidget(separator)
        
        # Botones a la derecha
        self.btnAddSim = QPushButton("➕ Agregar fila")
        self.btnAddSim.setObjectName("btnAddSim")
        self.btnAddSim.clicked.connect(self.on_add_simulation_row)
        title_bar.addWidget(self.btnAddSim)
        
        self.btnDelSim = QPushButton("🗑️ Eliminar")
        self.btnDelSim.setObjectName("btnDelSim")
        self.btnDelSim.clicked.connect(self._on_delete_button_clicked)
        title_bar.addWidget(self.btnDelSim)
        
        # Pequeño espaciador entre botones de gestión y acción
        title_bar.addSpacing(10)
        
        self.btnRun = QPushButton("▶️ Simular")
        self.btnRun.setObjectName("btnRun")
        self.btnRun.clicked.connect(self._on_run_button_clicked)
        title_bar.addWidget(self.btnRun)
        
        self.btnSaveSel = QPushButton("💾 Guardar selección")
        self.btnSaveSel.setObjectName("btnSaveSel")
        self.btnSaveSel.clicked.connect(self._on_save_button_clicked)
        title_bar.addWidget(self.btnSaveSel)
        
        title_bar.addStretch()
        
        section_layout.addLayout(title_bar)
        
        # Tabla de simulaciones
        self.tblSimulaciones = QTableView()
        self.tblSimulaciones.setObjectName("tblSimulaciones")
        self.tblSimulaciones.setAlternatingRowColors(True)
        self.tblSimulaciones.setSortingEnabled(True)
        self.tblSimulaciones.setSelectionBehavior(QTableView.SelectRows)
        self.tblSimulaciones.setSelectionMode(QTableView.ExtendedSelection)
        self.tblSimulaciones.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        section_layout.addWidget(self.tblSimulaciones)
        
        return section
    
    def _create_operations_section(self) -> QWidget:
        """Crea la sección de operaciones vigentes con filtros y tabla."""
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(8)
        section_layout.setContentsMargins(0, 5, 0, 5)
        
        # Título
        lbl_title = QLabel("Operaciones vigentes del cliente")
        font_title = QFont()
        font_title.setPointSize(11)
        font_title.setBold(True)
        lbl_title.setFont(font_title)
        section_layout.addWidget(lbl_title)
        
        # Tabla de operaciones vigentes (sin filtros)
        self.tblVigentes = QTableView()
        self.tblVigentes.setObjectName("tblVigentes")
        self.tblVigentes.setAlternatingRowColors(True)
        self.tblVigentes.setSortingEnabled(True)
        self.tblVigentes.setSelectionBehavior(QTableView.SelectRows)
        self.tblVigentes.setEditTriggers(QTableView.NoEditTriggers)  # Solo lectura
        section_layout.addWidget(self.tblVigentes)
        
        return section
    
    def _create_card(self, title: str) -> QGroupBox:
        """
        Crea un card (QGroupBox) con estilo.
        
        Args:
            title: Título del card
            
        Returns:
            QGroupBox configurado como card
        """
        card = QGroupBox(title)
        card.setStyleSheet(
            "QGroupBox { font-weight: bold; border: 1px solid #ddd; "
            "border-radius: 5px; margin-top: 10px; padding-top: 10px; } "
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; "
            "padding: 0 5px; color: #333; }"
        )
        return card
    
    # ================================================================
    # Handlers internos de botones (emiten señales)
    # ================================================================
    
    def _on_load_415_button_clicked(self):
        """Handler interno para el botón de cargar 415."""
        # En implementación real, abriría QFileDialog
        # Por ahora emitimos con un path dummy para testing
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo 415",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.on_load_415_clicked(file_path)
    
    def _on_client_combo_changed(self, text: str):
        """Handler interno para cambio de cliente en combo."""
        if text and text != "-- Seleccione un cliente --":
            # Extraer NIT del texto (asumiendo formato "NIT - Nombre")
            nit = text.split(" - ")[0] if " - " in text else text
            self.on_client_selected(nit)
    
    def _on_load_415_button_clicked(self):
        """Handler interno para el botón Cargar 415."""
        from PySide6.QtWidgets import QFileDialog
        
        # Abrir diálogo de selección de archivo
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo 415",
            "",
            "Archivos CSV (*.csv);;Todos los archivos (*.*)"
        )
        
        # Si se seleccionó un archivo, emitir señal
        if file_path:
            self.on_load_415_clicked(file_path)
    
    def _on_load_ibr_button_clicked(self):
        """Handler interno para el botón Cargar IBR."""
        from PySide6.QtWidgets import QFileDialog
        
        # Abrir diálogo de selección de archivo
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo IBR",
            "",
            "Archivos CSV (*.csv);;Todos los archivos (*.*)"
        )
        
        # Si se seleccionó un archivo, emitir señal
        if file_path:
            self.on_load_ibr_clicked(file_path)
    
    def _on_delete_button_clicked(self):
        """Handler interno para eliminar simulaciones."""
        selected_rows = list(set(index.row() for index in self.tblSimulaciones.selectedIndexes()))
        if selected_rows:
            self.on_delete_simulation_rows(selected_rows)
        else:
            print("[ForwardView] No hay filas seleccionadas para eliminar")
    
    def _on_run_button_clicked(self):
        """Handler interno para simular fila seleccionada."""
        print("[ForwardView] _on_run_button_clicked")
        self.simulate_selected_requested.emit()
    
    def _on_save_button_clicked(self):
        """Handler interno para guardar simulaciones."""
        selected_rows = list(set(index.row() for index in self.tblSimulaciones.selectedIndexes()))
        if selected_rows:
            self.on_save_selected_simulations(selected_rows)
    
    # ================================================================
    # Eventos del usuario (métodos que emiten señales)
    # ================================================================
    
    def on_load_415_clicked(self, file_path: str) -> None:
        """
        Maneja el clic en botón cargar 415.
        
        Args:
            file_path: Ruta del archivo seleccionado
        """
        print(f"[ForwardView] on_load_415_clicked: {file_path}")
        self.load_415_requested.emit(file_path)
    
    def on_load_ibr_clicked(self, file_path: str) -> None:
        """
        Maneja el clic en botón cargar IBR.
        
        Args:
            file_path: Ruta del archivo IBR seleccionado
        """
        print(f"[ForwardView] on_load_ibr_clicked: {file_path}")
        self.load_ibr_requested.emit(file_path)
    
    def on_client_selected(self, nit: str) -> None:
        """
        Maneja la selección de cliente.
        
        Args:
            nit: NIT del cliente seleccionado
        """
        print(f"[ForwardView] on_client_selected: {nit}")
        self.client_selected.emit(nit)
    
    def on_add_simulation_row(self) -> None:
        """Maneja el clic en agregar fila de simulación."""
        print("[ForwardView] on_add_simulation_row")
        self.add_simulation_requested.emit()
    
    def on_delete_simulation_rows(self, rows: List[int]) -> None:
        """
        Maneja el clic en eliminar filas.
        
        Args:
            rows: Lista de índices de filas a eliminar
        """
        print(f"[ForwardView] on_delete_simulation_rows: {rows}")
        self.delete_simulations_requested.emit(rows)
    
    def on_save_selected_simulations(self, rows: List[int]) -> None:
        """
        Maneja el clic en guardar simulaciones.
        
        Args:
            rows: Lista de índices de filas a guardar
        """
        print(f"[ForwardView] on_save_selected_simulations: {rows}")
        self.save_simulations_requested.emit(rows)
    
    # ================================================================
    # Métodos para actualizar UI (slots que reciben datos)
    # ================================================================
    
    def set_client_list(self, clientes: List[str]) -> None:
        """
        Carga la lista de clientes en el combo box sin seleccionar automáticamente.
        
        Args:
            clientes: Lista de nombres de clientes
        """
        print(f"[ForwardView] set_client_list: {len(clientes)} clientes")
        
        # Bloquear señales para evitar triggers automáticos
        self.cmbClientes.blockSignals(True)
        
        # Limpiar combo
        self.cmbClientes.clear()
        
        # Agregar clientes
        for nombre in sorted(clientes):
            self.cmbClientes.addItem(nombre)
        
        # NO seleccionar automáticamente ningún cliente
        self.cmbClientes.setCurrentIndex(-1)
        
        # Desbloquear señales
        self.cmbClientes.blockSignals(False)
        
        print(f"   ✓ Combo de clientes actualizado con {len(clientes)} opciones (sin selección)")
    
    def show_basic_info(self, patrimonio: float, trm: float,
                        corte_415: Optional[date], estado_415: str) -> None:
        """
        Actualiza la información básica del 415.
        
        NOTA: Patrimonio y TRM ya NO se actualizan aquí, se actualizan automáticamente
        desde SettingsModel mediante señales Qt. Los parámetros se mantienen por
        compatibilidad pero se ignoran.
        
        Args:
            patrimonio: [IGNORADO] Patrimonio técnico (actualizado por SettingsModel)
            trm: [IGNORADO] TRM (actualizado por SettingsModel)
            corte_415: Fecha de corte del 415
            estado_415: Estado del archivo
        """
        print(f"[ForwardView] show_basic_info: corte={corte_415}, estado={estado_415}")
        print(f"   (Patrimonio y TRM se actualizan automáticamente desde SettingsModel)")
        
        # Patrimonio y TRM ya no se actualizan aquí, lo hace SettingsModel automáticamente
        
        if corte_415:
            self.lblFechaCorte415.setText(f"Fecha corte 415: {corte_415.strftime('%d/%m/%Y')}")
        else:
            self.lblFechaCorte415.setText("Fecha corte 415: --")
        
        # Actualizar badge de estado
        self.lblEstado415.setText(estado_415.capitalize())
        if estado_415 == "valido":
            self.lblEstado415.setStyleSheet(
                "QLabel { background-color: #4caf50; color: white; "
                "padding: 4px 12px; border-radius: 3px; }"
            )
        elif estado_415 == "no_cargado":
            self.lblEstado415.setStyleSheet(
                "QLabel { background-color: #999; color: white; "
                "padding: 4px 12px; border-radius: 3px; }"
            )
        else:
            self.lblEstado415.setStyleSheet(
                "QLabel { background-color: #f44336; color: white; "
                "padding: 4px 12px; border-radius: 3px; }"
            )
    
    def update_banner_415(
        self,
        nombre: str,
        tamano_kb: float,
        fecha_cargue: Optional[Any],
        estado: str
    ) -> None:
        """
        Actualiza el banner con información del archivo 415.
        
        Args:
            nombre: Nombre del archivo
            tamano_kb: Tamaño del archivo en KB
            fecha_cargue: Timestamp de cargue
            estado: Estado del archivo
        """
        from datetime import datetime
        
        fecha_str = "—"
        if fecha_cargue:
            if isinstance(fecha_cargue, datetime):
                fecha_str = fecha_cargue.strftime("%Y-%m-%d %H:%M")
        
        # Actualizar label del banner
        banner_text = f"Archivo: {nombre} | Tamaño: {tamano_kb:.2f} KB | Fecha cargue: {fecha_str}"
        self.lblArchivo415.setText(banner_text)
        
        # Mostrar el banner
        banner = self.findChild(QFrame, "banner415")
        if banner:
            banner.setVisible(True)
            
            # Aplicar color de fondo al banner según estado
            if estado == "valido":
                color_fondo = "#e8f5e9"  # Verde claro
            elif estado == "invalido":
                color_fondo = "#ffebee"  # Rojo claro
            else:
                color_fondo = "#f0f4f8"  # Gris claro
            
            banner.setStyleSheet(
                f"QFrame#banner415 {{ background-color: {color_fondo}; "
                f"border: 1px solid #d1d9e0; border-radius: 4px; padding: 8px; }}"
            )
    
    def set_credit_params(self, linea: str, colchon: str, limite: str) -> None:
        """
        Actualiza los parámetros de crédito del cliente (línea, colchón, límite).
        Acepta strings directos para máxima flexibilidad (ej. "—" o valores formateados).
        
        Args:
            linea: Línea de crédito (texto formateado o "—")
            colchon: Colchón de seguridad (texto formateado o "—")
            limite: Límite máximo permitido (texto formateado o "—")
        """
        print(f"[ForwardView] set_credit_params: linea={linea}, colchon={colchon}, limite={limite}")
        
        # Asignar directamente los textos sin disparar eventos
        self.lblLineaCredito.setText(linea)
        self.lblColchonInterno.setText(colchon)
        self.lblLimiteMax.setText(limite)
    
    def show_exposure(self, outstanding: float = None, total_con_simulacion: float = None,
                     disponibilidad: float = None) -> None:
        """
        Actualiza la información de exposición.
        
        Args:
            outstanding: Exposición actual (opcional)
            total_con_simulacion: Exposición total con simulaciones (opcional)
            disponibilidad: Límite disponible (opcional)
        """
        print(f"[ForwardView] show_exposure: outstanding={outstanding}, "
              f"total={total_con_simulacion}, disponibilidad={disponibilidad}")
        
        # Actualizar solo los valores que no sean None
        if outstanding is not None:
            self.lblOutstanding.setText(f"$ {outstanding:,.2f}")
        else:
            self.lblOutstanding.setText("—")
        
        # Outstanding + simulación: solo mostrar si se proporcionó un valor
        if total_con_simulacion is not None:
            self.lblOutstandingSim.setText(f"$ {total_con_simulacion:,.2f}")
        else:
            self.lblOutstandingSim.setText("—")  # No igualar al Outstanding
        
        if disponibilidad is not None:
            self.lblDisponibilidad.setText(f"$ {disponibilidad:,.2f}")
            
            # Cambiar color según disponibilidad
            if disponibilidad < 0:
                self.lblDisponibilidad.setStyleSheet("QLabel { color: #d32f2f; font-weight: bold; }")
            elif disponibilidad < 1000000:  # Menos de 1 millón
                self.lblDisponibilidad.setStyleSheet("QLabel { color: #f57c00; font-weight: bold; }")
            else:
                self.lblDisponibilidad.setStyleSheet("QLabel { color: #2e7d32; font-weight: bold; }")
        else:
            self.lblDisponibilidad.setText("—")
    
    def update_chart(self, data: Dict[str, Any]) -> None:
        """
        Actualiza el gráfico de exposición.
        
        Args:
            data: Datos para el gráfico
                linea_total, consumo_actual, consumo_con_simulacion, disponibilidad
        """
        print(f"[ForwardView] update_chart: {data}")
        
        # Por ahora, actualizar el texto del placeholder
        # En producción, aquí se implementaría un gráfico de barras con QtCharts
        linea_total = data.get("linea_total", 0)
        consumo_actual = data.get("consumo_actual", 0)
        consumo_con_sim = data.get("consumo_con_simulacion", 0)
        disponibilidad = data.get("disponibilidad", 0)
        
        # Calcular porcentajes
        pct_actual = (consumo_actual / linea_total * 100) if linea_total > 0 else 0
        pct_con_sim = (consumo_con_sim / linea_total * 100) if linea_total > 0 else 0
        pct_disp = (disponibilidad / linea_total * 100) if linea_total > 0 else 0
        
        chart_text = f"""<div style='padding: 20px; text-align: center;'>
<h3>Consumo de Línea de Crédito</h3>
<hr>
<p style='font-size: 12pt;'>
    <b>Línea Total:</b> $ {linea_total:,.0f}<br><br>
    <b style='color: blue;'>Consumo Actual:</b> $ {consumo_actual:,.0f} ({pct_actual:.1f}%)<br>
    <b style='color: orange;'>Consumo con Simulación:</b> $ {consumo_con_sim:,.0f} ({pct_con_sim:.1f}%)<br>
    <b style='color: green;'>Disponibilidad:</b> $ {disponibilidad:,.0f} ({pct_disp:.1f}%)<br>
</p>
<hr>
<p style='font-size: 10pt; color: gray;'>
    (Placeholder - integrar gráfica real con QtCharts)
</p>
</div>"""
        
        # Buscar el label dentro del chartContainer y actualizar su texto
        for child in self.chartContainer.findChildren(QLabel):
            child.setText(chart_text)
    
    def set_operations_table(self, model: Any) -> None:
        """
        Establece el modelo de tabla de operaciones vigentes.
        
        Args:
            model: Instancia de OperationsTableModel
        """
        from PySide6.QtWidgets import QHeaderView, QAbstractItemView
        
        print(f"[ForwardView] set_operations_table: {model}")
        if model:
            self.tblVigentes.setModel(model)
            
            # Configurar ancho proporcional uniforme para todas las columnas
            header = self.tblVigentes.horizontalHeader()
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.Stretch)  # Todas las columnas con ancho proporcional
            
            # Configurar tabla
            self.tblVigentes.verticalHeader().setVisible(False)
            self.tblVigentes.setAlternatingRowColors(True)
            self.tblVigentes.setSortingEnabled(True)
            self.tblVigentes.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tblVigentes.setSelectionMode(QAbstractItemView.SingleSelection)
    
    def set_simulations_table(self, model: Any) -> None:
        """
        Establece el modelo de tabla de simulaciones.
        
        Args:
            model: Instancia de SimulationsTableModel
        """
        print(f"[ForwardView] set_simulations_table: {model}")
        if model:
            self.tblSimulaciones.setModel(model)
            
            # Configurar delegates personalizados
            from src.views.simulations_delegates import PuntaClienteDelegate, FechaDelegate
            
            # Delegate para "Punta Cli" (columna 1)
            punta_col_idx = model.get_column_index("Punta Cli")
            if punta_col_idx >= 0:
                self.tblSimulaciones.setItemDelegateForColumn(
                    punta_col_idx, 
                    PuntaClienteDelegate(self.tblSimulaciones)
                )
                print(f"   [OK] Delegate configurado para columna 'Punta Cli' (indice {punta_col_idx})")
            
            # Delegate para "Fec Venc" (columna 5)
            fecha_col_idx = model.get_column_index("Fec Venc")
            if fecha_col_idx >= 0:
                self.tblSimulaciones.setItemDelegateForColumn(
                    fecha_col_idx,
                    FechaDelegate(self.tblSimulaciones)
                )
                print(f"   [OK] Delegate configurado para columna 'Fec Venc' (indice {fecha_col_idx})")
            
            # Configurar tabla con distribución uniforme de columnas
            from PySide6.QtWidgets import QHeaderView, QAbstractItemView
            
            self.tblSimulaciones.setAlternatingRowColors(True)
            self.tblSimulaciones.setSortingEnabled(True)
            self.tblSimulaciones.setSelectionBehavior(QAbstractItemView.SelectRows)
            
            # Distribución uniforme de columnas
            self.tblSimulaciones.horizontalHeader().setStretchLastSection(True)
            self.tblSimulaciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Ocultar números de fila verticales
            self.tblSimulaciones.verticalHeader().setVisible(False)
    
    def update_ibr_status(
        self,
        file_path: Optional[str],
        estado: str,
        tamano_kb: Optional[float] = None,
        timestamp: Optional[str] = None
    ) -> None:
        """
        Actualiza el banner con información del archivo IBR.
        
        Args:
            file_path: Ruta del archivo (None si inválido)
            estado: Estado del archivo ("Cargado" o "Inválido")
            tamano_kb: Tamaño en KB (opcional)
            timestamp: Fecha/hora de cargue (opcional)
        """
        from pathlib import Path
        
        # Obtener nombre del archivo
        if file_path:
            nombre = Path(file_path).name
        else:
            nombre = "—"
        
        # Actualizar labels
        self.lblArchivoIBR.setText(f"Archivo: {nombre}")
        
        if tamano_kb is not None:
            self.lblTamanoIBR.setText(f"Tamaño: {tamano_kb:.2f} KB")
        else:
            self.lblTamanoIBR.setText("Tamaño: —")
        
        if timestamp:
            self.lblFechaIBR.setText(f"Fecha: {timestamp}")
        else:
            self.lblFechaIBR.setText("Fecha: —")
        
        # Actualizar badge de estado
        if estado == "Cargado":
            self.lblEstadoIBR.setText("✅ Cargado")
            self.lblEstadoIBR.setStyleSheet(
                "QLabel { background-color: #4caf50; color: white; "
                "padding: 4px 12px; border-radius: 3px; }"
            )
            color_fondo = "#e8f5e9"  # Verde claro
        else:
            self.lblEstadoIBR.setText("⛔ Inválido")
            self.lblEstadoIBR.setStyleSheet(
                "QLabel { background-color: #f44336; color: white; "
                "padding: 4px 12px; border-radius: 3px; }"
            )
            color_fondo = "#ffebee"  # Rojo claro
        
        # Aplicar color de fondo al banner
        if self.bannerIBR:
            self.bannerIBR.setStyleSheet(
                f"QFrame#bannerIBR {{ background-color: {color_fondo}; "
                f"border: 1px solid #d1d9e0; border-radius: 4px; padding: 8px; }}"
            )
            # Mostrar el banner
            self.bannerIBR.setVisible(True)
        
        print(f"[ForwardView] update_ibr_status: {nombre} | {estado} | {tamano_kb} KB | {timestamp}")
    
    def get_selected_simulation_index(self):
        """
        Obtiene el índice de la fila seleccionada en la tabla de simulaciones.
        
        Returns:
            QModelIndex de la fila seleccionada, o QModelIndex inválido si no hay selección
        """
        from PySide6.QtCore import QModelIndex
        sm = self.tblSimulaciones.selectionModel()
        return sm.currentIndex() if sm else QModelIndex()
    
    def get_selected_simulation_rows(self):
        """
        Obtiene los índices de todas las filas seleccionadas en la tabla de simulaciones.
        Permite selección múltiple con Ctrl o Shift.
        
        Returns:
            Lista de enteros con los índices de filas seleccionadas (ordenados)
        """
        sm = self.tblSimulaciones.selectionModel()
        if not sm:
            return []
        
        # Obtener todas las filas seleccionadas
        selected_indexes = sm.selectedRows()
        
        # Extraer solo los números de fila y ordenarlos
        selected_rows = sorted(set(index.row() for index in selected_indexes))
        
        return selected_rows
    
    def notify(self, message: str, level: str) -> None:
        """
        Muestra una notificación al usuario.
        
        Args:
            message: Mensaje a mostrar
            level: Nivel de severidad ("info", "warning", "error")
        """
        print(f"[ForwardView] notify [{level}]: {message}")
        # Aquí se podría usar QMessageBox o un sistema de notificaciones toast
