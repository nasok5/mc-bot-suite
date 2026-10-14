const { EVT, LOG_LEVEL } = require('./protocol');
const { t } = require('./i18n');

const DEFAULT_INTERVAL_MS = 600;
const DEFAULT_RADIUS = 3.0;

class CombatController {
  constructor({ getBot, log, send }) {
    this.getBot = getBot;
    this.log = log;
    this.send = send;

    this.enabled = false;
    this.intervalMs = DEFAULT_INTERVAL_MS;
    this.radius = DEFAULT_RADIUS;
    this.ignorePlayers = true;

    this._timer = null;
    this._busy = false;
    this._lastTarget = null;
  }

  configure({ interval_ms, radius, ignore_players } = {}) {
    if (Number.isFinite(interval_ms)) {
      this.intervalMs = Math.max(100, Math.min(5000, interval_ms));
    }
    if (Number.isFinite(radius)) {
      this.radius = Math.max(1, Math.min(6, radius));
    }
    if (typeof ignore_players === 'boolean') {
      this.ignorePlayers = ignore_players;
    }
    this.log(LOG_LEVEL.INFO, 'log.combat_config', {
      interval: this.intervalMs,
      radius: this.radius,
      ignore: this.ignorePlayers
    });
    if (this.enabled) {
      this.start();
    }
  }

  start() {
    this.stop();
    this.enabled = true;
    this._timer = setInterval(() => this._tick(), this.intervalMs);
    this.log(LOG_LEVEL.INFO, 'log.combat_start');
    this.send(EVT.COMBAT_STATUS, { enabled: true });
  }

  stop() {
    if (this._timer) {
      clearInterval(this._timer);
      this._timer = null;
    }
    if (this.enabled) {
      this.log(LOG_LEVEL.INFO, 'log.combat_stop');
      this.send(EVT.COMBAT_STATUS, { enabled: false });
    }
    this.enabled = false;
    this._busy = false;
    this._lastTarget = null;
  }

  async _tick() {
    if (!this.enabled || this._busy) return;

    const bot = this.getBot();
    if (!bot || !bot.entity) return;

    const target = this._findTarget(bot);
    if (!target) return;

    this._busy = true;
    try {
      const wasPhysics = bot.physicsEnabled;
      bot.physicsEnabled = false;

      const lookY = target.height ? target.height * 0.85 : 0.9;
      await bot.lookAt(target.position.offset(0, lookY, 0), true);
      bot.attack(target);

      await new Promise((r) => setTimeout(r, 50));
      bot.physicsEnabled = wasPhysics;

      this._lastTarget = target.id;
    } catch (err) {
      // Игнорируем — цель могла умереть или уйти
    } finally {
      this._busy = false;
    }
  }

  _findTarget(bot) {
    const filter = (entity) => {
      if (!entity) return false;
      if (entity === bot.entity) return false;
      if (!entity.isValid) return false;
      const type = entity.type;
      if (type === 'player' && this.ignorePlayers) return false;
      if (type !== 'mob' && type !== 'player' && type !== 'hostile') return false;
      return true;
    };

    return bot.nearestEntity((entity) => {
      if (!filter(entity)) return false;
      const dist = bot.entity.position.distanceTo(entity.position);
      return dist <= this.radius;
    });
  }
}

module.exports = CombatController;