"""
Vista para el módulo de operaciones Forward.
Layout visual completo con cards, tablas y toolbar.
"""

from typing import Optional, List, Dict, Any
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTableView,
    QGroupBox, QFrame, QToolBar, QCheckBox, QSplitter
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
    client_selected = Signal(str)              # nit
    add_simulation_requested = Signal()
    duplicate_simulation_requested = Signal(int)      # row
    delete_simulations_requested = Signal(list)       # rows
    run_simulations_requested = Signal()
    save_simulations_requested = Signal(list)         # rows
    
    def __init__(self, parent=None):
        """
        Inicializa la vista Forward.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        
        # Referencias a widgets principales (se crean en _setup_ui)
        self.btnLoad415 = None
        self.lblTituloForward = None
        self.lblFechaCorte415 = None
        self.lblEstado415 = None
        self.lblArchivo415 = None
        
        self.lblPatrimonio = None
        self.lblTRM = None
        self.cmbClientes = None
        self.txtBuscarCliente = None
        
        self.lblLineaCredito = None
        self.lblColchonInterno = None
        self.lblLimiteMax = None
        self.lblOutstanding = None
        self.lblOutstandingSim = None
        self.lblDisponibilidad = None
        
        self.chartContainer = None
        
        self.btnAddSim = None
        self.btnDupSim = None
        self.btnDelSim = None
        self.btnRunAll = None
        self.btnSaveSel = None
        self.tblSimulaciones = None
        
        self.txtFiltroVigentes = None
        self.chkIncluirCalculo = None
        self.tblVigentes = None
        
        self.banner415 = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario completa."""
        # Layout principal vertical
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 1. Header
        main_layout.addWidget(self._create_header())
        
        # 2. Banner estado 415
        self.banner415 = self._create_banner_415()
        main_layout.addWidget(self.banner415)
        
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
    
    def _create_upper_panel(self) -> QWidget:
        """Crea el panel superior con 3 columnas de cards."""
        panel_widget = QWidget()
        panel_layout = QHBoxLayout(panel_widget)
        panel_layout.setSpacing(15)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        
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
        card_a_layout = QVBoxLayout()
        
        # Patrimonio técnico
        lbl_pat_title = QLabel("Patrimonio técnico vigente:")
        self.lblPatrimonio = QLabel("$ 0.00")
        self.lblPatrimonio.setObjectName("lblPatrimonio")
        font_value = QFont()
        font_value.setBold(True)
        self.lblPatrimonio.setFont(font_value)
        card_a_layout.addWidget(lbl_pat_title)
        card_a_layout.addWidget(self.lblPatrimonio)
        
        card_a_layout.addSpacing(10)
        
        # TRM vigente
        lbl_trm_title = QLabel("TRM vigente:")
        self.lblTRM = QLabel("$ 0.00")
        self.lblTRM.setObjectName("lblTRM")
        self.lblTRM.setFont(font_value)
        card_a_layout.addWidget(lbl_trm_title)
        card_a_layout.addWidget(self.lblTRM)
        
        card_a.setLayout(card_a_layout)
        column_layout.addWidget(card_a)
        
        # Card B: Cliente
        card_b = self._create_card("Cliente")
        card_b_layout = QVBoxLayout()
        
        # Búsqueda de cliente
        lbl_buscar = QLabel("Buscar cliente:")
        self.txtBuscarCliente = QLineEdit()
        self.txtBuscarCliente.setObjectName("txtBuscarCliente")
        self.txtBuscarCliente.setPlaceholderText("Buscar por NIT o nombre...")
        card_b_layout.addWidget(lbl_buscar)
        card_b_layout.addWidget(self.txtBuscarCliente)
        
        card_b_layout.addSpacing(5)
        
        # ComboBox de clientes
        lbl_cliente = QLabel("Seleccionar cliente:")
        self.cmbClientes = QComboBox()
        self.cmbClientes.setObjectName("cmbClientes")
        self.cmbClientes.addItem("-- Seleccione un cliente --")
        # Agregando clientes mock con formato "NIT - Nombre"
        self.cmbClientes.addItem("123456789 - Cliente Ejemplo S.A.")
        self.cmbClientes.addItem("987654321 - Corporación ABC Ltda.")
        self.cmbClientes.addItem("555444333 - Empresa XYZ S.A.S.")
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
        card_c_layout = QVBoxLayout()
        
        # Línea de crédito
        lbl_linea_title = QLabel("Línea de crédito:")
        self.lblLineaCredito = QLabel("$ 0.00")
        self.lblLineaCredito.setObjectName("lblLineaCredito")
        font_value = QFont()
        font_value.setBold(True)
        self.lblLineaCredito.setFont(font_value)
        card_c_layout.addWidget(lbl_linea_title)
        card_c_layout.addWidget(self.lblLineaCredito)
        
        card_c_layout.addSpacing(8)
        
        # Colchón interno
        lbl_colchon_title = QLabel("Colchón interno:")
        self.lblColchonInterno = QLabel("0.0%")
        self.lblColchonInterno.setObjectName("lblColchonInterno")
        self.lblColchonInterno.setFont(font_value)
        card_c_layout.addWidget(lbl_colchon_title)
        card_c_layout.addWidget(self.lblColchonInterno)
        
        card_c_layout.addSpacing(8)
        
        # Límite máximo
        lbl_limite_title = QLabel("Límite máximo permitido:")
        self.lblLimiteMax = QLabel("$ 0.00")
        self.lblLimiteMax.setObjectName("lblLimiteMax")
        self.lblLimiteMax.setFont(font_value)
        card_c_layout.addWidget(lbl_limite_title)
        card_c_layout.addWidget(self.lblLimiteMax)
        
        card_c.setLayout(card_c_layout)
        column_layout.addWidget(card_c)
        
        # Card D: Exposición
        card_d = self._create_card("Exposición")
        card_d_layout = QVBoxLayout()
        
        # Outstanding
        lbl_out_title = QLabel("Outstanding:")
        self.lblOutstanding = QLabel("$ 0.00")
        self.lblOutstanding.setObjectName("lblOutstanding")
        self.lblOutstanding.setFont(font_value)
        card_d_layout.addWidget(lbl_out_title)
        card_d_layout.addWidget(self.lblOutstanding)
        
        card_d_layout.addSpacing(8)
        
        # Outstanding + simulación
        lbl_outsim_title = QLabel("Outstanding + simulación:")
        self.lblOutstandingSim = QLabel("$ 0.00")
        self.lblOutstandingSim.setObjectName("lblOutstandingSim")
        self.lblOutstandingSim.setFont(font_value)
        card_d_layout.addWidget(lbl_outsim_title)
        card_d_layout.addWidget(self.lblOutstandingSim)
        
        card_d_layout.addSpacing(8)
        
        # Disponibilidad
        lbl_disp_title = QLabel("Disponibilidad de línea:")
        self.lblDisponibilidad = QLabel("$ 0.00")
        self.lblDisponibilidad.setObjectName("lblDisponibilidad")
        self.lblDisponibilidad.setFont(font_value)
        self.lblDisponibilidad.setStyleSheet("QLabel { color: #2e7d32; }")
        card_d_layout.addWidget(lbl_disp_title)
        card_d_layout.addWidget(self.lblDisponibilidad)
        
        card_d.setLayout(card_d_layout)
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
        """Crea la sección de simulaciones con toolbar y tabla."""
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(8)
        section_layout.setContentsMargins(0, 5, 0, 5)
        
        # Título
        lbl_title = QLabel("Simulaciones Forward")
        font_title = QFont()
        font_title.setPointSize(11)
        font_title.setBold(True)
        lbl_title.setFont(font_title)
        section_layout.addWidget(lbl_title)
        
        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        self.btnAddSim = QPushButton("➕ Agregar fila")
        self.btnAddSim.setObjectName("btnAddSim")
        self.btnAddSim.clicked.connect(self.on_add_simulation_row)
        toolbar.addWidget(self.btnAddSim)
        
        self.btnDupSim = QPushButton("📋 Duplicar")
        self.btnDupSim.setObjectName("btnDupSim")
        self.btnDupSim.clicked.connect(self._on_duplicate_button_clicked)
        toolbar.addWidget(self.btnDupSim)
        
        self.btnDelSim = QPushButton("🗑️ Eliminar")
        self.btnDelSim.setObjectName("btnDelSim")
        self.btnDelSim.clicked.connect(self._on_delete_button_clicked)
        toolbar.addWidget(self.btnDelSim)
        
        toolbar.addSeparator()
        
        self.btnRunAll = QPushButton("▶️ Simular todo")
        self.btnRunAll.setObjectName("btnRunAll")
        self.btnRunAll.clicked.connect(self.on_run_simulations)
        toolbar.addWidget(self.btnRunAll)
        
        self.btnSaveSel = QPushButton("💾 Guardar selección")
        self.btnSaveSel.setObjectName("btnSaveSel")
        self.btnSaveSel.clicked.connect(self._on_save_button_clicked)
        toolbar.addWidget(self.btnSaveSel)
        
        section_layout.addWidget(toolbar)
        
        # Tabla de simulaciones
        self.tblSimulaciones = QTableView()
        self.tblSimulaciones.setObjectName("tblSimulaciones")
        self.tblSimulaciones.setAlternatingRowColors(True)
        self.tblSimulaciones.setSortingEnabled(True)
        self.tblSimulaciones.setSelectionBehavior(QTableView.SelectRows)
        self.tblSimulaciones.setSelectionMode(QTableView.ExtendedSelection)
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
        
        # Filtros
        filters_layout = QHBoxLayout()
        
        lbl_filtro = QLabel("Filtrar:")
        filters_layout.addWidget(lbl_filtro)
        
        self.txtFiltroVigentes = QLineEdit()
        self.txtFiltroVigentes.setObjectName("txtFiltroVigentes")
        self.txtFiltroVigentes.setPlaceholderText("Buscar en operaciones vigentes...")
        self.txtFiltroVigentes.setMaximumWidth(300)
        filters_layout.addWidget(self.txtFiltroVigentes)
        
        filters_layout.addSpacing(20)
        
        self.chkIncluirCalculo = QCheckBox("Incluir en cálculo")
        self.chkIncluirCalculo.setObjectName("chkIncluirCalculo")
        self.chkIncluirCalculo.setChecked(True)
        filters_layout.addWidget(self.chkIncluirCalculo)
        
        filters_layout.addStretch()
        
        section_layout.addLayout(filters_layout)
        
        # Tabla de operaciones vigentes
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
    
    def _on_duplicate_button_clicked(self):
        """Handler interno para duplicar simulación."""
        selected = self.tblSimulaciones.selectedIndexes()
        if selected:
            row = selected[0].row()
            self.on_duplicate_simulation_row(row)
        else:
            print("[ForwardView] No hay fila seleccionada para duplicar")
    
    def _on_delete_button_clicked(self):
        """Handler interno para eliminar simulaciones."""
        selected_rows = list(set(index.row() for index in self.tblSimulaciones.selectedIndexes()))
        if selected_rows:
            self.on_delete_simulation_rows(selected_rows)
        else:
            print("[ForwardView] No hay filas seleccionadas para eliminar")
    
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
    
    def on_duplicate_simulation_row(self, row: int) -> None:
        """
        Maneja el clic en duplicar fila.
        
        Args:
            row: Índice de la fila a duplicar
        """
        print(f"[ForwardView] on_duplicate_simulation_row: {row}")
        self.duplicate_simulation_requested.emit(row)
    
    def on_delete_simulation_rows(self, rows: List[int]) -> None:
        """
        Maneja el clic en eliminar filas.
        
        Args:
            rows: Lista de índices de filas a eliminar
        """
        print(f"[ForwardView] on_delete_simulation_rows: {rows}")
        self.delete_simulations_requested.emit(rows)
    
    def on_run_simulations(self) -> None:
        """Maneja el clic en ejecutar simulaciones."""
        print("[ForwardView] on_run_simulations")
        self.run_simulations_requested.emit()
    
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
    
    def show_basic_info(self, patrimonio: float, trm: float,
                       corte_415: Optional[date], estado_415: str) -> None:
        """
        Actualiza la información básica.
        
        Args:
            patrimonio: Patrimonio técnico en COP
            trm: Tasa Representativa del Mercado
            corte_415: Fecha de corte del 415
            estado_415: Estado del archivo
        """
        print(f"[ForwardView] show_basic_info: patrimonio={patrimonio}, trm={trm}, "
              f"corte={corte_415}, estado={estado_415}")
        
        # Actualizar labels
        self.lblPatrimonio.setText(f"$ {patrimonio:,.2f}")
        self.lblTRM.setText(f"$ {trm:,.2f}")
        
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
    
    def show_client_limits(self, linea: float, colchon_pct: float,
                          limite_max: float) -> None:
        """
        Actualiza la información de límites del cliente.
        
        Args:
            linea: Línea de crédito aprobada
            colchon_pct: Porcentaje de colchón
            limite_max: Límite máximo
        """
        print(f"[ForwardView] show_client_limits: linea={linea}, "
              f"colchon={colchon_pct}, limite_max={limite_max}")
        
        self.lblLineaCredito.setText(f"$ {linea:,.2f}")
        self.lblColchonInterno.setText(f"{colchon_pct:.1f}%")
        self.lblLimiteMax.setText(f"$ {limite_max:,.2f}")
    
    def show_exposure(self, outstanding: float, total_con_simulacion: float,
                     disponibilidad: float) -> None:
        """
        Actualiza la información de exposición.
        
        Args:
            outstanding: Exposición actual
            total_con_simulacion: Exposición total con simulaciones
            disponibilidad: Límite disponible
        """
        print(f"[ForwardView] show_exposure: outstanding={outstanding}, "
              f"total={total_con_simulacion}, disponibilidad={disponibilidad}")
        
        self.lblOutstanding.setText(f"$ {outstanding:,.2f}")
        self.lblOutstandingSim.setText(f"$ {total_con_simulacion:,.2f}")
        self.lblDisponibilidad.setText(f"$ {disponibilidad:,.2f}")
        
        # Cambiar color según disponibilidad
        if disponibilidad < 0:
            self.lblDisponibilidad.setStyleSheet("QLabel { color: #d32f2f; font-weight: bold; }")
        elif disponibilidad < 1000000:  # Menos de 1 millón
            self.lblDisponibilidad.setStyleSheet("QLabel { color: #f57c00; font-weight: bold; }")
        else:
            self.lblDisponibilidad.setStyleSheet("QLabel { color: #2e7d32; font-weight: bold; }")
    
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
        print(f"[ForwardView] set_operations_table: {model}")
        if model:
            self.tblVigentes.setModel(model)
            # Configurar tabla
            self.tblVigentes.setAlternatingRowColors(True)
            self.tblVigentes.setSortingEnabled(True)
            self.tblVigentes.resizeColumnsToContents()
            # Ajustar ancho de columnas
            self.tblVigentes.horizontalHeader().setStretchLastSection(True)
    
    def set_simulations_table(self, model: Any) -> None:
        """
        Establece el modelo de tabla de simulaciones.
        
        Args:
            model: Instancia de SimulationsTableModel
        """
        print(f"[ForwardView] set_simulations_table: {model}")
        if model:
            self.tblSimulaciones.setModel(model)
            # Configurar tabla
            self.tblSimulaciones.setAlternatingRowColors(True)
            self.tblSimulaciones.setSortingEnabled(True)
            self.tblSimulaciones.resizeColumnsToContents()
            # Ajustar ancho de columnas
            self.tblSimulaciones.horizontalHeader().setStretchLastSection(True)
    
    def notify(self, message: str, level: str) -> None:
        """
        Muestra una notificación al usuario.
        
        Args:
            message: Mensaje a mostrar
            level: Nivel de severidad ("info", "warning", "error")
        """
        print(f"[ForwardView] notify [{level}]: {message}")
        # Aquí se podría usar QMessageBox o un sistema de notificaciones toast
