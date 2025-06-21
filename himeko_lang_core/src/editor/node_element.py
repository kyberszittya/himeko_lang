from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPainterPath
from hypergraph_element import VisualHypergraphElement

class VisualNode(VisualHypergraphElement):
    def __init__(self, x, y, name, radius=30):
        super().__init__(name, width=radius*2, height=radius*2)
        self.radius = radius
        self.setPos(x - radius, y - radius)
        self.setFlag(QGraphicsItem.ItemClipsChildrenToShape, True)
        self._updateGeometry()

    def _updateGeometry(self):
        super()._updateGeometry()

    def paint(self, painter, option, widget):
        self._updateGeometry()
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        if self.children_elements:
            path = QPainterPath()
            path.addRoundedRect(0, 0, self.rect_width, self.rect_height, 20, 20)
            painter.drawPath(path)
        else:
            painter.drawEllipse(int(0), int(0), int(self.rect_width), int(self.rect_height))
        # ...existing code for selection, etc...
        # Draw attributes (they are QGraphicsItem children, so will be drawn automatically)
