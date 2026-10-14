import random
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QSpinBox, QCheckBox, QGroupBox,
    QFormLayout, QMessageBox, QAbstractItemView, QInputDialog
)

from i18n import tr


class MessagesTab(QWidget):
    """Вкладка автосообщений."""

    def __init__(self, storage, send_chat_config, append_log, send_manual_chat):
        super().__init__()
        self.storage = storage
        self.send_chat_config = send_chat_config
        self.append_log = append_log
        self.send_manual_chat = send_manual_chat

        self.data = self.storage.load("messages")
        self.settings = self.storage.load("settings")

        self._build_ui()
        self._reload_list()

    def _build_ui(self):
        root = QVBoxLayout(self)

        list_box = QGroupBox(tr("msg.list"))
        lbox = QVBoxLayout(list_box)

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.itemDoubleClicked.connect(self._edit_selected)
        lbox.addWidget(self.list)

        btn_row = QHBoxLayout()
        self.btn_add = QPushButton(tr("msg.add"))
        self.btn_edit = QPushButton(tr("msg.edit"))
        self.btn_del = QPushButton(tr("msg.delete"))
        self.btn_del.setObjectName("danger")
        self.btn_preview = QPushButton(tr("msg.preview"))
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_edit)
        btn_row.addWidget(self.btn_del)
        btn_row.addStretch(1)
        btn_row.addWidget(self.btn_preview)
        lbox.addLayout(btn_row)

        self.btn_add.clicked.connect(self._add_message)
        self.btn_edit.clicked.connect(self._edit_selected)
        self.btn_del.clicked.connect(self._delete_selected)
        self.btn_preview.clicked.connect(self._preview_random)

        root.addWidget(list_box)

        cfg_box = QGroupBox(tr("msg.auto_box"))
        cfg_form = QFormLayout(cfg_box)

        self.chk_enabled = QCheckBox(tr("msg.auto_enabled"))
        self.spin_min = QSpinBox(); self.spin_min.setRange(10, 3600); self.spin_min.setSuffix(" s")
        self.spin_max = QSpinBox(); self.spin_max.setRange(10, 7200); self.spin_max.setSuffix(" s")
        self.chk_random = QCheckBox(tr("msg.random_interval"))

        cfg_form.addRow("", self.chk_enabled)
        cfg_form.addRow(tr("msg.min_interval"), self.spin_min)
        cfg_form.addRow(tr("msg.max_interval"), self.spin_max)
        cfg_form.addRow("", self.chk_random)

        ms = self.settings.get("messages", {})
        self.chk_enabled.setChecked(bool(ms.get("enabled", False)))
        self.spin_min.setValue(int(ms.get("min_interval_sec", 60)))
        self.spin_max.setValue(int(ms.get("max_interval_sec", 180)))
        self.chk_random.setChecked(bool(ms.get("use_random_interval", True)))

        self.chk_enabled.stateChanged.connect(self._apply)
        self.spin_min.valueChanged.connect(self._apply)
        self.spin_max.valueChanged.connect(self._apply)
        self.chk_random.stateChanged.connect(self._apply)

        root.addWidget(cfg_box)

        manual_box = QGroupBox(tr("msg.send_now"))
        mlay = QHBoxLayout(manual_box)
        self.inp_manual = QLineEdit()
        self.inp_manual.setPlaceholderText(tr("msg.send_placeholder"))
        self.btn_manual = QPushButton(tr("msg.send_btn"))
        self.btn_manual.setObjectName("primary")
        mlay.addWidget(self.inp_manual)
        mlay.addWidget(self.btn_manual)
        self.btn_manual.clicked.connect(self._send_manual)
        self.inp_manual.returnPressed.connect(self._send_manual)
        root.addWidget(manual_box)

        root.addStretch(1)

    def _reload_list(self):
        self.list.clear()
        for m in self.data["items"]:
            self.list.addItem(QListWidgetItem(m))

    def _add_message(self):
        text, ok = QInputDialog.getText(
            self, tr("msg.new_title"), tr("msg.new_prompt")
        )
        if ok and text.strip():
            self.data["items"].append(text.strip())
            self._persist_and_apply()
            self._reload_list()

    def _edit_selected(self):
        row = self.list.currentRow()
        if row < 0:
            return
        old = self.data["items"][row]
        text, ok = QInputDialog.getText(
            self, tr("msg.edit_title"), tr("msg.edit_prompt"), text=old
        )
        if ok and text.strip():
            self.data["items"][row] = text.strip()
            self._persist_and_apply()
            self._reload_list()
            self.list.setCurrentRow(row)

    def _delete_selected(self):
        row = self.list.currentRow()
        if row < 0:
            return
        old = self.data["items"][row]
        reply = QMessageBox.question(
            self, tr("msg.delete_title"),
            tr("msg.delete_prompt", msg=old),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del self.data["items"][row]
            self._persist_and_apply()
            self._reload_list()

    def _preview_random(self):
        if not self.data["items"]:
            QMessageBox.information(
                self, tr("msg.empty_title"), tr("msg.empty_msg")
            )
            return
        msg = random.choice(self.data["items"])
        QMessageBox.information(self, tr("msg.random_title"), msg)

    def _persist_and_apply(self):
        self.storage.save("messages", self.data)
        self._apply()

    def _apply(self):
        cfg = {
            "messages": self.data["items"],
            "enabled": self.chk_enabled.isChecked(),
            "min_interval_sec": self.spin_min.value(),
            "max_interval_sec": max(self.spin_max.value(), self.spin_min.value()),
            "use_random_interval": self.chk_random.isChecked(),
        }
        self.storage.update("settings", {"messages": {
            "enabled": cfg["enabled"],
            "min_interval_sec": cfg["min_interval_sec"],
            "max_interval_sec": cfg["max_interval_sec"],
            "use_random_interval": cfg["use_random_interval"],
        }})
        self.send_chat_config(cfg)

    def _send_manual(self):
        text = self.inp_manual.text().strip()
        if not text:
            return
        self.send_manual_chat(text)
        self.inp_manual.clear()