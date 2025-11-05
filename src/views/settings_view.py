"""
Vista para el módulo de Configuración.
Interfaz de usuario para gestionar la configuración del sistema.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QFormLayout,
    QLineEdit, QDoubleSpinBox, QFileDialog, QTableView, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import Dict, Any


class SettingsView(QWidget):
    """
    Vista del módulo Settings.
    
    Responsabilidades:
    - Mostrar parámetros generales (Patrimonio, TRM)
    - Mostrar parámetros normativos (factores de riesgo)
    - Gestionar líneas de crédito vigentes
    """
    
    # Señales personalizadas
    load_lineas_credito_requested = Signal(str)  # file_path
    
    def __init__(self, parent: QWidget = None):
        """
        Inicializa la vista de configuración.
        
        Args:
            parent: Widget padre (opcional)
        """
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        
        print("[SettingsView] Vista de configuracion inicializada")
    
    def _setup_ui(self) -> None:
        """
        Configura la interfaz de usuario.
        """
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)
        
        # Título del módulo
        title_label = QLabel("⚙️ Configuraciones del Sistema")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        main_layout.addSpacing(8)
        
        # === 1. PARÁMETROS GENERALES ===
        group_general = self._create_parametros_generales()
        main_layout.addWidget(group_general)
        
        # === 2. PARÁMETROS NORMATIVOS ===
        group_normativos = self._create_parametros_normativos()
        main_layout.addWidget(group_normativos)
        
        # === 3. LÍNEAS DE CRÉDITO VIGENTES ===
        group_lineas = self._create_lineas_credito()
        main_layout.addWidget(group_lineas)
        
        # Stretch al final
        main_layout.addStretch()
        
        # Aplicar estilos
        self._apply_styles()
    
    def _create_parametros_generales(self) -> QGroupBox:
        """
        Crea el bloque de Parámetros Generales.
        
        Returns:
            QGroupBox con Patrimonio Técnico y TRM
        """
        group = QGroupBox("Parámetros Generales")
        layout = QFormLayout(group)
        layout.setSpacing(8)
        
        # Patrimonio Técnico Vigente (COP reales, no millones)
        self.inpPatrimonio = QDoubleSpinBox()
        self.inpPatrimonio.setDecimals(2)
        self.inpPatrimonio.setMaximum(1_000_000_000_000.00)  # 1 billón COP
        self.inpPatrimonio.setMinimum(0.00)
        self.inpPatrimonio.setSingleStep(1_000_000.00)       # pasos de $1M COP
        self.inpPatrimonio.setValue(50_000_000_000.00)       # Default: 50 mil millones COP
        self.inpPatrimonio.setSuffix(" COP")
        self.inpPatrimonio.setGroupSeparatorShown(True)
        layout.addRow("Patrimonio Técnico Vigente (COP):", self.inpPatrimonio)
        
        # TRM vigente del día
        self.inpTRM = QDoubleSpinBox()
        self.inpTRM.setRange(0, 10000)
        self.inpTRM.setValue(4200.50)  # Default: 4200.50
        self.inpTRM.setDecimals(2)
        self.inpTRM.setSuffix(" COP/USD")
        self.inpTRM.setGroupSeparatorShown(True)
        layout.addRow("TRM vigente del día:", self.inpTRM)
        
        return group
    
    def _create_parametros_normativos(self) -> QGroupBox:
        """
        Crea el bloque de Parámetros Normativos.
        
        Returns:
            QGroupBox con los 5 parámetros normativos
        """
        group = QGroupBox("Parámetros Normativos")
        layout = QFormLayout(group)
        layout.setSpacing(8)
        
        # Factor de ajuste (Anexo 3, Cap. XVIII – CE011/23)
        self.inpFactorAjuste = QDoubleSpinBox()
        self.inpFactorAjuste.setRange(0, 10)
        self.inpFactorAjuste.setValue(1.4)
        self.inpFactorAjuste.setDecimals(2)
        self.inpFactorAjuste.setSingleStep(0.1)
        layout.addRow("Factor de ajuste (Anexo 3, Cap. XVIII – CE011/23):", self.inpFactorAjuste)
        
        # Límite máx. endeudamiento individual (%)
        self.inpLimEndeud = QDoubleSpinBox()
        self.inpLimEndeud.setRange(0, 100)
        self.inpLimEndeud.setValue(10)
        self.inpLimEndeud.setDecimals(1)
        self.inpLimEndeud.setSuffix(" %")
        layout.addRow("Límite máx. endeudamiento individual (%):", self.inpLimEndeud)
        
        # Límite máx. concentración con SBLC (%)
        self.inpLimSBLC = QDoubleSpinBox()
        self.inpLimSBLC.setRange(0, 100)
        self.inpLimSBLC.setValue(30)
        self.inpLimSBLC.setDecimals(1)
        self.inpLimSBLC.setSuffix(" %")
        layout.addRow("Límite máx. concentración con SBLC (%):", self.inpLimSBLC)
        
        # Límite máx. concentración entidades financieras (%)
        self.inpLimEntFin = QDoubleSpinBox()
        self.inpLimEntFin.setRange(0, 100)
        self.inpLimEntFin.setValue(30)
        self.inpLimEntFin.setDecimals(1)
        self.inpLimEntFin.setSuffix(" %")
        layout.addRow("Límite máx. concentración entidades financieras (%):", self.inpLimEntFin)
        
        # Colchón de seguridad (%)
        self.inpColchon = QDoubleSpinBox()
        self.inpColchon.setRange(0, 50)
        self.inpColchon.setValue(5)
        self.inpColchon.setDecimals(1)
        self.inpColchon.setSuffix(" %")
        layout.addRow("Colchón de seguridad (%):", self.inpColchon)
        
        return group
    
    def _create_lineas_credito(self) -> QGroupBox:
        """
        Crea el bloque de Líneas de Crédito Vigentes.
        
        Returns:
            QGroupBox con tabla y botón de carga
        """
        group = QGroupBox("Líneas de Crédito Vigentes")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Encabezado con botón de carga
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.btnCargarLineas = QPushButton("📁 Cargar archivo...")
        self.btnCargarLineas.clicked.connect(self._on_cargar_lineas_clicked)
        header_layout.addWidget(self.btnCargarLineas)
        
        layout.addLayout(header_layout)
        
        # Tabla de líneas de crédito
        self.tblLineasCredito = QTableView()
        self.tblLineasCredito.setObjectName("tblLineasCredito")
        
        # Configurar tabla
        header = self.tblLineasCredito.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        self.tblLineasCredito.verticalHeader().setVisible(False)
        self.tblLineasCredito.setAlternatingRowColors(True)
        self.tblLineasCredito.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tblLineasCredito.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tblLineasCredito.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        layout.addWidget(self.tblLineasCredito)
        
        return group
    
    def _connect_signals(self) -> None:
        """
        Conecta las señales de los widgets.
        """
        # Las conexiones se manejan directamente en los widgets
        pass
    
    def _on_cargar_lineas_clicked(self):
        """Handler para el botón Cargar archivo de líneas de crédito."""
        print("[SettingsView] Abriendo dialogo para cargar lineas de credito...")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de Líneas de Crédito",
            "",
            "Archivos CSV (*.csv);;Todos los archivos (*.*)"
        )
        
        if file_path:
            print(f"[SettingsView] Archivo seleccionado: {file_path}")
            # Emitir señal para que el controller maneje la carga
            self.load_lineas_credito_requested.emit(file_path)
    
    def load_parametros_generales(self, patrimonio_cop: float, trm: float) -> None:
        """
        Carga los parámetros generales en la interfaz.
        
        Args:
            patrimonio_cop: Patrimonio técnico en COP (valor real, no millones)
            trm: TRM vigente del día
        """
        self.inpPatrimonio.blockSignals(True)
        self.inpTRM.blockSignals(True)
        
        self.inpPatrimonio.setValue(patrimonio_cop)
        self.inpTRM.setValue(trm)
        
        self.inpPatrimonio.blockSignals(False)
        self.inpTRM.blockSignals(False)
        
        print(f"[SettingsView] Parametros generales cargados: Patrimonio={patrimonio_cop:,.2f} COP, TRM={trm}")
    
    def load_parametros_normativos(self, factor_ajuste: float, lim_endeud: float, 
                                   lim_sblc: float, lim_entfin: float, colchon: float) -> None:
        """
        Carga los parámetros normativos en la interfaz.
        
        Args:
            factor_ajuste: Factor de ajuste
            lim_endeud: Límite máx. endeudamiento individual (%)
            lim_sblc: Límite máx. concentración SBLC (%)
            lim_entfin: Límite máx. concentración ent. financieras (%)
            colchon: Colchón de seguridad (%)
        """
        self.inpFactorAjuste.blockSignals(True)
        self.inpLimEndeud.blockSignals(True)
        self.inpLimSBLC.blockSignals(True)
        self.inpLimEntFin.blockSignals(True)
        self.inpColchon.blockSignals(True)
        
        self.inpFactorAjuste.setValue(factor_ajuste)
        self.inpLimEndeud.setValue(lim_endeud)
        self.inpLimSBLC.setValue(lim_sblc)
        self.inpLimEntFin.setValue(lim_entfin)
        self.inpColchon.setValue(colchon)
        
        self.inpFactorAjuste.blockSignals(False)
        self.inpLimEndeud.blockSignals(False)
        self.inpLimSBLC.blockSignals(False)
        self.inpLimEntFin.blockSignals(False)
        self.inpColchon.blockSignals(False)
        
        print(f"[SettingsView] Parametros normativos cargados")
    
    def get_parametros_generales(self) -> Dict[str, float]:
        """
        Obtiene los parámetros generales actuales.
        
        Returns:
            Diccionario con patrimonio_cop (valor en COP, no millones) y TRM
        """
        return {
            "patrimonio_cop": self.inpPatrimonio.value(),
            "trm": self.inpTRM.value()
        }
    
    def get_parametros_normativos(self) -> Dict[str, float]:
        """
        Obtiene los parámetros normativos actuales.
        
        Returns:
            Diccionario con los 5 parámetros normativos
        """
        return {
            "factor_ajuste": self.inpFactorAjuste.value(),
            "lim_endeud": self.inpLimEndeud.value(),
            "lim_sblc": self.inpLimSBLC.value(),
            "lim_entfin": self.inpLimEntFin.value(),
            "colchon": self.inpColchon.value()
        }
    
    def set_lineas_credito_model(self, model) -> None:
        """
        Establece el modelo de la tabla de líneas de crédito.
        
        Args:
            model: Modelo QAbstractTableModel con los datos
        """
        self.tblLineasCredito.setModel(model)
        
        # Reconfigurar el header después de establecer el modelo
        header = self.tblLineasCredito.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        print(f"[SettingsView] Modelo de lineas de credito establecido")
    
    def _apply_styles(self):
        """Aplica estilos CSS corporativos sobrios a la vista."""
        self.setStyleSheet("""
            /* QGroupBox - Estilo corporativo */
            QGroupBox {
                font-weight: 600;
                margin-top: 12px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px 12px 12px 12px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            
            /* Labels */
            QLabel {
                color: #333333;
            }
            
            /* Inputs */
            QLineEdit, QDoubleSpinBox {
                padding: 4px 6px;
                border: 1px solid #D6D6D6;
                border-radius: 6px;
            }
            
            QLineEdit:focus, QDoubleSpinBox:focus {
                border: 1px solid #0078D7;
            }
            
            /* Tabla */
            #tblLineasCredito {
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                gridline-color: #F0F0F0;
            }
            
            #tblLineasCredito::item:selected {
                background-color: #E3F2FD;
                color: #000000;
            }
            
            /* Botón Cargar archivo */
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 6px 14px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #005a9e;
            }
            
            QPushButton:pressed {
                background-color: #004578;
            }
        """)

