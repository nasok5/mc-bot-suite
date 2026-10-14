"""
Генератор QSS-тем для MC Bot Suite.

- Предустановленные палитры (6 штук).
- Свободный выбор цвета фона через QColorDialog.
- Автоконтраст текста (светлый фон -> тёмный текст и наоборот).
"""

from PySide6.QtGui import QColor


# ===== Палитры предустановленных тем =====
# Каждая палитра — набор базовых цветов, из которых строится QSS.
# bg     — основной фон
# panel  — панели/группы
# panel2 — поля ввода/списки
# border — рамки
# accent — акцентный цвет
# accent2— акцент при hover
# text   — основной текст
# muted  — приглушённый текст
# success/warning/error — состояния

PRESETS = {
    "dark_blue": {
        "name": "theme.dark_blue",
        "bg":      "#0d1b2a",
        "panel":   "#1b263b",
        "panel2":  "#14243a",
        "border":  "#2f4f7f",
        "accent":  "#4a90e2",
        "accent2": "#6aa8f0",
        "text":    "#e0e6ed",
        "muted":   "#8fa3bf",
    },
    "dark_gray": {
        "name": "theme.dark_gray",
        "bg":      "#1a1a1a",
        "panel":   "#252525",
        "panel2":  "#1e1e1e",
        "border":  "#3d3d3d",
        "accent":  "#888888",
        "accent2": "#aaaaaa",
        "text":    "#e6e6e6",
        "muted":   "#8a8a8a",
    },
    "dark_green": {
        "name": "theme.dark_green",
        "bg":      "#0d1b12",
        "panel":   "#16281d",
        "panel2":  "#102018",
        "border":  "#2d4d38",
        "accent":  "#2ecc71",
        "accent2": "#55d98d",
        "text":    "#e0ede6",
        "muted":   "#7fa38b",
    },
    "dark_purple": {
        "name": "theme.dark_purple",
        "bg":      "#1a0d2a",
        "panel":   "#291b3b",
        "panel2":  "#20143a",
        "border":  "#4a2f7f",
        "accent":  "#9b59b6",
        "accent2": "#b07cc6",
        "text":    "#ece0ed",
        "muted":   "#a38fbf",
    },
    "light": {
        "name": "theme.light",
        "bg":      "#f0f0f0",
        "panel":   "#ffffff",
        "panel2":  "#f8f8f8",
        "border":  "#c0c0c0",
        "accent":  "#2a7ae2",
        "accent2": "#4a9af0",
        "text":    "#1a1a1a",
        "muted":   "#666666",
    },
    "minecraft": {
        "name": "theme.minecraft",
        "bg":      "#2b2118",
        "panel":   "#3a2e20",
        "panel2":  "#332720",
        "border":  "#5a4632",
        "accent":  "#7fae3f",
        "accent2": "#9bc95f",
        "text":    "#e8d9b8",
        "muted":   "#a89170",
    },
}


# ===== Цвета состояний (одинаковы для всех тем) =====
SUCCESS = "#2ecc71"
WARNING = "#f1c40f"
ERROR   = "#e74c3c"


def _contrast_text(bg_hex: str) -> str:
    """Вернуть чёрный или белый текст в зависимости от яркости фона."""
    c = QColor(bg_hex)
    # W3C-формула яркости
    r, g, b = c.redF(), c.greenF(), c.blueF()
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#1a1a1a" if lum > 0.5 else "#f0f0f0"


def _shift(hex_color: str, delta: int) -> str:
    """Осветлить (delta > 0) или затемнить (delta < 0) HEX-цвет."""
    c = QColor(hex_color)
    r = max(0, min(255, c.red() + delta))
    g = max(0, min(255, c.green() + delta))
    b = max(0, min(255, c.blue() + delta))
    return QColor(r, g, b).name()


def _mix(hex1: str, hex2: str, t: float = 0.5) -> str:
    """Смешать два цвета. t=0 — только hex1, t=1 — только hex2."""
    c1, c2 = QColor(hex1), QColor(hex2)
    r = int(c1.red()   * (1 - t) + c2.red()   * t)
    g = int(c1.green() * (1 - t) + c2.green() * t)
    b = int(c1.blue()  * (1 - t) + c2.blue()  * t)
    return QColor(r, g, b).name()


