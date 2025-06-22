from PyQt5.QtWidgets import QGraphicsItem, QInputDialog, QColorDialog, QMenu
from PyQt5.QtGui import QPen, QBrush, QPolygonF, QPainterPath, QColor
from PyQt5.QtCore import Qt, QPointF, QRectF
import math
from node_element import VisualNode
from edge_element import VisualHyperedge

class VisualGraphConnection(QGraphicsItem):
    def __init__(self, source, target, value=None):
        super().__init__()
        # Ensure source and target are either Node or Hyperedge
        if not ((isinstance(source, VisualNode) and isinstance(target, VisualHyperedge)) or
                (isinstance(source, VisualHyperedge) and isinstance(target, VisualNode))):
            raise ValueError("Connections must be between a Node and a Hyperedge.")
        self.source = source
        self.target = target
        self.value = value
        self.source.connections.append(self)
        self.target.connections.append(self)
        self.arrow_size = 10
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setZValue(1000)
        self.path = QPainterPath()
        self.arrow_head = QPolygonF()
        self.color = Qt.black
        self.direction_normal = True  # True: source->target, False: target->source
        self.updatePosition()

    @staticmethod
    def _ellipse_edge_point_static(center, rx, ry, toward):
        """Return the point on the ellipse boundary from center toward 'toward'."""
        dx = toward.x() - center.x()
        dy = toward.y() - center.y()
        if dx == 0 and dy == 0:
            return center
        angle = math.atan2(dy, dx)
        bx = center.x() + rx * math.cos(angle)
        by = center.y() + ry * math.sin(angle)
        return QPointF(bx, by)

    @staticmethod
    def _rect_edge_point_static(center, w, h, toward):
        """Return the point on the rectangle boundary from center toward 'toward'."""
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

    def mapToSceneRectBoundary(self, item, toward_point):
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

    def updatePosition(self):
        self.prepareGeometryChange()
        # Handle directionality
        if self.direction_normal:
            resolved_source = self.source
            resolved_target = self.target
        else:
            resolved_source = self.target
            resolved_target = self.source

        source_rect = resolved_source.boundingRect()
        target_rect = resolved_target.boundingRect()
        source_center_scene = resolved_source.mapToScene(QPointF(source_rect.width() / 2, source_rect.height() / 2))
        target_center_scene = resolved_target.mapToScene(QPointF(target_rect.width() / 2, target_rect.height() / 2))

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
        if self.path.isEmpty():
            return QRectF()
        return self.path.boundingRect().adjusted(-self.arrow_size, -self.arrow_size, self.arrow_size, self.arrow_size)

    def paint(self, painter, option, widget):
        if self.path.isEmpty():
            return
        if self.isSelected():
            pen = QPen(QColor(self.color), 3, Qt.SolidLine)
        else:
            pen = QPen(QColor(self.color), 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawPath(self.path)
        painter.setBrush(QBrush(QColor(self.color)))
        painter.drawPolygon(self.arrow_head)
        # Draw value if present, on the arrow
        if self.value is not None:
            # Draw the value at 2/3 along the arrow, slightly offset above the line
            pos = self.path.pointAtPercent(0.66)
            # Calculate a perpendicular offset for better visibility
            if self.path.length() > 0:
                angle = self.path.angleAtPercent(0.66)
                dx = 10 * -math.sin(math.radians(angle))
                dy = 10 * -math.cos(math.radians(angle))
                pos = QPointF(pos.x() + dx, pos.y() + dy)
            painter.setPen(Qt.darkBlue)
            painter.drawText(pos, str(self.value))

    def mouseDoubleClickEvent(self, event):
        value, ok = QInputDialog.getText(None, "Set Connection Value", "Enter value:", text=str(self.value) if self.value is not None else "")
        if ok:
            self.value = value
            self.update()
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu()
        direction_action = menu.addAction("Toggle Direction")
        color_action = menu.addAction("Change Color...")
        selected_action = menu.exec_(event.screenPos())
        if selected_action == direction_action:
            self.direction_normal = not self.direction_normal
            self.updatePosition()
            self.update()
        elif selected_action == color_action:
            color = QColorDialog.getColor(QColor(self.color))
            if color.isValid():
                self.color = color
                self.update()
        else:
            super().contextMenuEvent(event)
