from PyQt5.QtGui import QPen, QPainter, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsScene, QInputDialog, QMessageBox, QGraphicsView

from editor.connection_element import VisualGraphConnection
from editor.edge_element import VisualHyperedge
from editor.graphics_helpers import EditorState, ellipse_edge_point, rect_edge_point, ViewportController
from editor.hypergraph_factory import HyMeKoVisualHypergraphFactory
import logging
import sys
from PyQt5.QtCore import Qt, QPointF

from editor.node_element import VisualNode

# Setup logger
logger = logging.getLogger("hypergraph_editor")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
# Prevent duplicate handlers
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    logger.addHandler(handler)


class HypergraphScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 2000, 2000)
        self.current_state = EditorState.SELECT
        self.temp_connection = None
        self.source_item = None
        self.factory = HyMeKoVisualHypergraphFactory()  # <-- Add factory instance

    def attemptToRevertSelect(self):
        if hasattr(self.parent(), 'revertToSelect'):
            self.parent().revertToSelect()  # Directly call revertToSelect

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.scenePos()
            items_at_pos = self.items(pos)
            # Fix: Use type() instead of isinstance() for Node/Hyperedge to avoid PyQt/Python import confusion
            from node_element import VisualNode as NodeType
            from edge_element import VisualHyperedge as HyperedgeType
            if self.current_state == EditorState.ADD_NODE:
                try:
                    name, ok = QInputDialog.getText(None, "Node Name", "Enter node name:")
                    if ok and name.strip():
                        parent_candidate = None
                        for candidate in items_at_pos:
                            if type(candidate) is NodeType or type(candidate) is HyperedgeType:
                                parent_candidate = candidate
                                break
                        node_elem = self.factory.create_node(name.strip(), pos.x(), pos.y(), parent=parent_candidate)
                        self.addItem(node_elem)  # <-- FIX: Remove .visual
                        if parent_candidate:
                            logger.info(f"Node '{name.strip()}' created as subelement of '{parent_candidate.name}'")
                        else:
                            logger.info(f"Node '{name.strip()}' created at ({pos.x()}, {pos.y()})")
                        if hasattr(self.parent(), "updateHierarchyPanel"):
                            self.parent().updateHierarchyPanel()
                        self.attemptToRevertSelect()
                except Exception as e:
                    logger.error(f"Error creating node: {e}")
                    QMessageBox.critical(None, "Error", f"Error creating node: {e}")
            elif self.current_state == EditorState.ADD_HYPEREDGE:
                try:
                    name, ok = QInputDialog.getText(None, "Hyperedge Name", "Enter hyperedge name:")
                    if ok and name.strip():
                        parent_candidate = None
                        for candidate in items_at_pos:
                            if type(candidate) is NodeType or type(candidate) is HyperedgeType:
                                parent_candidate = candidate
                                break
                        edge_elem = self.factory.create_hyperedge(name.strip(), pos.x(), pos.y(), parent=parent_candidate)
                        self.addItem(edge_elem)  # <-- FIX: Remove .visual
                        if parent_candidate:
                            logger.info(f"Hyperedge '{name.strip()}' created as subelement of '{parent_candidate.name}'")
                        else:
                            logger.info(f"Hyperedge '{name.strip()}' created at ({pos.x()}, {pos.y()})")
                        if hasattr(self.parent(), "updateHierarchyPanel"):
                            self.parent().updateHierarchyPanel()
                        self.attemptToRevertSelect()
                except Exception as e:
                    logger.error(f"Error creating hyperedge: {e}")
                    QMessageBox.critical(None, "Error", f"Error creating hyperedge: {e}")
            elif self.current_state == EditorState.ADD_CONNECTION:
                item = None
                for candidate in items_at_pos:
                    if type(candidate) is NodeType or type(candidate) is HyperedgeType:
                        item = candidate
                        break
                if item:
                    if not self.source_item:
                        self.source_item = item
                        # --- Draw temp connection from edge, not center ---
                        if type(item) is NodeType:
                            srect = item.boundingRect()
                            # Add parent position if item is contained
                            spos = item.scenePos()
                            scenter = QPointF(spos.x() + srect.width()/2, spos.y() + srect.height()/2)
                            sradius_x = srect.width()/2
                            sradius_y = srect.height()/2
                            start = VisualGraphConnection._ellipse_edge_point_static(scenter, sradius_x, sradius_y, pos)
                        else:
                            srect = item.boundingRect()
                            spos = item.scenePos()
                            scenter = QPointF(spos.x() + srect.width()/2, spos.y() + srect.height()/2)
                            swidth = srect.width()
                            sheight = srect.height()
                            start = VisualGraphConnection._rect_edge_point_static(scenter, swidth, sheight, pos)
                        self.temp_connection = self.addLine(
                            item.scenePos().x() + item.boundingRect().width()/2,
                            item.scenePos().y() + item.boundingRect().height()/2,
                            pos.x(), pos.y(),
                            QPen(Qt.DashLine)
                        )
                    else:
                        if self.source_item != item:
                            # Ensure connections between nodes and hyperedges
                            if type(self.source_item) is NodeType and type(item) is HyperedgeType:
                                conn = self.factory.create_connection(self.source_item, item)
                                self.addItem(conn)
                                self.attemptToRevertSelect()
                                logger.info(
                                    f"Connection created: Node '{getattr(self.source_item, 'name', '?')}' -> Hyperedge '{getattr(item, 'name', '?')}'"
                                )
                                # --- Update HyMeKo text after connection ---
                                if hasattr(self.parent(), "updateHierarchyPanel"):
                                    self.parent().updateHierarchyPanel()
                            elif type(self.source_item) is HyperedgeType and type(item) is NodeType:
                                conn = self.factory.create_connection(self.source_item, item)
                                self.addItem(conn)
                                self.attemptToRevertSelect()
                                logger.info(
                                    f"Connection created: Hyperedge '{getattr(self.source_item, 'name', '?')}' -> Node '{getattr(item, 'name', '?')}'"
                                )
                                # --- Update HyMeKo text after connection ---
                                if hasattr(self.parent(), "updateHierarchyPanel"):
                                    self.parent().updateHierarchyPanel()
                            else:
                                logger.warning("Connections must be between a Node and a Hyperedge.")
                                QMessageBox.warning(None, "Invalid Connection", "Connections must be between a Node and a Hyperedge.")
                        self.resetConnectionState()
                else:
                    self.resetConnectionState()
            elif self.current_state == EditorState.ADD_ATTRIBUTE:
                # Add attribute to the element under the cursor
                for candidate in items_at_pos:
                    if type(candidate) is NodeType or type(candidate) is HyperedgeType:
                        attr_name, ok = QInputDialog.getText(None, "Attribute Name", "Enter attribute name:")
                        if ok and attr_name.strip():
                            self.factory.add_attribute(candidate, attr_name.strip())
                            if hasattr(self.parent(), "updateHierarchyPanel"):
                                self.parent().updateHierarchyPanel()
                            self.attemptToRevertSelect()
                            logger.info(f"Attribute '{attr_name.strip()}' added to '{candidate.name}'")
                        break
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
            if isinstance(item, VisualNode):
                srect = item.boundingRect()
                spos = item.scenePos()
                scenter = QPointF(spos.x() + srect.width()/2, spos.y() + srect.height()/2)
                sradius_x = srect.width()/2
                sradius_y = srect.height()/2
                start = ellipse_edge_point(scenter, sradius_x, sradius_y, pos)
            else:
                srect = item.boundingRect()
                spos = item.scenePos()
                scenter = QPointF(spos.x() + srect.width()/2, spos.y() + srect.height()/2)
                swidth = srect.width()
                sheight = srect.height()
                start = rect_edge_point(scenter, swidth, sheight, pos)
            self.temp_connection.setLine(
                item.scenePos().x() + item.boundingRect().width()/2,
                item.scenePos().y() + item.boundingRect().height()/2,
                pos.x(), pos.y()
            )
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        pos = event.scenePos()
        items_at_pos = self.items(pos)
        for item in items_at_pos:
            if isinstance(item, VisualNode) or isinstance(item, VisualHyperedge):
                name, ok = QInputDialog.getText(None, "Rename", "Enter new name:", text=item.name)
                if ok and name.strip():
                    item.name = name.strip()
                    item.label.setPlainText(item.name)
                    item._updateLabel()
                    item.rename(name)
                break
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        pos = event.scenePos()
        items_at_pos = self.items(pos)
        item = None
        for candidate in items_at_pos:
            if isinstance(candidate, VisualNode) or isinstance(candidate, VisualHyperedge):
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
                elements = [i for i in self.items() if (isinstance(i, VisualNode) or isinstance(i, VisualHyperedge)) and i != item]
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
        # Offset the origin point to the center of the default view
        self._origin_offset = QPointF(1000, 1000)
        self.centerOn(self._origin_offset)
        self._panning = False
        self._pan_start = QPointF()
        self.viewport_controller = ViewportController(self)
        self._show_grid = True
        self._show_axis = True

    def wheelEvent(self, event):
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.viewport_controller.zoom(factor, self.mapToScene(event.pos()))

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._panning = True
            self.setCursor(Qt.ClosedHandCursor)
            self._pan_start = event.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            # Adjust panning by current zoom factor
            self.viewport_controller.pan(delta.x() / self.viewport_controller.zoom_factor,
                                         delta.y() / self.viewport_controller.zoom_factor)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def setShowGrid(self, show):
        self._show_grid = show
        self.viewport().update()

    def setShowAxis(self, show):
        self._show_axis = show
        self.viewport().update()

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        # Draw axes offset to the origin
        ox, oy = int(self._origin_offset.x()), int(self._origin_offset.y())
        # Draw grid and/or axes based on flags
        if self._show_grid or self._show_axis:
            from editor.graphics_helpers import draw_grid_background
            draw_grid_background(
                painter, rect, ox, oy,
                show_grid=self._show_grid,
                show_axis=self._show_axis
            )