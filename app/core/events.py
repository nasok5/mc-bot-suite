from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    state_updated = Signal(dict)
    log_message = Signal(dict)
    connected = Signal()
    disconnected = Signal(str)
    error_occurred = Signal(str)
    chat_sent = Signal(dict)
    chat_auto_sent = Signal(dict)
    route_progress = Signal(dict)
    route_completed = Signal(dict)
    damage_taken = Signal(dict)
    stat_snapshot = Signal(dict)
    safety_warning = Signal(dict)
    safety_ok = Signal(dict)
    inventory_updated = Signal(dict)
    combat_status = Signal(dict)
    dig_status = Signal(dict)
    ws_status_changed = Signal(bool)


bus = EventBus()