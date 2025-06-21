import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QToolBar, QAction, QInputDialog, QGraphicsView, QGraphicsScene, QLabel,
    QGraphicsTextItem, QGraphicsItem,
    QTreeWidget, QTreeWidgetItem, QSplitter
)
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QTransform, QPolygonF, QPainterPath
from PyQt5.QtCore import Qt, QPointF, QRectF
from enum import Enum
from hypergraph_element import HypergraphElement
from node_element import Node
from edge_element import Hyperedge

class EditorState(Enum):
    SELECT = 1
    ADD_NODE = 2
    ADD_HYPEREDGE = 3
    ADD_CONNECTION = 4

class HypergraphScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 2000, 2000)
        self.current_state = EditorState.SELECT
        self.temp_connection = None
        self.source_item = None

    def attemptToRevertSelect(self):
        if hasattr(self.parent(), 'revertToSelect'):
            self.parent().revertToSelect()  # Directly call revertToSelect

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.scenePos()
            if self.current_state == EditorState.ADD_NODE:
                try:
                    name, ok = QInputDialog.getText(None, "Node Name", "Enter node name:")
                    if ok and name.strip():  # Ensure name is not empty or whitespace
                        new_node = Node(pos.x(), pos.y(), name.strip())
                        self.addItem(new_node)
                        # --- Update hierarchy panel when a new node is added ---
                        if hasattr(self.parent(), "updateHierarchyPanel"):
                            self.parent().updateHierarchyPanel()
                        self.attemptToRevertSelect()
                except Exception as e:
                    print(f"Error creating node: {e}")  # Log any errors
            elif self.current_state == EditorState.ADD_HYPEREDGE:
                try:
                    name, ok = QInputDialog.getText(None, "Hyperedge Name", "Enter hyperedge name:")
                    if ok and name.strip():  # Ensure name is not empty or whitespace
                        new_edge = Hyperedge(pos.x(), pos.y(), name.strip())
                        self.addItem(new_edge)
                        # --- Update hierarchy panel when a new hyperedge is added ---
                        if hasattr(self.parent(), "updateHierarchyPanel"):
                            self.parent().updateHierarchyPanel()
                        self.attemptToRevertSelect()
                except Exception as e:
                    print(f"Error creating hyperedge: {e}")  # Log any errors
            elif self.current_state == EditorState.ADD_CONNECTION:
                # Use items(pos) to get all items at the position, pick the topmost Node/Hyperedge
                items_at_pos = self.items(pos)
                item = None
                for candidate in items_at_pos:
                    if isinstance(candidate, Node) or isinstance(candidate, Hyperedge):
                        item = candidate
                        break
                if item:
                    if not self.source_item:
                        self.source_item = item
                        # --- Draw temp connection from edge, not center ---
                        if isinstance(item, Node):
                            srect = item.boundingRect()
                            spos = item.pos()
                            scenter = QPointF(spos.x() + srect.width()/2, spos.y() + srect.height()/2)
                            sradius_x = srect.width()/2
                            sradius_y = srect.height()/2
                            start = Connection._ellipse_edge_point_static(scenter, sradius_x, sradius_y, pos)
                        else:
                            srect = item.boundingRect()
                            spos = item.pos()
                            scenter = QPointF(spos.x() + srect.width()/2, spos.y() + srect.height()/2)
                            swidth = srect.width()
                            sheight = srect.height()
                            start = Connection._rect_edge_point_static(scenter, swidth, sheight, pos)
                        self.temp_connection = self.addLine(
                            item.x() + item.boundingRect().width()/2,
                            item.y() + item.boundingRect().height()/2,
                            pos.x(), pos.y(),
                            QPen(Qt.DashLine)
                        )
                    else:
                        if self.source_item != item:
                            # Ensure connections between nodes and hyperedges
                            if isinstance(self.source_item, Node) and isinstance(item, Hyperedge):
                                conn = Connection(self.source_item, item)
                                self.addItem(conn)
                                self.attemptToRevertSelect()
                            elif isinstance(self.source_item, Hyperedge) and isinstance(item, Node):
                                conn = Connection(self.source_item, item)
                                self.addItem(conn)
                                self.attemptToRevertSelect()
                            else:
                                print("Connections must be between a Node and a Hyperedge.")
                        self.resetConnectionState()
                else:
                    # If clicked on empty space, reset connection state
                    self.resetConnectionState()
        super().mousePressEvent(event)

    def resetConnectionState(self):
        """Reset temporary connection state."""
        if self.temp_connection:
            self.removeItem(self.temp_connection)
        self.temp_connection = None
        self.source_item = None

    def mouseMoveEvent(self, event):
        if self.temp_connection and self.source_item:
            pos = event.scenePos()
            # --- Update temp connection to follow edge logic ---
            item = self.source_item
            if isinstance(item, Node):
                srect = item.boundingRect()
                spos = item.pos()
                scenter = QPointF(spos.x() + srect.width()/2, spos.y() + srect.height()/2)
                sradius_x = srect.width()/2
                sradius_y = srect.height()/2
                start = Connection._ellipse_edge_point_static(scenter, sradius_x, sradius_y, pos)
            else:
                srect = item.boundingRect()
                spos = item.pos()
                scenter = QPointF(spos.x() + srect.width()/2, spos.y() + srect.height()/2)
                swidth = srect.width()
                sheight = srect.height()
                start = Connection._rect_edge_point_static(scenter, swidth, sheight, pos)
            self.temp_connection.setLine(
                self.source_item.x() + self.source_item.boundingRect().width()/2,
                self.source_item.y() + self.source_item.boundingRect().height()/2,
                pos.x(), pos.y()
            )
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        pos = event.scenePos()
        items_at_pos = self.items(pos)
        for item in items_at_pos:
            if isinstance(item, Node) or isinstance(item, Hyperedge):
                name, ok = QInputDialog.getText(None, "Rename", "Enter new name:", text=item.name)
                if ok and name.strip():
                    item.name = name.strip()
                    item.label.setPlainText(item.name)
                    item._updateLabel()
                break
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        pos = event.scenePos()
        items_at_pos = self.items(pos)
        item = None
        for candidate in items_at_pos:
            if isinstance(candidate, Node) or isinstance(candidate, Hyperedge):
                item = candidate
                break
        if item:
            from PyQt5.QtWidgets import QMenu
            menu = QMenu()
            insert_action = menu.addAction("Insert Into...")
            remove_action = menu.addAction("Remove From Parent")  # Add remove option
            color_action = menu.addAction("Change Color...")  # Add color change option
            selected_action = menu.exec_(event.screenPos())
            if selected_action == insert_action:
                # Show dialog to pick parent from other elements
                elements = [i for i in self.items() if (isinstance(i, Node) or isinstance(i, Hyperedge)) and i != item]
                names = [e.name for e in elements]
                if names:
                    parent_name, ok = QInputDialog.getItem(None, "Insert Into", "Select parent:", names, editable=False)
                    if ok:
                        parent = next(e for e in elements if e.name == parent_name)
                        item.insert_into(parent)
                        if hasattr(self.parent(), 'updateHierarchyPanel'):
                            self.parent().updateHierarchyPanel()
            elif selected_action == remove_action:
                if hasattr(item, "remove_from_parent"):
                    item.remove_from_parent()
            elif selected_action == color_action:
                item.changeColor()
        else:
            super().contextMenuEvent(event)

