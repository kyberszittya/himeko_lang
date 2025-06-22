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

    def rename(self, new_name):
        old_name = self.name
        self.name = new_name
        if hasattr(self, "label"):
            self.label.setPlainText(self.name)
            self._updateLabel()
        # Update the hypergraph element's name if possible
        if hasattr(self, "hypergraph_element") and self.hypergraph_element is not None:
            hg_elem = self.hypergraph_element
            hg_elem.name = new_name
        print(self.hypergraph_element.name)
        # Update hierarchy and HyMeKo text if possible
        scene = self.scene()
        if scene and hasattr(scene.parent(), "updateHierarchyPanel"):
            scene.parent().updateHierarchyPanel()
        if scene and hasattr(scene.parent(), "generate_hymeko_equivalent"):
            scene.parent().generate_hymeko_equivalent()

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
        # --- Ensure hypergraph_element parent/children are updated as well ---
        if hasattr(self, "hypergraph_element") and hasattr(parent, "hypergraph_element"):
            self_hg = self.hypergraph_element
            parent_hg = parent.hypergraph_element
            # Use set_parent if available
            if hasattr(self_hg, "set_parent"):
                self_hg.set_parent(parent_hg)
            else:
                # Fallback to legacy behavior
                if hasattr(self_hg, "parent"):
                    self_hg.parent = parent_hg
                if hasattr(parent_hg, "children") and self_hg not in getattr(parent_hg, "children", []):
                    parent_hg.children.append(self_hg)
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
            # --- Update hypergraph_element parent/children as well ---
            if hasattr(self, "hypergraph_element") and hasattr(self.parent_element, "hypergraph_element"):
                self_hg = self.hypergraph_element
                parent_hg = self.parent_element.hypergraph_element
                # Use set_parent(None) if available
                if hasattr(self_hg, "set_parent"):
                    self_hg.set_parent(None)
                else:
                    # Fallback to legacy behavior
                    if hasattr(self_hg, "parent"):
                        self_hg.parent = None
                    if hasattr(parent_hg, "children") and self_hg in getattr(parent_hg, "children", []):
                        parent_hg.children.remove(self_hg)
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
                # Clamp position to keep the entire element within parent boundaries
                x = min(max(0, value.x()), parent_rect.width() - my_rect.width())
                y = min(max(0, value.y()), parent_rect.height() - my_rect.height())
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
        return attr

    def mouseDoubleClickEvent(self, event):
        # Only handle double-click if the click is on this element, not a child (like label or attribute)
        if self.isUnderMouse():
            # Optionally, implement renaming or other logic here for the base element
            pass
        else:
            event.ignore()
        # Do not call super().mouseDoubleClickEvent(event) to prevent propagation to parent

class Attribute(VisualHypergraphElement):
    def __init__(self, name, parent_element):
        super().__init__(name, width=60, height=30)
        self.name = name
        self.parent_element = parent_element
        self._width = 60
        self._height = 30
        self.label = QGraphicsTextItem(name, self)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self._updateLabel()
        self.hypergraph_element = None
        self.value = ""  # Add value property

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
        # Draw the label (handled by QGraphicsTextItem)
        # Draw the value below the label, if present
        if self.value != "":
            painter.setPen(Qt.darkGreen)
            painter.drawText(
                QRectF(0, self._height / 2, self._width, self._height / 2),
                Qt.AlignCenter | Qt.TextWordWrap,
                str(self.value)
            )

    def mouseDoubleClickEvent(self, event):
        # Only handle double-click if the click is on this attribute, not its parent
        if self.isUnderMouse():
            name, ok = QInputDialog.getText(None, "Attribute Name", "Enter attribute name:", text=self.name)
            if ok and name.strip():
                self.rename(name.strip())
                value, ok2 = QInputDialog.getText(None, "Attribute Value", "Enter value:", text=str(self.value))
                if ok2:
                    try:
                        parsed_value = float(value)
                    except ValueError:
                        parsed_value = value
                    self.value = parsed_value
                    if self.hypergraph_element is not None:
                        self.hypergraph_element.value = parsed_value
                    self.update()
        else:
            event.ignore()
        # Do not call super().mouseDoubleClickEvent(event) to prevent propagation to parent

    def contextMenuEvent(self, event):
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        set_value_action = menu.addAction("Set Value")
        insert_action = menu.addAction("Insert Into...")
        remove_action = menu.addAction("Remove From Parent")
        color_action = menu.addAction("Change Color...")
        selected_action = menu.exec_(event.screenPos())
        if selected_action == set_value_action:
            value, ok = QInputDialog.getText(None, "Set Attribute Value", "Enter value:", text=str(self.value))
            if ok:
                try:
                    parsed_value = float(value)
                except ValueError:
                    parsed_value = value
                self.value = parsed_value
                if self.hypergraph_element is not None:
                    self.hypergraph_element.value = parsed_value
                self.update()
        elif selected_action == insert_action:
            # Show dialog to pick parent from other elements
            scene = self.scene()
            if scene:
                elements = [i for i in scene.items() if hasattr(i, "name") and i != self]
                names = [e.name for e in elements]
                if names:
                    parent_name, ok = QInputDialog.getItem(None, "Insert Into", "Select parent:", names, editable=False)
                    if ok:
                        parent = next(e for e in elements if e.name == parent_name)
                        self.insert_into(parent)
                        if scene.parent() and hasattr(scene.parent(), 'updateHierarchyPanel'):
                            scene.parent().updateHierarchyPanel()
        elif selected_action == remove_action:
            if hasattr(self, "remove_from_parent"):
                self.remove_from_parent()
        elif selected_action == color_action:
            self.changeColor()
        else:
            super().contextMenuEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange or change == QGraphicsItem.ItemTransformChange:
            if self.parentItem():
                parent_rect = self.parentItem().boundingRect()
                my_rect = self.boundingRect()
                x = min(max(0, value.x()), parent_rect.width() - my_rect.width())
                y = min(max(0, value.y()), parent_rect.height() - my_rect.height())
                value = QPointF(x, y)
        return super().itemChange(change, value)

class ElementLabel(QGraphicsTextItem):
    def __init__(self, text, parent):
        super().__init__(text, parent)
        self.parent_element = parent

    def mouseDoubleClickEvent(self, event):
        # Only handle double-click if the click is on this label, not its parent
        if self.isUnderMouse():
            name, ok = QInputDialog.getText(None, "Rename", "Enter new name:", text=self.parent_element.name)
            if ok and name.strip():
                self.parent_element.rename(name.strip())
        else:
            event.ignore()
        # Do not call super().mouseDoubleClickEvent(event) to prevent propagation to parent
