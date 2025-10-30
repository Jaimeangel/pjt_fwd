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
        "Spot",
        "Puntos",
        "Tasa Fwd",
        "Tasa IBR",
        "Derecho",
        "Obligación",
        "Fair Value"
    ]
    
    # Índices de columnas editables
    # Editables: Cliente, Punta Cli, Nominal USD, fechas, Spot, Tasa IBR, Derecho, Obligación
    EDITABLE_COLUMNS = [0, 1, 3, 4, 5, 6, 9, 10, 11]
    
    def __init__(self, simulations_model=None, parent=None):
        """
        Inicializa el modelo de tabla de simulaciones.
        
        Args:
            simulations_model: Instancia de SimulationsModel
            parent: Widget padre
        """
        super().__init__(parent)
        self._simulations_model = simulations_model
        
        # Datos dummy para testing
        self._rows = [
            {
                "cliente": "Cliente Ejemplo S.A.",
                "punta_cli": "Compra",
                "punta_emp": "Venta",
                "nominal_usd": 100000.0,
                "fec_sim": "2025-10-28",
                "fec_venc": "2025-12-15",
                "spot": 4250.50,
                "puntos": 25.75,
                "tasa_fwd": 4276.25,
                "tasa_ibr": 0.1120,
                "derecho": 425050000.0,
                "obligacion": 427625000.0,
                "fair_value": -2575000.0
            },
            {
                "cliente": "Corporación ABC Ltda.",
                "punta_cli": "Venta",
                "punta_emp": "Compra",
                "nominal_usd": 50000.0,
                "fec_sim": "2025-10-28",
                "fec_venc": "2026-01-30",
                "spot": 4250.50,
                "puntos": 42.30,
                "tasa_fwd": 4292.80,
                "tasa_ibr": 0.1150,
                "derecho": 214640000.0,
                "obligacion": 212525000.0,
                "fair_value": 2115000.0
            },
            {
                "cliente": "Empresa XYZ S.A.S.",
                "punta_cli": "Compra",
                "punta_emp": "Venta",
                "nominal_usd": 75000.0,
                "fec_sim": "2025-10-28",
                "fec_venc": "2025-11-28",
                "spot": 4250.50,
                "puntos": 15.25,
                "tasa_fwd": 4265.75,
                "tasa_ibr": 0.1100,
                "derecho": 319931250.0,
                "obligacion": 318787500.0,
                "fair_value": 1143750.0
            }
        ]
    
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
                nominal = row_data.get("nominal_usd", 0.0)
                return f"{nominal:,.2f}"
            elif col == 4:  # Fec Sim
                return row_data.get("fec_sim", "")
            elif col == 5:  # Fec Venc
                return row_data.get("fec_venc", "")
            elif col == 6:  # Spot
                spot = row_data.get("spot", 0.0)
                return f"{spot:,.2f}"
            elif col == 7:  # Puntos
                puntos = row_data.get("puntos", 0.0)
                return f"{puntos:,.2f}"
            elif col == 8:  # Tasa Fwd
                tasa_fwd = row_data.get("tasa_fwd", 0.0)
                return f"{tasa_fwd:,.2f}"
            elif col == 9:  # Tasa IBR
                tasa_ibr = row_data.get("tasa_ibr", 0.0)
                return f"{tasa_ibr * 100:.2f}%"
            elif col == 10:  # Derecho
                derecho = row_data.get("derecho", 0.0)
                return f"$ {derecho:,.2f}"
            elif col == 11:  # Obligación
                obligacion = row_data.get("obligacion", 0.0)
                return f"$ {obligacion:,.2f}"
            elif col == 12:  # Fair Value
                fair_value = row_data.get("fair_value", 0.0)
                return f"$ {fair_value:,.2f}"
        
        # EditRole: valor crudo para edición
        elif role == Qt.EditRole:
            if col == 0:  # Cliente
                return row_data.get("cliente", "")
            elif col == 1:  # Punta Cli
                return row_data.get("punta_cli", "")
            elif col == 3:  # Nominal USD
                return row_data.get("nominal_usd", 0.0)
            elif col == 4:  # Fec Sim
                return row_data.get("fec_sim", "")
            elif col == 5:  # Fec Venc
                return row_data.get("fec_venc", "")
            elif col == 6:  # Spot
                return row_data.get("spot", 0.0)
            elif col == 9:  # Tasa IBR
                return row_data.get("tasa_ibr", 0.0)
            elif col == 10:  # Derecho
                return row_data.get("derecho", 0.0)
            elif col == 11:  # Obligación
                return row_data.get("obligacion", 0.0)
        
        # TextAlignmentRole: alineación de texto
        elif role == Qt.TextAlignmentRole:
            # Alinear números a la derecha
            if col in [3, 6, 7, 8, 9, 10, 11, 12]:
                return Qt.AlignRight | Qt.AlignVCenter
            else:
                return Qt.AlignLeft | Qt.AlignVCenter
        
        # BackgroundRole: color de fondo para celdas calculadas
        elif role == Qt.BackgroundRole:
            # Celdas calculadas (no editables) con fondo ligeramente gris
            if col in [2, 7, 8, 12]:  # Punta Emp, Puntos, Tasa Fwd, Fair Value
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
            if col == 0:  # Cliente
                row_data["cliente"] = str(value)
            elif col == 1:  # Punta Cli
                punta = str(value).strip().capitalize()
                if punta in ["Compra", "Venta"]:
                    row_data["punta_cli"] = punta
                    # Auto-actualizar Punta Emp
                    row_data["punta_emp"] = "Venta" if punta == "Compra" else "Compra"
                    # Emitir cambio también para Punta Emp
                    punta_emp_index = self.index(index.row(), 2)
                    self.dataChanged.emit(punta_emp_index, punta_emp_index)
                else:
                    return False
            elif col == 3:  # Nominal USD
                nominal = float(value) if value else 0.0
                if nominal >= 0:
                    row_data["nominal_usd"] = nominal
                else:
                    return False
            elif col == 4:  # Fec Sim
                row_data["fec_sim"] = str(value)
            elif col == 5:  # Fec Venc
                row_data["fec_venc"] = str(value)
            elif col == 6:  # Spot
                spot = float(value) if value else 0.0
                if spot > 0:
                    row_data["spot"] = spot
                else:
                    return False
            elif col == 9:  # Tasa IBR
                tasa = float(value) if value else 0.0
                if tasa >= 0:
                    row_data["tasa_ibr"] = tasa
                else:
                    return False
            elif col == 10:  # Derecho
                derecho = float(value) if value else 0.0
                row_data["derecho"] = derecho
            elif col == 11:  # Obligación
                obligacion = float(value) if value else 0.0
                row_data["obligacion"] = obligacion
            else:
                return False
            
            # Emitir señal de cambio de datos
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
            
        except (ValueError, TypeError):
            return False
    
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
    
    def add_row(self, row_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Agrega una nueva fila a la tabla.
        
        Args:
            row_data: Datos de la fila (o None para fila vacía)
        """
        row_count = len(self._rows)
        self.beginInsertRows(QModelIndex(), row_count, row_count)
        
        if row_data:
            self._rows.append(row_data)
        else:
            # Fila vacía por defecto
            self._rows.append({
                "cliente": "",
                "punta_cli": "Compra",
                "punta_emp": "Venta",
                "nominal_usd": 0.0,
                "fec_sim": "",
                "fec_venc": "",
                "spot": 0.0,
                "puntos": 0.0,
                "tasa_fwd": 0.0,
                "tasa_ibr": 0.0,
                "derecho": 0.0,
                "obligacion": 0.0,
                "fair_value": 0.0
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
