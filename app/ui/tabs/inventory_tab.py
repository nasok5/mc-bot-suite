from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QCheckBox, QGroupBox,
    QMessageBox, QSizePolicy, QFrame, QSpinBox, QScrollArea
)
from PySide6.QtGui import QFont

from i18n import tr


SLOT_BG = "#14243a"
SLOT_BG_HOVER = "#1f3550"
SLOT_BG_EMPTY = "#0f1c2e"
SLOT_BORDER = "#2f4f7f"
SLOT_SELECTED_BORDER = "#4a90e2"
FOOD_BORDER = "#2ecc71"


def _short_name(name: str, max_len: int = 10) -> str:
    if not name:
        return ""
    name = name.replace("_", " ")
    if len(name) <= max_len:
        return name
    return name[:max_len - 1] + "…"


_BTN_PRIMARY_STYLE = """
QPushButton {
    background-color: #4a90e2;
    color: #ffffff;
    border: 1px solid #4a90e2;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 10pt;
}
QPushButton:hover { background-color: #6aa8f0; border-color: #6aa8f0; }
QPushButton:pressed { background-color: #3a70b2; }
QPushButton:disabled { background-color: #2a3f5f; color: #6a7f9f; border-color: #2f4f7f; }
"""


class SlotWidget(QFrame):
    clicked = Signal(int)
    double_clicked = Signal(int)

    def __init__(self, slot_index: int, parent=None):
        super().__init__(parent)
        self.slot_index = slot_index
        self.setFrameShape(QFrame.NoFrame)
        self.setFixedSize(64, 64)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.lbl_name = QLabel("")
        self.lbl_name.setAlignment(Qt.AlignCenter)
        self.lbl_name.setWordWrap(True)
        self.lbl_name.setFont(QFont("Segoe UI", 6))
        self.lbl_name.setStyleSheet("color: #e0e6ed; background: transparent;")

        self.lbl_count = QLabel("")
        self.lbl_count.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.lbl_count.setFont(QFont("Segoe UI", 7, QFont.Bold))
        self.lbl_count.setStyleSheet("color: #f1c40f; background: transparent;")

        layout.addWidget(self.lbl_name, 1)
        layout.addWidget(self.lbl_count, 0)

        self._selected = False
        self._is_food = False
        self._has_item = False
        self._update_style()

    def set_data(self, item: dict):
        self._has_item = bool(item.get("name"))
        self._is_food = bool(item.get("isFood"))
        if self._has_item:
            display = item.get("displayName") or item.get("name") or ""
            self.lbl_name.setText(_short_name(display, 12))
            count = int(item.get("count", 0))
            self.lbl_count.setText(f"×{count}" if count > 1 else "")
        else:
            self.lbl_name.setText("")
            self.lbl_count.setText("")
        self._update_style()

    def set_selected(self, selected: bool):
        self._selected = selected
        self._update_style()

    def _update_style(self):
        if not self._has_item:
            bg = SLOT_BG_EMPTY
        elif self._selected:
            bg = SLOT_BG_HOVER
        else:
            bg = SLOT_BG
        border_color = SLOT_BORDER
        if self._selected:
            border_color = SLOT_SELECTED_BORDER
        elif self._is_food:
            border_color = FOOD_BORDER
        border_width = 2 if self._selected else 1
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: {border_width}px solid {border_color};
                border-radius: 4px;
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.slot_index)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.slot_index)
        super().mouseDoubleClickEvent(event)


