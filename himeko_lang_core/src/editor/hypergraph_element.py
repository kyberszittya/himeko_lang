from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QInputDialog, QColorDialog
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtCore import QRectF, Qt

class HypergraphElement(QGraphicsItem):
    def __init__(self, name, width=60, height=60):
        super().__init__()
        self.name = name
        self.rect_width = width
        self.rect_height = height
        self.brush = QBrush(QColor(200, 230, 255))
        self.pen = QPen(Qt.black, 2)
        self.label = ElementLabel(name, self)
        self.parent_element = None
        self.children_elements = []
        self.connections = []
        self._updateLabel()
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def setBrush(self, brush):
        self.brush = brush
        self.update()

    def setPen(self, pen):
        self.pen = pen
        self.update()

    def changeColor(self):
        color = QColorDialog.getColor(self.brush.color())
        if color.isValid():
            self.setBrush(QBrush(color))

    def _updateLabel(self):
        tw = self.label.boundingRect().width()
        th = self.label.boundingRect().height()
        if self.children_elements:
            # Place label at the top center if there are children
            self.label.setPos(self.rect_width/2 - tw/2, 0)
        else:
            # Center label if no children
            self.label.setPos(self.rect_width/2 - tw/2, self.rect_height/2 - th/2)

    def _updateGeometry(self):
        # Dynamically shrink/grow to fit children and label
        padding = 10
        label_rect = self.label.boundingRect()
        min_width = label_rect.width() + 2 * padding
        min_height = label_rect.height() + 2 * padding

        if self.children_elements:
            children_rect = QRectF()
            for child in self.children_elements:
                child_rect = child.mapRectToParent(child.boundingRect())
                children_rect = children_rect.united(child_rect)
            # Ensure label is always visible at the top
            self.rect_width = max(min_width, children_rect.right() + padding)
            self.rect_height = max(min_height, children_rect.bottom() + padding, label_rect.height() + 2 * padding)
        else:
            self.rect_width = min_width
            self.rect_height = min_height

        self._updateLabel()

    def boundingRect(self):
        return QRectF(0, 0, self.rect_width, self.rect_height)

    def insert_into(self, parent):
        if self.parent_element:
            self.parent_element.children_elements.remove(self)
        self.parent_element = parent
        parent.children_elements.append(self)
        self.setParentItem(parent)
        self.setPos(parent.rect_width / 2 - self.rect_width / 2, parent.rect_height / 2 - self.rect_height / 2)
        parent._updateGeometry()
        parent.update()
        self.update()

class ElementLabel(QGraphicsTextItem):
    def __init__(self, text, parent):
        super().__init__(text, parent)
        self.parent_element = parent

    def mouseDoubleClickEvent(self, event):
        name, ok = QInputDialog.getText(None, "Rename", "Enter new name:", text=self.parent_element.name)
        if ok and name.strip():
            self.parent_element.name = name.strip()
            self.setPlainText(self.parent_element.name)
            self.parent_element._updateLabel()
        super().mouseDoubleClickEvent(event)
