import math
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPen, QColor, QBrush
from enum import Enum

from node_element import VisualNode

class EditorState(Enum):
    SELECT = 1
    ADD_NODE = 2
    ADD_HYPEREDGE = 3
    ADD_CONNECTION = 4
    ADD_ATTRIBUTE = 5

def ellipse_edge_point(center, rx, ry, toward):
    dx = toward.x() - center.x()
    dy = toward.y() - center.y()
    if dx == 0 and dy == 0:
        return center
    angle = math.atan2(dy, dx)
    bx = center.x() + rx * math.cos(angle)
    by = center.y() + ry * math.sin(angle)
    return QPointF(bx, by)

def rect_edge_point(center, w, h, toward):
    dx = toward.x() - center.x()
    dy = toward.y() - center.y()
    if dx == 0 and dy == 0:
        return center
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    if abs_dx * h > abs_dy * w:
        scale = (w / 2) / abs_dx
    else:
        scale = (h / 2) / abs_dy
    bx = center.x() + dx * scale
    by = center.y() + dy * scale
    return QPointF(bx, by)

def map_to_scene_rect_boundary(item, toward_point):
    rect = item.boundingRect()
    center_local = QPointF(rect.width() / 2, rect.height() / 2)
    center_scene = item.mapToScene(center_local)
    dx = toward_point.x() - center_scene.x()
    dy = toward_point.y() - center_scene.y()
    if dx == 0 and dy == 0:
        return center_scene
    angle = math.atan2(dy, dx)
    if isinstance(item, VisualNode):
        rx = rect.width() / 2
        ry = rect.height() / 2
        bx = center_scene.x() + rx * math.cos(angle)
        by = center_scene.y() + ry * math.sin(angle)
        return QPointF(bx, by)
    else:
        w = rect.width()
        h = rect.height()
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        if abs_dx * h > abs_dy * w:
            scale = (w / 2) / abs_dx
        else:
            scale = (h / 2) / abs_dy
        bx = center_scene.x() + dx * scale
        by = center_scene.y() + dy * scale
        return QPointF(bx, by)

def draw_grid_background(painter, rect, ox=0, oy=0, show_grid=True, show_axis=True):
    # Draw grid
    grid_size = 40
    if show_grid:
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        right = int(rect.right())
        bottom = int(rect.bottom())
        painter.setPen(QPen(QColor(230, 230, 230), 1))
        for x in range(left, right, grid_size):
            painter.drawLine(int(x), int(top), int(x), int(bottom))
        for y in range(top, bottom, grid_size):
            painter.drawLine(int(left), int(y), int(right), int(y))
    # Draw axes
    if show_axis:
        painter.setPen(QPen(QColor(0, 120, 0), 2))
        painter.drawLine(ox, int(rect.top()), ox, int(rect.bottom()))  # Y axis
        painter.setPen(QPen(QColor(180, 0, 0), 2))
        painter.drawLine(int(rect.left()), oy, int(rect.right()), oy)  # X axis
        # Draw origin point
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(QPointF(0, 0), 4, 4)

class ViewportController:
    def __init__(self, view):
        self.view = view
        self.zoom_factor = 1.0

    def zoom(self, factor, center=None):
        self.zoom_factor *= factor
        self.view.scale(factor, factor)
        if center is not None:
            self.view.centerOn(center)

    def pan(self, dx, dy):
        # Adjust panning by zoom factor, ensure integer values for scrollbars
        hbar = self.view.horizontalScrollBar()
        vbar = self.view.verticalScrollBar()
        hbar.setValue(int(hbar.value() - int(round(dx))))
        vbar.setValue(int(vbar.value() - int(round(dy))))

    def reset_zoom(self):
        self.view.resetTransform()
        self.zoom_factor = 1.0