def _build_custom_qss(bg_hex: str) -> str:
    """
    Построить QSS из одного пользовательского цвета фона.
    Автоматически вычисляет панели, кнопки, рамки, текст.
    """
    is_light = QColor(bg_hex).lightness() > 128

    if is_light:
        panel   = _shift(bg_hex, -12)
        panel2  = _shift(bg_hex, -20)
        border  = _shift(bg_hex, -60)
        accent  = "#2a7ae2"
        accent2 = "#4a9af0"
        text    = "#1a1a1a"
        muted   = "#555555"
    else:
        panel   = _shift(bg_hex, +18)
        panel2  = _shift(bg_hex, +10)
        border  = _shift(bg_hex, +50)
        accent  = _mix(bg_hex, "#4a90e2", 0.5)
        accent2 = _shift(accent, +30)
        text    = "#f0f0f0"
        muted   = _shift(bg_hex, +90)

    return _render_qss({
        "bg": bg_hex,
        "panel": panel,
        "panel2": panel2,
        "border": border,
        "accent": accent,
        "accent2": accent2,
        "text": text,
        "muted": muted,
    })


def _build_preset_qss(name: str) -> str:
    if name not in PRESETS:
        name = "dark_blue"
    return _render_qss(PRESETS[name])


def build_qss(theme_name: str = "dark_blue", custom_bg: str | None = None) -> str:
    """Главная функция. Возвращает QSS для применения через app.setStyleSheet()."""
    if custom_bg:
        try:
            return _build_custom_qss(custom_bg)
        except Exception:
            # Если пользовательский цвет некорректный — откат на пресет
            return _build_preset_qss("dark_blue")
    return _build_preset_qss(theme_name)


def theme_display_names() -> dict:
    """{id: 'Локализованное название'} для выпадающего списка."""
    from i18n import get_language
    lang = get_language()

    names = {
        "ru": {
            "dark_blue":   "Тёмно-синяя",
            "dark_gray":   "Тёмно-серая",
            "dark_green":  "Тёмно-зелёная",
            "dark_purple": "Тёмно-фиолетовая",
            "light":       "Светлая",
            "minecraft":   "Minecraft",
        },
        "en": {
            "dark_blue":   "Dark blue",
            "dark_gray":   "Dark gray",
            "dark_green":  "Dark green",
            "dark_purple": "Dark purple",
            "light":       "Light",
            "minecraft":   "Minecraft",
        },
    }
    table = names.get(lang, names["ru"])
    return {key: table.get(key, key) for key in PRESETS.keys()}


# ===== Собственно шаблон QSS =====

