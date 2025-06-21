from hypergraph_element import VisualHypergraphElement

class VisualHyperedge(VisualHypergraphElement):
    def __init__(self, x, y, name, width=80, height=30):
        super().__init__(name, width, height)
        self.setPos(x - width / 2, y - height / 2)
        self._updateGeometry()

    def _updateGeometry(self):
        super()._updateGeometry()

    def paint(self, painter, option, widget):
        self._updateGeometry()
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawRect(int(0), int(0), int(self.rect_width), int(self.rect_height))
        # ...existing code for selection, etc...
        # Draw attributes (they are QGraphicsItem children, so will be drawn automatically)
