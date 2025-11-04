"""
Delegates personalizados para la tabla de simulaciones.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QComboBox, QDateEdit
from PySide6.QtCore import QDate


class PuntaClienteDelegate(QStyledItemDelegate):
    """Delegate para la columna 'Punta Cliente' con dropdown."""
    
    def createEditor(self, parent, option, index):
        """
        Crea un QComboBox para seleccionar Compra/Venta.
        
        Args:
            parent: Widget padre
            option: Opciones de estilo
            index: Índice de la celda
            
        Returns:
            QComboBox configurado
        """
        editor = QComboBox(parent)
        editor.addItems(["Compra", "Venta"])
        return editor
    
    def setEditorData(self, editor, index):
        """
        Carga el valor actual en el editor.
        
        Args:
            editor: QComboBox
            index: Índice de la celda
        """
        value = index.model().data(index, role=2)  # Qt.EditRole = 2
        if value:
            editor.setCurrentText(str(value))
    
    def setModelData(self, editor, model, index):
        """
        Guarda el valor del editor en el modelo.
        
        Args:
            editor: QComboBox
            model: Modelo de la tabla
            index: Índice de la celda
        """
        value = editor.currentText()
        model.setData(index, value, role=2)  # Qt.EditRole = 2


class FechaDelegate(QStyledItemDelegate):
    """Delegate para columnas de fecha con date picker."""
    
    def createEditor(self, parent, option, index):
        """
        Crea un QDateEdit con calendario popup.
        
        Args:
            parent: Widget padre
            option: Opciones de estilo
            index: Índice de la celda
            
        Returns:
            QDateEdit configurado
        """
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDisplayFormat("yyyy-MM-dd")
        editor.setDate(QDate.currentDate())
        return editor
    
    def setEditorData(self, editor, index):
        """
        Carga el valor actual en el editor.
        
        Args:
            editor: QDateEdit
            index: Índice de la celda
        """
        value = index.model().data(index, role=2)  # Qt.EditRole = 2
        if value:
            # Intentar parsear la fecha
            try:
                if isinstance(value, str):
                    # Formato: YYYY-MM-DD
                    parts = value.split('-')
                    if len(parts) == 3:
                        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                        editor.setDate(QDate(year, month, day))
                elif hasattr(value, 'year'):
                    # Es un objeto date de Python
                    editor.setDate(QDate(value.year, value.month, value.day))
            except (ValueError, IndexError):
                editor.setDate(QDate.currentDate())
        else:
            editor.setDate(QDate.currentDate())
    
    def setModelData(self, editor, model, index):
        """
        Guarda el valor del editor en el modelo.
        
        Args:
            editor: QDateEdit
            model: Modelo de la tabla
            index: Índice de la celda
        """
        value = editor.date().toString("yyyy-MM-dd")
        model.setData(index, value, role=2)  # Qt.EditRole = 2