def _render_qss(p: dict) -> str:
    return f"""
/* ===== MC Bot Suite — QSS ===== */
QWidget {{
    background-color: {p['bg']};
    color: {p['text']};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 10pt;
}}

QMainWindow, QDialog {{
    background-color: {p['bg']};
}}

/* ===== Вкладки ===== */
QTabWidget::pane {{
    border: 1px solid {p['panel']};
    background: {p['panel']};
    border-radius: 6px;
}}
QTabBar::tab {{
    background: {p['bg']};
    color: {p['muted']};
    padding: 8px 18px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{
    background: {p['panel']};
    color: {p['text']};
    border-bottom: 2px solid {p['accent']};
}}
QTabBar::tab:hover {{
    color: {p['text']};
}}

/* ===== Кнопки ===== */
QPushButton {{
    background-color: {p['panel']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 6px;
    padding: 8px 16px;
    min-height: 22px;
}}
QPushButton:hover {{
    background-color: {p['border']};
    border-color: {p['accent']};
}}
QPushButton:pressed {{
    background-color: {p['panel2']};
}}
QPushButton:disabled {{
    background-color: {p['panel2']};
    color: {p['muted']};
    border-color: {p['border']};
}}
QPushButton#primary {{
    background-color: {p['accent']};
    color: #ffffff;
    border: 1px solid {p['accent']};
    border-radius: 4px;
    padding: 6px 14px;
}}
QPushButton#primary:hover {{
    background-color: {p['accent2']};
    border-color: {p['accent2']};
}}
QPushButton#primary:pressed {{
    background-color: {_shift(p['accent'], -30)};
}}
QPushButton#primary:disabled {{
    background-color: {p['panel2']};
    color: {p['muted']};
    border-color: {p['border']};
}}
QPushButton#danger {{
    background-color: #7a2323;
    color: #ffffff;
    border: 1px solid #a03030;
    border-radius: 4px;
    padding: 6px 14px;
}}
QPushButton#danger:hover {{
    background-color: #a03030;
}}
QPushButton#danger:pressed {{
    background-color: #5a1818;
}}
QPushButton#danger:disabled {{
    background-color: {p['panel2']};
    color: {p['muted']};
    border-color: {p['border']};
}}

/* ===== Поля ввода ===== */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit, QTextEdit {{
    background-color: {p['panel2']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: {p['accent']};
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus,
QPlainTextEdit:focus, QTextEdit:focus {{
    border-color: {p['accent']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background: {p['panel']};
    color: {p['text']};
    selection-background-color: {p['accent']};
    border: 1px solid {p['border']};
}}

/* ===== Списки ===== */
QListWidget, QTreeWidget, QTableWidget {{
    background-color: {p['panel2']};
    border: 1px solid {p['border']};
    border-radius: 6px;
    color: {p['text']};
    gridline-color: {p['panel']};
}}
QListWidget::item:selected, QTreeWidget::item:selected,
QTableWidget::item:selected {{
    background-color: {p['accent']};
    color: #ffffff;
}}
QHeaderView::section {{
    background-color: {p['panel']};
    color: {p['muted']};
    border: none;
    padding: 6px;
}}

/* ===== Скроллбары ===== */
QScrollBar:vertical {{
    background: {p['bg']};
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background: {p['border']};
    border-radius: 5px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {p['accent']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {p['bg']};
    height: 10px;
}}
QScrollBar::handle:horizontal {{
    background: {p['border']};
    border-radius: 5px;
    min-width: 24px;
}}

/* ===== Группы ===== */
QGroupBox {{
    background-color: {p['panel']};
    border: 1px solid {p['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {p['muted']};
}}

/* ===== Метки ===== */
QLabel#value {{
    color: {p['accent']};
    font-weight: 600;
    font-size: 12pt;
}}
QLabel#success {{ color: {SUCCESS}; }}
QLabel#warning {{ color: {WARNING}; }}
QLabel#error   {{ color: {ERROR}; }}
QLabel#muted   {{ color: {p['muted']}; }}
QLabel#critical {{
    color: {ERROR};
    font-weight: 700;
}}
QLabel#warningText {{
    color: {WARNING};
    font-weight: 600;
}}

/* ===== Прогресс-бары ===== */
QProgressBar {{
    background-color: {p['panel2']};
    border: 1px solid {p['border']};
    border-radius: 6px;
    text-align: center;
    color: {p['text']};
    height: 18px;
}}
QProgressBar::chunk {{
    background-color: {p['accent']};
    border-radius: 5px;
}}
QProgressBar#health::chunk {{ background-color: {ERROR}; }}
QProgressBar#food::chunk   {{ background-color: {WARNING}; }}
QProgressBar#healthCritical::chunk {{ background-color: {ERROR}; }}
QProgressBar#foodCritical::chunk   {{ background-color: {ERROR}; }}

/* ===== Статус-бар ===== */
QStatusBar {{
    background: {p['panel']};
    color: {p['muted']};
    border-top: 1px solid {p['border']};
}}

/* ===== Меню ===== */
QMenuBar {{
    background: {p['bg']};
    color: {p['text']};
}}
QMenuBar::item:selected {{ background: {p['panel']}; }}
QMenu {{
    background: {p['panel']};
    color: {p['text']};
    border: 1px solid {p['border']};
}}
QMenu::item:selected {{ background: {p['accent']}; }}

/* ===== Тултипы ===== */
QToolTip {{
    background: {p['panel']};
    color: {p['text']};
    border: 1px solid {p['accent']};
    padding: 4px;
}}

/* ===== Критические состояния ===== */
QGroupBox#warningBox {{
    border: 2px solid {WARNING};
    background-color: {p['panel']};
}}
"""