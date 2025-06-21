from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPainterPath
from hypergraph_element import HypergraphElement

class Node(HypergraphElement):
    def __init__(self, x, y, name, radius=30):
        super().__init__(name, width=radius*2, height=radius*2)
        self.radius = radius
        self.setPos(x - radius, y - radius)
        self.setFlag(QGraphicsItem.ItemClipsChildrenToShape, True)
        self._updateGeometry()

    def _updateGeometry(self):
        # Let the boundary shrink/grow to the smallest possible to fit children and label
        padding = 10
        label_rect = self.label.boundingRect()
        min_width = label_rect.width() + 2 * padding
        min_height = label_rect.height() + 2 * padding

        if self.children_elements:
            children_rect = QRectF()
            for child in self.children_elements:
                child_rect = child.mapRectToParent(child.boundingRect())
                children_rect = children_rect.united(child_rect)
            self.rect_width = max(min_width, children_rect.right() + padding)
            self.rect_height = max(min_height, children_rect.bottom() + padding, label_rect.height() + 2 * padding)
        else:
            self.rect_width = min_width
            self.rect_height = min_height

        self._updateLabel()

    def paint(self, painter, option, widget):
        self._updateGeometry()
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        if self.children_elements:
            path = QPainterPath()
            path.addRoundedRect(0, 0, self.rect_width, self.rect_height, 20, 20)
            painter.drawPath(path)
        else:
            # Ensure all arguments to drawEllipse are int
            painter.drawEllipse(int(0), int(0), int(self.rect_width), int(self.rect_height))
        # ...existing code for selection, etc...

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            if self.parentItem():
                parent_rect = self.parentItem().boundingRect()
                my_rect = self.boundingRect()
                x = max(0, min(value.x(), parent_rect.width() - my_rect.width()))
                y = max(0, min(value.y(), parent_rect.height() - my_rect.height()))
                value = QPointF(x, y)
            for conn in self.connections:
                conn.updatePosition()
        elif change == QGraphicsItem.ItemSceneChange and value is None:
            for conn in list(self.connections):
                if conn.scene():
                    conn.scene().removeItem(conn)
        return super().itemChange(change, value)
