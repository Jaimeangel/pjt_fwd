"""
Modelo de tabla Qt para simulaciones (editable).
"""

from typing import Any, List, Dict, Optional
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex


class SimulationsTableModel(QAbstractTableModel):
    """
    Modelo de tabla Qt para simulaciones (editable).
    
    Responsabilidades:
    - Presentar simulaciones en QTableView
    - Permitir edición de celdas específicas
    - Validar datos editados
    - Sincronizar con SimulationsModel
    """
    
    # Headers de columnas
    HEADERS = [
        "Cliente",
        "Punta Cli",
        "Punta Emp",
        "Nominal USD",
        "Fec Sim",
        "Fec Venc",
        "Plazo",
        "Spot",
        "Puntos",
        "Tasa Fwd",
        "Tasa IBR",
        "Derecho",
        "Obligación",
        "Fair Value"
    ]
    
    # Índices de columnas editables
    # Editables: Punta Cli, Nominal USD, Fec Venc, Spot, Puntos
    EDITABLE_COLUMNS = [1, 3, 5, 7, 8]
    
    def __init__(self, simulations_model=None, parent=None, ibr_resolver=None):
        """
        Inicializa el modelo de tabla de simulaciones.
        
        Args:
            simulations_model: Instancia de SimulationsModel
            parent: Widget padre
            ibr_resolver: Función callback (dias: int) -> float que retorna tasa IBR en %
        """
        super().__init__(parent)
        self._simulations_model = simulations_model
        self._ibr_resolver = ibr_resolver  # Callback para resolver tasa IBR
        
        # Iniciar con tabla vacía
        self._rows = []
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Retorna el número de filas (simulaciones).
        
        Args:
            parent: Índice padre
            
        Returns:
            Cantidad de simulaciones
        """
        if parent.isValid():
            return 0
        return len(self._rows)
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Retorna el número de columnas.
        
        Args:
            parent: Índice padre
            
        Returns:
            Cantidad de columnas
        """
        if parent.isValid():
            return 0
        return len(self.HEADERS)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """
        Retorna el dato para una celda específica.
        
        Args:
            index: Índice de la celda
            role: Rol de los datos
            
        Returns:
            Dato según el rol
        """
        if not index.isValid():
            return None
        
        if index.row() >= len(self._rows) or index.row() < 0:
            return None
        
        if index.column() >= len(self.HEADERS) or index.column() < 0:
            return None
        
        row_data = self._rows[index.row()]
        col = index.column()
        
        # DisplayRole: texto a mostrar
        if role == Qt.DisplayRole:
            if col == 0:  # Cliente
                return row_data.get("cliente", "")
            elif col == 1:  # Punta Cli
                return row_data.get("punta_cli", "")
            elif col == 2:  # Punta Emp
                return row_data.get("punta_emp", "")
            elif col == 3:  # Nominal USD
                nominal = row_data.get("nominal_usd")
                if nominal is None:
                    return "—"
                return f"{nominal:,.2f}"
            elif col == 4:  # Fec Sim
                fec_sim = row_data.get("fec_sim")
                return fec_sim if fec_sim else "—"
            elif col == 5:  # Fec Venc
                fec_venc = row_data.get("fec_venc")
                return fec_venc if fec_venc else "—"
            elif col == 6:  # Plazo
                plazo = row_data.get("plazo")
                if plazo is None:
                    return "—"
                return f"{plazo} días"
            elif col == 7:  # Spot
                spot = row_data.get("spot")
                if spot is None:
                    return "—"
                return f"{spot:,.2f}"
            elif col == 8:  # Puntos
                puntos = row_data.get("puntos")
                if puntos is None:
                    return "—"
                return f"{puntos:,.2f}"
            elif col == 9:  # Tasa Fwd
                tasa_fwd = row_data.get("tasa_fwd")
                if tasa_fwd is None:
                    return "—"
                return f"{tasa_fwd:,.2f}"
            elif col == 10:  # Tasa IBR
                tasa_ibr = row_data.get("tasa_ibr")
                if tasa_ibr is None:
                    return "—"
                return f"{tasa_ibr * 100:.2f}%"
            elif col == 11:  # Derecho
                derecho = row_data.get("derecho")
                if derecho is None:
                    return "—"
                return f"$ {derecho:,.2f}"
            elif col == 12:  # Obligación
                obligacion = row_data.get("obligacion")
                if obligacion is None:
                    return "—"
                return f"$ {obligacion:,.2f}"
            elif col == 13:  # Fair Value
                fair_value = row_data.get("fair_value")
                if fair_value is None:
                    return "—"
                return f"$ {fair_value:,.2f}"
        
        # EditRole: valor crudo para edición
        elif role == Qt.EditRole:
            if col == 1:  # Punta Cli
                return row_data.get("punta_cli", "Compra")
            elif col == 3:  # Nominal USD
                value = row_data.get("nominal_usd")
                return value if value is not None else 0.0
            elif col == 5:  # Fec Venc
                return row_data.get("fec_venc", "")
            elif col == 7:  # Spot
                value = row_data.get("spot")
                return value if value is not None else 0.0
            elif col == 8:  # Puntos
                value = row_data.get("puntos")
                return value if value is not None else 0.0
        
        # TextAlignmentRole: alineación de texto
        elif role == Qt.TextAlignmentRole:
            # Centrar todo el contenido para mejor estética
            return Qt.AlignCenter
        
        # BackgroundRole: color de fondo para celdas calculadas
        elif role == Qt.BackgroundRole:
            # Celdas calculadas (no editables) con fondo ligeramente gris
            if col in [2, 6, 9, 10, 11, 12, 13]:  # Punta Emp, Plazo, Tasa Fwd, Tasa IBR, Derecho, Obligación, Fair Value
                from PySide6.QtGui import QColor
                return QColor(245, 245, 245)  # Gris muy claro
        
        return None
    
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """
        Establece el valor de una celda (edición).
        
        Args:
            index: Índice de la celda
            value: Nuevo valor
            role: Rol
            
        Returns:
            True si se actualizó correctamente
        """
        if not index.isValid():
            return False
        
        if role != Qt.EditRole:
            return False
        
        if index.row() >= len(self._rows) or index.row() < 0:
            return False
        
        col = index.column()
        
        # Verificar si la columna es editable
        if col not in self.EDITABLE_COLUMNS:
            return False
        
        row_data = self._rows[index.row()]
        
        try:
            # Actualizar según la columna
            if col == 1:  # Punta Cli
                punta = str(value).strip()
                if punta in ["Compra", "Venta"]:
                    row_data["punta_cli"] = punta
                    # Auto-actualizar Punta Emp
                    row_data["punta_emp"] = "Venta" if punta == "Compra" else "Compra"
                    # Emitir cambio también para Punta Emp
                    punta_emp_index = self.index(index.row(), 2)
                    self.dataChanged.emit(punta_emp_index, punta_emp_index, [Qt.DisplayRole])
                    # Recalcular Derecho, Obligación y Fair Value
                    self._recalc_row(index.row())
                else:
                    return False
            elif col == 3:  # Nominal USD
                nominal = float(value) if value else 0.0
                if nominal >= 0:
                    row_data["nominal_usd"] = nominal
                    # Recalcular Derecho, Obligación y Fair Value
                    self._recalc_row(index.row())
                else:
                    return False
            elif col == 5:  # Fec Venc
                row_data["fec_venc"] = str(value)
                # Calcular Plazo automáticamente (esto también actualiza Tasa IBR)
                self._recalculate_plazo(index.row())
                # Recalcular Derecho, Obligación y Fair Value
                self._recalc_row(index.row())
            elif col == 7:  # Spot
                spot = float(value) if value else 0.0
                if spot >= 0:
                    row_data["spot"] = spot
                    # Recalcular todo (incluye Tasa Forward, Derecho, Obligación, Fair Value)
                    self._recalc_row(index.row())
                else:
                    return False
            elif col == 8:  # Puntos
                puntos = float(value) if value else 0.0
                row_data["puntos"] = puntos
                # Recalcular todo (incluye Tasa Forward, Derecho, Obligación, Fair Value)
                self._recalc_row(index.row())
            else:
                return False
            
            # Emitir señal de cambio de datos
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
            
        except (ValueError, TypeError):
            return False
    
    def _recalculate_tasa_fwd(self, row: int) -> None:
        """
        Recalcula la Tasa Forward cuando cambian Spot o Puntos.
        
        Fórmula: Tasa Forward = Spot + Puntos (suma directa)
        
        Args:
            row: Índice de la fila
        """
        if 0 <= row < len(self._rows):
            row_data = self._rows[row]
            spot = float(row_data.get("spot", 0) or 0)
            puntos = float(row_data.get("puntos", 0) or 0)
            
            # Calcular Tasa Forward (nueva fórmula: suma directa)
            tasa_fwd = spot + puntos
            row_data["tasa_fwd"] = tasa_fwd
            
            # Emitir cambio para la columna Tasa Fwd (col 9)
            tasa_fwd_index = self.index(row, 9)
            self.dataChanged.emit(tasa_fwd_index, tasa_fwd_index, [Qt.DisplayRole])
    
    def _recalc_row(self, r: int) -> None:
        """
        Recalcula Tasa Forward, Derecho, Obligación y Fair Value de la fila r
        con base en Punta, Spot, Puntos, Nominal, Plazo y Tasa IBR (%).
        No redondea internamente; solo formatea en display.
        
        Fórmulas:
        - Forward = Spot + Puntos
        - df = 1 + (IBR%/100) * (Plazo/360)
        - Si Punta Cliente = "Compra":
            Derecho = (Spot + Puntos)/df * Nominal
            Obligación = Spot/df * Nominal
        - Si Punta Cliente = "Venta":
            Derecho = Spot/df * Nominal
            Obligación = (Spot + Puntos)/df * Nominal
        - Fair Value = Derecho - Obligación
        
        Args:
            r: Índice de la fila
        """
        if not (0 <= r < len(self._rows)):
            return
        
        row_data = self._rows[r]
        
        # Leer valores seguros (default 0 si None)
        punta_cliente = row_data.get("punta_cli", "Compra")
        spot = float(row_data.get("spot", 0) or 0)
        puntos = float(row_data.get("puntos", 0) or 0)
        nominal = float(row_data.get("nominal_usd", 0) or 0)
        plazo = row_data.get("plazo")
        tasa_ibr_decimal = row_data.get("tasa_ibr")  # Ya está en decimal
        
        # Calcular Tasa Forward
        tasa_fwd = spot + puntos
        row_data["tasa_fwd"] = tasa_fwd
        
        # Validar insumos para cálculo de df
        if plazo is None or tasa_ibr_decimal is None or plazo < 0:
            # Sin datos suficientes, setear valores a 0
            row_data["derecho"] = 0.0
            row_data["obligacion"] = 0.0
            row_data["fair_value"] = 0.0
        else:
            # Convertir tasa IBR de decimal a porcentaje para el cálculo
            ibr_pct = tasa_ibr_decimal * 100.0
            
            # Calcular factor de descuento
            # df = 1 + (IBR%/100) * (Plazo/360)
            df = 1.0 + (ibr_pct / 100.0) * (plazo / 360.0)
            
            # Validar df
            if df <= 0:
                row_data["derecho"] = 0.0
                row_data["obligacion"] = 0.0
                row_data["fair_value"] = 0.0
            else:
                # Calcular Derecho y Obligación según la punta
                if punta_cliente == "Compra":
                    # Derecho = (Spot + Puntos)/df * Nominal
                    derecho = (spot + puntos) / df * nominal
                    # Obligación = Spot/df * Nominal
                    obligacion = spot / df * nominal
                else:  # "Venta"
                    # Derecho = Spot/df * Nominal
                    derecho = spot / df * nominal
                    # Obligación = (Spot + Puntos)/df * Nominal
                    obligacion = (spot + puntos) / df * nominal
                
                # Fair Value = Derecho - Obligación
                fair_value = derecho - obligacion
                
                # Guardar valores
                row_data["derecho"] = derecho
                row_data["obligacion"] = obligacion
                row_data["fair_value"] = fair_value
        
        # Emitir cambios para las columnas calculadas
        # Col 9: Tasa Fwd, Col 11: Derecho, Col 12: Obligación, Col 13: Fair Value
        for col in [9, 11, 12, 13]:
            idx = self.index(r, col)
            self.dataChanged.emit(idx, idx, [Qt.DisplayRole])
    
    def _recalculate_plazo(self, row: int) -> None:
        """
        Recalcula el Plazo cuando cambia la Fecha de Vencimiento.
        También actualiza la Tasa IBR basándose en el plazo calculado.
        
        Plazo = días entre Fecha Vencimiento y hoy
        
        Args:
            row: Índice de la fila
        """
        from datetime import date, datetime
        
        if 0 <= row < len(self._rows):
            row_data = self._rows[row]
            fecha_venc_str = row_data.get("fec_venc")
            
            if fecha_venc_str:
                try:
                    # Parsear la fecha
                    if isinstance(fecha_venc_str, str):
                        # Formato: YYYY-MM-DD
                        fecha_venc = datetime.strptime(fecha_venc_str, "%Y-%m-%d").date()
                    elif hasattr(fecha_venc_str, 'toPyDate'):
                        # QDate
                        fecha_venc = fecha_venc_str.toPyDate()
                    else:
                        fecha_venc = fecha_venc_str
                    
                    # Calcular plazo
                    hoy = date.today()
                    plazo_dias = (fecha_venc - hoy).days
                    
                    # Evitar plazos negativos
                    plazo_dias = plazo_dias if plazo_dias >= 0 else 0
                    row_data["plazo"] = plazo_dias
                    
                    # Actualizar Tasa IBR usando el callback
                    if self._ibr_resolver and plazo_dias is not None:
                        tasa_ibr_pct = self._ibr_resolver(plazo_dias)
                        row_data["tasa_ibr"] = tasa_ibr_pct / 100.0  # Guardar como decimal
                        
                        # Emitir cambio para la columna Tasa IBR (col 10)
                        ibr_index = self.index(row, 10)
                        self.dataChanged.emit(ibr_index, ibr_index, [Qt.DisplayRole])
                    
                    # Emitir cambio para la columna Plazo (col 6)
                    plazo_index = self.index(row, 6)
                    self.dataChanged.emit(plazo_index, plazo_index, [Qt.DisplayRole])
                    
                except (ValueError, AttributeError):
                    row_data["plazo"] = None
                    row_data["tasa_ibr"] = None
            else:
                row_data["plazo"] = None
                row_data["tasa_ibr"] = None
    
    def set_ibr_resolver(self, resolver_func) -> None:
        """
        Establece la función callback para resolver tasas IBR.
        
        Args:
            resolver_func: Función (dias: int) -> float que retorna tasa IBR en %
        """
        self._ibr_resolver = resolver_func
    
    def recalc_row(self, r: int) -> None:
        """
        Método público para recalcular una fila específica.
        
        Este método es llamado externamente (por el controller) cuando
        se actualiza la Tasa IBR o cualquier otro valor que requiera
        recalcular Derecho, Obligación y Fair Value.
        
        Args:
            r: Índice de la fila (0-based)
        """
        self._recalc_row(r)
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Retorna flags de la celda.
        
        Args:
            index: Índice de la celda
            
        Returns:
            Flags según si la columna es editable
        """
        if not index.isValid():
            return Qt.NoItemFlags
        
        base_flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
        # Si la columna es editable, agregar flag de edición
        if index.column() in self.EDITABLE_COLUMNS:
            return base_flags | Qt.ItemIsEditable
        
        return base_flags
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole) -> Any:
        """
        Retorna datos del header.
        
        Args:
            section: Número de columna/fila
            orientation: Horizontal o Vertical
            role: Rol de los datos
            
        Returns:
            Nombre de columna o número de fila
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if 0 <= section < len(self.HEADERS):
                    return self.HEADERS[section]
            elif orientation == Qt.Vertical:
                return str(section + 1)  # Número de fila (1-based)
        
        return None
    
    def set_simulations_model(self, simulations_model) -> None:
        """
        Establece el modelo de datos de simulaciones.
        
        Args:
            simulations_model: Instancia de SimulationsModel
        """
        self._simulations_model = simulations_model
        self.refresh()
    
    def refresh(self) -> None:
        """Refresca toda la tabla desde el modelo de datos."""
        self.beginResetModel()
        # Aquí se sincronizaría con self._simulations_model.all()
        # Por ahora mantenemos los datos dummy
        self.endResetModel()
    
    def add_row(self, row_data: Optional[Dict[str, Any]] = None, cliente_nombre: str = "") -> None:
        """
        Agrega una nueva fila a la tabla.
        
        Args:
            row_data: Datos de la fila (o None para fila vacía)
            cliente_nombre: Nombre del cliente seleccionado
        """
        from datetime import date
        
        row_count = len(self._rows)
        self.beginInsertRows(QModelIndex(), row_count, row_count)
        
        if row_data:
            self._rows.append(row_data)
        else:
            # Fila nueva con datos por defecto
            fecha_hoy = date.today().strftime("%Y-%m-%d")
            self._rows.append({
                "cliente": cliente_nombre,
                "punta_cli": "Compra",
                "punta_emp": "Venta",
                "nominal_usd": 0.0,
                "fec_sim": fecha_hoy,
                "fec_venc": None,
                "plazo": None,
                "spot": 0.0,
                "puntos": 0.0,
                "tasa_fwd": 0.0,
                "tasa_ibr": None,
                "derecho": None,
                "obligacion": None,
                "fair_value": None
            })
        
        self.endInsertRows()
    
    def remove_rows(self, rows: List[int]) -> bool:
        """
        Elimina múltiples filas.
        
        Args:
            rows: Lista de índices de filas a eliminar
            
        Returns:
            True si se eliminó al menos una
        """
        if not rows:
            return False
        
        # Ordenar en reversa para eliminar de abajo hacia arriba
        rows_sorted = sorted(rows, reverse=True)
        
        for row in rows_sorted:
            if 0 <= row < len(self._rows):
                self.beginRemoveRows(QModelIndex(), row, row)
                del self._rows[row]
                self.endRemoveRows()
        
        return True
    
    def get_all_rows(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las filas de datos.
        
        Returns:
            Lista de diccionarios con datos de simulaciones
        """
        return self._rows.copy()
    
    def get_row_data(self, row: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de una fila específica.
        
        Args:
            row: Índice de fila (0-based)
            
        Returns:
            Diccionario con datos de la fila o None
        """
        if 0 <= row < len(self._rows):
            return self._rows[row].copy()
        return None
    
    def update_row(self, row: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza una fila completa con nuevos datos.
        
        Args:
            row: Índice de fila (0-based)
            data: Diccionario con nuevos datos
            
        Returns:
            True si se actualizó correctamente
        """
        if not (0 <= row < len(self._rows)):
            return False
        
        # Actualizar datos
        self._rows[row].update(data)
        
        # Emitir señal de cambio para toda la fila
        left_index = self.index(row, 0)
        right_index = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(left_index, right_index)
        
        return True
    
    def get_column_index(self, column_name: str) -> int:
        """
        Obtiene el índice de una columna por su nombre.
        
        Args:
            column_name: Nombre de la columna
            
        Returns:
            Índice de la columna o -1 si no existe
        """
        try:
            return self.HEADERS.index(column_name)
        except ValueError:
            return -1
