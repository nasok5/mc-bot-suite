"""
Универсальное JSON-хранилище для MC Bot Suite.

Принципы:
- Атомарная запись (temp-файл + os.replace).
- Резервная копия повреждённого файла -> .bak.
- Значения по умолчанию для каждого файла.
- Блокировка чтения/записи через threading.Lock.
"""

import json
import os
import shutil
import threading
from pathlib import Path
from typing import Any


# ---------- Пути ----------

# data/ рядом с папкой app/
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = _PROJECT_ROOT / "data"


# ---------- Дефолтные схемы ----------

DEFAULTS: dict[str, Any] = {
    "settings": {
        "minecraft": {
            "host": "your-server.aternos.me",
            "port": 25565,
            "version": "1.20.5",
            "username": "AFKBot",
            "auth": "offline",       # offline | microsoft
            "auto_connect_on_start": False,
        },
        "behavior": {
            "use_random_walk": False,
            "use_routes": True,
            "loop_routes": False,
            "return_home_after_route": False,
            "auto_reconnect": True,
            "max_reconnect_attempts": 5,
            "reconnect_base_delay_sec": 5,
        },
        "messages": {
            "enabled": False,
            "min_interval_sec": 60,
            "max_interval_sec": 180,
            "use_random_interval": True,
        },
        "safety": {
            "min_health": 6,
            "min_food": 6,
            "critical_action": "pause",   # pause | disconnect | none
        },
        "auto_eat": {
            "enabled": False,
            "threshold": 17,
        },
        "ui": {
            "last_tab": 0,
            "window_geometry": None,
            "theme": "dark_blue",
            "custom_bg": None,
            "language": "ru",    # base64 QByteArray или None
        },
    },
    "routes": {
        "routes": [],   # [{"id", "name", "loop", "return_home", "points":[{"name","x","y","z"}]}]
    },
    "messages": {
        "items": [
            "Всем привет!",
            "Бот продолжает работать.",
            "Всё под контролем.",
            "Я всё ещё здесь :)",
        ]
    },
    "nicks": {
        "use_random": False,
        "selected": "AFKBot",
        "list": ["AFKBot", "MinerBot", "HelperBot", "AFK_01"],
    },
    "statistics": {
        "total_uptime_sec": 0,
        "total_connection_sec": 0,
        "reconnect_count": 0,
        "distance_traveled": 0.0,
        "messages_sent": 0,
        "routes_completed": 0,
        "damage_taken": 0.0,
    },
}


# ---------- Хранилище ----------

class Storage:
    """Простое потокобезопасное JSON-хранилище для набора именованных файлов."""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._locks: dict[str, threading.Lock] = {
            name: threading.Lock() for name in DEFAULTS
        }
        self._cache: dict[str, dict] = {}

    # -------- публичный API --------

    def load(self, name: str) -> dict:
        """Загрузить файл по имени (settings/routes/...). Кэшируется в памяти."""
        self._validate_name(name)
        with self._locks[name]:
            if name in self._cache:
                return self._cache[name]

            path = self._path(name)
            default = self._deep_copy(DEFAULTS[name])

            if not path.exists():
                self._cache[name] = default
                self._atomic_write(path, default)
                return default

            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                merged = self._merge(default, data)
                self._cache[name] = merged
                return merged
            except (json.JSONDecodeError, OSError) as e:
                # Повреждённый файл -> .bak, ставим дефолт
                bak = path.with_suffix(path.suffix + ".bak")
                try:
                    shutil.copy2(path, bak)
                except OSError:
                    pass
                self._cache[name] = default
                self._atomic_write(path, default)
                print(f"[Storage] Файл {name}.json повреждён ({e}), "
                      f"сохранён как {bak.name}, применены значения по умолчанию.")
                return default

    def save(self, name: str, data: dict) -> None:
        """Сохранить данные в файл по имени. Сливает с дефолтом."""
        self._validate_name(name)
        with self._locks[name]:
            default = self._deep_copy(DEFAULTS[name])
            merged = self._merge(default, data)
            self._cache[name] = merged
            self._atomic_write(self._path(name), merged)

    def update(self, name: str, patch: dict) -> dict:
        """Обновить часть данных (глубокое слияние) и сохранить."""
        current = self.load(name)
        merged = self._merge(current, patch)
        self.save(name, merged)
        return merged

    def reset(self, name: str) -> dict:
        """Сбросить файл к дефолту."""
        self._validate_name(name)
        default = self._deep_copy(DEFAULTS[name])
        self.save(name, default)
        return default

    def export_all(self) -> dict:
        """Собрать все файлы в один dict (для бэкапа)."""
        return {name: self.load(name) for name in DEFAULTS}

    def import_all(self, payload: dict) -> None:
        """Импорт всех файлов (для восстановления из бэкапа)."""
        for name in DEFAULTS:
            if name in payload:
                self.save(name, payload[name])

    # -------- внутренняя кухня --------

    def _validate_name(self, name: str) -> None:
        if name not in DEFAULTS:
            raise KeyError(f"Неизвестный файл хранилища: {name}")

    def _path(self, name: str) -> Path:
        return self.data_dir / f"{name}.json"

    @staticmethod
    def _deep_copy(obj):
        # Быстрее и надёжнее, чем copy.deepcopy для чистых JSON-структур
        return json.loads(json.dumps(obj, ensure_ascii=False))

    @staticmethod
    def _merge(base: Any, override: Any) -> Any:
        """Глубокое слияние: значения override поверх base. Списки — заменяются целиком."""
        if isinstance(base, dict) and isinstance(override, dict):
            result = dict(base)
            for k, v in override.items():
                result[k] = Storage._merge(base.get(k), v) if k in base else v
            return result
        return override

    @staticmethod
    def _atomic_write(path: Path, data: dict) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)   # атомарно на Windows и POSIX