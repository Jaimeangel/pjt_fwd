"""
Vista para el módulo de Configuración.
Interfaz de usuario para gestionar la configuración del sistema.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QFormLayout,
    QLineEdit, QDoubleSpinBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox
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
        
        # Almacenar DataFrame de líneas de crédito
        self.df_lineas_credito = None
        
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
        self.btnCargarLineas.clicked.connect(self.cargar_csv_lineas_credito)
        header_layout.addWidget(self.btnCargarLineas)
        
        layout.addLayout(header_layout)
        
        # Tabla de líneas de crédito (QTableWidget para manejo directo)
        self.tblLineasCredito = QTableWidget()
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
    
    def cargar_csv_lineas_credito(self):
        """
        Carga el archivo CSV de líneas de crédito y muestra los datos en la tabla.
        Versión robusta que soporta múltiples codificaciones y variaciones en encabezados.
        
        Reglas:
        - CSV delimitado por ';'
        - Columnas requeridas: NIT, Contraparte, Grupo Conectado de Contrapartes, Monto (COP)
        - NIT: eliminar guiones "-"
        - Monto (COP): está en miles de millones → multiplicar por 1_000_000_000
        - Soporta UTF-8, UTF-8 con BOM, y Latin-1
        - Normaliza nombres de columnas (elimina BOM, NBSP, espacios extras)
        - Reconoce variaciones en nombres de columnas (case-insensitive)
        """
        print("[SettingsView] Abriendo dialogo para cargar lineas de credito...")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de líneas de crédito",
            "",
            "Archivos CSV (*.csv);;Todos los archivos (*)"
        )
        
        if not file_path:
            print("[SettingsView] Carga cancelada por el usuario")
            return
        
        try:
            import pandas as pd
            import re
            
            print(f"[SettingsView] Cargando archivo: {file_path}")
            
            # 🔹 Función de lectura robusta
            def leer_csv_robusto(path):
                """
                Lee un CSV intentando múltiples codificaciones.
                Soporta UTF-8, UTF-8 con BOM, y Latin-1.
                """
                df = None
                # Intentar con utf-8-sig (maneja BOM automáticamente) y latin1
                for enc in ("utf-8-sig", "latin1"):
                    try:
                        print(f"      Intentando con codificación: {enc}")
                        df = pd.read_csv(
                            path,
                            sep=";",
                            engine="python",
                            encoding=enc,
                            dtype=str,
                            keep_default_na=False  # Evita convertir strings vacíos a NaN
                        )
                        print(f"      ✓ Lectura exitosa con {enc}")
                        break
                    except Exception as e:
                        print(f"      ✗ Falló con {enc}: {e}")
                        df = None
                
                if df is None:
                    raise ValueError("No se pudo leer el CSV con ninguna codificación estándar (utf-8-sig o latin1).")
                
                # 🔹 Normalizar nombres de columnas
                def normalizar(c):
                    """Normaliza un nombre de columna eliminando caracteres especiales."""
                    c = c.replace("\ufeff", "")        # Eliminar BOM (Byte Order Mark)
                    c = c.replace("\xa0", " ")         # Eliminar NBSP (Non-Breaking Space)
                    c = re.sub(r"\s+", " ", c).strip() # Colapsar múltiples espacios en uno
                    return c
                
                df.columns = [normalizar(c) for c in df.columns]
                print(f"      ✓ Columnas normalizadas: {list(df.columns)}")
                
                return df
            
            # Leer archivo con robustez
            df = leer_csv_robusto(file_path)
            
            # 🔹 Normalizar headers usando alias (case-insensitive)
            alias = {
                "nit": "NIT",
                "contraparte": "Contraparte",
                "grupo conectado de contrapartes": "Grupo Conectado de Contrapartes",
                "monto (cop)": "Monto (COP)",
                "monto(cop)": "Monto (COP)",  # Sin espacio antes del paréntesis
                "monto": "Monto (COP)",        # Solo "Monto"
            }
            
            # Mapear columnas según alias (insensible a mayúsculas/minúsculas)
            df.rename(columns=lambda c: alias.get(c.lower(), c), inplace=True)
            print(f"   ✓ Columnas después de mapeo: {list(df.columns)}")
            
            # Columnas esperadas
            columnas_esperadas = ["NIT", "Contraparte", "Grupo Conectado de Contrapartes", "Monto (COP)"]
            
            # Validar columnas requeridas
            faltantes = [col for col in columnas_esperadas if col not in df.columns]
            if faltantes:
                print(f"   ❌ Error: Columnas faltantes en el archivo")
                print(f"      Faltantes: {faltantes}")
                print(f"      Detectadas: {list(df.columns)}")
                QMessageBox.warning(
                    self,
                    "Error de formato",
                    f"El archivo no contiene las columnas requeridas:\n{', '.join(faltantes)}\n\n"
                    f"Columnas detectadas: {', '.join(df.columns)}"
                )
                return
            
            print(f"   ✓ Columnas validadas correctamente")
            print(f"   → Filas leídas: {len(df)}")
            
            # 🔹 Limpiar y normalizar la columna NIT (quitar guiones)
            df["NIT"] = df["NIT"].str.replace("-", "", regex=False).str.strip()
            print(f"   ✓ NITs normalizados (guiones eliminados)")
            
            # 🔹 Convertir monto de miles de millones a valor real (COP)
            df["Monto (COP)"] = pd.to_numeric(df["Monto (COP)"], errors="coerce") * 1_000_000_000
            print(f"   ✓ Montos convertidos (miles de millones → COP reales)")
            
            # 🔹 Limpiar filas sin NIT o Contraparte
            filas_antes = len(df)
            df = df.dropna(subset=["NIT", "Contraparte"])
            filas_despues = len(df)
            
            if filas_antes > filas_despues:
                print(f"   ⚠️  {filas_antes - filas_despues} filas eliminadas por NIT o Contraparte vacío")
            
            # Guardar el DataFrame temporalmente
            self.df_lineas_credito = df
            print(f"   ✓ DataFrame guardado en memoria ({len(df)} filas)")
            
            # Mostrar los datos en la tabla
            self.mostrar_lineas_credito(df)
            
            # Mensaje de éxito
            QMessageBox.information(
                self,
                "Carga exitosa",
                f"El archivo de líneas de crédito fue cargado correctamente.\n\n"
                f"Líneas de crédito cargadas: {len(df)}"
            )
            
            print(f"   ✅ Carga completada exitosamente")
        
        except Exception as e:
            print(f"   ❌ Error al cargar archivo: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error al cargar",
                f"Ocurrió un error al leer el archivo:\n{str(e)}"
            )
    
    def mostrar_lineas_credito(self, df):
        """
        Muestra los datos del DataFrame de líneas de crédito en la tabla.
        
        Args:
            df: DataFrame de pandas con las líneas de crédito
        """
        print(f"[SettingsView] Mostrando {len(df)} líneas de crédito en la tabla...")
        
        # Limpiar tabla
        self.tblLineasCredito.setRowCount(0)
        self.tblLineasCredito.setColumnCount(4)
        
        # Configurar encabezados
        self.tblLineasCredito.setHorizontalHeaderLabels(["NIT", "Contraparte", "Grupo", "Monto (COP)"])
        
        # Insertar filas
        for i, row in df.iterrows():
            self.tblLineasCredito.insertRow(i)
            
            # NIT (string)
            self.tblLineasCredito.setItem(i, 0, QTableWidgetItem(str(row["NIT"])))
            
            # Contraparte (string)
            self.tblLineasCredito.setItem(i, 1, QTableWidgetItem(str(row["Contraparte"])))
            
            # Grupo Conectado (string)
            self.tblLineasCredito.setItem(i, 2, QTableWidgetItem(str(row["Grupo Conectado de Contrapartes"])))
            
            # Monto (COP) - formato numérico con separadores de miles
            monto_value = float(row["Monto (COP)"])
            monto_formatted = f"{monto_value:,.2f}"
            self.tblLineasCredito.setItem(i, 3, QTableWidgetItem(monto_formatted))
        
        # Ajustar columnas para distribución uniforme
        header = self.tblLineasCredito.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        print(f"   ✓ Tabla actualizada con {len(df)} filas")
    
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
        [OBSOLETO] Este método ya no es necesario.
        
        La tabla de líneas de crédito ahora usa QTableWidget y se actualiza
        directamente desde el método cargar_csv_lineas_credito().
        
        Args:
            model: Modelo QAbstractTableModel (ignorado)
        """
        print("[SettingsView] set_lineas_credito_model está obsoleto - use cargar_csv_lineas_credito()")
        pass
    
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

