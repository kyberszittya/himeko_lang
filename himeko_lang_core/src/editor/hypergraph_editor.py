import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QToolBar, QAction, QInputDialog, QGraphicsView, QGraphicsScene, QLabel,
    QGraphicsTextItem,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QWidget, QHBoxLayout, QSizePolicy, QVBoxLayout,
    QMessageBox, QFileDialog
)
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QPointF
from enum import Enum
from node_element import VisualNode
from edge_element import VisualHyperedge
from connection_element import VisualGraphConnection
from hypergraph_factory import HyMeKoVisualHypergraphFactory  # <-- Add import
# Add import for TextGenerator
from himeko.transformations.text.generate_text import TextGenerator
import json

# Setup logger
logger = logging.getLogger("hypergraph_editor")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
# Prevent duplicate handlers
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    logger.addHandler(handler)

class EditorState(Enum):
    SELECT = 1
    ADD_NODE = 2
    ADD_HYPEREDGE = 3
    ADD_CONNECTION = 4
    ADD_ATTRIBUTE = 5

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
                start = VisualGraphConnection._ellipse_edge_point_static(scenter, sradius_x, sradius_y, pos)
            else:
                srect = item.boundingRect()
                spos = item.scenePos()
                scenter = QPointF(spos.x() + srect.width()/2, spos.y() + srect.height()/2)
                swidth = srect.width()
                sheight = srect.height()
                start = VisualGraphConnection._rect_edge_point_static(scenter, swidth, sheight, pos)
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
        self.factory = self.scene.factory
        self.text_generator = None  # Will be initialized on demand

        # --- Layout without QSplitter ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main view (left)
        self.view = HypergraphView(self.scene)
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.view, 3)

        # Right side: vertical layout for hierarchy and HyMeKo textbox
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        main_layout.addWidget(right_panel, 2)

        # Hierarchy panel (top right)
        self.hierarchy_panel = QTreeWidget()
        self.hierarchy_panel.setHeaderLabel("Hierarchy")
        self.hierarchy_panel.setMinimumHeight(150)
        right_layout.addWidget(self.hierarchy_panel, 1)

        # HyMeKo equivalent textbox (bottom right, wider)
        self.hymeko_textbox = QTextEdit()
        self.hymeko_textbox.setReadOnly(True)
        self.hymeko_textbox.setPlaceholderText(">")
        self.hymeko_textbox.setMinimumHeight(200)
        right_layout.addWidget(self.hymeko_textbox, 2)

        self.createToolbar()
        self.status_label = QLabel("Ready")
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
        add_attribute = QAction("Add Attribute", self)
        add_attribute.triggered.connect(lambda: self.setMode("add_attribute"))
        toolbar.addAction(add_attribute)
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.deleteSelectedItems)
        toolbar.addAction(delete_action)
        save_json_action = QAction("Save as JSON", self)
        save_json_action.triggered.connect(self.save_as_json)
        toolbar.addAction(save_json_action)
        load_json_action = QAction("Load from JSON", self)
        load_json_action.triggered.connect(self.load_from_json)
        toolbar.addAction(load_json_action)

    def setMode(self, mode):
        if mode == "select":
            self.scene.current_state = EditorState.SELECT
        elif mode == "add_node":
            self.scene.current_state = EditorState.ADD_NODE
        elif mode == "add_hyperedge":
            self.scene.current_state = EditorState.ADD_HYPEREDGE
        elif mode == "add_connection":
            self.scene.current_state = EditorState.ADD_CONNECTION
        elif mode == "add_attribute":
            self.scene.current_state = EditorState.ADD_ATTRIBUTE
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
            if isinstance(item, VisualNode) or isinstance(item, VisualHyperedge):
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
            if (isinstance(item, VisualNode) or isinstance(item, VisualHyperedge)) and item.parent_element is None:
                add_element_tree(item, root_item)
        self.hierarchy_panel.expandAll()

        # --- Generate HyMeKo equivalent on every hierarchy update ---
        self.generate_hymeko_equivalent()

    def generate_hymeko_equivalent(self):
        """
        Generate the HyMeKo equivalent for the current graph using TextGenerator.
        This updates self.hymeko_textbox with the generated code.
        """
        # Find all top-level visual elements
        roots = [
            item for item in self.scene.items()
            if (isinstance(item, VisualNode) or isinstance(item, VisualHyperedge)) and item.parent_element is None
        ]
        # Only generate if there is at least one root with a hypergraph_element
        texts = []
        for root in roots:
            hg_elem = getattr(root, "hypergraph_element", None)
            if hg_elem is not None:
                # Lazy init TextGenerator with root's hypergraph element info
                if self.text_generator is None:
                    # Use root's info for TextGenerator constructor
                    self.text_generator = TextGenerator(
                        "text_generator",
                        getattr(hg_elem, "timestamp", 0),
                        getattr(hg_elem, "serial", 0),
                        getattr(hg_elem, "guid", b""),
                        getattr(hg_elem, "suid", b""),
                        getattr(hg_elem, "label", ""),
                        getattr(hg_elem, "parent", None)
                    )
                try:
                    text = self.text_generator(hg_elem)
                except Exception as e:
                    text = f"// Error generating text: {e}"
                texts.append(text)
        if texts:
            self.hymeko_textbox.setPlainText('\n\n'.join(texts))
        else:
            self.hymeko_textbox.setPlainText("// HyMeKo equivalent will be generated here.\n// TODO: Implement actual generation logic.")

    def save_as_json(self):
        """
        Save the current graphical elements and their hierarchy into a JSON file.
        """
        data = {
            "nodes": [],
            "hyperedges": [],
            "connections": [],
        }

        # Helper to get a unique id for each element
        def get_elem_id(elem):
            return id(elem)

        # Serialize nodes and hyperedges
        for item in self.scene.items():
            if isinstance(item, VisualNode):
                node_data = {
                    "id": get_elem_id(item),
                    "type": "node",
                    "name": item.name,
                    "x": item.pos().x(),
                    "y": item.pos().y(),
                    "radius": getattr(item, "radius", 30),
                    "parent": get_elem_id(item.parent_element) if item.parent_element else None,
                    "attributes": [attr.name for attr in getattr(item, "attributes", [])],
                    "children": [get_elem_id(child) for child in getattr(item, "children_elements", [])],
                }
                data["nodes"].append(node_data)
            elif isinstance(item, VisualHyperedge):
                edge_data = {
                    "id": get_elem_id(item),
                    "type": "hyperedge",
                    "name": item.name,
                    "x": item.pos().x(),
                    "y": item.pos().y(),
                    "width": getattr(item, "rect_width", 80),
                    "height": getattr(item, "rect_height", 30),
                    "parent": get_elem_id(item.parent_element) if item.parent_element else None,
                    "attributes": [attr.name for attr in getattr(item, "attributes", [])],
                    "children": [get_elem_id(child) for child in getattr(item, "children_elements", [])],
                }
                data["hyperedges"].append(edge_data)

        # Serialize connections
        for item in self.scene.items():
            if isinstance(item, VisualGraphConnection):
                conn_data = {
                    "source": get_elem_id(item.source),
                    "target": get_elem_id(item.target),
                    "value": item.value,
                }
                data["connections"].append(conn_data)

        # Save to file
        filename, _ = QFileDialog.getSaveFileName(self, "Save as JSON", "", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                self.statusBar().showMessage(f"Saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save JSON: {e}")

    def load_from_json(self):
        """
        Load graphical elements and their hierarchy from a JSON file.
        """
        filename, _ = QFileDialog.getOpenFileName(self, "Load from JSON", "", "JSON Files (*.json)")
        if not filename:
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load JSON: {e}")
            return

        # Clear current scene
        self.scene.clear()
        self.factory.reset()

        # Maps for reconstructing relationships
        id_to_elem = {}

        # Create nodes
        for node_data in data.get("nodes", []):
            node = self.factory.create_node(
                node_data["name"],
                node_data["x"],
                node_data["y"],
                radius=node_data.get("radius", 30),
                parent=None  # Parent will be set later
            )
            id_to_elem[node_data["id"]] = node

        # Create hyperedges
        for edge_data in data.get("hyperedges", []):
            edge = self.factory.create_hyperedge(
                edge_data["name"],
                edge_data["x"],
                edge_data["y"],
                width=edge_data.get("width", 80),
                height=edge_data.get("height", 30),
                parent=None  # Parent will be set later
            )
            id_to_elem[edge_data["id"]] = edge

        # Set parents and children
        for node_data in data.get("nodes", []):
            node = id_to_elem.get(node_data["id"])
            parent_id = node_data.get("parent")
            if parent_id and parent_id in id_to_elem:
                node.insert_into(id_to_elem[parent_id])
            # Attributes
            for attr_name in node_data.get("attributes", []):
                self.factory.add_attribute(node, attr_name)

        for edge_data in data.get("hyperedges", []):
            edge = id_to_elem.get(edge_data["id"])
            parent_id = edge_data.get("parent")
            if parent_id and parent_id in id_to_elem:
                edge.insert_into(id_to_elem[parent_id])
            # Attributes
            for attr_name in edge_data.get("attributes", []):
                self.factory.add_attribute(edge, attr_name)

        # Add all nodes and edges to the scene
        for elem in id_to_elem.values():
            self.scene.addItem(elem)

        # Create connections
        for conn_data in data.get("connections", []):
            source = id_to_elem.get(conn_data["source"])
            target = id_to_elem.get(conn_data["target"])
            if source and target:
                conn = self.factory.create_connection(source, target, value=conn_data.get("value"))
                self.scene.addItem(conn)

        self.updateHierarchyPanel()
        self.statusBar().showMessage(f"Loaded from {filename}")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = HypergraphEditor()
    editor.show()
    sys.exit(app.exec_())
