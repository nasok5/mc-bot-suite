const CMD = {
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  GOTO: 'goto',
  ROUTE: 'route',
  CHAT: 'chat',
  CHAT_CONFIG: 'chat_config',
  SAFETY_CONFIG: 'safety_config',
  AUTO_EAT_CONFIG: 'auto_eat_config',
  STAT_RESET: 'stat_reset',
  CLEAR_TRACK: 'clear_track',
  EAT_ITEM: 'eat_item',
  DROP_ITEM: 'drop_item',
  REFRESH_INVENTORY: 'refresh_inventory',
  COMBAT_START: 'combat_start',
  COMBAT_STOP: 'combat_stop',
  COMBAT_CONFIG: 'combat_config',
  LOOK_AT: 'look_at',
  DIG_START: 'dig_start',
  DIG_STOP: 'dig_stop',
  SET_LANGUAGE: 'set_language',
  STOP: 'stop',
  PAUSE: 'pause',
  RESUME: 'resume',
  RANDOM_WALK: 'random_walk'
};

// EVT и LOG_LEVEL — без изменений

const EVT = {
  STATE: 'state',
  LOG: 'log',
  ERROR: 'error',
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  CHAT_SENT: 'chat_sent',
  CHAT_AUTO_SENT: 'chat_auto_sent',
  ROUTE_PROGRESS: 'route_progress',
  ROUTE_COMPLETED: 'route_completed',
  DAMAGE: 'damage',
  STAT_SNAPSHOT: 'stat_snapshot',
  SAFETY_WARNING: 'safety_warning',
  SAFETY_OK: 'safety_ok',
  INVENTORY: 'inventory',
  COMBAT_STATUS: 'combat_status',
  DIG_STATUS: 'dig_status'
};

const LOG_LEVEL = {
  INFO: 'INFO',
  WARNING: 'WARNING',
  ERROR: 'ERROR',
  CHAT: 'CHAT'
};

module.exports = { CMD, EVT, LOG_LEVEL };