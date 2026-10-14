"""
Локализация MC Bot Suite (RU ↔ EN).

Использование:
    from i18n import tr, set_language, get_language

    label = QLabel(tr("btn.connect"))
    set_language("en")  # переключить на английский
"""

from __future__ import annotations

_current = "ru"


STRINGS: dict[str, dict[str, str]] = {
    # ====================== РУССКИЙ ======================
    "ru": {
        # Общее
        "app.title": "MC Bot Suite — автономный бот для Minecraft",
        "app.header": "MC Bot Suite",

        # Вкладки
        "tab.dashboard": "Панель",
        "tab.map": "Карта",
        "tab.routes": "Маршруты",
        "tab.messages": "Сообщения",
        "tab.inventory": "Инвентарь",
        "tab.control": "Управление",
        "tab.statistics": "Статистика",
        "tab.settings": "Настройки",
        "tab.log": "Журнал",

        # Кнопки — Панель
        "btn.connect": "Подключиться",
        "btn.disconnect": "Отключиться",
        "btn.start": "Запустить",
        "btn.pause": "Пауза",
        "btn.resume": "Продолжить",
        "btn.stop": "Остановить",

        # Панель — заголовки
        "panel.status": "Статус",
        "panel.state": "Состояние",
        "panel.task": "Текущая задача",
        "panel.control": "Управление",
        "panel.appearance": "Внешний вид",

        # Панель — поля
        "field.connection": "Состояние:",
        "field.nick": "Ник:",
        "field.version": "Версия:",
        "field.task.default": "Ожидание",
        "field.position": "📍 X: {x}  Y: {y}  Z: {z}",

                # Задачи (текущая задача)
        "task.idle": "Ожидание",
        "task.paused": "Пауза",
        "task.running_route": "Выполнение маршрута «{name}»",
        "task.running_route_unnamed": "Выполнение маршрута",
        "task.moving_to": "Перемещение к точке «{name}» ({i}/{n})",
        "task.moving_to_unnamed": "Перемещение к точке №{i} ({i}/{n})",
        "task.moving_to_xy": "Перемещение к ({x}, {y}, {z})",
        "task.safety_pause": "⚠️ Критическое состояние — пауза",
        "task.safety_disconnect": "⚠️ Критическое состояние — отключение",

        # Статусы бота
        "status.disconnected": "⚫ Не подключён",
        "status.connecting": "🔵 Подключается",
        "status.connected": "🟢 Работает",
        "status.reconnecting": "🟣 Переподключение",
        "status.paused": "🟡 Пауза",
        "status.stopped": "🔴 Остановлен",
        "status.warning": "⚠️ Внимание",

        # Внешний вид
        "appearance.theme": "Тема:",
        "appearance.custom_bg": "Выбрать свой цвет фона…",
        "appearance.custom_bg_none": "Свой цвет: не задан",
        "appearance.custom_bg_set": "Свой цвет: {color}",
        "appearance.reset_theme": "Сбросить к тёмно-синей",
        "appearance.language": "Язык:",
        "language.ru": "Русский",
        "language.en": "English",

        # Карта
        "map.clear_route": "Очистить маршрут на карте",
        "map.placeholder": "Нет данных — подключитесь и запустите маршрут",
        "map.home": "Дом",
        "map.grid_step": "сетка {step} бл.",

        # Статистика
        "stats.box": "Статистика",
        "stats.uptime": "Время работы приложения:",
        "stats.connection": "Время в подключении:",
        "stats.reconnects": "Переподключений:",
        "stats.distance": "Пройденное расстояние:",
        "stats.messages": "Отправлено сообщений:",
        "stats.routes": "Маршрутов завершено:",
        "stats.damage": "Получено урона:",
        "stats.reset": "Сбросить статистику",

        # Настройки — Minecraft
        "settings.minecraft": "Minecraft",
        "settings.host": "Адрес сервера:",
        "settings.port": "Порт:",
        "settings.version": "Версия Minecraft:",
        "settings.auth": "Тип авторизации:",
        "settings.auto_connect": "Подключаться автоматически при запуске",

        # Настройки — Ники
        "settings.nicks": "Ники",
        "settings.nick_add": "Добавить",
        "settings.nick_edit": "Редактировать",
        "settings.nick_del": "Удалить",
        "settings.nick_random": "Выбирать случайный ник при подключении",
        "settings.nick_current": "Текущий ник:",
        "settings.nick_pick": "Выбрать",

        # Настройки — Поведение
        "settings.behavior": "Поведение",
        "settings.behavior.random_walk": "Использовать случайное перемещение",
        "settings.behavior.use_routes": "Использовать маршруты",
        "settings.behavior.loop_routes": "Повторять маршрут",
        "settings.behavior.return_home": "Возвращаться домой после маршрута",
        "settings.behavior.show_track": "Показывать трек пути на карте",
        "settings.behavior.auto_reconnect": "Автоматически переподключаться",
        "settings.behavior.max_reconnect": "Макс. попыток переподключения:",
        "settings.behavior.reconnect_delay": "Базовая задержка:",

        # Настройки — Безопасность
        "settings.safety": "Безопасность",
        "settings.safety.min_health": "Минимально допустимое здоровье:",
        "settings.safety.min_food": "Минимально допустимый голод:",
        "settings.safety.action": "Действие при критическом состоянии:",

        # Настройки — кнопки
        "settings.save": "Сохранить",
        "settings.save_dirty": "Сохранить ●",
        "settings.reset": "Сбросить к умолчаниям",

        # Журнал
        "log.clear": "Очистить журнал",

        # Инвентарь
        "inv.armor": "Экипировка",
        "inv.inventory": "Инвентарь",
        "inv.hotbar": "Хотбар",
        "inv.selection": "Выделение",
        "inv.slot": "Слот:",
        "inv.nothing": "— ничего —",
        "inv.slot_empty": "слот {slot} — пусто",
        "inv.slot_info": "[{slot}] {name} ×{count}{food_suffix}",
        "inv.quick_actions": "Быстрые действия",
        "inv.eat": "Съесть выделенное",
        "inv.use": "Использовать",
        "inv.drop_box": "Выброс предмета",
        "inv.drop_amount": "Количество:",
        "inv.drop_btn": "Выбросить выделенное",
        "inv.refresh": "Обновить",
        "inv.filter": "Фильтр",
        "inv.filter_nonempty": "Показывать только непустые слоты",
        "inv.auto_eat": "Автопитание",
        "inv.auto_eat_enabled": "Автоматически есть",
        "inv.auto_eat_threshold": "при голоде <",

        # Инвентарь — ошибки
        "inv.error.not_food": "Не еда",
        "inv.error.not_food_msg": "Этот предмет нельзя съесть.",
        "inv.error.no_selection": "Нет выделения",
        "inv.error.no_selection_msg": "Сначала выберите слот.",
        "inv.error.empty": "Пусто",
        "inv.error.empty_msg": "Слот пуст.",
        "inv.error.too_many": "Слишком много",
        "inv.error.too_many_msg": "В слоте только {count} предметов. Нельзя выбросить {n}.",
        "inv.log.eat_request": "Запрос съесть слот {slot}.",
        "inv.log.drop_request": "Запрос выбросить слот {slot} ×{count}.",
        "inv.log.refresh_request": "Запрос обновления инвентаря.",
        "inv.log.use_stub": "Использовать слот {slot} (будет в 10.4).",
        "inv.log.double_click": "Двойной клик: слот {slot} («{name}»).",
        "inv.log.auto_eat": "Автопитание: {state}, порог {threshold}.",
        "inv.log.auto_eat_on": "вкл",
        "inv.log.auto_eat_off": "выкл",

        # Управление
        "ctrl.active_action": "Активное действие: {state}",
        "ctrl.active.none": "⚪ Нет",
        "ctrl.active.combat": "🔴 Атака моба",
        "ctrl.active.dig": "🔵 Копание",
        "ctrl.active.look": "🟢 Поворот",
        "ctrl.combat.title": "Авто-удар   *ДО 1.20.5",
        "ctrl.combat.warn": ("⚠️ На версиях 1.20.5+ авто-удар может вызывать кик "
                             "из-за ограничений Mineflayer. Функция работает на 1.20.4 и ниже."),
        "ctrl.combat.tooltip": ("На Minecraft 1.20.5 и выше многие серверы (включая Aternos с античитами) "
                                "кикают бота при использовании авто-удара из-за ограничений протокола Mineflayer.\n\n"
                                "Используйте на версиях 1.20.4 и ниже."),
        "ctrl.combat.interval": "Интервал удара:",
        "ctrl.combat.radius": "Радиус поиска:",
        "ctrl.combat.ignore_players": "Игнорировать игроков",
        "ctrl.combat.start": "Запустить",
        "ctrl.combat.stop": "Остановить",
        "ctrl.dig.title": "Копание",
        "ctrl.dig.x": "Точка взгляда X:",
        "ctrl.dig.y": "Y:",
        "ctrl.dig.z": "Z:",
        "ctrl.look.title": "Поворот",
        "ctrl.look.x": "Точка X:",
        "ctrl.look.y": "Y:",
        "ctrl.look.z": "Z:",
        "ctrl.look.btn": "Повернуть",
        "ctrl.log.combat_start": "Авто-удар запущен.",
        "ctrl.log.combat_stop": "Авто-удар остановлен.",
        "ctrl.log.dig_start": "Копание запущено: ({x}, {y}, {z})",
        "ctrl.log.dig_stop": "Копание остановлено.",
        "ctrl.log.look": "Поворот на ({x}, {y}, {z})",

        # Маршруты
        "routes.saved": "Сохранённые маршруты",
        "routes.create": "Создать",
        "routes.delete": "Удалить",
        "routes.editor": "Редактор маршрута",
        "routes.name": "Название:",
        "routes.loop": "Повторять маршрут",
        "routes.return_home": "Возвращаться домой после завершения",
        "routes.points": "Точки маршрута:",
        "routes.point_name": "Название",
        "routes.add_point": "+ Добавить точку",
        "routes.delete_point": "Удалить точку",
        "routes.save": "Сохранить",
        "routes.start": "Запустить",
        "routes.pause": "Пауза",
        "routes.resume": "Продолжить",
        "routes.stop": "Стоп",
        "routes.route_label": "{name} ({n} т.)",
        "routes.new_title": "Новый маршрут",
        "routes.new_prompt": "Название маршрута:",
        "routes.delete_title": "Удаление маршрута",
        "routes.delete_prompt": "Удалить маршрут «{name}»?",
        "routes.new_point": "Новая точка",
        "routes.new_point_prompt": "Название точки:",
        "routes.error_coords": "Некорректные координаты в строке {row}.",
        "routes.error_title": "Ошибка",
        "routes.empty_title": "Пустой маршрут",
        "routes.empty_msg": "Добавьте хотя бы одну точку.",

        # Сообщения (чат)
        "msg.list": "Список сообщений",
        "msg.add": "Добавить",
        "msg.edit": "Редактировать",
        "msg.delete": "Удалить",
        "msg.preview": "Предпросмотр случайного",
        "msg.auto_box": "Автоотправка",
        "msg.auto_enabled": "Отправлять сообщения автоматически",
        "msg.min_interval": "Минимальный интервал:",
        "msg.max_interval": "Максимальный интервал:",
        "msg.random_interval": "Случайный интервал между мин и макс",
        "msg.send_now": "Отправить сейчас",
        "msg.send_placeholder": "Введите сообщение и нажмите Enter…",
        "msg.send_btn": "Отправить",
        "msg.new_title": "Новое сообщение",
        "msg.new_prompt": "Введите текст:",
        "msg.edit_title": "Редактирование",
        "msg.edit_prompt": "Измените текст:",
        "msg.delete_title": "Удаление",
        "msg.delete_prompt": "Удалить сообщение «{msg}»?",
        "msg.random_title": "Случайное сообщение",
        "msg.empty_title": "Пусто",
        "msg.empty_msg": "Список сообщений пуст.",

        # Общие диалоги
        "dlg.yes": "Да",
        "dlg.no": "Нет",
        "dlg.restart_title": "Перезапуск",
        "dlg.restart_msg": "Перезапустить интерфейс? Текущая сессия будет завершена.",
        "dlg.exit_title": "Выход",
        "dlg.exit_msg": "Бот подключён. Отключиться и выйти?",
        "dlg.disconnect_title": "Отключение",
        "dlg.disconnect_msg": "Вы действительно хотите отключить бота?",
        "dlg.stop_title": "Остановка",
        "dlg.stop_msg": "Вы действительно хотите остановить бота?",
        "dlg.reset_settings_title": "Сброс настроек",
        "dlg.reset_settings_msg": "Сбросить все настройки к значениям по умолчанию?",
        "dlg.reset_stats_title": "Сброс статистики",
        "dlg.reset_stats_msg": "Сбросить всю статистику к нулю?",
        "dlg.nick_add_title": "Новый ник",
        "dlg.nick_add_prompt": "Введите ник:",
        "dlg.nick_edit_title": "Редактирование ника",
        "dlg.nick_edit_prompt": "Измените ник:",
        "dlg.nick_del_title": "Удаление",
        "dlg.nick_del_prompt": "Удалить ник «{nick}»?",
        "dlg.nick_not_selected_title": "Ник не выбран",
        "dlg.nick_not_selected_msg": "Сначала выделите ник в списке слева.",

        # Уведомления (тосты)
        "toast.route_done": "Маршрут «{name}» завершён",
        "toast.damage": "Получен урон: -{amount:.1f} HP",
        "toast.safety_warning": "⚠️ {reason}\n{action}",
        "toast.safety_ok": "✅ Состояние в норме (HP {hp:.1f}, голод {food:.1f})",
        "toast.theme_saved": "Тема сохранена",

        # Логи
        "log.info": "ИНФО",
        "log.warning": "ПРЕД",
        "log.error": "ОШИБКА",
        "log.chat": "ЧАТ",

        # Дополнительные
        "misc.connected": "Подключено",
        "misc.disconnected": "Отключено",
        "misc.conn_lost": "Соединение потеряно",
        "misc.coords_copied": "Координаты скопированы",
        "misc.settings_saved": "Настройки сохранены",
        "misc.track_cleared": "Трек пути очищен.",
    },

    # ====================== ENGLISH ======================
    "en": {
        "app.title": "MC Bot Suite — autonomous Minecraft bot",
        "app.header": "MC Bot Suite",

        "tab.dashboard": "Dashboard",
        "tab.map": "Map",
        "tab.routes": "Routes",
        "tab.messages": "Messages",
        "tab.inventory": "Inventory",
        "tab.control": "Control",
        "tab.statistics": "Statistics",
        "tab.settings": "Settings",
        "tab.log": "Log",

        "btn.connect": "Connect",
        "btn.disconnect": "Disconnect",
        "btn.start": "Start",
        "btn.pause": "Pause",
        "btn.resume": "Resume",
        "btn.stop": "Stop",

        "panel.status": "Status",
        "panel.state": "State",
        "panel.task": "Current task",
        "panel.control": "Controls",
        "panel.appearance": "Appearance",

        "theme.dark_blue": "Dark blue",
        "theme.dark_gray": "Dark gray",
        "theme.dark_green": "Dark green",
        "theme.dark_purple": "Dark purple",
        "theme.light": "Light",
        "theme.minecraft": "Minecraft",

                # Названия тем
        "theme.dark_blue": "Тёмно-синяя",
        "theme.dark_gray": "Тёмно-серая",
        "theme.dark_green": "Тёмно-зелёная",
        "theme.dark_purple": "Тёмно-фиолетовая",
        "theme.light": "Светлая",
        "theme.minecraft": "Minecraft",

        "field.connection": "State:",
        "field.nick": "Nickname:",
        "field.version": "Version:",
        "field.task.default": "Idle",
        "field.position": "📍 X: {x}  Y: {y}  Z: {z}",

                "task.idle": "Idle",
        "task.paused": "Paused",
        "task.running_route": "Running route «{name}»",
        "task.running_route_unnamed": "Running route",
        "task.moving_to": "Moving to point «{name}» ({i}/{n})",
        "task.moving_to_unnamed": "Moving to point #{i} ({i}/{n})",
        "task.moving_to_xy": "Moving to ({x}, {y}, {z})",
        "task.safety_pause": "⚠️ Critical state — paused",
        "task.safety_disconnect": "⚠️ Critical state — disconnecting",

        "status.disconnected": "⚫ Disconnected",
        "status.connecting": "🔵 Connecting",
        "status.connected": "🟢 Running",
        "status.reconnecting": "🟣 Reconnecting",
        "status.paused": "🟡 Paused",
        "status.stopped": "🔴 Stopped",
        "status.warning": "⚠️ Warning",

        "appearance.theme": "Theme:",
        "appearance.custom_bg": "Choose custom background color…",
        "appearance.custom_bg_none": "Custom color: not set",
        "appearance.custom_bg_set": "Custom color: {color}",
        "appearance.reset_theme": "Reset to dark blue",
        "appearance.language": "Language:",
        "language.ru": "Русский",
        "language.en": "English",

        "map.clear_route": "Clear route on map",
        "map.placeholder": "No data — connect and start a route",
        "map.home": "Home",
        "map.grid_step": "grid {step} blocks",

        "stats.box": "Statistics",
        "stats.uptime": "App uptime:",
        "stats.connection": "Time connected:",
        "stats.reconnects": "Reconnects:",
        "stats.distance": "Distance traveled:",
        "stats.messages": "Messages sent:",
        "stats.routes": "Routes completed:",
        "stats.damage": "Damage taken:",
        "stats.reset": "Reset statistics",

        "settings.minecraft": "Minecraft",
        "settings.host": "Server address:",
        "settings.port": "Port:",
        "settings.version": "Minecraft version:",
        "settings.auth": "Auth type:",
        "settings.auto_connect": "Auto-connect on startup",

        "settings.nicks": "Nicknames",
        "settings.nick_add": "Add",
        "settings.nick_edit": "Edit",
        "settings.nick_del": "Delete",
        "settings.nick_random": "Pick random nickname on connect",
        "settings.nick_current": "Current nickname:",
        "settings.nick_pick": "Choose",

        "settings.behavior": "Behavior",
        "settings.behavior.random_walk": "Use random walking",
        "settings.behavior.use_routes": "Use routes",
        "settings.behavior.loop_routes": "Loop route",
        "settings.behavior.return_home": "Return home after route",
        "settings.behavior.show_track": "Show path track on map",
        "settings.behavior.auto_reconnect": "Auto-reconnect",
        "settings.behavior.max_reconnect": "Max reconnect attempts:",
        "settings.behavior.reconnect_delay": "Base delay:",

        "settings.safety": "Safety",
        "settings.safety.min_health": "Minimum health:",
        "settings.safety.min_food": "Minimum food:",
        "settings.safety.action": "Action on critical state:",

        "settings.save": "Save",
        "settings.save_dirty": "Save ●",
        "settings.reset": "Reset to defaults",

        "log.clear": "Clear log",

        "inv.armor": "Equipment",
        "inv.inventory": "Inventory",
        "inv.hotbar": "Hotbar",
        "inv.selection": "Selection",
        "inv.slot": "Slot:",
        "inv.nothing": "— nothing —",
        "inv.slot_empty": "slot {slot} — empty",
        "inv.slot_info": "[{slot}] {name} ×{count}{food_suffix}",
        "inv.quick_actions": "Quick actions",
        "inv.eat": "Eat selected",
        "inv.use": "Use",
        "inv.drop_box": "Drop item",
        "inv.drop_amount": "Amount:",
        "inv.drop_btn": "Drop selected",
        "inv.refresh": "Refresh",
        "inv.filter": "Filter",
        "inv.filter_nonempty": "Show only non-empty slots",
        "inv.auto_eat": "Auto-eat",
        "inv.auto_eat_enabled": "Eat automatically",
        "inv.auto_eat_threshold": "when food <",

        "inv.error.not_food": "Not food",
        "inv.error.not_food_msg": "This item cannot be eaten.",
        "inv.error.no_selection": "No selection",
        "inv.error.no_selection_msg": "Select a slot first.",
        "inv.error.empty": "Empty",
        "inv.error.empty_msg": "The slot is empty.",
        "inv.error.too_many": "Too many",
        "inv.error.too_many_msg": "The slot contains only {count} items. Cannot drop {n}.",
        "inv.log.eat_request": "Request to eat slot {slot}.",
        "inv.log.drop_request": "Request to drop slot {slot} ×{count}.",
        "inv.log.refresh_request": "Request to refresh inventory.",
        "inv.log.use_stub": "Use slot {slot} (coming in 10.4).",
        "inv.log.double_click": "Double click: slot {slot} («{name}»).",
        "inv.log.auto_eat": "Auto-eat: {state}, threshold {threshold}.",
        "inv.log.auto_eat_on": "on",
        "inv.log.auto_eat_off": "off",

        "ctrl.active_action": "Active action: {state}",
        "ctrl.active.none": "⚪ None",
        "ctrl.active.combat": "🔴 Combat",
        "ctrl.active.dig": "🔵 Digging",
        "ctrl.active.look": "🟢 Look",
        "ctrl.combat.title": "Auto-combat   *UP TO 1.20.5",
        "ctrl.combat.warn": ("⚠️ On versions 1.20.5+ auto-combat may cause a kick "
                             "due to Mineflayer limitations. Works on 1.20.4 and below."),
        "ctrl.combat.tooltip": ("On Minecraft 1.20.5+ many servers (including Aternos with anticheats) "
                                "kick the bot when using auto-combat due to Mineflayer protocol limitations.\n\n"
                                "Use on 1.20.4 and below."),
        "ctrl.combat.interval": "Attack interval:",
        "ctrl.combat.radius": "Search radius:",
        "ctrl.combat.ignore_players": "Ignore players",
        "ctrl.combat.start": "Start",
        "ctrl.combat.stop": "Stop",
        "ctrl.dig.title": "Digging",
        "ctrl.dig.x": "Look point X:",
        "ctrl.dig.y": "Y:",
        "ctrl.dig.z": "Z:",
        "ctrl.look.title": "Look at",
        "ctrl.look.x": "Point X:",
        "ctrl.look.y": "Y:",
        "ctrl.look.z": "Z:",
        "ctrl.look.btn": "Look",
        "ctrl.log.combat_start": "Auto-combat started.",
        "ctrl.log.combat_stop": "Auto-combat stopped.",
        "ctrl.log.dig_start": "Digging started: ({x}, {y}, {z})",
        "ctrl.log.dig_stop": "Digging stopped.",
        "ctrl.log.look": "Look at ({x}, {y}, {z})",

        "routes.saved": "Saved routes",
        "routes.create": "Create",
        "routes.delete": "Delete",
        "routes.editor": "Route editor",
        "routes.name": "Name:",
        "routes.loop": "Loop route",
        "routes.return_home": "Return home after completion",
        "routes.points": "Route points:",
        "routes.point_name": "Name",
        "routes.add_point": "+ Add point",
        "routes.delete_point": "Delete point",
        "routes.save": "Save",
        "routes.start": "Start",
        "routes.pause": "Pause",
        "routes.resume": "Resume",
        "routes.stop": "Stop",
        "routes.route_label": "{name} ({n} pts)",
        "routes.new_title": "New route",
        "routes.new_prompt": "Route name:",
        "routes.delete_title": "Delete route",
        "routes.delete_prompt": "Delete route «{name}»?",
        "routes.new_point": "New point",
        "routes.new_point_prompt": "Point name:",
        "routes.error_coords": "Invalid coordinates in row {row}.",
        "routes.error_title": "Error",
        "routes.empty_title": "Empty route",
        "routes.empty_msg": "Add at least one point.",

        "msg.list": "Message list",
        "msg.add": "Add",
        "msg.edit": "Edit",
        "msg.delete": "Delete",
        "msg.preview": "Preview random",
        "msg.auto_box": "Auto-send",
        "msg.auto_enabled": "Send messages automatically",
        "msg.min_interval": "Min interval:",
        "msg.max_interval": "Max interval:",
        "msg.random_interval": "Random interval between min and max",
        "msg.send_now": "Send now",
        "msg.send_placeholder": "Type a message and press Enter…",
        "msg.send_btn": "Send",
        "msg.new_title": "New message",
        "msg.new_prompt": "Enter text:",
        "msg.edit_title": "Edit",
        "msg.edit_prompt": "Edit text:",
        "msg.delete_title": "Delete",
        "msg.delete_prompt": "Delete message «{msg}»?",
        "msg.random_title": "Random message",
        "msg.empty_title": "Empty",
        "msg.empty_msg": "Message list is empty.",

        "dlg.yes": "Yes",
        "dlg.no": "No",
        "dlg.restart_title": "Restart",
        "dlg.restart_msg": "Restart the interface? Current session will end.",
        "dlg.exit_title": "Exit",
        "dlg.exit_msg": "Bot is connected. Disconnect and exit?",
        "dlg.disconnect_title": "Disconnect",
        "dlg.disconnect_msg": "Are you sure you want to disconnect the bot?",
        "dlg.stop_title": "Stop",
        "dlg.stop_msg": "Are you sure you want to stop the bot?",
        "dlg.reset_settings_title": "Reset settings",
        "dlg.reset_settings_msg": "Reset all settings to defaults?",
        "dlg.reset_stats_title": "Reset statistics",
        "dlg.reset_stats_msg": "Reset all statistics to zero?",
        "dlg.nick_add_title": "New nickname",
        "dlg.nick_add_prompt": "Enter nickname:",
        "dlg.nick_edit_title": "Edit nickname",
        "dlg.nick_edit_prompt": "Edit nickname:",
        "dlg.nick_del_title": "Delete",
        "dlg.nick_del_prompt": "Delete nickname «{nick}»?",
        "dlg.nick_not_selected_title": "No nickname selected",
        "dlg.nick_not_selected_msg": "Select a nickname in the list first.",

        "toast.route_done": "Route «{name}» completed",
        "toast.damage": "Damage taken: -{amount:.1f} HP",
        "toast.safety_warning": "⚠️ {reason}\n{action}",
        "toast.safety_ok": "✅ State is normal (HP {hp:.1f}, food {food:.1f})",
        "toast.theme_saved": "Theme saved",

        "log.info": "INFO",
        "log.warning": "WARN",
        "log.error": "ERROR",
        "log.chat": "CHAT",

        "misc.connected": "Connected",
        "misc.disconnected": "Disconnected",
        "misc.conn_lost": "Connection lost",
        "misc.coords_copied": "Coordinates copied",
        "misc.settings_saved": "Settings saved",
        "misc.track_cleared": "Path track cleared.",
    },
}


def set_language(lang: str) -> None:
    """Установить текущий язык. Значение сохраняется в памяти процесса."""
    global _current
    if lang in STRINGS:
        _current = lang


def get_language() -> str:
    """Вернуть текущий код языка (ru/en)."""
    return _current


def tr(key: str, **kwargs) -> str:
    """
    Получить перевод по ключу.
    Если ключа нет — вернуть сам ключ (чтобы не падало).
    Если переданы kwargs — подставить их через str.format.
    """
    table = STRINGS.get(_current) or STRINGS["ru"]
    text = table.get(key)
    if text is None:
        # fallback: сначала пробуем русский
        text = STRINGS["ru"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text