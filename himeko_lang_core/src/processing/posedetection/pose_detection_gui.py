import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsSimpleTextItem, QInputDialog, QWidget, QVBoxLayout,
    QGraphicsItem, QLabel,
    QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt, QPointF, QRectF

JOINT_RADIUS = 10

class JointItem(QGraphicsEllipseItem):
    counter = 1
    def __init__(self, scene, x, y, parent=None):
        super().__init__(-JOINT_RADIUS, -JOINT_RADIUS, JOINT_RADIUS*2, JOINT_RADIUS*2, parent)
        self.scene_ref = scene
        self.setPos(x, y)
        self.setBrush(QBrush(Qt.blue))
        self.setFlags(QGraphicsEllipseItem.ItemIsMovable |
                      QGraphicsEllipseItem.ItemSendsGeometryChanges |
                      QGraphicsEllipseItem.ItemIsSelectable)
        self.order = JointItem.counter
        JointItem.counter += 1
        self.name = f"Joint{self.order}"
        self.name_item = QGraphicsSimpleTextItem(self.name, self)
        self.name_item.setFlag(QGraphicsSimpleTextItem.ItemIgnoresTransformations)
        self.update_label_position()

    def update_label_position(self):
        rect = self.name_item.boundingRect()
        self.name_item.setPos(-rect.width()/2, -JOINT_RADIUS - rect.height())

    def set_name(self, new_name):
        self.name = new_name
        self.name_item.setText(new_name)
        self.update_label_position()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for link in self.scene_ref.links:
                link.update_position()
            self.update_label_position()
        return super().itemChange(change, value)

class LinkItem(QGraphicsLineItem):
    counter = 1
    def __init__(self, scene, joint1, joint2, parent=None):
        super().__init__(parent)
        self.scene_ref = scene
        self.joint1 = joint1
        self.joint2 = joint2
        self.order = LinkItem.counter
        LinkItem.counter += 1
        self.name = f"Link{self.order}"
        self.setPen(QPen(Qt.red, 8))
        self.setZValue(-1)

        # Make the link selectable
        self.setFlags(QGraphicsLineItem.ItemIsSelectable)

        # Add text label for the link
        self.text_item = QGraphicsSimpleTextItem(self.name, self)
        self.text_item.setFlag(QGraphicsSimpleTextItem.ItemIgnoresTransformations)

        self.update_position()

    def update_position(self):
        p1 = self.joint1.scenePos()
        p2 = self.joint2.scenePos()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())

        # Update text position to be at the middle of the line
        midpoint = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
        rect = self.text_item.boundingRect()
        self.text_item.setPos(midpoint - QPointF(rect.width()/2, rect.height()/2))

    def set_name(self, new_name):
        """Update the name of the link"""
        self.name = new_name
        self.text_item.setText(new_name)
        self.update_position()  # Update to reposition the text

class PoseScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.dragging_joint = None
        self.links = []
        self.joints = []

    def add_joint(self, x, y):
        j = JointItem(self, x, y)
        self.addItem(j)
        self.joints.append(j)

    def add_link(self, j1, j2):
        if j1 != j2 and not self.link_exists(j1, j2):
            link = LinkItem(self, j1, j2)
            self.links.append(link)
            self.addItem(link)

    def link_exists(self, j1, j2):
        return any(
            (l.joint1 == j1 and l.joint2 == j2) or
            (l.joint1 == j2 and l.joint2 == j1)
            for l in self.links
        )

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if isinstance(item, JointItem):
            self.dragging_joint = item
        else:
            self.dragging_joint = None
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        end_item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if isinstance(end_item, JointItem) and self.dragging_joint and end_item != self.dragging_joint:
            self.add_link(self.dragging_joint, end_item)
        self.dragging_joint = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        clicked_item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if isinstance(clicked_item, JointItem):
            new_name, ok = QInputDialog.getText(self.views()[0], "Rename Joint", "Name:", text=clicked_item.name)
            if ok and new_name:
                clicked_item.set_name(new_name)
        elif isinstance(clicked_item, LinkItem):
            # Add ability to rename links
            new_name, ok = QInputDialog.getText(self.views()[0], "Rename Link", "Name:", text=clicked_item.name)
            if ok and new_name:
                clicked_item.set_name(new_name)
        else:
            pos = event.scenePos()
            self.add_joint(pos.x(), pos.y())
        super().mouseDoubleClickEvent(event)

class PoseEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag & Drop Kinematic Pose Editor")
        self.scene = PoseScene()
        self.view = QGraphicsView(self.scene)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        top_bar = QHBoxLayout()

        btn_save = QPushButton("Save Pose")
        btn_save.clicked.connect(self.save_pose)
        top_bar.addWidget(btn_save)

        layout.addLayout(top_bar)
        layout.addWidget(self.view)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.resize(800, 600)

    def save_pose(self):
        joint_data = [
            {"order": j.order, "name": j.name, "pos": (j.pos().x(), j.pos().y())}
            for j in self.scene.joints
        ]
        link_data = [
            {"order": l.order, "name": l.name,
             "joints": (self.scene.joints.index(l.joint1), self.scene.joints.index(l.joint2))}
            for l in self.scene.links
        ]
        print("Joints:", joint_data)
        print("Links:", link_data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = PoseEditor()
    editor.show()
    sys.exit(app.exec_())
