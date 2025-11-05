"""
Vista para el módulo de Configuración.
Interfaz de usuario para gestionar la configuración del sistema.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTabWidget, QPushButton, QGroupBox, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QCheckBox, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import Dict, Any


class SettingsView(QWidget):
    """
    Vista del módulo Settings.
    
    Responsabilidades:
    - Mostrar opciones de configuración
    - Permitir la edición de parámetros
    - Gestionar preferencias de usuario
    - Guardar y cargar configuraciones
    """
    
    # Señales personalizadas
    setting_changed = Signal(str, object)
    settings_saved = Signal()
    settings_reset = Signal()
    
    def __init__(self, parent: QWidget = None):
        """
        Inicializa la vista de configuración.
        
        Args:
            parent: Widget padre (opcional)
        """
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        
        print("[SettingsView] Vista de configuración inicializada")
    
    def _setup_ui(self) -> None:
        """
        Configura la interfaz de usuario.
        """
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título del módulo
        title_label = QLabel("⚙️ Configuraciones del Sistema")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Gestione los parámetros y preferencias del simulador")
        subtitle_label.setStyleSheet("color: #666666;")
        main_layout.addWidget(subtitle_label)
        
        main_layout.addSpacing(10)
        
        # Tabs de configuración
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_general_settings_tab(), "General")
        self.tab_widget.addTab(self._create_database_settings_tab(), "Base de Datos")
        self.tab_widget.addTab(self._create_appearance_settings_tab(), "Apariencia")
        self.tab_widget.addTab(self._create_advanced_settings_tab(), "Avanzado")
        
        main_layout.addWidget(self.tab_widget)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.btn_reset = QPushButton("🔄 Restaurar Valores Predeterminados")
        self.btn_reset.clicked.connect(self._on_reset_clicked)
        buttons_layout.addWidget(self.btn_reset)
        
        self.btn_save = QPushButton("💾 Guardar Configuración")
        self.btn_save.setObjectName("btnSave")
        self.btn_save.clicked.connect(self._on_save_clicked)
        buttons_layout.addWidget(self.btn_save)
        
        main_layout.addLayout(buttons_layout)
        
        # Aplicar estilos
        self._apply_styles()
    
    def _create_general_settings_tab(self) -> QWidget:
        """
        Crea la pestaña de configuración general.
        
        Returns:
            Widget con la configuración general
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Grupo: Configuración del Sistema
        group_system = QGroupBox("Configuración del Sistema")
        group_layout = QFormLayout(group_system)
        
        self.txt_empresa = QLineEdit("Banco XYZ S.A.")
        group_layout.addRow("Nombre de la Empresa:", self.txt_empresa)
        
        self.txt_nit = QLineEdit("900123456-7")
        group_layout.addRow("NIT:", self.txt_nit)
        
        self.combo_moneda = QComboBox()
        self.combo_moneda.addItems(["COP", "USD", "EUR"])
        group_layout.addRow("Moneda Base:", self.combo_moneda)
        
        layout.addWidget(group_system)
        
        # Grupo: Parámetros de Riesgo
        group_risk = QGroupBox("Parámetros de Riesgo")
        group_risk_layout = QFormLayout(group_risk)
        
        self.spin_fc_global = QSpinBox()
        self.spin_fc_global.setRange(0, 100)
        self.spin_fc_global.setValue(12)
        self.spin_fc_global.setSuffix(" %")
        group_risk_layout.addRow("Factor de Conversión (FC) Global:", self.spin_fc_global)
        
        self.spin_colchon = QSpinBox()
        self.spin_colchon.setRange(0, 50)
        self.spin_colchon.setValue(10)
        self.spin_colchon.setSuffix(" %")
        group_risk_layout.addRow("Colchón de Seguridad:", self.spin_colchon)
        
        layout.addWidget(group_risk)
        
        layout.addStretch()
        
        return tab
    
    def _create_database_settings_tab(self) -> QWidget:
        """
        Crea la pestaña de configuración de base de datos.
        
        Returns:
            Widget con la configuración de BD
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        group = QGroupBox("Configuración de Base de Datos")
        group_layout = QFormLayout(group)
        
        self.txt_db_path = QLineEdit("./data/simulador.db")
        group_layout.addRow("Ruta de BD:", self.txt_db_path)
        
        self.check_auto_backup = QCheckBox("Habilitar respaldo automático")
        self.check_auto_backup.setChecked(True)
        group_layout.addRow("", self.check_auto_backup)
        
        self.spin_backup_interval = QSpinBox()
        self.spin_backup_interval.setRange(1, 30)
        self.spin_backup_interval.setValue(7)
        self.spin_backup_interval.setSuffix(" días")
        group_layout.addRow("Intervalo de Respaldo:", self.spin_backup_interval)
        
        layout.addWidget(group)
        layout.addStretch()
        
        return tab
    
    def _create_appearance_settings_tab(self) -> QWidget:
        """
        Crea la pestaña de configuración de apariencia.
        
        Returns:
            Widget con la configuración de apariencia
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        group = QGroupBox("Configuración de Apariencia")
        group_layout = QFormLayout(group)
        
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Claro", "Oscuro", "Automático"])
        group_layout.addRow("Tema:", self.combo_theme)
        
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(8, 16)
        self.spin_font_size.setValue(10)
        self.spin_font_size.setSuffix(" pt")
        group_layout.addRow("Tamaño de Fuente:", self.spin_font_size)
        
        self.check_animations = QCheckBox("Habilitar animaciones")
        self.check_animations.setChecked(True)
        group_layout.addRow("", self.check_animations)
        
        layout.addWidget(group)
        layout.addStretch()
        
        return tab
    
    def _create_advanced_settings_tab(self) -> QWidget:
        """
        Crea la pestaña de configuración avanzada.
        
        Returns:
            Widget con la configuración avanzada
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        group = QGroupBox("Configuración Avanzada")
        group_layout = QFormLayout(group)
        
        self.check_debug_mode = QCheckBox("Habilitar modo de depuración")
        group_layout.addRow("", self.check_debug_mode)
        
        self.check_log_verbose = QCheckBox("Logs detallados")
        group_layout.addRow("", self.check_log_verbose)
        
        self.spin_cache_size = QSpinBox()
        self.spin_cache_size.setRange(10, 1000)
        self.spin_cache_size.setValue(100)
        self.spin_cache_size.setSuffix(" MB")
        group_layout.addRow("Tamaño de Caché:", self.spin_cache_size)
        
        layout.addWidget(group)
        layout.addStretch()
        
        return tab
    
    def _connect_signals(self) -> None:
        """
        Conecta las señales de los widgets.
        """
        # Las conexiones específicas se pueden agregar aquí según se necesiten
        pass
    
    def _on_save_clicked(self):
        """Handler para el botón Guardar."""
        print("[SettingsView] Guardando configuración...")
        
        # Emitir señal
        self.settings_saved.emit()
        
        # Mostrar mensaje de éxito
        QMessageBox.information(
            self,
            "Configuración Guardada",
            "La configuración se ha guardado exitosamente.",
            QMessageBox.Ok
        )
    
    def _on_reset_clicked(self):
        """Handler para el botón Restaurar."""
        reply = QMessageBox.question(
            self,
            "Restaurar Configuración",
            "¿Está seguro de que desea restaurar los valores predeterminados?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            print("[SettingsView] Restaurando valores predeterminados...")
            self.reset_to_defaults()
            self.settings_reset.emit()
    
    def load_settings(self, settings: Dict[str, Any]) -> None:
        """
        Carga las configuraciones en la interfaz.
        
        Args:
            settings: Diccionario con las configuraciones
        """
        print(f"[SettingsView] Cargando configuración: {len(settings)} parámetros")
        # Implementar lógica de carga según el diccionario
        pass
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Obtiene las configuraciones actuales de la interfaz.
        
        Returns:
            Diccionario con las configuraciones
        """
        settings = {
            "empresa": self.txt_empresa.text(),
            "nit": self.txt_nit.text(),
            "moneda_base": self.combo_moneda.currentText(),
            "fc_global": self.spin_fc_global.value(),
            "colchon": self.spin_colchon.value(),
            "db_path": self.txt_db_path.text(),
            "auto_backup": self.check_auto_backup.isChecked(),
            "backup_interval": self.spin_backup_interval.value(),
            "theme": self.combo_theme.currentText(),
            "font_size": self.spin_font_size.value(),
            "animations": self.check_animations.isChecked(),
            "debug_mode": self.check_debug_mode.isChecked(),
            "log_verbose": self.check_log_verbose.isChecked(),
            "cache_size": self.spin_cache_size.value(),
        }
        return settings
    
    def reset_to_defaults(self) -> None:
        """
        Restaura los valores predeterminados.
        """
        # General
        self.txt_empresa.setText("Banco XYZ S.A.")
        self.txt_nit.setText("900123456-7")
        self.combo_moneda.setCurrentText("COP")
        self.spin_fc_global.setValue(12)
        self.spin_colchon.setValue(10)
        
        # Base de Datos
        self.txt_db_path.setText("./data/simulador.db")
        self.check_auto_backup.setChecked(True)
        self.spin_backup_interval.setValue(7)
        
        # Apariencia
        self.combo_theme.setCurrentText("Claro")
        self.spin_font_size.setValue(10)
        self.check_animations.setChecked(True)
        
        # Avanzado
        self.check_debug_mode.setChecked(False)
        self.check_log_verbose.setChecked(False)
        self.spin_cache_size.setValue(100)
        
        print("[SettingsView] Valores predeterminados restaurados")
    
    def show_success_message(self, message: str) -> None:
        """
        Muestra un mensaje de éxito.
        
        Args:
            message: Mensaje a mostrar
        """
        QMessageBox.information(self, "Éxito", message, QMessageBox.Ok)
    
    def _apply_styles(self):
        """Aplica estilos CSS a la vista."""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            #btnSave {
                background-color: #0078D7;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            
            #btnSave:hover {
                background-color: #005a9e;
            }
            
            #btnSave:pressed {
                background-color: #004578;
            }
        """)

