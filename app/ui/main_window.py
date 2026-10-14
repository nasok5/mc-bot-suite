import base64
import random
import re
import sys
import os

from PySide6.QtCore import Qt, QDateTime, QTimer, QByteArray
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QCloseEvent, QColor
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox, QComboBox, QCheckBox,
    QProgressBar, QGroupBox, QTabWidget, QPlainTextEdit,
    QMessageBox, QStatusBar, QFormLayout, QListWidget, QListWidgetItem,
    QInputDialog, QColorDialog, QScrollArea, QApplication
)

from core.state import BotState
from core.events import bus
from modules.storage import Storage
from modules.theme import build_qss, theme_display_names
from i18n import tr, set_language, get_language
from ui.tabs.routes_tab import RoutesTab
from ui.tabs.messages_tab import MessagesTab
from ui.tabs.inventory_tab import InventoryTab
from ui.tabs.control_tab import ControlTab
from ui.widgets.toast import show_toast
from ui.widgets.minimap import MinimapWidget


HOST_RE = re.compile(r"^[a-zA-Z0-9\.\-_]+$")


class MainWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.state_model = BotState()
        self.storage = Storage()
        self.settings = self.storage.load("settings")
        self.nicks_data = self.storage.load("nicks")
        self.stats_data = self.storage.load("statistics")

        self._safety_active = False
        self._settings_dirty = False
        self._current_route_points = []
        self._current_route_home = None
        self._current_route_index = -1

        self.setWindowTitle(tr("app.title"))
        self.resize(1280, 840)

        self._build_ui()
        self._wire_events()
        self._setup_shortcuts()
        self._load_settings_into_ui()
        self._load_nicks_into_ui()
        self._restore_window_state()
        self._refresh_dashboard()
        self._refresh_statistics()

        QTimer.singleShot(500, self._push_chat_config)

        if self.settings["minecraft"].get("auto_connect_on_start", False):
            self._append_log("INFO", tr("misc.connected"))
            QTimer.singleShot(1500, self._on_connect)

    # ---------- построение интерфейса ----------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        title = QLabel(tr("app.header"))
        title.setStyleSheet("font-size: 18pt; font-weight: 700;")
        root.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_dashboard_tab(), tr("tab.dashboard"))
        self.tabs.addTab(self._build_map_tab(), tr("tab.map"))

        self.routes_tab = RoutesTab(
            storage=self.storage,
            send_command=self._send,
            append_log=self._append_log,
        )
        self.tabs.addTab(self.routes_tab, tr("tab.routes"))

        self.messages_tab = MessagesTab(
            storage=self.storage,
            send_chat_config=lambda cfg: self._send("chat_config", cfg),
            append_log=self._append_log,
            send_manual_chat=lambda text: self._send("chat", {"message": text}),
        )
        self.tabs.addTab(self.messages_tab, tr("tab.messages"))

        self.inventory_tab = InventoryTab(
            send_command=self._send,
            append_log=self._append_log,
            storage=self.storage,
        )
        self.tabs.addTab(self.inventory_tab, tr("tab.inventory"))

        self.control_tab = ControlTab(
            send_command=self._send,
            append_log=self._append_log,
        )
        self.tabs.addTab(self.control_tab, tr("tab.control"))

        self.tabs.addTab(self._build_statistics_tab(), tr("tab.statistics"))
        self.tabs.addTab(self._build_settings_tab(), tr("tab.settings"))
        self.tabs.addTab(self._build_log_tab(), tr("tab.log"))
        root.addWidget(self.tabs)

        self.setStatusBar(QStatusBar())
        self.ws_indicator = QLabel("⚫ " + tr("misc.disconnected"))
        self.statusBar().addPermanentWidget(self.ws_indicator)

    def _build_dashboard_tab(self) -> QWidget:
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        w = QVBoxLayout(content)
        w.setContentsMargins(10, 10, 10, 10)
        w.setSpacing(10)

        status_card = QGroupBox(tr("panel.status"))
        grid = QGridLayout(status_card)
        self.lbl_status = QLabel(tr("status.disconnected"))
        self.lbl_status.setObjectName("value")
        self.lbl_nick = QLabel("—")
        self.lbl_version = QLabel("1.21.4")
        grid.addWidget(QLabel(tr("field.connection")), 0, 0)
        grid.addWidget(self.lbl_status, 0, 1)
        grid.addWidget(QLabel(tr("field.nick")), 1, 0)
        grid.addWidget(self.lbl_nick, 1, 1)
        grid.addWidget(QLabel(tr("field.version")), 2, 0)
        grid.addWidget(self.lbl_version, 2, 1)
        w.addWidget(status_card)

        state_card = QGroupBox(tr("panel.state"))
        sgrid = QGridLayout(state_card)
        self.lbl_health = QLabel("❤️ 0.0/20")
        self.bar_health = QProgressBar()
        self.bar_health.setObjectName("health")
        self.bar_health.setRange(0, 20)
        self.bar_health.setTextVisible(False)
        self.lbl_food = QLabel("🍖 0.0/20")
        self.bar_food = QProgressBar()
        self.bar_food.setObjectName("food")
        self.bar_food.setRange(0, 20)
        self.bar_food.setTextVisible(False)
        self.lbl_pos = QLabel(tr("field.position", x=0, y=0, z=0))
        self.lbl_pos.setObjectName("value")
        self.lbl_pos.setToolTip(tr("misc.coords_copied"))
        self.lbl_pos.mouseDoubleClickEvent = lambda e: self._copy_coords()
        sgrid.addWidget(self.lbl_health, 0, 0)
        sgrid.addWidget(self.bar_health, 0, 1)
        sgrid.addWidget(self.lbl_food, 1, 0)
        sgrid.addWidget(self.bar_food, 1, 1)
        sgrid.addWidget(self.lbl_pos, 2, 0, 1, 2)
        w.addWidget(state_card)

        task_card = QGroupBox(tr("panel.task"))
        tlay = QVBoxLayout(task_card)
        self.lbl_task = QLabel(tr("field.task.default"))
        self.lbl_task.setObjectName("value")
        tlay.addWidget(self.lbl_task)
        w.addWidget(task_card)

        ctrl_card = QGroupBox(tr("panel.control"))
        cgrid = QHBoxLayout(ctrl_card)
        self.btn_connect = QPushButton(tr("btn.connect"))
        self.btn_connect.setObjectName("primary")
        self.btn_start = QPushButton(tr("btn.start"))
        self.btn_pause = QPushButton(tr("btn.pause"))
        self.btn_resume = QPushButton(tr("btn.resume"))
        self.btn_stop = QPushButton(tr("btn.stop"))
        self.btn_disconnect = QPushButton(tr("btn.disconnect"))
        self.btn_disconnect.setObjectName("danger")
        for b in (self.btn_connect, self.btn_start, self.btn_pause,
                  self.btn_resume, self.btn_stop, self.btn_disconnect):
            cgrid.addWidget(b)
        w.addWidget(ctrl_card)

        # ===== Внешний вид =====
        theme_box = QGroupBox(tr("panel.appearance"))
        theme_form = QFormLayout(theme_box)

        self.cmb_theme = QComboBox()
        self._theme_names = theme_display_names()
        for theme_id, theme_label in self._theme_names.items():
            self.cmb_theme.addItem(theme_label, theme_id)

        self.btn_custom_bg = QPushButton(tr("appearance.custom_bg"))
        self.btn_custom_bg.clicked.connect(self._pick_custom_bg)

        self.btn_reset_theme = QPushButton(tr("appearance.reset_theme"))
        self.btn_reset_theme.clicked.connect(self._reset_theme)

        self.lbl_custom_bg = QLabel(tr("appearance.custom_bg_none"))
        self.lbl_custom_bg.setObjectName("muted")

        # Селектор языка
        self.cmb_language = QComboBox()
        self.cmb_language.addItem(tr("language.ru"), "ru")
        self.cmb_language.addItem(tr("language.en"), "en")
        cur_lang = get_language()
        idx_lang = self.cmb_language.findData(cur_lang)
        if idx_lang >= 0:
            self.cmb_language.setCurrentIndex(idx_lang)

        theme_form.addRow(tr("appearance.theme"), self.cmb_theme)
        theme_form.addRow("", self.btn_custom_bg)
        theme_form.addRow("", self.lbl_custom_bg)
        theme_form.addRow("", self.btn_reset_theme)
        theme_form.addRow(tr("appearance.language"), self.cmb_language)

        w.addWidget(theme_box)
        w.addStretch(1)

        scroll.setWidget(content)
        outer.addWidget(scroll)

        wrapper = QWidget()
        wrapper.setLayout(outer)

        self.btn_connect.clicked.connect(self._on_connect)
        self.btn_disconnect.clicked.connect(self._on_disconnect)
        self.btn_start.clicked.connect(lambda: self._send("resume"))
        self.btn_pause.clicked.connect(lambda: self._send("pause"))
        self.btn_resume.clicked.connect(lambda: self._send("resume"))
        self.btn_stop.clicked.connect(self._on_stop)
        self.cmb_theme.currentIndexChanged.connect(self._on_theme_changed)
        self.cmb_language.currentIndexChanged.connect(self._on_language_changed)
        self._update_buttons("disconnected")

        return wrapper

    def _build_map_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        self.minimap = MinimapWidget()
        layout.addWidget(self.minimap)

        btn_row = QHBoxLayout()
        btn_clear = QPushButton(tr("map.clear_route"))
        btn_clear.clicked.connect(self._clear_map_route)
        btn_row.addStretch(1)
        btn_row.addWidget(btn_clear)
        layout.addLayout(btn_row)

        return w

    def _build_statistics_tab(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)

        box = QGroupBox(tr("stats.box"))
        form = QFormLayout(box)

        self.stat_labels = {}
        fields = [
            ("total_uptime_sec", tr("stats.uptime")),
            ("total_connection_sec", tr("stats.connection")),
            ("reconnect_count", tr("stats.reconnects")),
            ("distance_traveled", tr("stats.distance")),
            ("messages_sent", tr("stats.messages")),
            ("routes_completed", tr("stats.routes")),
            ("damage_taken", tr("stats.damage")),
        ]
        for key, label in fields:
            val = QLabel("—")
            val.setObjectName("value")
            self.stat_labels[key] = val
            form.addRow(label, val)

        outer.addWidget(box)

        btn_row = QHBoxLayout()
        btn_reset = QPushButton(tr("stats.reset"))
        btn_reset.setObjectName("danger")
        btn_reset.clicked.connect(self._reset_stats)
        btn_row.addStretch(1)
        btn_row.addWidget(btn_reset)
        outer.addLayout(btn_row)
        outer.addStretch(1)

        return w

    def _build_settings_tab(self) -> QWidget:
        outer_outer = QVBoxLayout()
        outer_outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        w = QVBoxLayout(content)
        w.setContentsMargins(10, 10, 10, 10)
        w.setSpacing(10)

        # ===== Minecraft =====
        mc_box = QGroupBox(tr("settings.minecraft"))
        mc_form = QFormLayout(mc_box)
        self.inp_host = QLineEdit()
        self.inp_port = QSpinBox(); self.inp_port.setRange(1, 65535)
        self.inp_version = QComboBox()
        self.inp_version.addItems(
            ["1.21.4", "1.21.1", "1.21", "1.20.5", "1.20.4", "1.20.1", "1.19.4"]
        )
        self.inp_auth = QComboBox()
        self.inp_auth.addItems(["offline", "microsoft"])
        self.chk_auto_connect = QCheckBox(tr("settings.auto_connect"))
        mc_form.addRow(tr("settings.host"), self.inp_host)
        mc_form.addRow(tr("settings.port"), self.inp_port)
        mc_form.addRow(tr("settings.version"), self.inp_version)
        mc_form.addRow(tr("settings.auth"), self.inp_auth)
        mc_form.addRow("", self.chk_auto_connect)
        w.addWidget(mc_box)

        # ===== Ники =====
        nicks_box = QGroupBox(tr("settings.nicks"))
        nicks_layout = QVBoxLayout(nicks_box)
        self.list_nicks = QListWidget()
        self.list_nicks.setMaximumHeight(140)
        nicks_layout.addWidget(self.list_nicks)

        nicks_btns = QHBoxLayout()
        self.btn_nick_add = QPushButton(tr("settings.nick_add"))
        self.btn_nick_edit = QPushButton(tr("settings.nick_edit"))
        self.btn_nick_del = QPushButton(tr("settings.nick_del"))
        self.btn_nick_del.setObjectName("danger")
        nicks_btns.addWidget(self.btn_nick_add)
        nicks_btns.addWidget(self.btn_nick_edit)
        nicks_btns.addWidget(self.btn_nick_del)
        nicks_layout.addLayout(nicks_btns)

        self.chk_use_random_nick = QCheckBox(tr("settings.nick_random"))
        nicks_layout.addWidget(self.chk_use_random_nick)

        cur_row = QHBoxLayout()
        cur_row.addWidget(QLabel(tr("settings.nick_current")))
        self.lbl_current_nick = QLabel("—")
        self.lbl_current_nick.setObjectName("value")
        cur_row.addWidget(self.lbl_current_nick)
        cur_row.addStretch(1)
        self.btn_nick_pick = QPushButton(tr("settings.nick_pick"))
        cur_row.addWidget(self.btn_nick_pick)
        nicks_layout.addLayout(cur_row)
        w.addWidget(nicks_box)

        self.btn_nick_add.clicked.connect(self._nick_add)
        self.btn_nick_edit.clicked.connect(self._nick_edit)
        self.btn_nick_del.clicked.connect(self._nick_del)
        self.btn_nick_pick.clicked.connect(self._nick_pick_now)

        # ===== Поведение =====
        beh_box = QGroupBox(tr("settings.behavior"))
        beh_form = QFormLayout(beh_box)
        self.chk_use_random_walk = QCheckBox(tr("settings.behavior.random_walk"))
        self.chk_use_routes = QCheckBox(tr("settings.behavior.use_routes"))
        self.chk_loop_routes = QCheckBox(tr("settings.behavior.loop_routes"))
        self.chk_return_home = QCheckBox(tr("settings.behavior.return_home"))
        self.chk_show_track = QCheckBox(tr("settings.behavior.show_track"))
        self.chk_auto_reconnect = QCheckBox(tr("settings.behavior.auto_reconnect"))
        self.spin_max_reconnect = QSpinBox(); self.spin_max_reconnect.setRange(0, 100)
        self.spin_reconnect_delay = QSpinBox(); self.spin_reconnect_delay.setRange(1, 120)
        self.spin_reconnect_delay.setSuffix(" s")
        beh_form.addRow("", self.chk_use_random_walk)
        beh_form.addRow("", self.chk_use_routes)
        beh_form.addRow("", self.chk_loop_routes)
        beh_form.addRow("", self.chk_return_home)
        beh_form.addRow("", self.chk_show_track)
        beh_form.addRow("", self.chk_auto_reconnect)
        beh_form.addRow(tr("settings.behavior.max_reconnect"), self.spin_max_reconnect)
        beh_form.addRow(tr("settings.behavior.reconnect_delay"), self.spin_reconnect_delay)
        w.addWidget(beh_box)

        # ===== Безопасность =====
        safe_box = QGroupBox(tr("settings.safety"))
        safe_form = QFormLayout(safe_box)
        self.spin_min_health = QSpinBox(); self.spin_min_health.setRange(0, 20)
        self.spin_min_food = QSpinBox(); self.spin_min_food.setRange(0, 20)
        self.inp_critical_action = QComboBox()
        self.inp_critical_action.addItems(["pause", "disconnect", "none"])
        safe_form.addRow(tr("settings.safety.min_health"), self.spin_min_health)
        safe_form.addRow(tr("settings.safety.min_food"), self.spin_min_food)
        safe_form.addRow(tr("settings.safety.action"), self.inp_critical_action)
        w.addWidget(safe_box)

        # ===== Кнопки =====
        btn_row = QHBoxLayout()
        self.btn_save_settings = QPushButton(tr("settings.save"))
        self.btn_save_settings.setObjectName("primary")
        self.btn_reset_settings = QPushButton(tr("settings.reset"))
        btn_row.addStretch(1)
        btn_row.addWidget(self.btn_reset_settings)
        btn_row.addWidget(self.btn_save_settings)
        w.addLayout(btn_row)
        w.addStretch(1)

        scroll.setWidget(content)
        outer_outer.addWidget(scroll)

        wrapper = QWidget()
        wrapper.setLayout(outer_outer)

        self.btn_save_settings.clicked.connect(self._save_settings_from_ui)
        self.btn_reset_settings.clicked.connect(self._reset_settings)

        for wgt in (
            self.inp_host, self.inp_port, self.inp_version, self.inp_auth,
            self.chk_auto_connect,
            self.chk_use_random_walk, self.chk_use_routes, self.chk_loop_routes,
            self.chk_return_home, self.chk_show_track, self.chk_auto_reconnect,
            self.spin_max_reconnect, self.spin_reconnect_delay,
            self.spin_min_health, self.spin_min_food, self.inp_critical_action,
        ):
            if isinstance(wgt, QLineEdit):
                wgt.textChanged.connect(self._mark_settings_dirty)
            elif isinstance(wgt, QSpinBox):
                wgt.valueChanged.connect(self._mark_settings_dirty)
            elif isinstance(wgt, QComboBox):
                wgt.currentTextChanged.connect(self._mark_settings_dirty)
            elif isinstance(wgt, QCheckBox):
                wgt.stateChanged.connect(self._mark_settings_dirty)

        return wrapper

    def _build_log_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        btn_clear = QPushButton(tr("log.clear"))
        btn_clear.clicked.connect(self.log_view.clear)
        layout.addWidget(self.log_view)
        layout.addWidget(btn_clear, alignment=Qt.AlignRight)
        return w

    # ---------- горячие клавиши ----------

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+C"), self, activated=self._on_connect)
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self._on_disconnect)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save_settings_from_ui)
        QShortcut(QKeySequence("F5"), self, activated=self._restart_ui)

    def _restart_ui(self):
        reply = QMessageBox.question(
            self, tr("dlg.restart_title"),
            tr("dlg.restart_msg"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.closeEvent(QCloseEvent())
            self.client.stop()
            os.execv(sys.executable, [sys.executable] + sys.argv)

    # ---------- состояние окна ----------

    def _restore_window_state(self):
        geo = self.settings.get("ui", {}).get("window_geometry")
        if geo:
            try:
                ba = QByteArray(base64.b64decode(geo))
                self.restoreGeometry(ba)
            except Exception:
                pass
        last_tab = self.settings.get("ui", {}).get("last_tab", 0)
        if isinstance(last_tab, int) and 0 <= last_tab < self.tabs.count():
            self.tabs.setCurrentIndex(last_tab)

    def _save_window_state(self):
        try:
            geo = bytes(self.saveGeometry().toBase64()).decode("ascii")
            self.storage.update("settings", {"ui": {
                "window_geometry": geo,
                "last_tab": self.tabs.currentIndex(),
            }})
        except Exception:
            pass

    # ---------- события ----------

    def _wire_events(self):
        bus.state_updated.connect(self._on_state)
        bus.log_message.connect(self._on_log)
        bus.connected.connect(self._on_connected)
        bus.disconnected.connect(self._on_disconnected)
        bus.error_occurred.connect(self._on_error)
        bus.chat_sent.connect(self._on_chat_sent)
        bus.route_progress.connect(self._on_route_progress)
        bus.route_completed.connect(self._on_route_completed)
        bus.damage_taken.connect(self._on_damage)
        bus.stat_snapshot.connect(self._on_stat_snapshot)
        bus.safety_warning.connect(self._on_safety_warning)
        bus.safety_ok.connect(self._on_safety_ok)
        bus.inventory_updated.connect(self._on_inventory_updated)
        bus.combat_status.connect(self._on_combat_status)
        bus.dig_status.connect(self._on_dig_status)
        bus.ws_status_changed.connect(self._on_ws_status)

    def _on_state(self, payload: dict):
        self.state_model.apply(payload)
        self._refresh_dashboard()

        pos = payload.get("position")
        if pos and hasattr(self, "minimap"):
            self.minimap.set_bot_position(pos.get("x", 0), pos.get("y", 0), pos.get("z", 0))

        show_track = True
        if hasattr(self, "chk_show_track"):
            show_track = self.chk_show_track.isChecked()

        if show_track:
            track = payload.get("track")
            if track is not None and hasattr(self, "minimap"):
                self.minimap.set_track(track)
        else:
            if hasattr(self, "minimap"):
                self.minimap.clear_track()

    def _refresh_dashboard(self):
        s = self.state_model
        # Локализованная метка статуса
        status_key = f"status.{s.status}" if s.status else "status.disconnected"
        self.lbl_status.setText(tr(status_key))
        self.lbl_nick.setText(s.username)
        self.lbl_version.setText(s.version)
        self.lbl_health.setText(f"❤️ {s.health:.1f}/{s.max_health:.0f}")
        self.bar_health.setValue(int(round(s.health)))
        self.lbl_food.setText(f"🍖 {s.food:.1f}/{s.max_food:.0f}")
        self.bar_food.setValue(int(round(s.food)))
        self.lbl_pos.setText(
            tr("field.position", x=s.position['x'], y=s.position['y'], z=s.position['z'])
        )
        self.lbl_task.setText(self._localize_task(s.task))
        self._update_buttons(s.status)
        self._update_safety_colors(s)
    def _localize_task(self, task):
        """
        Преобразовать task в строку.
        task может быть:
        - строкой (старый формат) — вернуть как есть;
        - dict {key, params} — перевести через tr().
        """
        if isinstance(task, str):
            return task
        if isinstance(task, dict):
            key = task.get("key")
            params = task.get("params", {}) or {}
            if key:
                try:
                    return tr(key, **params)
                except Exception:
                    return key
        return tr("task.idle")

    def _update_safety_colors(self, s):
        min_h = self.spin_min_health.value() if hasattr(self, "spin_min_health") else 6
        min_f = self.spin_min_food.value() if hasattr(self, "spin_min_food") else 6

        if s.status == "connected":
            if s.health <= min_h:
                self.lbl_health.setObjectName("critical")
                self.bar_health.setObjectName("healthCritical")
            elif s.health <= min_h + 4:
                self.lbl_health.setObjectName("warningText")
                self.bar_health.setObjectName("health")
            else:
                self.lbl_health.setObjectName("")
                self.bar_health.setObjectName("health")

            if s.food <= min_f:
                self.lbl_food.setObjectName("critical")
                self.bar_food.setObjectName("foodCritical")
            elif s.food <= min_f + 4:
                self.lbl_food.setObjectName("warningText")
                self.bar_food.setObjectName("food")
            else:
                self.lbl_food.setObjectName("")
                self.bar_food.setObjectName("food")
        else:
            self.lbl_health.setObjectName("")
            self.lbl_food.setObjectName("")
            self.bar_health.setObjectName("health")
            self.bar_food.setObjectName("food")

        for wgt in (self.lbl_health, self.lbl_food, self.bar_health, self.bar_food):
            wgt.style().unpolish(wgt)
            wgt.style().polish(wgt)

    def _update_buttons(self, status: str):
        connected = status == "connected"
        self.btn_connect.setEnabled(status == "disconnected")
        self.btn_disconnect.setEnabled(
            status in ("connected", "connecting", "reconnecting")
        )
        self.btn_start.setEnabled(connected)
        self.btn_pause.setEnabled(connected)
        self.btn_resume.setEnabled(connected)
        self.btn_stop.setEnabled(connected)

    def _on_connected(self):
        self._safety_active = False
        self._append_log("INFO", tr("misc.connected"))
        self.statusBar().showMessage(tr("misc.connected"), 3000)
        # Передать язык в bot-core
        self._send("set_language", {"lang": get_language()})
        self._push_chat_config()
        self._push_safety_config()
        self._push_auto_eat_config()

    def _on_disconnected(self, reason: str):
        if reason == "manual":
            self._append_log("INFO", tr("misc.disconnected"))
            self.statusBar().showMessage(tr("misc.disconnected"), 3000)
        else:
            self._append_log("WARNING", tr("misc.conn_lost"))
            self.statusBar().showMessage(tr("misc.conn_lost"), 5000)
        self.state_model.status = "disconnected"
        self._safety_active = False
        if hasattr(self, "minimap"):
            self.minimap.clear_route()
            self.minimap.clear_track()
        self._refresh_dashboard()

    def _on_error(self, message: str):
        self._append_log("ERROR", message)

    def _on_log(self, payload: dict):
        self._append_log(payload.get("level", "INFO"), payload.get("message", ""))

    def _on_chat_sent(self, payload: dict):
        msg = payload.get("message", "")
        auto = payload.get("auto", False)
        prefix = "Auto" if auto else "Manual"
        self._append_log("CHAT", f"{prefix}: «{msg}»")

    def _on_route_progress(self, payload: dict):
        idx = payload.get("index", -1)
        self._current_route_index = idx
        if hasattr(self, "minimap"):
            self.minimap.set_active_point(idx)

    def _on_route_completed(self, payload: dict):
        name = payload.get("route", "—")
        self._append_log("INFO", tr("toast.route_done", name=name))
        show_toast(self, tr("toast.route_done", name=name), "success", 3000)
        if hasattr(self, "minimap"):
            self.minimap.clear_route()

    def _on_damage(self, payload: dict):
        amount = float(payload.get("amount", 0))
        show_toast(self, tr("toast.damage", amount=amount), "warning", 2500)

    def _on_stat_snapshot(self, payload: dict):
        self.stats_data.update(payload)
        self.storage.save("statistics", self.stats_data)
        self._refresh_statistics(payload)

    def _on_safety_warning(self, payload: dict):
        self._safety_active = True
        reason = payload.get("reason", "?")
        action = payload.get("action", "pause")
        action_text = {
            "pause": "Pause",
            "disconnect": "Disconnect",
            "none": "None",
        }.get(action, action)
        show_toast(self, tr("toast.safety_warning", reason=reason, action=action_text),
                   "warning", 6000)

    def _on_safety_ok(self, payload: dict):
        self._safety_active = False
        hp = float(payload.get("health", 0))
        food = float(payload.get("food", 0))
        show_toast(self, tr("toast.safety_ok", hp=hp, food=food), "success", 2500)

    def _on_inventory_updated(self, payload: dict):
        if hasattr(self, "inventory_tab"):
            self.inventory_tab.update_inventory(payload)

    def _on_combat_status(self, payload: dict):
        if hasattr(self, "control_tab"):
            self.control_tab.on_combat_status(payload)

    def _on_dig_status(self, payload: dict):
        if hasattr(self, "control_tab"):
            self.control_tab.on_dig_status(payload)

    def _on_ws_status(self, ok: bool):
        if ok:
            self.ws_indicator.setText("🟢 " + tr("misc.connected"))
            self.ws_indicator.setObjectName("success")
        else:
            self.ws_indicator.setText("🔴 " + tr("misc.disconnected"))
            self.ws_indicator.setObjectName("error")
        self.ws_indicator.style().unpolish(self.ws_indicator)
        self.ws_indicator.style().polish(self.ws_indicator)

    def _append_log(self, level: str, message: str):
        ts = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.log_view.appendPlainText(f"[{ts}] [{level}] {message}")

    # ---------- вспомогательное ----------

    def _copy_coords(self):
        text = self.lbl_pos.text().replace("📍 ", "")
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage(tr("misc.coords_copied"), 2000)

    def _mark_settings_dirty(self):
        if not self._settings_dirty:
            self._settings_dirty = True
            self.btn_save_settings.setText(tr("settings.save_dirty"))

    def _clear_map_route(self):
        self._send("clear_track", {})
        if hasattr(self, "minimap"):
            self.minimap.clear_track()
            self.minimap.clear_route()
        self._current_route_points = []
        self._current_route_index = -1
        self._append_log("INFO", tr("misc.track_cleared"))

    # ---------- статистика ----------

    @staticmethod
    def _fmt_duration(sec: int) -> str:
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h}h {m:02d}m {s:02d}s"

    def _refresh_statistics(self, snapshot: dict | None = None):
        data = snapshot if snapshot else self.stats_data
        self.stat_labels["total_uptime_sec"].setText(
            self._fmt_duration(int(data.get("total_uptime_sec", 0)))
        )
        self.stat_labels["total_connection_sec"].setText(
            self._fmt_duration(int(data.get("total_connection_sec", 0)))
        )
        self.stat_labels["reconnect_count"].setText(str(int(data.get("reconnect_count", 0))))
        self.stat_labels["distance_traveled"].setText(
            f"{float(data.get('distance_traveled', 0)):.2f}"
        )
        self.stat_labels["messages_sent"].setText(str(int(data.get("messages_sent", 0))))
        self.stat_labels["routes_completed"].setText(
            str(int(data.get("routes_completed", 0)))
        )
        self.stat_labels["damage_taken"].setText(
            f"{float(data.get('damage_taken', 0)):.1f}"
        )

    def _reset_stats(self):
        reply = QMessageBox.question(
            self, tr("dlg.reset_stats_title"),
            tr("dlg.reset_stats_msg"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.stats_data = self.storage.reset("statistics")
            self._send("stat_reset", {})
            self._refresh_statistics()

    # ---------- ник ----------

    def _load_nicks_into_ui(self):
        self.list_nicks.clear()
        for nick in self.nicks_data["list"]:
            self.list_nicks.addItem(QListWidgetItem(nick))
        self.chk_use_random_nick.setChecked(bool(self.nicks_data.get("use_random", False)))
        self.lbl_current_nick.setText(self.nicks_data.get("selected", "—"))

    def _save_nicks(self):
        self.nicks_data["use_random"] = self.chk_use_random_nick.isChecked()
        self.storage.save("nicks", self.nicks_data)

    def _nick_add(self):
        text, ok = QInputDialog.getText(self, tr("dlg.nick_add_title"), tr("dlg.nick_add_prompt"))
        if ok and text.strip():
            self.nicks_data["list"].append(text.strip())
            self._save_nicks()
            self._load_nicks_into_ui()

    def _nick_edit(self):
        row = self.list_nicks.currentRow()
        if row < 0:
            return
        old = self.nicks_data["list"][row]
        text, ok = QInputDialog.getText(
            self, tr("dlg.nick_edit_title"), tr("dlg.nick_edit_prompt"), text=old
        )
        if ok and text.strip():
            self.nicks_data["list"][row] = text.strip()
            self._save_nicks()
            self._load_nicks_into_ui()

    def _nick_del(self):
        row = self.list_nicks.currentRow()
        if row < 0:
            return
        old = self.nicks_data["list"][row]
        reply = QMessageBox.question(
            self, tr("dlg.nick_del_title"),
            tr("dlg.nick_del_prompt", nick=old),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del self.nicks_data["list"][row]
            self._save_nicks()
            self._load_nicks_into_ui()

    def _nick_pick_now(self):
        row = self.list_nicks.currentRow()
        if row < 0 or row >= len(self.nicks_data["list"]):
            QMessageBox.information(
                self, tr("dlg.nick_not_selected_title"),
                tr("dlg.nick_not_selected_msg")
            )
            return
        nick = self.nicks_data["list"][row]
        self.nicks_data["selected"] = nick
        self._save_nicks()
        self.lbl_current_nick.setText(nick)

    def _resolve_username(self) -> str:
        if self.chk_use_random_nick.isChecked() and self.nicks_data["list"]:
            nick = random.choice(self.nicks_data["list"])
        else:
            nick = self.nicks_data.get("selected") or "AFKBot"
        self.nicks_data["selected"] = nick
        self._save_nicks()
        self.lbl_current_nick.setText(nick)
        return nick

    # ---------- чат / безопасность / автоедство ----------

    def _push_chat_config(self):
        msgs = self.storage.load("messages")["items"]
        ms = self.storage.load("settings")["messages"]
        self._send("chat_config", {
            "messages": msgs,
            "enabled": ms.get("enabled", False),
            "min_interval_sec": ms.get("min_interval_sec", 60),
            "max_interval_sec": ms.get("max_interval_sec", 180),
            "use_random_interval": ms.get("use_random_interval", True),
        })

    def _push_safety_config(self):
        self._send("safety_config", {
            "min_health": self.spin_min_health.value(),
            "min_food": self.spin_min_food.value(),
            "critical_action": self.inp_critical_action.currentText(),
        })

    def _push_auto_eat_config(self):
        if not hasattr(self, "inventory_tab"):
            return
        self._send("auto_eat_config", {
            "enabled": self.inventory_tab.chk_auto_eat.isChecked(),
            "threshold": self.inventory_tab.spin_eat_threshold.value(),
        })

    # ---------- настройки ----------

    def _load_settings_into_ui(self):
        s = self.settings
        mc = s["minecraft"]
        self.inp_host.setText(mc["host"])
        self.inp_port.setValue(int(mc["port"]))
        idx = self.inp_version.findText(mc["version"])
        if idx >= 0:
            self.inp_version.setCurrentIndex(idx)
        idx = self.inp_auth.findText(mc.get("auth", "offline"))
        if idx >= 0:
            self.inp_auth.setCurrentIndex(idx)
        self.chk_auto_connect.setChecked(bool(mc.get("auto_connect_on_start", False)))

        beh = s["behavior"]
        self.chk_use_random_walk.setChecked(bool(beh.get("use_random_walk", False)))
        self.chk_use_routes.setChecked(bool(beh.get("use_routes", True)))
        self.chk_loop_routes.setChecked(bool(beh.get("loop_routes", False)))
        self.chk_return_home.setChecked(bool(beh.get("return_home_after_route", False)))
        self.chk_show_track.setChecked(bool(beh.get("show_track", True)))
        self.chk_auto_reconnect.setChecked(bool(beh.get("auto_reconnect", True)))
        self.spin_max_reconnect.setValue(int(beh.get("max_reconnect_attempts", 5)))
        self.spin_reconnect_delay.setValue(int(beh.get("reconnect_base_delay_sec", 5)))

        sf = s["safety"]
        self.spin_min_health.setValue(int(sf["min_health"]))
        self.spin_min_food.setValue(int(sf["min_food"]))
        idx = self.inp_critical_action.findText(sf["critical_action"])
        if idx >= 0:
            self.inp_critical_action.setCurrentIndex(idx)

        ui = s.get("ui", {})
        theme_id = ui.get("theme", "dark_blue")
        idx = self.cmb_theme.findData(theme_id)
        if idx >= 0:
            self.cmb_theme.blockSignals(True)
            self.cmb_theme.setCurrentIndex(idx)
            self.cmb_theme.blockSignals(False)
        self._update_custom_bg_label(ui.get("custom_bg"))

        self._settings_dirty = False
        if hasattr(self, "btn_save_settings"):
            self.btn_save_settings.setText(tr("settings.save"))

    def _collect_settings_from_ui(self) -> dict:
        return {
            "minecraft": {
                "host": self.inp_host.text().strip(),
                "port": self.inp_port.value(),
                "version": self.inp_version.currentText(),
                "username": self.nicks_data.get("selected", "AFKBot"),
                "auth": self.inp_auth.currentText(),
                "auto_connect_on_start": self.chk_auto_connect.isChecked(),
            },
            "behavior": {
                "use_random_walk": self.chk_use_random_walk.isChecked(),
                "use_routes": self.chk_use_routes.isChecked(),
                "loop_routes": self.chk_loop_routes.isChecked(),
                "return_home_after_route": self.chk_return_home.isChecked(),
                "show_track": self.chk_show_track.isChecked(),
                "auto_reconnect": self.chk_auto_reconnect.isChecked(),
                "max_reconnect_attempts": self.spin_max_reconnect.value(),
                "reconnect_base_delay_sec": self.spin_reconnect_delay.value(),
            },
            "safety": {
                "min_health": self.spin_min_health.value(),
                "min_food": self.spin_min_food.value(),
                "critical_action": self.inp_critical_action.currentText(),
            },
        }

    def _save_settings_from_ui(self):
        patch = self._collect_settings_from_ui()
        self.settings = self.storage.update("settings", patch)
        self.statusBar().showMessage(tr("misc.settings_saved"), 2500)
        self._settings_dirty = False
        self.btn_save_settings.setText(tr("settings.save"))
        self._push_chat_config()
        self._push_safety_config()
        self._push_auto_eat_config()

    def _reset_settings(self):
        reply = QMessageBox.question(
            self, tr("dlg.reset_settings_title"),
            tr("dlg.reset_settings_msg"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.settings = self.storage.reset("settings")
            self._load_settings_into_ui()

    # ---------- внешний вид ----------

    def _apply_theme_now(self, theme_id: str, custom_bg: str | None = None):
        app = QApplication.instance()
        if app:
            app.setStyleSheet(build_qss(theme_id, custom_bg))

    def _on_theme_changed(self, index: int):
        theme_id = self.cmb_theme.itemData(index) or "dark_blue"
        self._apply_theme_now(theme_id, None)
        self._save_theme_to_storage(theme_id, None)
        self._update_custom_bg_label(None)

    def _pick_custom_bg(self):
        current = self.settings.get("ui", {}).get("custom_bg") or "#0d1b2a"
        color = QColorDialog.getColor(QColor(current), self, tr("appearance.custom_bg"))
        if not color.isValid():
            return
        hex_color = color.name()
        self._apply_theme_now("dark_blue", hex_color)
        self._save_theme_to_storage(self.cmb_theme.currentData() or "dark_blue", hex_color)
        self._update_custom_bg_label(hex_color)

    def _update_custom_bg_label(self, custom_bg: str | None):
        if custom_bg:
            self.lbl_custom_bg.setText(tr("appearance.custom_bg_set", color=custom_bg))
        else:
            self.lbl_custom_bg.setText(tr("appearance.custom_bg_none"))

    def _reset_theme(self):
        self._apply_theme_now("dark_blue", None)
        self._save_theme_to_storage("dark_blue", None)
        idx = self.cmb_theme.findData("dark_blue")
        if idx >= 0:
            self.cmb_theme.blockSignals(True)
            self.cmb_theme.setCurrentIndex(idx)
            self.cmb_theme.blockSignals(False)
        self._update_custom_bg_label(None)

    def _save_theme_to_storage(self, theme_id: str, custom_bg: str | None):
        self.storage.update("settings", {
            "ui": {
                "theme": theme_id,
                "custom_bg": custom_bg,
            }
        })

    def _on_language_changed(self, index: int):
        lang = self.cmb_language.itemData(index) or "ru"
        if lang == get_language():
            return
        # Сохраняем язык
        self.storage.update("settings", {"ui": {"language": lang}})
        # Отправить язык в bot-core немедленно (пока соединение живо)
        self._send("set_language", {"lang": lang})
        # Подтверждение перезапуска
        reply = QMessageBox.question(
            self, tr("dlg.restart_title"),
            tr("dlg.restart_msg"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.closeEvent(QCloseEvent())
            self.client.stop()
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            # Откатываем выбор
            idx = self.cmb_language.findData(get_language())
            if idx >= 0:
                self.cmb_language.blockSignals(True)
                self.cmb_language.setCurrentIndex(idx)
                self.cmb_language.blockSignals(False)

    # ---------- кнопки ----------

    def _on_connect(self):
        host = self.inp_host.text().strip()
        if not host or not HOST_RE.match(host):
            QMessageBox.warning(
                self, tr("routes.error_title"),
                "Invalid server address."
            )
            return
        username = self._resolve_username()
        config = {
            "host": host,
            "port": self.inp_port.value(),
            "version": self.inp_version.currentText(),
            "username": username,
            "auth": self.inp_auth.currentText(),
            "reconnect": {
                "auto": self.chk_auto_reconnect.isChecked(),
                "max_attempts": self.spin_max_reconnect.value(),
                "base_delay_sec": self.spin_reconnect_delay.value(),
            },
            "safety": {
                "min_health": self.spin_min_health.value(),
                "min_food": self.spin_min_food.value(),
                "critical_action": self.inp_critical_action.currentText(),
            },
            "auto_eat": {
                "enabled": self.inventory_tab.chk_auto_eat.isChecked(),
                "threshold": self.inventory_tab.spin_eat_threshold.value(),
            },
            "show_track": self.chk_show_track.isChecked(),
            "stats_base": dict(self.stats_data),
        }
        self.state_model.version = config["version"]
        self.state_model.username = username
        self._send("connect", config)

    def _on_disconnect(self):
        reply = QMessageBox.question(
            self, tr("dlg.disconnect_title"),
            tr("dlg.disconnect_msg"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._send("disconnect")

    def _on_stop(self):
        reply = QMessageBox.question(
            self, tr("dlg.stop_title"),
            tr("dlg.stop_msg"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._send("stop")

    def _send(self, cmd_type: str, payload: dict | None = None):
        self.client.send_command(cmd_type, payload)

    # ---------- закрытие ----------

    def closeEvent(self, event):
        if self.state_model.status in ("connected", "connecting", "reconnecting"):
            reply = QMessageBox.question(
                self, tr("dlg.exit_title"),
                tr("dlg.exit_msg"),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
            self._send("disconnect")

        try:
            self._save_settings_from_ui()
            self._save_nicks()
            self.storage.save("statistics", self.stats_data)
            self._save_window_state()
        except Exception:
            pass
        super().closeEvent(event)