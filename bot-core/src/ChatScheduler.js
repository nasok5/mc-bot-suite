const { EVT, LOG_LEVEL } = require('./protocol');
const { t } = require('./i18n');

class ChatScheduler {
  constructor({ log, send, canSend }) {
    this.log = log;
    this.send = send;
    this.canSend = canSend;

    this.messages = [];
    this.enabled = false;
    this.minInterval = 60;
    this.maxInterval = 180;
    this.useRandomInterval = true;

    this.timer = null;
    this.lastIndex = -1;
  }

  configure({ messages, enabled, min_interval_sec, max_interval_sec, use_random_interval }) {
    if (Array.isArray(messages)) {
      this.messages = messages.filter((m) => typeof m === 'string' && m.trim().length > 0);
    }
    if (typeof enabled === 'boolean') this.enabled = enabled;
    if (Number.isFinite(min_interval_sec)) this.minInterval = Math.max(10, min_interval_sec);
    if (Number.isFinite(max_interval_sec)) this.maxInterval = Math.max(this.minInterval, max_interval_sec);
    if (typeof use_random_interval === 'boolean') this.useRandomInterval = use_random_interval;

    this.log(LOG_LEVEL.INFO, 'log.chat_scheduler', {
      enabled: this.enabled,
      min: this.minInterval,
      max: this.maxInterval,
      n: this.messages.length,
      random: this.useRandomInterval
    });

    this._reschedule();
  }

  start() {
    this.enabled = true;
    this._reschedule();
  }

  stop() {
    const wasEnabled = this.enabled;
    this.enabled = false;
    this._clear();
    if (wasEnabled) {
      this.log(LOG_LEVEL.INFO, 'log.chat_scheduler_stopped');
    }
  }

  _clear() {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }

  _reschedule() {
    this._clear();
    if (!this.enabled) return;
    if (this.messages.length === 0) {
      this.log(LOG_LEVEL.WARNING, 'log.chat_scheduler_empty');
      return;
    }
    const delay = this._nextDelay() * 1000;
    this.timer = setTimeout(() => this._tick(), delay);
  }

  _nextDelay() {
    if (!this.useRandomInterval) return this.minInterval;
    const lo = Math.min(this.minInterval, this.maxInterval);
    const hi = Math.max(this.minInterval, this.maxInterval);
    return lo + Math.random() * (hi - lo);
  }

  _pickMessage() {
    if (this.messages.length === 1) return this.messages[0];
    let idx;
    do {
      idx = Math.floor(Math.random() * this.messages.length);
    } while (idx === this.lastIndex && this.messages.length > 1);
    this.lastIndex = idx;
    return this.messages[idx];
  }

  _tick() {
    if (!this.enabled) return;
    if (!this.canSend()) {
      this.timer = setTimeout(() => this._tick(), 5000);
      return;
    }
    const msg = this._pickMessage();
    try {
      this.send(EVT.CHAT_AUTO_SENT, { message: msg });
      this.log(LOG_LEVEL.CHAT, 'log.chat_auto', { msg });
    } catch (err) {
      this.log(LOG_LEVEL.ERROR, 'log.chat_auto_error', { error: err.message });
    }
    this._reschedule();
  }
}

module.exports = ChatScheduler;