class HypergraphView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setBackgroundBrush(QBrush(QColor(255, 255, 255)))  # Set to white

    def wheelEvent(self, event):
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.scale(factor, factor)

class HypergraphEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hypergraph Editor")
        self.resize(1200, 800)
        self.scene = HypergraphScene(self)  # Pass self (the editor) to the scene

        self.splitter = QSplitter()
        self.splitter.setStyleSheet("background-color: white;")  # Set background to white
        self.setCentralWidget(self.splitter)

        # Main view
        self.view = HypergraphView(self.scene)
        self.splitter.addWidget(self.view)

        # Hierarchy panel (now on the right)
        self.hierarchy_panel = QTreeWidget()
        self.hierarchy_panel.setHeaderLabel("Hierarchy")
        self.splitter.addWidget(self.hierarchy_panel)

        self.createToolbar()
        self.status_label = QLabel("Ready")
        # Remove central_widget and layout, since splitter is now central widget
        self.statusBar().addWidget(self.status_label)
        self.updateHierarchyPanel()

    def createToolbar(self):
        toolbar = QToolBar("Editor Tools")
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        select_action = QAction("Select", self)
        select_action.triggered.connect(lambda: self.setMode("select"))
        toolbar.addAction(select_action)
        add_node = QAction("Add Node", self)
        add_node.triggered.connect(lambda: self.setMode("add_node"))
        toolbar.addAction(add_node)
        add_hyperedge = QAction("Add Hyperedge", self)
        add_hyperedge.triggered.connect(lambda: self.setMode("add_hyperedge"))
        toolbar.addAction(add_hyperedge)
        add_connection = QAction("Add Connection", self)
        add_connection.triggered.connect(lambda: self.setMode("add_connection"))
        toolbar.addAction(add_connection)
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.deleteSelectedItems)
        toolbar.addAction(delete_action)

    def setMode(self, mode):
        if mode == "select":
            self.scene.current_state = EditorState.SELECT
        elif mode == "add_node":
            self.scene.current_state = EditorState.ADD_NODE
        elif mode == "add_hyperedge":
            self.scene.current_state = EditorState.ADD_HYPEREDGE
        elif mode == "add_connection":
            self.scene.current_state = EditorState.ADD_CONNECTION
        self.status_label.setText(f"Mode: {mode}")
        if mode == "select":
            self.view.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            self.view.setDragMode(QGraphicsView.NoDrag)
        if self.scene.temp_connection:
            self.scene.removeItem(self.scene.temp_connection)
            self.scene.temp_connection = None
        self.scene.source_item = None

    def deleteSelectedItems(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)
        self.updateHierarchyPanel()

    def revertToSelect(self):
        self.setMode("select")
        self.statusBar().showMessage("You have switched the editor to 'select' mode. Any new mouse clicks will select items instead of creating them.")

    def deleteSelectedItems(self):
        # Remove connections before removing nodes/hyperedges
        for item in self.scene.selectedItems():
            if isinstance(item, Node) or isinstance(item, Hyperedge):
                for conn in list(item.connections):
                    if conn.scene():
                        self.scene.removeItem(conn)
            self.scene.removeItem(item)
        self.updateHierarchyPanel()

    def updateHierarchyPanel(self):
        self.hierarchy_panel.clear()

        def add_element_tree(element, parent_item):
            item = QTreeWidgetItem([element.name])
            parent_item.addChild(item)
            for child in getattr(element, "children_elements", []):
                add_element_tree(child, item)

        # Unified root for all top-level elements
        root_item = QTreeWidgetItem(["Elements"])
        self.hierarchy_panel.addTopLevelItem(root_item)
        for item in self.scene.items():
            if (isinstance(item, Node) or isinstance(item, Hyperedge)) and item.parent_element is None:
                add_element_tree(item, root_item)
        self.hierarchy_panel.expandAll()

