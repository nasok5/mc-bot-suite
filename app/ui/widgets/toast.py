from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QWidget


class Toast(QLabel):
    """Всплывающее уведомление внутри родительского окна."""

    _active = []  # список текущих тостов (для стека снизу вверх)

    def __init__(self, parent: QWidget, text: str, level: str = "info", duration_ms: int = 4000):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        colors = {
            "info": "#4a90e2",
            "warning": "#f1c40f",
            "error": "#e74c3c",
            "success": "#2ecc71",
        }
        border = colors.get(level, "#4a90e2")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: #1b263b;
                color: #e0e6ed;
                border: 2px solid {border};
                border-radius: 8px;
                padding: 12px 18px;
                font-size: 10pt;
                font-weight: 600;
            }}
        """)
        self.setText(text)
        self.setWordWrap(True)
        self.setMaximumWidth(420)
        self.adjustSize()
        self.show()
        self.raise_()

        Toast._active.append(self)
        self._reposition_all()

        QTimer.singleShot(duration_ms, self._close_toast)

    @classmethod
    def _reposition_all(cls):
        """Расположить все активные тосты в правом нижнем углу снизу вверх."""
        # Чистим мёртвые ссылки
        cls._active = [t for t in cls._active if t.isVisible()]

        if not cls._active:
            return

        parent = cls._active[0].parentWidget()
        if not parent:
            return

        margin = 20
        spacing = 10
        y = parent.height() - margin

        # Идём от самого нового к старому снизу вверх
        for toast in reversed(cls._active):
            toast.adjustSize()
            y -= toast.height()
            x = parent.width() - toast.width() - margin
            toast.move(max(x, 0), max(y, 0))
            toast.raise_()
            y -= spacing

    def _close_toast(self):
        try:
            Toast._active.remove(self)
        except ValueError:
            pass
        self.close()
        self.deleteLater()
        Toast._reposition_all()


def show_toast(parent: QWidget, text: str, level: str = "info", duration_ms: int = 4000):
    """Показать тост внутри родительского окна."""
    if parent is None:
        return None
    try:
        return Toast(parent, text, level, duration_ms)
    except Exception as e:
        print(f"[Toast] Ошибка: {e}")
        return None