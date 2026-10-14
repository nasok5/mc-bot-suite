import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from core.bot_client import BotClient
from modules.storage import Storage
from modules.theme import build_qss
from i18n import set_language
from ui.main_window import MainWindow


def load_icon(app: QApplication) -> None:
    icon_path = Path(__file__).parent / "ui" / "theme" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))


def apply_saved_settings(app: QApplication, storage: Storage) -> None:
    settings = storage.load("settings")
    ui = settings.get("ui", {})

    # Язык
    lang = ui.get("language", "ru")
    if lang not in ("ru", "en"):
        lang = "ru"
    set_language(lang)

    # Тема
    theme_name = ui.get("theme", "dark_blue")
    custom_bg = ui.get("custom_bg")
    qss = build_qss(theme_name, custom_bg)
    app.setStyleSheet(qss)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("MC Bot Suite")
    app.setOrganizationName("MCBotSuite")
    load_icon(app)

    storage = Storage()
    apply_saved_settings(app, storage)
        # Отправить язык в bot-core (повторим при подключении)
    from i18n import get_language
    QTimer.singleShot(1500, lambda: client.send_command(
        "set_language", {"lang": get_language()}
    ))
    

    client = BotClient("ws://127.0.0.1:34567")
    client.start()

    window = MainWindow(client)
    window.show()

    exit_code = app.exec()
    client.stop()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())