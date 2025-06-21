from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QInputDialog, QColorDialog
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtCore import QRectF, Qt, QPointF

MARGIN_PUT_ELEMENT_FROM_PARENT = 20

class VisualHypergraphElement(QGraphicsItem):
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
        self.attributes = []  # List of Attribute objects
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
            self.label.setPos(self.rect_width/2 - tw/2, 0)
        else:
            self.label.setPos(self.rect_width/2 - tw/2, self.rect_height/2 - th/2)

    def _updateGeometry(self):
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
        scene = self.scene()
        if scene and hasattr(scene.parent(), "updateHierarchyPanel"):
            scene.parent().updateHierarchyPanel()
            if hasattr(scene.parent(), "generate_hymeko_equivalent"):
                scene.parent().generate_hymeko_equivalent()

    def remove_from_parent(self):
        if self.parent_element:
            parent_scene_pos = self.parent_element.mapToScene(self.parent_element.boundingRect().topLeft())
            self.parent_element.children_elements.remove(self)
            self.setParentItem(None)
            self.parent_element._updateGeometry()
            self.parent_element.update()
            self.parent_element = None
            margin = MARGIN_PUT_ELEMENT_FROM_PARENT
            new_top_left = parent_scene_pos - QPointF(self.rect_width + margin, 0)
            self.setPos(new_top_left)
            scene = self.scene()
            if scene and hasattr(scene.parent(), "updateHierarchyPanel"):
                scene.parent().updateHierarchyPanel()
                if hasattr(scene.parent(), "generate_hymeko_equivalent"):
                    scene.parent().generate_hymeko_equivalent()

    def itemChange(self, change, value):
        # Keep inside parent boundaries if has a parent
        if change == QGraphicsItem.ItemPositionChange or change == QGraphicsItem.ItemTransformChange:
            if self.parentItem():
                parent_rect = self.parentItem().boundingRect()
                my_rect = self.boundingRect()
                x = max(0, min(value.x(), parent_rect.width() - my_rect.width()))
                y = max(0, min(value.y(), parent_rect.height() - my_rect.height()))
                value = QPointF(x, y)
            # Always update connections, even if contained
            for conn in self.connections:
                conn.updatePosition()
            # Update all descendant connections as well
            def update_descendant_connections(element):
                for child in getattr(element, "children_elements", []):
                    for conn in getattr(child, "connections", []):
                        conn.updatePosition()
                    update_descendant_connections(child)
            update_descendant_connections(self)
        elif change == QGraphicsItem.ItemSceneChange and value is None:
            for conn in list(self.connections):
                if conn.scene():
                    conn.scene().removeItem(conn)
        return super().itemChange(change, value)

    def add_attribute(self, attr_name):
        attr = Attribute(attr_name, self)
        self.attributes.append(attr)
        attr.setParentItem(self)
        # Place attribute visually below existing attributes
        attr_y = self.rect_height + 10 + len(self.attributes) * (attr.height() + 10)
        attr.setPos(self.rect_width / 2 - attr.width() / 2, attr_y)
        self.children_elements.append(attr)
        self._updateGeometry()
        self.update()

class Attribute(QGraphicsItem):
    def __init__(self, name, parent_element):
        super().__init__(parent_element)
        self.name = name
        self.parent_element = parent_element
        self._width = 60
        self._height = 30
        self.label = QGraphicsTextItem(name, self)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self._updateLabel()

    def width(self):
        return self._width

    def height(self):
        return self._height

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option, widget):
        painter.setBrush(QBrush(QColor(220, 220, 255)))
        painter.setPen(QPen(Qt.darkBlue, 2))
        painter.drawEllipse(0, 0, self._width, self._height)
        # ...label is drawn by QGraphicsTextItem...

    def _updateLabel(self):
        tw = self.label.boundingRect().width()
        th = self.label.boundingRect().height()
        self.label.setPos(self._width/2 - tw/2, self._height/2 - th/2)

    def mouseDoubleClickEvent(self, event):
        name, ok = QInputDialog.getText(None, "Rename Attribute", "Enter new attribute name:", text=self.name)
        if ok and name.strip():
            self.name = name.strip()
            self.label.setPlainText(self.name)
            self._updateLabel()
        super().mouseDoubleClickEvent(event)

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
