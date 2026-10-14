from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QSpinBox, QCheckBox, QGroupBox,
    QFrame, QScrollArea
)

from i18n import tr


class ControlTab(QWidget):
    """Вкладка «Управление»."""

    use_item_requested = Signal(int)

    def __init__(self, send_command, append_log):
        super().__init__()
        self.send_command = send_command
        self.append_log = append_log

        self._active_action = None
        self._combat_running = False

        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        self.lbl_active = QLabel(tr("ctrl.active_action", state=tr("ctrl.active.none")))
        self.lbl_active.setStyleSheet(
            "font-size: 12pt; font-weight: 600; color: #4a90e2; padding: 6px;"
        )
        root.addWidget(self.lbl_active)

        # Авто-удар
        combat_box = QGroupBox(tr("ctrl.combat.title"))
        combat_box.setToolTip(tr("ctrl.combat.tooltip"))
        combat_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid #f1c40f;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: 600;
                color: #f1c40f;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #f1c40f;
            }
        """)

        combat_layout = QVBoxLayout(combat_box)

        warn_label = QLabel(tr("ctrl.combat.warn"))
        warn_label.setWordWrap(True)
        warn_label.setStyleSheet(
            "color: #f1c40f; font-size: 9pt; padding: 6px; "
            "background-color: rgba(241, 196, 15, 0.1); border-radius: 4px;"
        )
        combat_layout.addWidget(warn_label)

        combat_form = QFormLayout()
        self.spin_combat_interval = QSpinBox()
        self.spin_combat_interval.setRange(100, 5000)
        self.spin_combat_interval.setValue(600)
        self.spin_combat_interval.setSuffix(" ms")

        self.spin_combat_radius = QSpinBox()
        self.spin_combat_radius.setRange(1, 6)
        self.spin_combat_radius.setValue(3)

        self.chk_ignore_players = QCheckBox(tr("ctrl.combat.ignore_players"))
        self.chk_ignore_players.setChecked(True)

        combat_form.addRow(tr("ctrl.combat.interval"), self.spin_combat_interval)
        combat_form.addRow(tr("ctrl.combat.radius"), self.spin_combat_radius)
        combat_form.addRow("", self.chk_ignore_players)
        combat_layout.addLayout(combat_form)

        combat_btns = QHBoxLayout()
        self.btn_combat_start = QPushButton(tr("ctrl.combat.start"))
        self.btn_combat_start.setObjectName("primary")
        self.btn_combat_start.setMinimumHeight(36)
        self.btn_combat_stop = QPushButton(tr("ctrl.combat.stop"))
        self.btn_combat_stop.setObjectName("danger")
        self.btn_combat_stop.setMinimumHeight(36)
        self.btn_combat_stop.setEnabled(False)
        combat_btns.addWidget(self.btn_combat_start)
        combat_btns.addWidget(self.btn_combat_stop)
        combat_btns.addStretch(1)
        combat_layout.addLayout(combat_btns)

        root.addWidget(combat_box)

        # Копание
        dig_box = QGroupBox(tr("ctrl.dig.title"))
        dig_layout = QVBoxLayout(dig_box)

        dig_form = QFormLayout()
        self.spin_dig_x = QSpinBox(); self.spin_dig_x.setRange(-30000000, 30000000)
        self.spin_dig_y = QSpinBox(); self.spin_dig_y.setRange(-64, 320)
        self.spin_dig_z = QSpinBox(); self.spin_dig_z.setRange(-30000000, 30000000)
        dig_form.addRow(tr("ctrl.dig.x"), self.spin_dig_x)
        dig_form.addRow(tr("ctrl.dig.y"), self.spin_dig_y)
        dig_form.addRow(tr("ctrl.dig.z"), self.spin_dig_z)
        dig_layout.addLayout(dig_form)

        dig_btns = QHBoxLayout()
        self.btn_dig_start = QPushButton(tr("ctrl.combat.start"))
        self.btn_dig_start.setObjectName("primary")
        self.btn_dig_start.setMinimumHeight(36)
        self.btn_dig_stop = QPushButton(tr("ctrl.combat.stop"))
        self.btn_dig_stop.setObjectName("danger")
        self.btn_dig_stop.setMinimumHeight(36)
        self.btn_dig_stop.setEnabled(False)
        dig_btns.addWidget(self.btn_dig_start)
        dig_btns.addWidget(self.btn_dig_stop)
        dig_btns.addStretch(1)
        dig_layout.addLayout(dig_btns)

        root.addWidget(dig_box)

        # Поворот
        look_box = QGroupBox(tr("ctrl.look.title"))
        look_layout = QVBoxLayout(look_box)

        look_form = QFormLayout()
        self.spin_look_x = QSpinBox(); self.spin_look_x.setRange(-30000000, 30000000)
        self.spin_look_y = QSpinBox(); self.spin_look_y.setRange(-64, 320)
        self.spin_look_z = QSpinBox(); self.spin_look_z.setRange(-30000000, 30000000)
        look_form.addRow(tr("ctrl.look.x"), self.spin_look_x)
        look_form.addRow(tr("ctrl.look.y"), self.spin_look_y)
        look_form.addRow(tr("ctrl.look.z"), self.spin_look_z)
        look_layout.addLayout(look_form)

        self.btn_look = QPushButton(tr("ctrl.look.btn"))
        self.btn_look.setObjectName("primary")
        self.btn_look.setMinimumHeight(36)
        self.btn_look.setMaximumWidth(200)
        look_layout.addWidget(self.btn_look, alignment=Qt.AlignLeft)

        root.addWidget(look_box)
        root.addStretch(1)

        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.btn_combat_start.clicked.connect(self._on_combat_start)
        self.btn_combat_stop.clicked.connect(self._on_combat_stop)
        self.btn_dig_start.clicked.connect(self._on_dig_start)
        self.btn_dig_stop.clicked.connect(self._on_dig_stop)
        self.btn_look.clicked.connect(self._on_look)

    def set_active_action(self, action):
        self._active_action = action
        labels = {
            None: tr("ctrl.active.none"),
            "combat": tr("ctrl.active.combat"),
            "dig": tr("ctrl.active.dig"),
            "look": tr("ctrl.active.look"),
        }
        self.lbl_active.setText(tr("ctrl.active_action",
                                   state=labels.get(action, tr("ctrl.active.none"))))

    def _on_combat_start(self):
        self.send_command("combat_config", {
            "interval_ms": self.spin_combat_interval.value(),
            "radius": self.spin_combat_radius.value(),
            "ignore_players": self.chk_ignore_players.isChecked(),
        })
        self.send_command("combat_start", {})
        self._combat_running = True
        self.btn_combat_start.setEnabled(False)
        self.btn_combat_stop.setEnabled(True)
        self.set_active_action("combat")
        self.append_log("INFO", tr("ctrl.log.combat_start"))

    def _on_combat_stop(self):
        self.send_command("combat_stop", {})
        self._combat_running = False
        self.btn_combat_start.setEnabled(True)
        self.btn_combat_stop.setEnabled(False)
        if self._active_action == "combat":
            self.set_active_action(None)
        self.append_log("INFO", tr("ctrl.log.combat_stop"))

    def _on_dig_start(self):
        self.send_command("dig_start", {
            "x": self.spin_dig_x.value(),
            "y": self.spin_dig_y.value(),
            "z": self.spin_dig_z.value(),
        })
        self.btn_dig_start.setEnabled(False)
        self.btn_dig_stop.setEnabled(True)
        self.set_active_action("dig")
        self.append_log("INFO", tr("ctrl.log.dig_start",
                                   x=self.spin_dig_x.value(),
                                   y=self.spin_dig_y.value(),
                                   z=self.spin_dig_z.value()))

    def _on_dig_stop(self):
        self.send_command("dig_stop", {})
        self.btn_dig_start.setEnabled(True)
        self.btn_dig_stop.setEnabled(False)
        if self._active_action == "dig":
            self.set_active_action(None)
        self.append_log("INFO", tr("ctrl.log.dig_stop"))

    def _on_look(self):
        self.send_command("look_at", {
            "x": self.spin_look_x.value(),
            "y": self.spin_look_y.value(),
            "z": self.spin_look_z.value(),
        })
        self.append_log("INFO", tr("ctrl.log.look",
                                   x=self.spin_look_x.value(),
                                   y=self.spin_look_y.value(),
                                   z=self.spin_look_z.value()))

    def on_combat_status(self, payload: dict):
        enabled = bool(payload.get("enabled", False))
        self._combat_running = enabled
        self.btn_combat_start.setEnabled(not enabled)
        self.btn_combat_stop.setEnabled(enabled)
        if enabled:
            self.set_active_action("combat")
        elif self._active_action == "combat":
            self.set_active_action(None)

    def on_dig_status(self, payload: dict):
        active = bool(payload.get("active", False))
        self.btn_dig_start.setEnabled(not active)
        self.btn_dig_stop.setEnabled(active)
        if active:
            self.set_active_action("dig")
        elif self._active_action == "dig":
            self.set_active_action(None)