"""
Modelo de tabla Qt para operaciones vigentes (solo lectura).
"""

from typing import Any, List, Dict, Optional
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex


class OperationsTableModel(QAbstractTableModel):
    """
    Modelo de tabla Qt para operaciones vigentes (solo lectura).
    
    Responsabilidades:
    - Presentar operaciones vigentes del 415 en QTableView
    - Modo solo lectura (no editable)
    - Formatear datos para visualización
    """
    
    # Headers de columnas
    HEADERS = [
        "Contraparte",
        "Deal",
        "Operación",
        "VNA",
        "TRM",
        "Derecho",
        "Obligación",
        "Fecha venc.",
        "Plazo rem. (td)"
    ]
    
    def __init__(self, parent=None):
        """
        Inicializa el modelo de tabla de operaciones.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        
        # Inicializar sin datos (se cargarán al seleccionar un cliente)
        self._rows = []
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Retorna el número de filas (operaciones).
        
        Args:
            parent: Índice padre
            
        Returns:
            Cantidad de operaciones
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
            Dato formateado según el rol
        """
        if not index.isValid():
            return None
        
        if index.row() >= len(self._rows) or index.row() < 0:
            return None
        
        if index.column() >= len(self.HEADERS) or index.column() < 0:
            return None
        
        row_data = self._rows[index.row()]
        
        # DisplayRole: texto a mostrar
        if role == Qt.DisplayRole:
            col = index.column()
            
            if col == 0:  # Contraparte
                return row_data.get("contraparte", "")
            elif col == 1:  # Deal
                return row_data.get("deal", "")
            elif col == 2:  # Operación
                return row_data.get("tipo_operacion", "")
            elif col == 3:  # VNA
                vna = row_data.get("vna", 0.0)
                if vna:
                    return f"{vna:,.2f}"
                return ""
            elif col == 4:  # TRM
                trm = row_data.get("trm", 0.0)
                if trm:
                    return f"{trm:,.2f}"
                return ""
            elif col == 5:  # Derecho
                derecho = row_data.get("vr_derecho", 0.0)
                if derecho:
                    return f"$ {derecho:,.2f}"
                return ""
            elif col == 6:  # Obligación
                obligacion = row_data.get("vr_obligacion", 0.0)
                if obligacion:
                    return f"$ {obligacion:,.2f}"
                return ""
            elif col == 7:  # Fecha vencimiento
                fecha = row_data.get("fecha_liquidacion", "")
                # Formatear fecha si es datetime
                if hasattr(fecha, 'strftime'):
                    return fecha.strftime("%Y-%m-%d")
                return str(fecha) if fecha else ""
            elif col == 8:  # Plazo remanente (td)
                td = row_data.get("td", "")
                if td is not None and td != "":
                    return str(int(td)) if isinstance(td, (int, float)) else str(td)
                return ""
        
        # TextAlignmentRole: alineación de texto
        elif role == Qt.TextAlignmentRole:
            col = index.column()
            # Alinear números a la derecha
            if col in [3, 4, 5, 6, 8]:  # VNA, TRM, Derecho, Obligación, td
                return Qt.AlignRight | Qt.AlignVCenter
            else:
                return Qt.AlignLeft | Qt.AlignVCenter
        
        return None
    
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
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Retorna flags de la celda (solo lectura).
        
        Args:
            index: Índice de la celda
            
        Returns:
            Flags indicando seleccionable pero no editable
        """
        if not index.isValid():
            return Qt.NoItemFlags
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def set_operations(self, operations: List[Dict[str, Any]]) -> None:
        """
        Establece las operaciones a mostrar.
        
        Args:
            operations: Lista de operaciones vigentes
        """
        self.beginResetModel()
        self._rows = operations if operations else []
        self.endResetModel()
    
    def get_operation_at_row(self, row: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene la operación en una fila específica.
        
        Args:
            row: Índice de fila (0-based)
            
        Returns:
            Diccionario con datos de la operación o None
        """
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None
