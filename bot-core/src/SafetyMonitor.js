const { EVT, LOG_LEVEL } = require('./protocol');
const { t } = require('./i18n');

class SafetyMonitor {
  constructor({ log, send, onPause, onDisconnect }) {
    this.log = log;
    this.send = send;
    this.onPause = onPause;
    this.onDisconnect = onDisconnect;

    this.minHealth = 6;
    this.minFood = 6;
    this.action = 'pause';

    this.warningActive = false;
  }

  configure({ min_health, min_food, critical_action } = {}) {
    const newMinHealth = Number.isFinite(min_health)
      ? Math.max(0, Number(min_health))
      : this.minHealth;
    const newMinFood = Number.isFinite(min_food)
      ? Math.max(0, Number(min_food))
      : this.minFood;
    const newAction = typeof critical_action === 'string'
      ? critical_action
      : this.action;

    const changed =
      newMinHealth !== this.minHealth ||
      newMinFood !== this.minFood ||
      newAction !== this.action;

    this.minHealth = newMinHealth;
    this.minFood = newMinFood;
    this.action = newAction;

    if (changed) {
      this.warningActive = false;
      this.log(LOG_LEVEL.INFO, 'log.safety_config_updated', {
        min_h: this.minHealth,
        min_f: this.minFood,
        action: this.action
      });
    } else {
      this.log(LOG_LEVEL.INFO, 'log.safety_config', {
        min_h: this.minHealth,
        min_f: this.minFood,
        action: this.action
      });
    }
  }

  reset() {
    this.warningActive = false;
  }

  check(health, food) {
    const hpHit = health <= this.minHealth;
    const foodHit = food <= this.minFood;
    const problem = hpHit || foodHit;

    if (problem && !this.warningActive) {
      this.warningActive = true;

      const reason = hpHit && foodHit
        ? t('log.safety_reason_both', { hp: health, food })
        : hpHit
          ? t('log.safety_reason_hp', { hp: health })
          : t('log.safety_reason_food', { food });

      this.log(LOG_LEVEL.WARNING, 'log.safety_warning', {
        reason,
        action: this.action
      });

      this.send(EVT.SAFETY_WARNING, {
        health,
        food,
        reason,
        action: this.action,
        min_health: this.minHealth,
        min_food: this.minFood
      });

      if (this.action === 'pause') {
        try { this.onPause(); } catch (e) { /* ignore */ }
      } else if (this.action === 'disconnect') {
        try { this.onDisconnect(); } catch (e) { /* ignore */ }
      }
    } else if (!problem && this.warningActive) {
      if (health > this.minHealth + 1 && food > this.minFood + 1) {
        this.warningActive = false;
        this.log(LOG_LEVEL.INFO, 'log.safety_ok', { hp: health, food });
        this.send(EVT.SAFETY_OK, { health, food });
      }
    }
  }

  stop() {
    this.warningActive = false;
  }
}

module.exports = SafetyMonitor;