class InventoryTab(QWidget):
    """Вкладка инвентаря."""

    use_item_requested = Signal(int)

    def __init__(self, send_command, append_log, storage=None):
        super().__init__()
        self.send_command = send_command
        self.append_log = append_log
        self.storage = storage
        self.settings = storage.load("settings") if storage else {}

        self.items_by_slot = {}
        self.slot_widgets = {}
        self.selected_slot = None

        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # Экипировка
        armor_box = QGroupBox(tr("inv.armor"))
        armor_layout = QHBoxLayout(armor_box)
        armor_layout.setSpacing(6)
        for slot in (5, 6, 7, 8):
            w = SlotWidget(slot)
            w.clicked.connect(self._on_slot_clicked)
            w.double_clicked.connect(self._on_slot_double_clicked)
            self.slot_widgets[slot] = w
            armor_layout.addWidget(w)
        armor_layout.addStretch(1)
        root.addWidget(armor_box)

        # Инвентарь
        inv_box = QGroupBox(tr("inv.inventory"))
        inv_layout = QGridLayout(inv_box)
        inv_layout.setSpacing(4)
        for i, slot in enumerate(range(9, 36)):
            row = i // 9
            col = i % 9
            w = SlotWidget(slot)
            w.clicked.connect(self._on_slot_clicked)
            w.double_clicked.connect(self._on_slot_double_clicked)
            self.slot_widgets[slot] = w
            inv_layout.addWidget(w, row, col)
        root.addWidget(inv_box)

        # Хотбар
        hot_box = QGroupBox(tr("inv.hotbar"))
        hot_layout = QHBoxLayout(hot_box)
        hot_layout.setSpacing(6)
        for slot in range(36, 45):
            w = SlotWidget(slot)
            w.clicked.connect(self._on_slot_clicked)
            w.double_clicked.connect(self._on_slot_double_clicked)
            self.slot_widgets[slot] = w
            hot_layout.addWidget(w)
        hot_layout.addStretch(1)
        root.addWidget(hot_box)

        # Выделение
        info_box = QGroupBox(tr("inv.selection"))
        info_layout = QHBoxLayout(info_box)
        info_layout.setContentsMargins(12, 8, 12, 8)
        info_layout.addWidget(QLabel(tr("inv.slot")))
        self.lbl_selected = QLabel(tr("inv.nothing"))
        self.lbl_selected.setMinimumHeight(24)
        self.lbl_selected.setStyleSheet("color: #4a90e2; font-weight: 600; font-size: 11pt;")
        info_layout.addWidget(self.lbl_selected)
        info_layout.addStretch(1)
        root.addWidget(info_box)

        # Быстрые действия
        quick_box = QGroupBox(tr("inv.quick_actions"))
        quick_layout = QHBoxLayout(quick_box)
        quick_layout.setContentsMargins(12, 12, 12, 12)
        quick_layout.setSpacing(10)
        quick_layout.addStretch(1)

        self.btn_eat = QPushButton(tr("inv.eat"))
        self.btn_eat.setStyleSheet(_BTN_PRIMARY_STYLE)
        self.btn_eat.setEnabled(False)
        self.btn_eat.setMinimumHeight(40)
        self.btn_eat.setMinimumWidth(200)
        self.btn_eat.setCursor(Qt.PointingHandCursor)

        self.btn_use = QPushButton(tr("inv.use"))
        self.btn_use.setEnabled(False)
        self.btn_use.setMinimumHeight(40)
        self.btn_use.setMinimumWidth(160)
        self.btn_use.setCursor(Qt.PointingHandCursor)

        quick_layout.addWidget(self.btn_eat)
        quick_layout.addWidget(self.btn_use)
        root.addWidget(quick_box)

        # Выброс
        drop_box = QGroupBox(tr("inv.drop_box"))
        drop_layout = QHBoxLayout(drop_box)
        drop_layout.setContentsMargins(12, 12, 12, 12)
        drop_layout.setSpacing(10)

        drop_layout.addWidget(QLabel(tr("inv.drop_amount")))
        self.spin_drop_count = QSpinBox()
        self.spin_drop_count.setRange(1, 999)
        self.spin_drop_count.setValue(1)
        self.spin_drop_count.setFixedWidth(110)
        self.spin_drop_count.setMinimumHeight(36)
        drop_layout.addWidget(self.spin_drop_count)

        self.btn_drop = QPushButton(tr("inv.drop_btn"))
        self.btn_drop.setObjectName("danger")
        self.btn_drop.setEnabled(False)
        self.btn_drop.setMinimumHeight(36)
        self.btn_drop.setMinimumWidth(220)
        drop_layout.addWidget(self.btn_drop)

        drop_layout.addStretch(1)

        self.btn_refresh = QPushButton(tr("inv.refresh"))
        self.btn_refresh.setMinimumHeight(36)
        self.btn_refresh.setMinimumWidth(120)
        drop_layout.addWidget(self.btn_refresh)

        root.addWidget(drop_box)

        # Фильтр
        filter_box = QGroupBox(tr("inv.filter"))
        filter_layout = QHBoxLayout(filter_box)
        filter_layout.setContentsMargins(12, 8, 12, 8)
        self.chk_nonempty = QCheckBox(tr("inv.filter_nonempty"))
        filter_layout.addWidget(self.chk_nonempty)
        filter_layout.addStretch(1)
        root.addWidget(filter_box)

        # Автопитание
        eat_box = QGroupBox(tr("inv.auto_eat"))
        eat_layout = QHBoxLayout(eat_box)
        eat_layout.setContentsMargins(12, 8, 12, 8)
        eat_layout.setSpacing(10)
        self.chk_auto_eat = QCheckBox(tr("inv.auto_eat_enabled"))
        eat_layout.addWidget(self.chk_auto_eat)
        eat_layout.addWidget(QLabel(tr("inv.auto_eat_threshold")))
        self.spin_eat_threshold = QSpinBox()
        self.spin_eat_threshold.setRange(1, 20)
        self.spin_eat_threshold.setValue(17)
        self.spin_eat_threshold.setFixedWidth(70)
        eat_layout.addWidget(self.spin_eat_threshold)
        eat_layout.addStretch(1)
        root.addWidget(eat_box)

        self._load_auto_eat_settings()

        root.addStretch(1)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.btn_eat.clicked.connect(self._on_eat_clicked)
        self.btn_use.clicked.connect(self._on_use_clicked)
        self.btn_drop.clicked.connect(self._on_drop_clicked)
        self.btn_refresh.clicked.connect(self._on_refresh_clicked)
        self.chk_nonempty.stateChanged.connect(self._apply_filter)
        self.chk_auto_eat.stateChanged.connect(self._on_auto_eat_changed)
        self.spin_eat_threshold.valueChanged.connect(self._on_auto_eat_changed)

    def update_inventory(self, payload: dict):
        items = payload.get("items", [])
        self.items_by_slot = {int(it["slot"]): it for it in items}
        for slot, widget in self.slot_widgets.items():
            item = self.items_by_slot.get(slot, {})
            widget.set_data(item)
        self._apply_filter()
        self._refresh_selected_label()

    def _on_slot_clicked(self, slot: int):
        if self.selected_slot is not None and self.selected_slot in self.slot_widgets:
            self.slot_widgets[self.selected_slot].set_selected(False)
        self.selected_slot = slot
        if slot in self.slot_widgets:
            self.slot_widgets[slot].set_selected(True)
        item = self.items_by_slot.get(slot, {})
        if item.get("name"):
            count = int(item.get("count", 1))
            self.spin_drop_count.setMaximum(max(999, count))
            self.spin_drop_count.setValue(count)
        else:
            self.spin_drop_count.setMaximum(999)
            self.spin_drop_count.setValue(1)
        self._refresh_selected_label()

    def _on_slot_double_clicked(self, slot: int):
        item = self.items_by_slot.get(slot, {})
        if item.get("name"):
            self.append_log("INFO", tr("inv.log.double_click",
                                       slot=slot, name=item.get('displayName')))
            self.use_item_requested.emit(slot)

    def _refresh_selected_label(self):
        if self.selected_slot is None:
            self.lbl_selected.setText(tr("inv.nothing"))
            self.btn_eat.setEnabled(False)
            self.btn_use.setEnabled(False)
            self.btn_drop.setEnabled(False)
            return
        item = self.items_by_slot.get(self.selected_slot, {})
        if not item.get("name"):
            self.lbl_selected.setText(tr("inv.slot_empty", slot=self.selected_slot))
            self.btn_eat.setEnabled(False)
            self.btn_use.setEnabled(False)
            self.btn_drop.setEnabled(False)
            return
        display = item.get("displayName") or item.get("name")
        count = int(item.get("count", 1))
        is_food = item.get("isFood", False)
        suffix = " 🍖" if is_food else ""
        self.lbl_selected.setText(tr("inv.slot_info",
                                     slot=self.selected_slot, name=display,
                                     count=count, food_suffix=suffix))
        self.btn_eat.setEnabled(is_food)
        self.btn_use.setEnabled(True)
        self.btn_drop.setEnabled(True)

    def _on_eat_clicked(self):
        if self.selected_slot is None:
            return
        item = self.items_by_slot.get(self.selected_slot, {})
        if not item.get("isFood"):
            QMessageBox.information(
                self, tr("inv.error.not_food"), tr("inv.error.not_food_msg")
            )
            return
        self.send_command("eat_item", {"slot": self.selected_slot})
        self.append_log("INFO", tr("inv.log.eat_request", slot=self.selected_slot))

    def _on_use_clicked(self):
        if self.selected_slot is None:
            return
        self.append_log("INFO", tr("inv.log.use_stub", slot=self.selected_slot))
        self.use_item_requested.emit(self.selected_slot)

    def _on_drop_clicked(self):
        if self.selected_slot is None:
            QMessageBox.information(
                self, tr("inv.error.no_selection"), tr("inv.error.no_selection_msg")
            )
            return
        item = self.items_by_slot.get(self.selected_slot, {})
        if not item.get("name"):
            QMessageBox.information(self, tr("inv.error.empty"), tr("inv.error.empty_msg"))
            return
        n = self.spin_drop_count.value()
        count = int(item.get("count", 1))
        if n > count:
            QMessageBox.warning(
                self, tr("inv.error.too_many"),
                tr("inv.error.too_many_msg", count=count, n=n)
            )
            return
        self.send_command("drop_item", {"slot": self.selected_slot, "count": n})
        self.append_log("INFO", tr("inv.log.drop_request", slot=self.selected_slot, count=n))

    def _on_refresh_clicked(self):
        self.send_command("refresh_inventory", {})
        self.append_log("INFO", tr("inv.log.refresh_request"))

    def _apply_filter(self):
        only_nonempty = self.chk_nonempty.isChecked()
        for slot, widget in self.slot_widgets.items():
            item = self.items_by_slot.get(slot, {})
            has_item = bool(item.get("name"))
            widget.setVisible(not only_nonempty or has_item)

    # ---------- автопитание ----------

    def _load_auto_eat_settings(self):
        if not self.storage:
            return
        try:
            settings = self.storage.load("settings")
            ae = settings.get("auto_eat", {})
            self.chk_auto_eat.setChecked(bool(ae.get("enabled", False)))
            self.spin_eat_threshold.setValue(int(ae.get("threshold", 17)))
        except Exception:
            pass

    def _on_auto_eat_changed(self):
        if not self.storage:
            return
        enabled = self.chk_auto_eat.isChecked()
        threshold = self.spin_eat_threshold.value()
        self.storage.update("settings", {
            "auto_eat": {"enabled": enabled, "threshold": threshold}
        })
        self.send_command("auto_eat_config", {"enabled": enabled, "threshold": threshold})
        state_str = tr("inv.log.auto_eat_on") if enabled else tr("inv.log.auto_eat_off")
        self.append_log("INFO", tr("inv.log.auto_eat", state=state_str, threshold=threshold))