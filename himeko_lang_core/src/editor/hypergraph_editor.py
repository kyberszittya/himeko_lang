import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QToolBar, QAction, QInputDialog, QGraphicsView, QGraphicsScene, QLabel,
    QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QStatusBar
)
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QTransform, QPolygonF, QPainterPath
from PyQt5.QtCore import Qt, QPointF, QRectF
from enum import Enum

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
                        self.attemptToRevertSelect()
                except Exception as e:
                    print(f"Error creating node: {e}")  # Log any errors
            elif self.current_state == EditorState.ADD_HYPEREDGE:
                try:
                    name, ok = QInputDialog.getText(None, "Hyperedge Name", "Enter hyperedge name:")
                    if ok and name.strip():  # Ensure name is not empty or whitespace
                        new_edge = Hyperedge(pos.x(), pos.y(), name.strip())
                        self.addItem(new_edge)
                        self.attemptToRevertSelect()
                except Exception as e:
                    print(f"Error creating hyperedge: {e}")  # Log any errors
            elif self.current_state == EditorState.ADD_CONNECTION:
                item = self.itemAt(pos, self.views()[0].transform())  # Use view's transform
                if item and (isinstance(item, Node) or isinstance(item, Hyperedge)):
                    if not self.source_item:
                        self.source_item = item
                        self.temp_connection = self.addLine(
                            item.x() + item.boundingRect().width()/2,
                            item.y() + item.boundingRect().height()/2,
                            pos.x(), pos.y(),
                            QPen(Qt.DashLine)
                        )
                    else:
                        if self.source_item != item:
                            conn = Connection(self.source_item, item)
                            self.addItem(conn)
                            self.attemptToRevertSelect()
                        if self.temp_connection:
                            self.removeItem(self.temp_connection)
                        self.temp_connection = None
                        self.source_item = None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.temp_connection and self.source_item:
            pos = event.scenePos()
            self.temp_connection.setLine(
                self.source_item.x() + self.source_item.boundingRect().width()/2,
                self.source_item.y() + self.source_item.boundingRect().height()/2,
                pos.x(), pos.y()
            )
        super().mouseMoveEvent(event)

class HypergraphView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setBackgroundBrush(QBrush(QColor(240, 240, 240)))

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
        self.view = HypergraphView(self.scene)
        self.createToolbar()
        self.status_label = QLabel("Ready")
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.view)
        self.setCentralWidget(central_widget)
        self.statusBar().addWidget(self.status_label)

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

    def revertToSelect(self):
        self.setMode("select")
        self.statusBar().showMessage("You have switched the editor to 'select' mode. Any new mouse clicks will select items instead of creating them.")

class Node(QGraphicsEllipseItem):
    def __init__(self, x, y, name, radius=30):
        super().__init__(0, 0, radius*2, radius*2)
        self.setPos(x - radius, y - radius)
        self.setBrush(QBrush(QColor(200, 230, 255)))
        self.setPen(QPen(Qt.black, 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)
        self.name = name
        self.label = QGraphicsTextItem(name, self)
        self._updateLabel()
        self.connections = []

    def _updateLabel(self):
        rect = self.boundingRect()
        tw = self.label.boundingRect().width()
        th = self.label.boundingRect().height()
        self.label.setPos(rect.width()/2 - tw/2, rect.height()/2 - th/2)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for conn in self.connections:
                conn.updatePosition()
        return super().itemChange(change, value)

class Hyperedge(QGraphicsRectItem):
    def __init__(self, x, y, name, width=120, height=60):
        super().__init__(0, 0, width, height)
        self.setPos(x - width/2, y - height/2)
        self.setBrush(QBrush(QColor(255, 230, 200)))
        self.setPen(QPen(Qt.black, 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)
        self.name = name
        self.label = QGraphicsTextItem(name, self)
        self._updateLabel()
        self.connections = []

    def _updateLabel(self):
        rect = self.boundingRect()
        tw = self.label.boundingRect().width()
        th = self.label.boundingRect().height()
        self.label.setPos(rect.width()/2 - tw/2, rect.height()/2 - th/2)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for conn in self.connections:
                conn.updatePosition()
        return super().itemChange(change, value)

class Connection(QGraphicsItem):
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
        self.source.connections.append(self)
        self.target.connections.append(self)
        self.arrow_size = 10
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.path = QPainterPath()  # Initialize path
        self.arrow_head = QPolygonF()  # Initialize arrow_head
        self.updatePosition()

    def updatePosition(self):
        self.prepareGeometryChange()  # Call before modifying geometry
        srect = self.source.boundingRect()
        spos = self.source.pos()
        scenter = QPointF(spos.x() + srect.width()/2, spos.y() + srect.height()/2)
        trect = self.target.boundingRect()
        tpos = self.target.pos()
        tcenter = QPointF(tpos.x() + trect.width()/2, tpos.y() + trect.height()/2)
        self.path = QPainterPath(scenter)
        self.path.lineTo(tcenter)
        dx = tcenter.x() - scenter.x()
        dy = tcenter.y() - scenter.y()
        raw_angle = math.degrees(math.atan2(dy, dx))
        if raw_angle < 0:
            raw_angle += 360
        angle = raw_angle

        p1 = tcenter - QPointF(
            math.cos(math.radians(angle - 20)) * self.arrow_size,
            math.sin(math.radians(angle - 20)) * self.arrow_size
        )
        p2 = tcenter - QPointF(
            math.cos(math.radians(angle + 20)) * self.arrow_size,
            math.sin(math.radians(angle + 20)) * self.arrow_size
        )
        poly = QPolygonF()
        poly.append(tcenter)
        poly.append(p1)
        poly.append(p2)
        self.arrow_head = poly

    def paint(self, painter, option, widget):
        if self.path.isEmpty():  # Ensure path is valid
            return
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawPath(self.path)
        painter.setBrush(QBrush(Qt.black))
        painter.drawPolygon(self.arrow_head)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = HypergraphEditor()
    editor.show()
    sys.exit(app.exec_())
