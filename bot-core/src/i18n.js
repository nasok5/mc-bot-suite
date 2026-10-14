/**
 * Мини-локализация для bot-core.
 * Возвращает готовую строку по ключу для текущего языка.
 */

let _current = 'ru';

const STRINGS = {
  ru: {
    // Подключение
    'log.connecting': 'Подключение к {host}:{port} ({version})...',
    'log.bot_joined': 'Бот {user} успешно зашёл на сервер.',
    'log.conn_lost': 'Соединение потеряно: {reason}',
    'log.reconnect_attempt': 'Попытка переподключения №{n}/{max} через {delay}с...',
    'log.reconnect_off': 'Авто-переподключение выключено.',
    'log.reconnect_exhausted': 'Исчерпан лимит попыток переподключения.',
    'log.disconnected_manual': 'Отключение выполнено вручную — переподключение не выполняется.',
    'log.disconnected': 'Бот отключён вручную.',
    'log.already_connected': 'Бот уже подключён или подключается.',
    'log.create_error': 'Ошибка создания бота: {error}',
    'log.generic_error': 'Ошибка: {error}',
    'log.kicked': 'Кикнут: {reason}',
    'log.reconnect_params': 'Переподключение: auto={auto}, max={max}, base={base}с',
    'log.pathfinder_ok': 'Навигация (pathfinder) инициализирована.',
    'log.pathfinder_error': 'Не удалось инициализировать pathfinder: {error}',

    // Урон
    'log.damage_taken': 'Получен урон: -{amount} HP (осталось {hp}).',

    // Трек
    'log.track_cleared': 'Трек пути очищен.',

    // Маршруты
    'log.route_starting': 'Запуск маршрута «{name}» (точек: {n}).',
    'log.route_moving': 'Перемещение к точке {label} ({x}, {y}, {z}).',
    'log.route_reach_fail': 'Не удалось дойти до точки {label}: {error}',
    'log.route_timeout': 'Таймаут навигации к точке {label} — пропускаю.',
    'log.route_return_home': 'Возврат домой ({x}, {y}, {z}).',
    'log.route_home_fail': 'Не удалось вернуться домой: {error}',
    'log.route_looping': 'Маршрут завершён, начинаю заново (loop).',
    'log.route_loop_limit': 'Достигнут лимит повторов маршрута — остановлено.',
    'log.route_completed': 'Маршрут «{name}» завершён.',
    'log.route_stopped': 'Маршрут остановлен пользователем.',
    'log.route_paused': 'Маршрут поставлен на паузу.',
    'log.route_resumed': 'Маршрут продолжен.',
    'log.route_stopping': 'Останавливаю маршрут...',
    'log.route_empty': 'Маршрут пустой — нечего выполнять.',
    'log.route_running': 'Маршрут уже выполняется.',
    'log.route_error': 'Ошибка выполнения маршрута: {error}',
    'log.loop_protection': 'Loop-защита: маршрут повторялся {n} раз, останавливаю.',

    // Чат
    'log.chat_auto': 'Автосообщение: «{msg}»',
    'log.chat_sent': 'Отправлено: «{msg}»',
    'log.chat_auto_error': 'Ошибка автоотправки: {error}',
    'log.chat_not_connected': 'Нельзя отправить сообщение: бот не подключён.',
    'log.chat_scheduler': 'ChatScheduler: enabled={enabled}, интервал {min}-{max}с, сообщений: {n}, random={random}',
    'log.chat_scheduler_empty': 'ChatScheduler: список сообщений пуст, автоотправка отключена.',
    'log.chat_scheduler_stopped': 'Автосообщения остановлены.',

    // Инвентарь
    'log.inv_eaten': 'Съедено: «{name}» ×{n} (слот {slot}, осталось {left}).',
    'log.inv_eat_fail': 'Еда «{name}» не была съедена (голод, возможно, полный).',
    'log.inv_not_food': '«{name}» — не еда',
    'log.inv_slot_empty': 'Слот {slot} пуст',
    'log.inv_equip_fail': 'Не удалось взять предмет: {error}',
    'log.inv_hungry': 'Голод полный — есть не нужно',
    'log.inv_dropped': 'Выброшено: «{name}» ×{n} (слот {slot}).',
    'log.inv_drop_fail': 'Не удалось выбросить: {error}',
    'log.inv_drop_too_many': 'В слоте только {n} предметов',
    'log.inv_drop_min': 'Количество должно быть ≥ 1',
    'log.inv_cant_eat': 'Не удалось съесть: {error}',
    'log.inv_cant_drop': 'Не удалось выбросить: {error}',

    // Автопитание
    'log.auto_eat_config': 'AutoEater: enabled={enabled}, threshold={threshold}',
    'log.auto_eat_no_food': 'Автопитание: нет еды в инвентаре.',
    'log.auto_eat_error': 'Автопитание: ошибка — {error}',

    // Combat
    'log.combat_config': 'CombatController: interval={interval}ms, radius={radius}, ignorePlayers={ignore}',
    'log.combat_start': 'Авто-удар запущен.',
    'log.combat_stop': 'Авто-удар остановлен.',
    'log.combat_not_connected': 'Нельзя запустить авто-удар: бот не подключён.',

    // Копание
    'log.dig_start': 'Копание: направление на ({x}, {y}, {z})',
    'log.dig_no_block': 'Копание: на линии взгляда нет блока в радиусе {r}.',
    'log.dig_unbreakable': 'Копание: блок «{name}» неломаемый.',
    'log.dig_block_broken': 'Блок «{name}» сломан ({x}, {y}, {z}).',
    'log.dig_dig_fail': 'Не удалось сломать блок: {error}',
    'log.dig_error': 'Копание: ошибка — {error}',
    'log.dig_stopped': 'Копание остановлено.',
    'log.dig_not_connected': 'Нельзя начать копание: бот не подключён.',

    // Поворот
    'log.look_done': 'Поворот на ({x}, {y}, {z}) выполнен.',
    'log.look_fail': 'Не удалось повернуться: {error}',

    // Safety
    'log.safety_config': 'SafetyMonitor: min_health={min_h}, min_food={min_f}, action={action}',
    'log.safety_config_updated': 'SafetyMonitor обновлён: min_health={min_h}, min_food={min_f}, action={action}',
    'log.safety_warning': '⚠️ Внимание: {reason}. Действие: {action}',
    'log.safety_ok': '✅ Состояние в норме: HP={hp}, голод={food}.',
    'log.safety_reason_hp': 'критическое HP: {hp}/20',
    'log.safety_reason_food': 'критический голод: {food}/20',
    'log.safety_reason_both': 'критическое HP ({hp}) и голод ({food})',

    // Статистика
    'log.stats_reset': 'Статистика сброшена.',
    'log.stats_loaded': 'Статистика: базовые значения загружены.',

    // Логи
    'log.log_cleared': 'Трек пути очищен.',   // на случай, если нужно
    'log.auto_eat_on': 'вкл',
    'log.auto_eat_off': 'выкл',
  },

  en: {
    // Connection
    'log.connecting': 'Connecting to {host}:{port} ({version})...',
    'log.bot_joined': 'Bot {user} joined the server.',
    'log.conn_lost': 'Connection lost: {reason}',
    'log.reconnect_attempt': 'Reconnect attempt #{n}/{max} in {delay}s...',
    'log.reconnect_off': 'Auto-reconnect is disabled.',
    'log.reconnect_exhausted': 'Reconnect attempts exhausted.',
    'log.disconnected_manual': 'Manual disconnect — no reconnect.',
    'log.disconnected': 'Bot disconnected manually.',
    'log.already_connected': 'Bot is already connected or connecting.',
    'log.create_error': 'Bot creation error: {error}',
    'log.generic_error': 'Error: {error}',
    'log.kicked': 'Kicked: {reason}',
    'log.reconnect_params': 'Reconnect: auto={auto}, max={max}, base={base}s',
    'log.pathfinder_ok': 'Pathfinder initialized.',
    'log.pathfinder_error': 'Failed to initialize pathfinder: {error}',

    'log.damage_taken': 'Damage taken: -{amount} HP ({hp} left).',
    'log.track_cleared': 'Path track cleared.',

    'log.route_starting': 'Starting route «{name}» ({n} points).',
    'log.route_moving': 'Moving to point {label} ({x}, {y}, {z}).',
    'log.route_reach_fail': 'Failed to reach {label}: {error}',
    'log.route_timeout': 'Navigation timeout to {label} — skipping.',
    'log.route_return_home': 'Returning home ({x}, {y}, {z}).',
    'log.route_home_fail': 'Failed to return home: {error}',
    'log.route_looping': 'Route completed, restarting (loop).',
    'log.route_loop_limit': 'Route loop limit reached — stopped.',
    'log.route_completed': 'Route «{name}» completed.',
    'log.route_stopped': 'Route stopped by user.',
    'log.route_paused': 'Route paused.',
    'log.route_resumed': 'Route resumed.',
    'log.route_stopping': 'Stopping route...',
    'log.route_empty': 'Route is empty — nothing to execute.',
    'log.route_running': 'Route is already running.',
    'log.route_error': 'Route error: {error}',
    'log.loop_protection': 'Loop protection: route repeated {n} times, stopping.',

    'log.chat_auto': 'Auto-message: «{msg}»',
    'log.chat_sent': 'Sent: «{msg}»',
    'log.chat_auto_error': 'Auto-send error: {error}',
    'log.chat_not_connected': 'Cannot send message: bot is not connected.',
    'log.chat_scheduler': 'ChatScheduler: enabled={enabled}, interval {min}-{max}s, messages: {n}, random={random}',
    'log.chat_scheduler_empty': 'ChatScheduler: message list is empty, auto-send disabled.',
    'log.chat_scheduler_stopped': 'Auto-messages stopped.',

    'log.inv_eaten': 'Ate: «{name}» ×{n} (slot {slot}, {left} left).',
    'log.inv_eat_fail': 'Item «{name}» was not eaten (food may be full).',
    'log.inv_not_food': '«{name}» is not food',
    'log.inv_slot_empty': 'Slot {slot} is empty',
    'log.inv_equip_fail': 'Failed to equip item: {error}',
    'log.inv_hungry': 'Food is full — no need to eat',
    'log.inv_dropped': 'Dropped: «{name}» ×{n} (slot {slot}).',
    'log.inv_drop_fail': 'Failed to drop: {error}',
    'log.inv_drop_too_many': 'The slot contains only {n} items',
    'log.inv_drop_min': 'Amount must be ≥ 1',
    'log.inv_cant_eat': 'Failed to eat: {error}',
    'log.inv_cant_drop': 'Failed to drop: {error}',

    'log.auto_eat_config': 'AutoEater: enabled={enabled}, threshold={threshold}',
    'log.auto_eat_no_food': 'Auto-eat: no food in inventory.',
    'log.auto_eat_error': 'Auto-eat: error — {error}',

    'log.combat_config': 'CombatController: interval={interval}ms, radius={radius}, ignorePlayers={ignore}',
    'log.combat_start': 'Auto-combat started.',
    'log.combat_stop': 'Auto-combat stopped.',
    'log.combat_not_connected': 'Cannot start auto-combat: bot is not connected.',

    'log.dig_start': 'Digging: looking at ({x}, {y}, {z})',
    'log.dig_no_block': 'Digging: no block on the look line within {r} blocks.',
    'log.dig_unbreakable': 'Digging: block «{name}» is unbreakable.',
    'log.dig_block_broken': 'Block «{name}» broken ({x}, {y}, {z}).',
    'log.dig_dig_fail': 'Failed to break block: {error}',
    'log.dig_error': 'Digging: error — {error}',
    'log.dig_stopped': 'Digging stopped.',
    'log.dig_not_connected': 'Cannot start digging: bot is not connected.',

    'log.look_done': 'Looked at ({x}, {y}, {z}).',
    'log.look_fail': 'Failed to look: {error}',

    'log.safety_config': 'SafetyMonitor: min_health={min_h}, min_food={min_f}, action={action}',
    'log.safety_config_updated': 'SafetyMonitor updated: min_health={min_h}, min_food={min_f}, action={action}',
    'log.safety_warning': '⚠️ Warning: {reason}. Action: {action}',
    'log.safety_ok': '✅ State is normal: HP={hp}, food={food}.',
    'log.safety_reason_hp': 'critical HP: {hp}/20',
    'log.safety_reason_food': 'critical food: {food}/20',
    'log.safety_reason_both': 'critical HP ({hp}) and food ({food})',

    'log.stats_reset': 'Statistics reset.',
    'log.stats_loaded': 'Statistics: base values loaded.',

    'log.log_cleared': 'Path track cleared.',
    'log.auto_eat_on': 'on',
    'log.auto_eat_off': 'off',
  },
};

function setLanguage(lang) {
  if (lang === 'ru' || lang === 'en') _current = lang;
}

function getLanguage() {
  return _current;
}

function t(key, params) {
  const table = STRINGS[_current] || STRINGS.ru;
  let text = table[key];
  if (text === undefined) text = STRINGS.ru[key];
  if (text === undefined) return key;

  if (params && typeof params === 'object') {
    for (const k of Object.keys(params)) {
      text = text.replace(new RegExp(`\\{${k}\\}`, 'g'), params[k]);
    }
  }
  return text;
}

module.exports = { t, setLanguage, getLanguage };