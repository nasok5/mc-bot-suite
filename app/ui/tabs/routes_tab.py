import time
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QCheckBox, QGroupBox,
    QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QInputDialog, QAbstractItemView
)

from i18n import tr


class RoutesTab(QWidget):
    """Вкладка управления маршрутами."""

    def __init__(self, storage, send_command, append_log):
        super().__init__()
        self.storage = storage
        self.send_command = send_command
        self.append_log = append_log

        self.routes_data = self.storage.load("routes")
        self.current_index = -1

        self._build_ui()
        self._reload_routes_list()

    def _build_ui(self):
        root = QHBoxLayout(self)

        # ---------- Левая часть: список ----------
        left = QVBoxLayout()
        left.addWidget(QLabel(tr("routes.saved")))

        self.list_routes = QListWidget()
        self.list_routes.currentRowChanged.connect(self._on_route_selected)
        left.addWidget(self.list_routes)

        btn_row = QHBoxLayout()
        self.btn_new = QPushButton(tr("routes.create"))
        self.btn_del = QPushButton(tr("routes.delete"))
        self.btn_del.setObjectName("danger")
        btn_row.addWidget(self.btn_new)
        btn_row.addWidget(self.btn_del)
        left.addLayout(btn_row)

        self.btn_new.clicked.connect(self._create_route)
        self.btn_del.clicked.connect(self._delete_route)

        left_box = QWidget()
        left_box.setLayout(left)
        left_box.setMaximumWidth(280)
        root.addWidget(left_box)

        # ---------- Правая часть: редактор ----------
        right = QVBoxLayout()

        self.editor_box = QGroupBox(tr("routes.editor"))
        editor_layout = QVBoxLayout(self.editor_box)

        meta_form = QFormLayout()
        self.inp_name = QLineEdit()
        self.chk_loop = QCheckBox(tr("routes.loop"))
        self.chk_return_home = QCheckBox(tr("routes.return_home"))
        meta_form.addRow(tr("routes.name"), self.inp_name)
        meta_form.addRow("", self.chk_loop)
        meta_form.addRow("", self.chk_return_home)
        editor_layout.addLayout(meta_form)

        editor_layout.addWidget(QLabel(tr("routes.points")))
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            tr("routes.point_name"), "X", "Y", "Z"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 4):
            self.table.horizontalHeader().setSectionResizeMode(
                c, QHeaderView.ResizeToContents
            )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        editor_layout.addWidget(self.table)

        pt_btns = QHBoxLayout()
        self.btn_add_point = QPushButton(tr("routes.add_point"))
        self.btn_up = QPushButton("↑")
        self.btn_down = QPushButton("↓")
        self.btn_del_point = QPushButton(tr("routes.delete_point"))
        self.btn_del_point.setObjectName("danger")
        pt_btns.addWidget(self.btn_add_point)
        pt_btns.addWidget(self.btn_up)
        pt_btns.addWidget(self.btn_down)
        pt_btns.addStretch(1)
        pt_btns.addWidget(self.btn_del_point)
        editor_layout.addLayout(pt_btns)

        self.btn_add_point.clicked.connect(self._add_point)
        self.btn_up.clicked.connect(lambda: self._move_point(-1))
        self.btn_down.clicked.connect(lambda: self._move_point(+1))
        self.btn_del_point.clicked.connect(self._delete_point)

        act_row = QHBoxLayout()
        self.btn_save = QPushButton(tr("routes.save"))
        self.btn_save.setObjectName("primary")
        self.btn_start = QPushButton(tr("routes.start"))
        self.btn_start.setObjectName("primary")
        self.btn_pause = QPushButton(tr("routes.pause"))
        self.btn_resume = QPushButton(tr("routes.resume"))
        self.btn_stop = QPushButton(tr("routes.stop"))
        self.btn_stop.setObjectName("danger")
        act_row.addWidget(self.btn_save)
        act_row.addStretch(1)
        act_row.addWidget(self.btn_start)
        act_row.addWidget(self.btn_pause)
        act_row.addWidget(self.btn_resume)
        act_row.addWidget(self.btn_stop)
        editor_layout.addLayout(act_row)

        self.btn_save.clicked.connect(self._save_current)
        self.btn_start.clicked.connect(self._start_current)
        self.btn_pause.clicked.connect(lambda: self.send_command("pause"))
        self.btn_resume.clicked.connect(lambda: self.send_command("resume"))
        self.btn_stop.clicked.connect(lambda: self.send_command("stop"))

        right.addWidget(self.editor_box)
        root.addLayout(right)

        self._set_editor_enabled(False)

    def _reload_routes_list(self):
        self.list_routes.clear()
        for r in self.routes_data["routes"]:
            label = tr("routes.route_label", name=r['name'], n=len(r['points']))
            self.list_routes.addItem(QListWidgetItem(label))
        if self.routes_data["routes"]:
            self.list_routes.setCurrentRow(0)

    def _on_route_selected(self, row: int):
        self.current_index = row
        if row < 0 or row >= len(self.routes_data["routes"]):
            self._set_editor_enabled(False)
            return

        r = self.routes_data["routes"][row]
        self.inp_name.setText(r["name"])
        self.chk_loop.setChecked(bool(r.get("loop", False)))
        self.chk_return_home.setChecked(bool(r.get("return_home", False)))

        self.table.setRowCount(0)
        for pt in r.get("points", []):
            self._append_point_row(pt["name"], pt["x"], pt["y"], pt["z"])

        self._set_editor_enabled(True)

    def _set_editor_enabled(self, enabled: bool):
        self.editor_box.setEnabled(enabled)

    def _create_route(self):
        name, ok = QInputDialog.getText(
            self, tr("routes.new_title"), tr("routes.new_prompt")
        )
        if not ok or not name.strip():
            return
        new_route = {
            "id": f"route-{int(time.time() * 1000)}",
            "name": name.strip(),
            "loop": False,
            "return_home": False,
            "points": []
        }
        self.routes_data["routes"].append(new_route)
        self._persist()
        self._reload_routes_list()
        self.list_routes.setCurrentRow(len(self.routes_data["routes"]) - 1)

    def _delete_route(self):
        if self.current_index < 0:
            return
        name = self.routes_data["routes"][self.current_index]["name"]
        reply = QMessageBox.question(
            self, tr("routes.delete_title"),
            tr("routes.delete_prompt", name=name),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        del self.routes_data["routes"][self.current_index]
        self._persist()
        self._reload_routes_list()

    def _add_point(self):
        if self.current_index < 0:
            return
        name, ok = QInputDialog.getText(
            self, tr("routes.new_point"), tr("routes.new_point_prompt")
        )
        if not ok:
            return
        self._append_point_row(name.strip() or "Point", 0, 64, 0)

    def _append_point_row(self, name: str, x, y, z):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(name)))
        self.table.setItem(row, 1, QTableWidgetItem(str(int(x))))
        self.table.setItem(row, 2, QTableWidgetItem(str(int(y))))
        self.table.setItem(row, 3, QTableWidgetItem(str(int(z))))

    def _move_point(self, delta: int):
        row = self.table.currentRow()
        if row < 0:
            return
        new_row = row + delta
        if not (0 <= new_row < self.table.rowCount()):
            return
        values_a = [self.table.item(row, c).text() for c in range(4)]
        values_b = [self.table.item(new_row, c).text() for c in range(4)]
        for c in range(4):
            self.table.item(row, c).setText(values_b[c])
            self.table.item(new_row, c).setText(values_a[c])
        self.table.setCurrentCell(new_row, 0)

    def _delete_point(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def _collect_route_from_editor(self):
        if self.current_index < 0:
            return None
        points = []
        for row in range(self.table.rowCount()):
            try:
                name = self.table.item(row, 0).text().strip() or f"Point {row + 1}"
                x = int(self.table.item(row, 1).text())
                y = int(self.table.item(row, 2).text())
                z = int(self.table.item(row, 3).text())
            except (AttributeError, ValueError):
                QMessageBox.warning(
                    self, tr("routes.error_title"),
                    tr("routes.error_coords", row=row + 1)
                )
                return None
            points.append({"name": name, "x": x, "y": y, "z": z})

        return {
            "name": self.inp_name.text().strip() or "Route",
            "loop": self.chk_loop.isChecked(),
            "return_home": self.chk_return_home.isChecked(),
            "points": points,
        }

    def _save_current(self):
        data = self._collect_route_from_editor()
        if data is None:
            return
        existing = self.routes_data["routes"][self.current_index]
        existing.update(data)
        self._persist()
        self._reload_routes_list()
        self.list_routes.setCurrentRow(self.current_index)

    def _start_current(self):
        data = self._collect_route_from_editor()
        if data is None:
            return
        if not data["points"]:
            QMessageBox.warning(
                self, tr("routes.empty_title"), tr("routes.empty_msg")
            )
            return
        self.send_command("route", data)

    def _persist(self):
        self.storage.save("routes", self.routes_data)