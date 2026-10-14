const { LOG_LEVEL } = require('./protocol');
const { t } = require('./i18n');

const DEFAULT_THRESHOLD = 17;
const DEFAULT_INTERVAL_MS = 3000;

class AutoEater {
  constructor({ getBot, log, getInventoryManager }) {
    this.getBot = getBot;
    this.log = log;
    this.getInventoryManager = getInventoryManager;

    this.enabled = false;
    this.threshold = DEFAULT_THRESHOLD;
    this.intervalMs = DEFAULT_INTERVAL_MS;

    this._timer = null;
    this._eating = false;
    this._noFoodLogged = false;
  }

  configure({ enabled, threshold } = {}) {
    if (typeof enabled === 'boolean') this.enabled = enabled;
    if (Number.isFinite(threshold)) {
      this.threshold = Math.max(0, Math.min(20, threshold));
    }

    this.log(LOG_LEVEL.INFO, 'log.auto_eat_config', {
      enabled: this.enabled,
      threshold: this.threshold
    });

    if (this.enabled) {
      this.start();
    } else {
      this.stop();
    }
  }

  start() {
    this.stop();
    this._noFoodLogged = false;
    this._timer = setInterval(() => this._tick(), this.intervalMs);
  }

  stop() {
    if (this._timer) {
      clearInterval(this._timer);
      this._timer = null;
    }
    this._eating = false;
  }

  reset() {
    this._noFoodLogged = false;
    this._eating = false;
  }

  async _tick() {
    if (!this.enabled) return;
    if (this._eating) return;

    const bot = this.getBot();
    if (!bot || !bot.entity || !bot.inventory) return;

    const food = bot.food || 0;
    if (food >= this.threshold) return;

    const inv = this.getInventoryManager();
    if (!inv) return;

    const slot = this._findFoodSlot(bot, inv);
    if (slot === null) {
      if (!this._noFoodLogged) {
        this.log(LOG_LEVEL.WARNING, 'log.auto_eat_no_food');
        this._noFoodLogged = true;
      }
      return;
    }

    this._noFoodLogged = false;

    this._eating = true;
    try {
      await inv.eat(slot);
    } catch (err) {
      this.log(LOG_LEVEL.WARNING, 'log.auto_eat_error', { error: err.message });
    } finally {
      this._eating = false;
    }
  }

  _findFoodSlot(bot, inv) {
    const items = bot.inventory.slots;
    const HOTBAR = [36, 37, 38, 39, 40, 41, 42, 43, 44];
    const INV = [];
    for (let i = 9; i <= 35; i++) INV.push(i);

    for (const s of HOTBAR) {
      const item = items[s];
      if (item && inv._isFood(item, bot) > 0) return s;
    }
    for (const s of INV) {
      const item = items[s];
      if (item && inv._isFood(item, bot) > 0) return s;
    }
    return null;
  }
}

module.exports = AutoEater;