import asyncio
import json
import threading
from typing import Optional

import websockets

from .events import bus


class BotClient:
    def __init__(self, uri: str = "ws://127.0.0.1:34567"):
        self.uri = uri
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ws = None
        self._outbox: Optional[asyncio.Queue] = None
        self._running = False

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop)

    def send_command(self, cmd_type: str, payload: dict | None = None) -> None:
        if not self._loop or not self._outbox:
            bus.error_occurred.emit("Нет связи с bot-core. Запустите Node-процесс.")
            return
        msg = {"type": cmd_type, "payload": payload or {}}
        asyncio.run_coroutine_threadsafe(self._outbox.put(msg), self._loop)

    def _run_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._main())
        finally:
            self._loop.close()

    async def _main(self) -> None:
        self._outbox = asyncio.Queue()
        backoff = 1
        while self._running:
            try:
                async with websockets.connect(self.uri, ping_interval=20) as ws:
                    self._ws = ws
                    bus.ws_status_changed.emit(True)
                    backoff = 1
                    await asyncio.gather(self._reader(ws), self._writer(ws))
            except (ConnectionRefusedError, OSError) as e:
                bus.ws_status_changed.emit(False)
                bus.error_occurred.emit(
                    f"Не удалось подключиться к bot-core: {e}. Повтор через {backoff}с."
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 15)
            except Exception as e:
                bus.error_occurred.emit(f"Ошибка WS-клиента: {e}")
                await asyncio.sleep(2)

    async def _reader(self, ws) -> None:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            self._dispatch(msg)

    async def _writer(self, ws) -> None:
        while True:
            msg = await self._outbox.get()
            await ws.send(json.dumps(msg))

    async def _shutdown(self) -> None:
        if self._ws:
            await self._ws.close()
        if self._outbox:
            await self._outbox.put({"type": "disconnect", "payload": {}})

    def _dispatch(self, msg: dict) -> None:
        t = msg.get("type")
        p = msg.get("payload") or {}

        if t == "state":
            bus.state_updated.emit(p)
        elif t == "log":
            bus.log_message.emit(p)
        elif t == "connected":
            bus.connected.emit()
        elif t == "disconnected":
            bus.disconnected.emit(p.get("reason", ""))
        elif t == "error":
            bus.error_occurred.emit(p.get("message", "Неизвестная ошибка"))
        elif t == "chat_sent":
            bus.chat_sent.emit(p)
        elif t == "chat_auto_sent":
            bus.chat_auto_sent.emit(p)
        elif t == "route_progress":
            bus.route_progress.emit(p)
        elif t == "route_completed":
            bus.route_completed.emit(p)
        elif t == "damage":
            bus.damage_taken.emit(p)
        elif t == "stat_snapshot":
            bus.stat_snapshot.emit(p)
        elif t == "safety_warning":
            bus.safety_warning.emit(p)
        elif t == "safety_ok":
            bus.safety_ok.emit(p)
        elif t == "inventory":
            bus.inventory_updated.emit(p)
        elif t == "combat_status":
            bus.combat_status.emit(p)
        elif t == "dig_status":
            bus.dig_status.emit(p)