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
from PySide6.QtGui import QFont, QDoubleValidator
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
    
    def __init__(self, parent: QWidget = None, settings_model=None):
        """
        Inicializa la vista de configuración.
        
        Args:
            parent: Widget padre (opcional)
            settings_model: Modelo compartido de configuración (opcional)
        """
        super().__init__(parent)
        
        # Referencia al modelo de configuración compartido
        self._settings_model = settings_model
        
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
            QGroupBox con TRM COP/USD y TRM EUR/USD
        """
        group = QGroupBox("Parámetros Generales")
        layout = QFormLayout(group)
        layout.setSpacing(8)
        
        # TRM Vigente del día COP/USD
        self.trm_cop_usd = QLineEdit()
        self.trm_cop_usd.setPlaceholderText("Ingrese TRM COP/USD")
        validator_cop = QDoubleValidator(0.0, 999999.0, 6)
        validator_cop.setNotation(QDoubleValidator.StandardNotation)
        self.trm_cop_usd.setValidator(validator_cop)
        self.trm_cop_usd.setMinimumWidth(200)
        layout.addRow("TRM Vigente del día (COP/USD):", self.trm_cop_usd)
        
        # TRM Vigente del día COP/EUR
        self.trm_cop_eur = QLineEdit()
        self.trm_cop_eur.setPlaceholderText("Ingrese TRM COP/EUR")
        validator_eur = QDoubleValidator(0.0, 999999.0, 6)
        validator_eur.setNotation(QDoubleValidator.StandardNotation)
        self.trm_cop_eur.setValidator(validator_eur)
        self.trm_cop_eur.setMinimumWidth(200)
        layout.addRow("TRM Vigente del día (COP/EUR):", self.trm_cop_eur)
        
        return group
    
    def _create_parametros_normativos(self) -> QGroupBox:
        """
        Crea el bloque de Parámetros Normativos.
        
        Returns:
            QGroupBox con parámetros normativos
        """
        group = QGroupBox("Parámetros Normativos")
        layout = QFormLayout(group)
        layout.setSpacing(8)
        
        # Límite máx. endeudamiento individual (%)
        self.inpLimEndeud = QDoubleSpinBox()
        self.inpLimEndeud.setRange(0, 100)
        self.inpLimEndeud.setValue(10)
        self.inpLimEndeud.setDecimals(1)
        self.inpLimEndeud.setSuffix(" %")
        layout.addRow("Límite máx. endeudamiento individual (%):", self.inpLimEndeud)
        
        # Límite máx. concentración entidades financieras (%)
        self.inpLimEntFin = QDoubleSpinBox()
        self.inpLimEntFin.setRange(0, 100)
        self.inpLimEntFin.setValue(30)
        self.inpLimEntFin.setDecimals(1)
        self.inpLimEntFin.setSuffix(" %")
        layout.addRow("Límite máx. concentración entidades financieras (%):", self.inpLimEntFin)
        
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
                "fecha pt última actualización": "Fecha PT última actualización",
                "fecha pt ultima actualizacion": "Fecha PT última actualización",
                "patrimonio técnico": "Patrimonio técnico",
                "patrimonio tecnico": "Patrimonio técnico",
                "lll 25% (cop)": "LLL 25% (COP)",
                "lll 25% (eur)": "LLL 25% (EUR)",
                "eur (mm)": "EUR (MM)",
                "cop (mm)": "COP (MM)",
            }
            
            # Mapear columnas según alias (insensible a mayúsculas/minúsculas)
            df.rename(columns=lambda c: alias.get(c.lower(), c), inplace=True)
            print(f"   ✓ Columnas después de mapeo: {list(df.columns)}")
            
            # Columnas esperadas (mínimas) - ya NO incluye "Monto (COP)"
            columnas_esperadas = ["NIT", "Contraparte", "Grupo Conectado de Contrapartes", "COP (MM)"]
            
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
            
            # 🔹 Función auxiliar para limpiar y convertir valores numéricos en MM (millones)
            def _to_mm(series: pd.Series) -> pd.Series:
                """
                Limpia y convierte una serie a valores numéricos en MM (millones).
                Mantiene los valores como están (en millones), NO multiplica.
                """
                return (series.astype(str).str.strip()
                        .str.replace(r"[^\d,.\-]", "", regex=True)
                        .str.replace(",", "", regex=False)
                        .str.replace(" ", "", regex=False)
                        .pipe(pd.to_numeric, errors="coerce").fillna(0))
            
            # 🔹 Procesar columnas numéricas (mantener en millones)
            if "Patrimonio técnico" in df.columns:
                df["Patrimonio técnico"] = _to_mm(df["Patrimonio técnico"])
                print(f"   ✓ Patrimonio técnico limpiado (MM)")
            
            if "LLL 25% (COP)" in df.columns:
                df["LLL 25% (COP)"] = _to_mm(df["LLL 25% (COP)"])
                print(f"   ✓ LLL 25% (COP) limpiado (MM)")
            
            if "EUR (MM)" in df.columns:
                df["EUR (MM)"] = _to_mm(df["EUR (MM)"])
                print(f"   ✓ EUR (MM) limpiado (MM)")
            
            if "COP (MM)" in df.columns:
                df["COP (MM)"] = _to_mm(df["COP (MM)"])
                print(f"   ✓ COP (MM) limpiado (MM)")
            
            # 🔹 Calcular columnas dinámicas basadas en TRM COP/EUR
            if self._settings_model:
                trm_cop_eur = self._settings_model.trm_cop_eur()
                
                # Calcular LLL 25% (EUR) solo si tenemos TRM COP/EUR
                if "LLL 25% (COP)" in df.columns:
                    if trm_cop_eur and trm_cop_eur > 0:
                        df["LLL 25% (EUR)"] = df["LLL 25% (COP)"] / float(trm_cop_eur)
                        print(f"   ✓ LLL 25% (EUR) calculado usando TRM COP/EUR = {trm_cop_eur:,.6f}")
                    else:
                        df["LLL 25% (EUR)"] = None
                        print(f"   ⚠️  LLL 25% (EUR) no calculado (falta TRM COP/EUR)")
                
                # Calcular COP (MM) solo si tenemos TRM COP/EUR y EUR (MM)
                if "EUR (MM)" in df.columns:
                    if trm_cop_eur and trm_cop_eur > 0:
                        df["COP (MM)"] = df["EUR (MM)"] * float(trm_cop_eur)
                        print(f"   ✓ COP (MM) calculado usando TRM COP/EUR = {trm_cop_eur:,.6f}")
                    else:
                        # Si no hay TRM, mantener COP (MM) como está en el archivo
                        print(f"   ⚠️  COP (MM) se mantiene como está en archivo (falta TRM COP/EUR)")
            else:
                print(f"   ⚠️  Modelo no disponible, columnas dinámicas no calculadas")
            
            # 🔹 Limpiar filas sin NIT o Contraparte
            filas_antes = len(df)
            df = df.dropna(subset=["NIT", "Contraparte"])
            filas_despues = len(df)
            
            if filas_antes > filas_despues:
                print(f"   ⚠️  {filas_antes - filas_despues} filas eliminadas por NIT o Contraparte vacío")
            
            # Guardar el DataFrame temporalmente en la vista
            self.df_lineas_credito = df
            print(f"   ✓ DataFrame guardado en memoria ({len(df)} filas)")
            
            # Guardar el DataFrame en el modelo compartido (si existe)
            if self._settings_model:
                self._settings_model.set_lineas_credito(df)
                print(f"   ✓ DataFrame guardado en SettingsModel")
            
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
        import pandas as pd
        
        print(f"[SettingsView] Mostrando {len(df)} líneas de crédito en la tabla...")
        
        # Determinar columnas a mostrar (orden sugerido según requerimientos)
        columnas_orden = ["NIT", "Contraparte", "Grupo Conectado de Contrapartes", 
                         "Fecha PT última actualización", "Patrimonio técnico",
                         "LLL 25% (COP)", "LLL 25% (EUR)", "EUR (MM)", "COP (MM)"]
        
        # Filtrar solo las que existen en el DataFrame
        columnas_a_mostrar = [col for col in columnas_orden if col in df.columns]
        
        # Limpiar tabla
        self.tblLineasCredito.setRowCount(0)
        self.tblLineasCredito.setColumnCount(len(columnas_a_mostrar))
        
        # Configurar encabezados (abreviar nombres largos)
        headers_display = []
        for col in columnas_a_mostrar:
            if col == "Grupo Conectado de Contrapartes":
                headers_display.append("Grupo")
            elif col == "Fecha PT última actualización":
                headers_display.append("Fecha PT")
            elif col == "Patrimonio técnico":
                headers_display.append("Patrimonio Téc.")
            else:
                headers_display.append(col)
        
        self.tblLineasCredito.setHorizontalHeaderLabels(headers_display)
        
        # Insertar filas
        for i, row in df.iterrows():
            self.tblLineasCredito.insertRow(i)
            
            for j, col in enumerate(columnas_a_mostrar):
                valor = row[col]
                
                # Formatear según tipo de dato
                if col == "NIT":
                    texto = str(valor)
                elif col in ["Contraparte", "Grupo Conectado de Contrapartes", "Fecha PT última actualización"]:
                    texto = str(valor) if pd.notna(valor) else ""
                elif col in ["Patrimonio técnico", "LLL 25% (COP)", "EUR (MM)", "COP (MM)"]:
                    # Formatear valores en millones (MM)
                    if pd.notna(valor) and valor is not None:
                        texto = f"{float(valor):,.2f} MM"
                    else:
                        texto = "—"
                elif col in ["LLL 25% (EUR)"]:
                    # Formatear valores en EUR (también en MM)
                    if pd.notna(valor) and valor is not None:
                        texto = f"{float(valor):,.2f} MM €"
                    else:
                        texto = "—"
                else:
                    texto = str(valor) if pd.notna(valor) else ""
                
                self.tblLineasCredito.setItem(i, j, QTableWidgetItem(texto))
        
        # Ajustar columnas para distribución proporcional
        header = self.tblLineasCredito.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Set column widths proporcionales
        total_width = self.tblLineasCredito.width()
        num_cols = len(columnas_a_mostrar)
        if num_cols <= 4:
            # Solo columnas básicas: anchos fijos
            header.resizeSection(0, 120)  # NIT
            header.resizeSection(1, 200)  # Contraparte
            header.resizeSection(2, 150)  # Grupo
            header.resizeSection(3, 150)  # Monto
        else:
            # Con columnas adicionales: distribución más uniforme
            for col_idx in range(num_cols):
                header.resizeSection(col_idx, total_width // num_cols)
        
        print(f"   ✓ Tabla actualizada con {len(df)} filas y {num_cols} columnas")
    
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
    
    def load_parametros_normativos(self, lim_endeud: float, lim_entfin: float, colchon: float) -> None:
        """
        Carga los parámetros normativos en la interfaz.
        
        Args:
            lim_endeud: Límite máx. endeudamiento individual (%)
            lim_entfin: Límite máx. concentración ent. financieras (%)
            colchon: Colchón de seguridad (%)
        """
        self.inpLimEndeud.blockSignals(True)
        self.inpLimEntFin.blockSignals(True)
        self.inpColchon.blockSignals(True)
        
        self.inpLimEndeud.setValue(lim_endeud)
        self.inpLimEntFin.setValue(lim_entfin)
        self.inpColchon.setValue(colchon)
        
        self.inpLimEndeud.blockSignals(False)
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
            Diccionario con los 3 parámetros normativos
        """
        return {
            "lim_endeud": self.inpLimEndeud.value(),
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

