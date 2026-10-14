from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPolygonF
from PySide6.QtWidgets import QWidget
from i18n import tr

class MinimapWidget(QWidget):
    """2D-карта: позиция бота, точки маршрута, линия, направление, трек пути."""

    BG = QColor("#0d1b2a")
    GRID = QColor("#1b263b")
    GRID_MAJOR = QColor("#2f4f7f")
    TEXT = QColor("#8fa3bf")
    ROUTE_LINE = QColor("#4a90e2")
    TRACK_LINE = QColor("#f1c40f")
    POINT_PAST = QColor("#5a6b80")
    POINT_FUTURE = QColor("#4a90e2")
    POINT_CURRENT = QColor("#f1c40f")
    POINT_HOME = QColor("#e74c3c")
    BOT = QColor("#2ecc71")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.setStyleSheet("background-color: #0d1b2a;")

        self.bot_pos = None
        self.bot_yaw = None
        self.route_points = []
        self.route_index = -1
        self.home_point = None
        self.active = False
        self.track = []          # [{x, z}]

        self._transform = None
        self._bounds = None

    # ---------- публичное API ----------

    def set_bot_position(self, x: float, y: float, z: float):
        self.bot_pos = (float(x), float(z))
        self.update()

    def set_bot_yaw(self, yaw_rad: float):
        self.bot_yaw = yaw_rad
        self.update()

    def set_route(self, points: list, home=None):
        self.route_points = [
            {"name": p.get("name", ""), "x": float(p["x"]), "z": float(p["z"])}
            for p in points
        ]
        self.home_point = home
        self.route_index = -1
        self.active = bool(points)
        self.update()

    def set_active_point(self, index: int):
        self.route_index = index
        self.update()

    def set_track(self, track: list):
        """track: [{"x": int, "z": int}]"""
        if not track:
            self.track = []
        else:
            self.track = [{"x": float(p["x"]), "z": float(p["z"])} for p in track]
        self.update()

    def clear_route(self):
        self.route_points = []
        self.route_index = -1
        self.home_point = None
        self.active = False
        self.update()

    def clear_track(self):
        self.track = []
        self.update()

    # ---------- отрисовка ----------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), self.BG)

        if not self.bot_pos and not self.route_points and not self.track:
            self._draw_placeholder(painter)
            return

        self._compute_transform()
        if self._transform is None:
            self._draw_placeholder(painter)
            return

        self._draw_grid(painter)
        self._draw_track(painter)
        if self.route_points:
            self._draw_route_line(painter)
            self._draw_route_points(painter)
        if self.home_point:
            self._draw_home_point(painter)
        if self.bot_pos:
            self._draw_bot(painter)

    def _draw_placeholder(self, painter):
        painter.setPen(self.TEXT)
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(self.rect(), Qt.AlignCenter, tr("map.placeholder"))

    def _compute_transform(self):
        xs, zs = [], []
        if self.bot_pos:
            xs.append(self.bot_pos[0])
            zs.append(self.bot_pos[1])
        for p in self.route_points:
            xs.append(p["x"])
            zs.append(p["z"])
        for p in self.track:
            xs.append(p["x"])
            zs.append(p["z"])
        if self.home_point:
            xs.append(self.home_point[0])
            zs.append(self.home_point[1])

        if not xs:
            self._transform = None
            return

        min_x, max_x = min(xs), max(xs)
        min_z, max_z = min(zs), max(zs)
        span_x = max(max_x - min_x, 20)
        span_z = max(max_z - min_z, 20)

        padding = 40
        avail_w = max(self.width() - padding * 2, 50)
        avail_h = max(self.height() - padding * 2, 50)

        scale = min(avail_w / span_x, avail_h / span_z)
        cx = (min_x + max_x) / 2
        cz = (min_z + max_z) / 2

        self._bounds = (min_x, max_x, min_z, max_z)
        self._transform = {"scale": scale, "cx": cx, "cz": cz}

    def _world_to_screen(self, wx: float, wz: float) -> QPointF:
        t = self._transform
        if t is None:
            return QPointF(0, 0)
        sx = self.width() / 2 + (wx - t["cx"]) * t["scale"]
        sy = self.height() / 2 - (wz - t["cz"]) * t["scale"]
        return QPointF(sx, sy)

    def _draw_grid(self, painter):
        t = self._transform
        if t is None:
            return
        scale = t["scale"]

        for step in (5, 10, 20, 50, 100):
            if step * scale >= 40:
                grid_step = step
                break
        else:
            grid_step = 100

        painter.setPen(QPen(self.GRID, 1))
        min_x, max_x, min_z, max_z = self._bounds
        x = int(min_x // grid_step) * grid_step
        while x <= max_x + grid_step:
            p1 = self._world_to_screen(x, min_z - grid_step)
            p2 = self._world_to_screen(x, max_z + grid_step)
            painter.drawLine(p1, p2)
            x += grid_step

        z = int(min_z // grid_step) * grid_step
        while z <= max_z + grid_step:
            p1 = self._world_to_screen(min_x - grid_step, z)
            p2 = self._world_to_screen(max_x + grid_step, z)
            painter.drawLine(p1, p2)
            z += grid_step

        painter.setPen(QPen(self.GRID_MAJOR, 2))
        if min_x <= 0 <= max_x:
            p1 = self._world_to_screen(0, min_z - grid_step)
            p2 = self._world_to_screen(0, max_z + grid_step)
            painter.drawLine(p1, p2)
        if min_z <= 0 <= max_z:
            p1 = self._world_to_screen(min_x - grid_step, 0)
            p2 = self._world_to_screen(max_x + grid_step, 0)
            painter.drawLine(p1, p2)

        painter.setPen(self.TEXT)
        painter.setFont(QFont("Consolas", 8))
        painter.drawText(10, self.height() - 10,
                         tr("map.grid_step", step=grid_step))

    def _draw_track(self, painter):
        if len(self.track) < 2:
            return
        # Полупрозрачная жёлтая линия
        color = QColor(self.TRACK_LINE)
        color.setAlpha(180)
        pen = QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        pts = [self._world_to_screen(p["x"], p["z"]) for p in self.track]
        for i in range(len(pts) - 1):
            painter.drawLine(pts[i], pts[i + 1])

    def _draw_route_line(self, painter):
        if len(self.route_points) < 2:
            return
        painter.setPen(QPen(self.ROUTE_LINE, 2, Qt.DashLine))
        pts = [self._world_to_screen(p["x"], p["z"]) for p in self.route_points]
        for i in range(len(pts) - 1):
            painter.drawLine(pts[i], pts[i + 1])

    def _draw_route_points(self, painter):
        font = QFont("Segoe UI", 8)
        for i, p in enumerate(self.route_points):
            pt = self._world_to_screen(p["x"], p["z"])

            if i == self.route_index:
                color = self.POINT_CURRENT
                radius = 8
            elif i < self.route_index:
                color = self.POINT_PAST
                radius = 5
            else:
                color = self.POINT_FUTURE
                radius = 6

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#0d1b2a"), 2))
            painter.drawEllipse(pt, radius, radius)

            painter.setPen(QColor("#0d1b2a"))
            painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
            painter.drawText(
                QRectF(pt.x() - 8, pt.y() - 8, 16, 16),
                Qt.AlignCenter,
                str(i + 1)
            )

            if p.get("name"):
                painter.setPen(self.TEXT)
                painter.setFont(font)
                painter.drawText(
                    QRectF(pt.x() - 60, pt.y() + 10, 120, 14),
                    Qt.AlignHCenter | Qt.AlignTop,
                    p["name"]
                )

    def _draw_home_point(self, painter):
        pt = self._world_to_screen(*self.home_point)
        painter.setBrush(QBrush(self.POINT_HOME))
        painter.setPen(QPen(QColor("#0d1b2a"), 2))
        poly = QPolygonF([
            QPointF(pt.x(), pt.y() - 7),
            QPointF(pt.x() + 7, pt.y()),
            QPointF(pt.x(), pt.y() + 7),
            QPointF(pt.x() - 7, pt.y()),
        ])
        painter.drawPolygon(poly)
        painter.setPen(self.TEXT)
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(
            QRectF(pt.x() - 40, pt.y() + 10, 80, 14),
            Qt.AlignHCenter | Qt.AlignTop,
            tr("map.home")
        )

    def _draw_bot(self, painter):
        pt = self._world_to_screen(*self.bot_pos)

        painter.setBrush(QBrush(self.BOT))
        painter.setPen(QPen(QColor("#0d1b2a"), 2))
        painter.drawEllipse(pt, 7, 7)

        if self.bot_yaw is not None:
            import math
            length = 16
            dx = math.sin(self.bot_yaw) * length
            dy = -math.cos(self.bot_yaw) * length
            painter.setPen(QPen(self.BOT, 3))
            painter.drawLine(pt, QPointF(pt.x() + dx, pt.y() + dy))

        painter.setPen(self.TEXT)
        painter.setFont(QFont("Consolas", 8))
        painter.drawText(
            QRectF(pt.x() + 12, pt.y() - 10, 120, 16),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"({int(self.bot_pos[0])}, {int(self.bot_pos[1])})"
        )