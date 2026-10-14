from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BotState:
    """Текущее состояние бота, получаемое от bot-core."""
    status: str = "disconnected"          # disconnected/connecting/connected/reconnecting
    username: str = "—"
    health: float = 0.0
    max_health: float = 20.0
    food: float = 0.0
    max_food: float = 20.0
    position: dict = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    task: dict = field(default_factory=lambda: {"key": "task.idle"})
    version: str = "1.20.5"

    def apply(self, payload: dict) -> None:
        """Обновить поля из payload, пришедшего от bot-core."""
        self.status = payload.get("status", self.status)
        self.username = payload.get("username", self.username)
        self.health = payload.get("health", self.health)
        self.food = payload.get("food", self.food)
        self.position = payload.get("position", self.position)
        self.task = payload.get("task", self.task)

    @property
    def status_label(self) -> str:
        """Человекочитаемая метка статуса с эмодзи."""
        return {
            "connected": "🟢 Работает",
            "connecting": "🔵 Подключается",
            "reconnecting": "🟣 Переподключение",
            "paused": "🟡 Пауза",
            "stopped": "🔴 Остановлен",
            "warning": "⚠️ Внимание",
            "disconnected": "⚫ Не подключён",
        }.get(self.status, "⚫ Не подключён")