class NodeLabel(QGraphicsTextItem):
    def __init__(self, text, parent):
        super().__init__(text, parent)
        self.parent_node = parent

    def mouseDoubleClickEvent(self, event):
        name, ok = QInputDialog.getText(None, "Rename", "Enter new name:", text=self.parent_node.name)
        if ok and name.strip():
            self.parent_node.name = name.strip()
            self.setPlainText(self.parent_node.name)
            self.parent_node._updateLabel()
        super().mouseDoubleClickEvent(event)

class EdgeLabel(QGraphicsTextItem):
    def __init__(self, text, parent):
        super().__init__(text, parent)
        self.parent_edge = parent

    def mouseDoubleClickEvent(self, event):
        name, ok = QInputDialog.getText(None, "Rename", "Enter new name:", text=self.parent_edge.name)
        if ok and name.strip():
            self.parent_edge.name = name.strip()
            self.setPlainText(self.parent_edge.name)
            self.parent_edge._updateLabel()
        super().mouseDoubleClickEvent(event)

class Connection(QGraphicsItem):
    def __init__(self, source, target):
        super().__init__()
        # Ensure source and target are either Node or Hyperedge
        if not ((isinstance(source, Node) and isinstance(target, Hyperedge)) or
                (isinstance(source, Hyperedge) and isinstance(target, Node))):
            raise ValueError("Connections must be between a Node and a Hyperedge.")
        self.source = source
        self.target = target
        self.source.connections.append(self)
        self.target.connections.append(self)
        self.arrow_size = 10
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(1000)  # Raise z-value to ensure connections are always in front of nodes/edges
        self.path = QPainterPath()
        self.arrow_head = QPolygonF()
        self.updatePosition()
        # Remove installSceneEventFilter: rely on itemChange in elements

    def sceneEventFilter(self, watched, event):
        # Update connection if either endpoint moves or is transformed
        if event.type() in (event.GraphicsSceneMove, event.GraphicsSceneTransformChanged):
            self.updatePosition()
        return False

    def mapToSceneRectBoundary(self, item, toward_point):
        """
        Return a point on the boundary of the item (ellipse or rect) in scene coordinates,
        in the direction of toward_point (scene coordinates).
        """
        rect = item.boundingRect()
        center_local = QPointF(rect.width() / 2, rect.height() / 2)
        center_scene = item.mapToScene(center_local)
        dx = toward_point.x() - center_scene.x()
        dy = toward_point.y() - center_scene.y()
        if isinstance(item, Node):
            # Ellipse boundary
            rx = rect.width() / 2
            ry = rect.height() / 2
            if dx == 0 and dy == 0:
                return center_scene
            angle = math.atan2(dy, dx)
            bx = center_scene.x() + rx * math.cos(angle)
            by = center_scene.y() + ry * math.sin(angle)
            return QPointF(bx, by)
        else:
            # Rect boundary
            if dx == 0 and dy == 0:
                return center_scene
            w = rect.width()
            h = rect.height()
            abs_dx = abs(dx)
            abs_dy = abs(dy)
            if abs_dx * h > abs_dy * w:
                # Intersection with left/right
                scale = (w / 2) / abs_dx
            else:
                # Intersection with top/bottom
                scale = (h / 2) / abs_dy
            bx = center_scene.x() + dx * scale
            by = center_scene.y() + dy * scale
            return QPointF(bx, by)

    def updatePosition(self):
        self.prepareGeometryChange()

        # --- CRITICAL FIX: Use the actual source/target, not their parents ---
        # The previous logic may have been "bubbling up" to the parent, causing the connection to go to the parent's (0,0)
        # Instead, always use the actual selected element for the connection point
        resolved_source = self.source
        resolved_target = self.target

        # Get scene centers
        source_rect = resolved_source.boundingRect()
        target_rect = resolved_target.boundingRect()
        source_center_scene = resolved_source.mapToScene(QPointF(source_rect.width() / 2, source_rect.height() / 2))
        target_center_scene = resolved_target.mapToScene(QPointF(target_rect.width() / 2, target_rect.height() / 2))

        # Compute boundary points
        start = self.mapToSceneRectBoundary(resolved_source, target_center_scene)
        end = self.mapToSceneRectBoundary(resolved_target, source_center_scene)

        start_local = self.mapFromScene(start)
        end_local = self.mapFromScene(end)

        self.path = QPainterPath(start_local)
        self.path.lineTo(end_local)

        dx = end_local.x() - start_local.x()
        dy = end_local.y() - start_local.y()
        raw_angle = math.degrees(math.atan2(dy, dx))
        if raw_angle < 0:
            raw_angle += 360
        angle = raw_angle

        p1 = end_local - QPointF(
            math.cos(math.radians(angle - 20)) * self.arrow_size,
            math.sin(math.radians(angle - 20)) * self.arrow_size
        )
        p2 = end_local - QPointF(
            math.cos(math.radians(angle + 20)) * self.arrow_size,
            math.sin(math.radians(angle + 20)) * self.arrow_size
        )
        poly = QPolygonF()
        poly.append(end_local)
        poly.append(p1)
        poly.append(p2)
        self.arrow_head = poly

    def boundingRect(self):
        # Return a rectangle that contains the connection line and arrow
        if self.path.isEmpty():
            return QRectF()
        return self.path.boundingRect().adjusted(-self.arrow_size, -self.arrow_size, self.arrow_size, self.arrow_size)

    def paint(self, painter, option, widget):
        if self.path.isEmpty():  # Ensure path is valid
            return
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawPath(self.path)
        painter.setBrush(QBrush(Qt.black))
        painter.drawPolygon(self.arrow_head)

    @staticmethod
    def _ellipse_edge_point_static(center, radius_x, radius_y, target_point):
        dx = target_point.x() - center.x()
        dy = target_point.y() - center.y()
        if dx == 0 and dy == 0:
            return center
        angle = math.atan2(dy, dx)
        x = center.x() + radius_x * math.cos(angle)
        y = center.y() + radius_y * math.sin(angle)
        return QPointF(x, y)

    @staticmethod
    def _rect_edge_point_static(rect_center, width, height, target_point):
        dx = target_point.x() - rect_center.x()
        dy = target_point.y() - rect_center.y()
        if dx == 0 and dy == 0:
            return rect_center
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        if abs_dx * height > abs_dy * width:
            scale = (width / 2) / abs_dx
        else:
            scale = (height / 2) / abs_dy
        x = rect_center.x() + dx * scale
        y = rect_center.y() + dy * scale
        return QPointF(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = HypergraphEditor()
    editor.show()
    sys.exit(app.exec_())
