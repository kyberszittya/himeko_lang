import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QToolBar, QAction, QGraphicsView, QLabel,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QWidget, QHBoxLayout, QSizePolicy, QVBoxLayout,
    QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem  # <-- Add QTableWidget imports
)
from PyQt5.QtCore import Qt

from editor.editor_commands import SaveJsonCommand, LoadJsonCommand
from editor.editor_commands import ClearCommand
from editor.editor_scene import HypergraphScene, HypergraphView
from editor.graphics_helpers import EditorState
from himeko.hbcm.elements.edge import HyperArc, EnumHyperarcDirection
from node_element import VisualNode
from edge_element import VisualHyperedge
from connection_element import VisualGraphConnection
# Add import for TextGenerator
from himeko.transformations.text.generate_text import TextGenerator

# Setup logger
logger = logging.getLogger("hypergraph_editor")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
# Prevent duplicate handlers
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    logger.addHandler(handler)





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

        # --- Left panel: vertical layout for controls and attribute table ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)
        main_layout.addWidget(left_panel, 1)

        # Toolbar (control buttons) at the top of the left panel
        self.toolbar = QToolBar("Editor Tools")
        left_layout.addWidget(self.toolbar, 0)

        # Attribute/Relationship Table below the toolbar, fills remaining space
        self.attribute_table = QTableWidget()
        self.attribute_table.setColumnCount(2)
        self.attribute_table.setHorizontalHeaderLabels(["Attribute/Relation", "Value"])
        self.attribute_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        self.attribute_table.itemChanged.connect(self.on_attribute_table_item_changed)
        self.attribute_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(self.attribute_table, 1)

        # Main view (center)
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

        # --- Prüfer code display under hierarchy ---
        self.prufer_label = QLabel("Prüfer code: ")
        self.prufer_label.setWordWrap(True)
        right_layout.addWidget(self.prufer_label, 0)

        # HyMeKo equivalent textbox (bottom right, wider)
        self.hymeko_textbox = QTextEdit()
        self.hymeko_textbox.setReadOnly(True)
        self.hymeko_textbox.setPlaceholderText(">")
        self.hymeko_textbox.setMinimumHeight(200)
        right_layout.addWidget(self.hymeko_textbox, 2)

        self.selected_element = None  # Track selected node/hyperedge for attribute editing

        self.createToolbar(self.toolbar)  # Pass toolbar to use the left panel's toolbar
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
        self.updateHierarchyPanel()

        self.createMenuBar()  # <-- Add this line to create the menubar

        # Connect selection change to update attribute table and Prüfer code
        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.hierarchy_panel.itemSelectionChanged.connect(self.on_hierarchy_selection_changed)

    def createMenuBar(self):
        menubar = self.menuBar()
        scene_menu = menubar.addMenu("Scene")
        blank_scene_action = QAction("Blank Scene", self)
        blank_scene_action.triggered.connect(self.blank_scene)
        scene_menu.addAction(blank_scene_action)
        # Add horizontal separator
        scene_menu.addSeparator()



        # Add Save as JSON and Load from JSON actions
        load_json_action = QAction("Load from JSON", self)
        load_json_action.triggered.connect(self.load_from_json)
        scene_menu.addAction(load_json_action)

        save_json_action = QAction("Save as JSON", self)
        save_json_action.triggered.connect(self.save_as_json)
        scene_menu.addAction(save_json_action)



        view_menu = menubar.addMenu("View")

        self.action_show_grid = QAction("Show Grid", self, checkable=True)
        self.action_show_grid.setChecked(True)
        self.action_show_grid.triggered.connect(self.toggle_grid)
        view_menu.addAction(self.action_show_grid)

        self.action_show_axis = QAction("Show Axis", self, checkable=True)
        self.action_show_axis.setChecked(True)
        self.action_show_axis.triggered.connect(self.toggle_axis)
        view_menu.addAction(self.action_show_axis)


    def toggle_grid(self, checked):
        self.view.setShowGrid(checked)

    def toggle_axis(self, checked):
        self.view.setShowAxis(checked)

    def on_selection_changed(self):
        selected = self.scene.selectedItems()
        if selected and (hasattr(selected[0], "attributes") or hasattr(selected[0], "relations")):
            self.selected_element = selected[0]
            self.update_attribute_table(self.selected_element)
            self.update_prufer_code(self.selected_element)
        else:
            self.selected_element = None
            self.attribute_table.setRowCount(0)
            self.prufer_label.setText("Prüfer code: ")

    def on_hierarchy_selection_changed(self):
        selected_items = self.hierarchy_panel.selectedItems()
        if not selected_items:
            self.prufer_label.setText("Prüfer code: ")
            return
        selected_name = selected_items[0].text(0)
        # Find the corresponding element by name
        for item in self.scene.items():
            if hasattr(item, "name") and item.name == selected_name:
                self.update_prufer_code(item)
                break

    def update_prufer_code(self, element):
        # Dummy Prüfer code generator for demonstration
        # Replace this with your actual Prüfer code logic as needed
        prufer_code = self.generate_prufer_code(element)
        self.prufer_label.setText(f"Prüfer code: {prufer_code}")

    def generate_prufer_code(self, element):
        # Placeholder: returns a string representation of the element's children names
        # Replace with actual Prüfer code computation for your structure
        if not hasattr(element, "children_elements") or not element.children_elements:
            return "-"
        return "[" + ", ".join(child.name for child in element.children_elements) + "]"

    def get_hyperarc_relationships(self, hg_elem):
        # For HyperEdge, hyperarcs are typically in .arcs or .hyperarcs or .relations
        # Try common attribute names
        if hasattr(hg_elem, "arcs") and isinstance(hg_elem.arcs, list):
            hyperarcs = hg_elem.arcs
        elif hasattr(hg_elem, "hyperarcs") and isinstance(hg_elem.hyperarcs, list):
            hyperarcs = hg_elem.hyperarcs
        elif hasattr(hg_elem, "relations") and isinstance(hg_elem.relations, list):
            hyperarcs = hg_elem.relations
        elif hasattr(hg_elem, "all_relations"):
            hyperarcs = list(hg_elem.all_relations())
        return hyperarcs if 'hyperarcs' in locals() else []

    def update_attribute_table(self, element):
        # Show both attributes and, for hyperedges, hyperarcs (relations)
        attributes = getattr(element, "attributes", [])
        hyperarcs = []
        arc_names = []
        arc_values = []
        # If the selected element is a hyperedge, try to get its hyperarcs
        if hasattr(element, "hypergraph_element"):
            hg_elem = element.hypergraph_element
            hyperarcs = self.get_hyperarc_relationships(hg_elem)

            # Try to extract arc names and values if possible
            for arc in hyperarcs:
                # Try to get a name and value for the arc
                arc_name = getattr(arc, "name", None)
                arc_value = getattr(arc, "value", None)
                # If not present, try to use string representation
                if arc_name is None:
                    arc_name = str(arc)
                arc_names.append(arc_name)
                arc_values.append(arc_value)

        total_rows = len(attributes) + len(hyperarcs)
        self.attribute_table.blockSignals(True)
        self.attribute_table.setRowCount(total_rows)
        # Attributes
        for row, attr in enumerate(attributes):
            name_item = QTableWidgetItem(attr.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.attribute_table.setItem(row, 0, name_item)
            value_item = QTableWidgetItem(str(attr.value))
            self.attribute_table.setItem(row, 1, value_item)
        # Hyperarcs (for hyperedges)
        for i, arc in enumerate(hyperarcs):
            row = len(attributes) + i
            arc: HyperArc
            arc_name = ""
            match arc.direction:
                case EnumHyperarcDirection.OUT:
                    arc_name += f"[OUT]{arc.target.name}"
                case EnumHyperarcDirection.IN:
                    arc_name += f"[IN]{arc.target.name}"

            arc_value = arc_values[i]
            name_item = QTableWidgetItem(f"{arc_name}")
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.attribute_table.setItem(row, 0, name_item)
            value_item = QTableWidgetItem(str(arc_value) if arc_value is not None else "")
            self.attribute_table.setItem(row, 1, value_item)
        self.attribute_table.blockSignals(False)

    def on_attribute_table_item_changed(self, item):
        if not self.selected_element:
            return
        row = item.row()
        col = item.column()
        # Count attributes and relations
        attributes = getattr(self.selected_element, "attributes", [])
        hyperarcs = []
        if hasattr(self.selected_element, "hypergraph_element"):
            hg_elem = self.selected_element.hypergraph_element
            hyperarcs = self.get_hyperarc_relationships(hg_elem)
        if col == 1:
            if row < len(attributes):
                attr = attributes[row]
                value = item.text()
                try:
                    parsed_value = float(value)
                except ValueError:
                    parsed_value = value
                attr.value = parsed_value
                if attr.hypergraph_element is not None:
                    attr.hypergraph_element.value = parsed_value
                attr.update()
            else:
                rel_idx = row - len(attributes)
                if 0 <= rel_idx < len(hyperarcs):
                    rel = hyperarcs[rel_idx]
                    value = item.text()
                    try:
                        parsed_value = float(value)
                    except ValueError:
                        parsed_value = value
                    # Try to set the value if possible
                    if hasattr(rel, "value"):
                        rel.value = parsed_value
                    # --- Update the table cell to reflect the new value ---
                    self.attribute_table.blockSignals(True)
                    self.attribute_table.item(row, 1).setText(str(parsed_value))
                    self.attribute_table.blockSignals(False)
            self.generate_hymeko_equivalent()
            # --- Force a redraw of the view to reflect changes visually ---
            self.view.viewport().update()

    def createToolbar(self, toolbar=None):
        # Accept an optional toolbar argument (for left panel)
        if toolbar is None:
            toolbar = QToolBar("Editor Tools")
            self.addToolBar(Qt.LeftToolBarArea, toolbar)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setAllowedAreas(Qt.AllToolBarAreas)
        toolbar.setOrientation(Qt.Vertical)
        toolbar.setVisible(True)  # Ensure toolbar is visible

        # Ensure all actions are always visible by not using overflow or hiding
        select_action = QAction("Select", self)
        select_action.setVisible(True)
        select_action.triggered.connect(lambda: self.setMode("select"))
        toolbar.addAction(select_action)

        add_node = QAction("Add Node", self)
        add_node.setVisible(True)
        add_node.triggered.connect(lambda: self.setMode("add_node"))
        toolbar.addAction(add_node)

        add_hyperedge = QAction("Add Hyperedge", self)
        add_hyperedge.setVisible(True)
        add_hyperedge.triggered.connect(lambda: self.setMode("add_hyperedge"))
        toolbar.addAction(add_hyperedge)

        add_connection = QAction("Add Connection", self)
        add_connection.setVisible(True)
        add_connection.triggered.connect(lambda: self.setMode("add_connection"))
        toolbar.addAction(add_connection)

        add_attribute = QAction("Add Attribute", self)
        add_attribute.setVisible(True)
        add_attribute.triggered.connect(lambda: self.setMode("add_attribute"))
        toolbar.addAction(add_attribute)

        delete_action = QAction("Delete", self)
        delete_action.setVisible(True)
        delete_action.triggered.connect(self.deleteSelectedItems)
        toolbar.addAction(delete_action)



        save_hymeko_action = QAction("Save HyMeKo Text", self)
        save_hymeko_action.setVisible(True)
        save_hymeko_action.triggered.connect(self.save_hymeko_text)
        toolbar.addAction(save_hymeko_action)

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

    def serialize_to_json(self):
        """
        Serialize the current graphical elements and their hierarchy into a JSON-serializable dict.
        """
        data = {
            "nodes": [],
            "hyperedges": [],
            "connections": [],
        }

        def get_elem_id(elem):
            return id(elem)

        # Serialize nodes
        for item in self.scene.items():
            if isinstance(item, VisualNode):
                node_data = {
                    "id": get_elem_id(item),
                    "name": getattr(item, "name", ""),
                    "x": item.pos().x(),
                    "y": item.pos().y(),
                    "radius": getattr(item, "radius", 30),
                    "z": item.zValue(),
                    "parent": get_elem_id(item.parent_element) if getattr(item, "parent_element", None) else None,
                    "attributes": [getattr(attr, "name", "") for attr in getattr(item, "attributes", [])],
                }
                data["nodes"].append(node_data)

        # Serialize hyperedges
        for item in self.scene.items():
            if isinstance(item, VisualHyperedge):
                edge_data = {
                    "id": get_elem_id(item),
                    "name": getattr(item, "name", ""),
                    "x": item.pos().x(),
                    "y": item.pos().y(),
                    "width": getattr(item, "width", 80),
                    "height": getattr(item, "height", 30),
                    "z": item.zValue(),
                    "parent": get_elem_id(item.parent_element) if getattr(item, "parent_element", None) else None,
                    "attributes": [getattr(attr, "name", "") for attr in getattr(item, "attributes", [])],
                }
                data["hyperedges"].append(edge_data)

        # Serialize connections
        for item in self.scene.items():
            if isinstance(item, VisualGraphConnection):
                conn_data = {
                    "source": get_elem_id(item.source),
                    "target": get_elem_id(item.target),
                    "value": getattr(item, "value", None),
                    "z": item.zValue(),
                }
                data["connections"].append(conn_data)
        return data

    def deserialize_from_json(self, data):
        """
        Load graphical elements and their hierarchy from a JSON-serializable dict.
        """
        # Clear current scene
        self.scene.clear()
        self.factory.reset()

        id_to_elem = {}
        z_orders = {}
        parent_map = {}
        pos_map = {}

        # Create nodes
        for node_data in data.get("nodes", []):
            node = self.factory.create_node(
                node_data["name"],
                0, 0,  # Temporary position, will set below
                radius=node_data.get("radius", 30),
                parent=None  # Parent will be set later
            )
            z_orders[node] = node_data.get("z", 0)
            id_to_elem[node_data["id"]] = node
            parent_map[node_data["id"]] = node_data.get("parent")
            pos_map[node_data["id"]] = (node_data["x"], node_data["y"])

        # Create hyperedges
        for edge_data in data.get("hyperedges", []):
            edge = self.factory.create_hyperedge(
                edge_data["name"],
                0, 0,  # Temporary position, will set below
                width=edge_data.get("width", 80),
                height=edge_data.get("height", 30),
                parent=None  # Parent will be set later
            )
            z_orders[edge] = edge_data.get("z", 0)
            id_to_elem[edge_data["id"]] = edge
            parent_map[edge_data["id"]] = edge_data.get("parent")
            pos_map[edge_data["id"]] = (edge_data["x"], edge_data["y"])

        # Set parents and children, and set positions
        # First, set all top-level elements (no parent)
        for elem_id, elem in id_to_elem.items():
            parent_id = parent_map.get(elem_id)
            rel_x, rel_y = pos_map[elem_id]
            if not parent_id or parent_id not in id_to_elem:
                elem.setParentItem(None)
                elem.setPos(rel_x, rel_y)

        # Then, set all contained elements (with parent)
        for elem_id, elem in id_to_elem.items():
            parent_id = parent_map.get(elem_id)
            rel_x, rel_y = pos_map[elem_id]
            if parent_id and parent_id in id_to_elem:
                parent_elem = id_to_elem[parent_id]
                elem.insert_into(parent_elem)
                elem.setPos(rel_x, rel_y)

            # Attributes
            if isinstance(elem, VisualNode):
                for node_data in data.get("nodes", []):
                    if node_data["id"] == elem_id:
                        for attr_name in node_data.get("attributes", []):
                            self.factory.add_attribute(elem, attr_name)
            elif isinstance(elem, VisualHyperedge):
                for edge_data in data.get("hyperedges", []):
                    if edge_data["id"] == elem_id:
                        for attr_name in edge_data.get("attributes", []):
                            self.factory.add_attribute(elem, attr_name)

        # Add all nodes and edges to the scene
        for elem in id_to_elem.values():
            self.scene.addItem(elem)

        # Create connections and store their z-orders
        conn_z_orders = []
        for conn_data in data.get("connections", []):
            source = id_to_elem.get(conn_data["source"])
            target = id_to_elem.get(conn_data["target"])
            if source and target:
                conn = self.factory.create_connection(source, target, value=conn_data.get("value"))
                conn_z_orders.append((conn, conn_data.get("z", 0)))
                self.scene.addItem(conn)

        # --- Set z-ordering for all elements after all are added ---
        for elem, z in sorted(z_orders.items(), key=lambda x: x[1]):
            elem.setZValue(z)
        for conn, z in sorted(conn_z_orders, key=lambda x: x[1]):
            conn.setZValue(z)

        self.updateHierarchyPanel()

    def save_as_json(self):
        """
        Save the current graphical elements and their hierarchy into a JSON file using the command pattern.
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Save as JSON", "", "JSON Files (*.json)")
        if filename:
            try:
                cmd = SaveJsonCommand(self, filename)
                cmd.execute()
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save JSON: {e}")

    def load_from_json(self):
        """
        Load graphical elements and their hierarchy from a JSON file using the command pattern.
        """
        filename, _ = QFileDialog.getOpenFileName(self, "Load from JSON", "", "JSON Files (*.json)")
        if not filename:
            return
        try:
            cmd = LoadJsonCommand(self, filename)
            cmd.execute()
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load JSON: {e}")

    def save_hymeko_text(self):
        """
        Save the generated HyMeKo description to a text file.
        """
        text = self.hymeko_textbox.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Save HyMeKo Text", "No HyMeKo text to save.")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Save HyMeKo Text", "", "HyMeKo Files (*.himeko);;Text Files (*.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text)
                self.statusBar().showMessage(f"HyMeKo text saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save HyMeKo text: {e}")

    def blank_scene(self):
        """Clear the scene to create a blank scene."""
        cmd = ClearCommand(self)
        cmd.execute()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = HypergraphEditor()
    editor.show()
    sys.exit(app.exec_())
