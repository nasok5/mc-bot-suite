const mineflayer = require('mineflayer');
const pathfinder = require('mineflayer-pathfinder').pathfinder;
const { GoalBlock } = require('mineflayer-pathfinder').goals;
const { Movements } = require('mineflayer-pathfinder');
const mcDataLoader = require('minecraft-data');
const Vec3 = require('vec3');
const RouteRunner = require('./RouteRunner');
const ChatScheduler = require('./ChatScheduler');
const StatsTracker = require('./StatsTracker');
const SafetyMonitor = require('./SafetyMonitor');
const InventoryManager = require('./InventoryManager');
const AutoEater = require('./AutoEater');
const CombatController = require('./CombatController');
const { EVT, LOG_LEVEL } = require('./protocol');
const { t } = require('./i18n');

const TRACK_MAX = 300;
const TRACK_MIN_DIST = 2.0;
const TELEPORT_THRESHOLD = 50;
const DIG_REACH = 4;

class BotController {
  constructor(sendEvent) {
    this.sendEvent = sendEvent;
    this.bot = null;
    this.state = 'disconnected';
    this.reconnectAttempts = 0;
    this.reconnectTimer = null;
    this.lastConfig = null;
    this.currentTask = { key: 'task.idle' };
    this.stateInterval = null;
    this.lastHealth = 20;

    this._manualDisconnect = false;
    this._abortNavigation = false;
    this._showTrack = true;

    this._digging = false;
    this._digTimer = null;

    this.track = [];

    this.reconnectOptions = {
      auto: true,
      max_attempts: 5,
      base_delay_sec: 5
    };

    this.stats = new StatsTracker({
      send: (type, payload) => this.sendEvent(type, payload),
      getBot: () => this.bot
    });

    this.inventory = new InventoryManager({
      getBot: () => this.bot,
      log: (lvl, msg, params) => this.log(lvl, msg, params),
      send: (type, payload) => this.sendEvent(type, payload)
    });

    this.autoEater = new AutoEater({
      getBot: () => this.bot,
      log: (lvl, msg, params) => this.log(lvl, msg, params),
      getInventoryManager: () => this.inventory
    });

    this.combat = new CombatController({
      getBot: () => this.bot,
      log: (lvl, msg, params) => this.log(lvl, msg, params),
      send: (type, payload) => this.sendEvent(type, payload)
    });

    this.safety = new SafetyMonitor({
      log: (lvl, msg, params) => this.log(lvl, msg, params),
      send: (type, payload) => this.sendEvent(type, payload),
      onPause: () => {
        this.routeRunner.pause();
        this.chatScheduler.stop();
        this.currentTask = { key: 'task.safety_pause' };
        this.pushState();
      },
      onDisconnect: () => {
        this.currentTask = { key: 'task.safety_disconnect' };
        this.pushState();
        setTimeout(() => this.disconnect(), 500);
      }
    });

    this.routeRunner = new RouteRunner({
      getBot: () => this.bot,
      log: (lvl, msg, params) => this.log(lvl, msg, params),
      send: (type, payload) => {
        if (type === EVT.ROUTE_PROGRESS && payload && payload.point) {
          this.currentTask = payload.point.name
            ? {
                key: 'task.moving_to',
                params: {
                  name: payload.point.name,
                  i: payload.index + 1,
                  n: payload.total
                }
              }
            : {
                key: 'task.moving_to_unnamed',
                params: {
                  i: payload.index + 1,
                  n: payload.total
                }
              };
          this.pushState();
        }
        if (type === EVT.ROUTE_COMPLETED) {
          this.stats.onRouteCompleted();
        }
        this.sendEvent(type, payload);
      },
      goto: (x, y, z) => this.goto(x, y, z)
    });

    this.chatScheduler = new ChatScheduler({
      log: (lvl, msg, params) => this.log(lvl, msg, params),
      send: (type, payload) => {
        if (type === EVT.CHAT_AUTO_SENT && payload) {
          this._sendChat(payload.message, true);
        }
      },
      canSend: () => this.bot !== null && this.state === 'connected'
    });
  }

  /**
   * Логирование. Если message начинается с "log.", то переводим через t().
   * Иначе — оставляем как есть (для строк от mineflayer).
   * @param {string} level
   * @param {string} message
   * @param {object} [params]
   */
  log(level, message, params) {
    let text;
    if (typeof message === 'string' && message.startsWith('log.')) {
      text = t(message, params);
    } else {
      text = message;
    }
    this.sendEvent(EVT.LOG, { level, message: text, timestamp: Date.now() });
  }

  connect(config) {
    if (this.bot) {
      this.log(LOG_LEVEL.WARNING, 'log.already_connected');
      return;
    }

    this._manualDisconnect = false;
    this._abortNavigation = false;
    this.reconnectAttempts = 0;
    this.lastConfig = config;
    this.safety.reset();
    this.track = [];

    if (config.reconnect && typeof config.reconnect === 'object') {
      this.reconnectOptions = {
        auto: config.reconnect.auto !== false,
        max_attempts: Math.max(0, parseInt(config.reconnect.max_attempts, 10) || 0),
        base_delay_sec: Math.max(1, parseInt(config.reconnect.base_delay_sec, 10) || 5)
      };
      this.log(LOG_LEVEL.INFO, 'log.reconnect_params', {
        auto: this.reconnectOptions.auto,
        max: this.reconnectOptions.max_attempts,
        base: this.reconnectOptions.base_delay_sec
      });
    }

    if (config.safety && typeof config.safety === 'object') {
      this.safety.configure(config.safety);
    }

    if (config.auto_eat && typeof config.auto_eat === 'object') {
      this.autoEater.configure(config.auto_eat);
    }

    this._showTrack = config.show_track !== false;

    if (config.stats_base && typeof config.stats_base === 'object') {
      this.stats.setBase(config.stats_base);
      this.log(LOG_LEVEL.INFO, 'log.stats_loaded');
    }

    this.state = 'connecting';
    this.log(LOG_LEVEL.INFO, 'log.connecting', {
      host: config.host,
      port: config.port,
      version: config.version
    });

    try {
      this.bot = mineflayer.createBot({
        host: config.host,
        port: parseInt(config.port, 10),
        username: config.username,
        version: config.version,
        auth: config.auth === 'microsoft' ? 'microsoft' : 'offline',
        hideErrors: false
      });
    } catch (err) {
      this.log(LOG_LEVEL.ERROR, 'log.create_error', { error: err.message });
      this.state = 'disconnected';
      this.bot = null;
      this.pushState();
      this.sendEvent(EVT.DISCONNECTED, { reason: err.message });
      return;
    }

    this.lastHealth = 20;
    this.setupListeners();
    this.pushState();
  }

  setupListeners() {
    const bot = this.bot;

    // Workaround для 1.21.2+ (может помочь на некоторых серверах)
    bot.on('physicTick', () => {
      try {
        if (bot._client && typeof bot._client.write === 'function') {
          const v = bot.version || '';
          if (v.startsWith('1.21.2') || v.startsWith('1.21.3') || v.startsWith('1.21.4')) {
            bot._client.write('tick_end', {});
          }
        }
      } catch (e) { /* ignore */ }
    });

    bot.once('spawn', () => {
      this.state = 'connected';
      this.reconnectAttempts = 0;
      this.lastHealth = bot.health || 20;
      this.log(LOG_LEVEL.INFO, 'log.bot_joined', { user: bot.username });
      this.stats.onConnected();

      try {
        bot.loadPlugin(pathfinder);
        const mcData = mcDataLoader(bot.version);
        const movements = new Movements(bot, mcData);
        movements.canDig = true;
        movements.allow1by1towers = false;
        movements.allowParkour = true;
        movements.allowSprinting = true;
        bot.pathfinder.setMovements(movements);
        this.log(LOG_LEVEL.INFO, 'log.pathfinder_ok');
      } catch (err) {
        this.log(LOG_LEVEL.ERROR, 'log.pathfinder_error', { error: err.message });
      }

      this.inventory.start();
      this.autoEater.reset();
      if (this.autoEater.enabled) this.autoEater.start();

      this.sendEvent(EVT.CONNECTED);
      this.pushState();
    });

    bot.on('end', (reason) => {
      this.state = 'disconnected';
      this.log(LOG_LEVEL.WARNING, 'log.conn_lost', {
        reason: reason || 'unknown'
      });
      this.stats.onDisconnected();
      this.inventory.stop();
      this.autoEater.stop();
      this.combat.stop();
      this._stopDig();
      this.sendEvent(EVT.DISCONNECTED, { reason });
      this.bot = null;
      this.track = [];
      this.pushState();

      if (this._manualDisconnect) {
        this.log(LOG_LEVEL.INFO, 'log.disconnected_manual');
        return;
      }

      if (
        this.lastConfig &&
        this.reconnectOptions.auto &&
        this.reconnectAttempts < this.reconnectOptions.max_attempts
      ) {
        this.scheduleReconnect();
      } else if (!this.reconnectOptions.auto) {
        this.log(LOG_LEVEL.INFO, 'log.reconnect_off');
      } else if (this.reconnectAttempts >= this.reconnectOptions.max_attempts) {
        this.log(LOG_LEVEL.WARNING, 'log.reconnect_exhausted');
      }
    });

    bot.on('error', (err) => {
      this.log(LOG_LEVEL.ERROR, 'log.generic_error', { error: err.message });
      this.sendEvent(EVT.ERROR, { message: err.message });
    });

    bot.on('kicked', (reason) => {
      this.log(LOG_LEVEL.WARNING, 'log.kicked', {
        reason: JSON.stringify(reason)
      });
    });

    bot.on('health', () => {
      const hp = bot.health || 0;
      if (this.lastHealth > hp) {
        const damage = this.lastHealth - hp;
        this.stats.onDamage(damage);
        this.sendEvent(EVT.DAMAGE, { amount: damage, health: hp });
        this.log(LOG_LEVEL.WARNING, 'log.damage_taken', {
          amount: damage,
          hp: hp
        });
      }
      this.lastHealth = hp;
      this.safety.check(hp, bot.food || 0);
      this.pushState();
    });

    bot.on('move', () => this.pushState());

    bot.on('windowUpdate', () => {
      this.inventory.forcePush();
    });

    bot.on('chat', (username, message) => {
      if (username === bot.username) return;
      this.sendEvent(EVT.LOG, {
        level: LOG_LEVEL.CHAT,
        message: `<${username}> ${message}`,
        timestamp: Date.now()
      });
    });

    if (this.stateInterval) clearInterval(this.stateInterval);
    this.stateInterval = setInterval(() => {
      this.pushState();
      if (this.bot && this.state === 'connected') {
        this.safety.check(this.bot.health || 0, this.bot.food || 0);
      }
    }, 1000);
  }

  scheduleReconnect() {
    this.reconnectAttempts++;
    this.stats.onReconnect();
    this.state = 'reconnecting';
    const delay = this.reconnectOptions.base_delay_sec * this.reconnectAttempts;
    this.log(LOG_LEVEL.INFO, 'log.reconnect_attempt', {
      n: this.reconnectAttempts,
      max: this.reconnectOptions.max_attempts,
      delay: delay
    });
    this.pushState();
    this.reconnectTimer = setTimeout(() => {
      if (this.lastConfig) this.connect(this.lastConfig);
    }, delay * 1000);
  }

  _pushTrackPoint(x, z) {
    if (!this._showTrack) return;
    if (this.track.length === 0) {
      this.track.push({ x, z });
      return;
    }

    const last = this.track[this.track.length - 1];
    const dx = x - last.x;
    const dz = z - last.z;
    const dist = Math.sqrt(dx * dx + dz * dz);

    if (dist > TELEPORT_THRESHOLD) {
      this.track = [{ x, z }];
      return;
    }
    if (dist < TRACK_MIN_DIST) return;

    if (this.track.length >= 2) {
      const prev = this.track[this.track.length - 2];
      const dxp = x - prev.x;
      const dzp = z - prev.z;
      const distToPrev = Math.sqrt(dxp * dxp + dzp * dzp);
      if (distToPrev < TRACK_MIN_DIST) {
        this.track.pop();
        return;
      }
    }

    const LOOKBACK = 30;
    const start = Math.max(0, this.track.length - LOOKBACK);
    for (let i = start; i < this.track.length - 1; i++) {
      const p = this.track[i];
      const ddx = x - p.x;
      const ddz = z - p.z;
      if (Math.sqrt(ddx * ddx + ddz * ddz) < TRACK_MIN_DIST) return;
    }

    this.track.push({ x, z });
    if (this.track.length > TRACK_MAX) this.track.shift();
  }

  pushState() {
    if (this.bot && this.bot.entity) {
      const pos = this.bot.entity.position;
      const px = Math.round(pos.x);
      const py = Math.round(pos.y);
      const pz = Math.round(pos.z);

      this._pushTrackPoint(px, pz);

      const payload = {
        status: this.state,
        username: this.bot.username || '—',
        health: this.bot.health || 0,
        food: this.bot.food || 0,
        position: { x: px, y: py, z: pz },
        task: this.currentTask,
        track: this.track
      };
      this.stats.onState(payload);
      this.sendEvent(EVT.STATE, payload);
      return;
    }

    this.sendEvent(EVT.STATE, {
      status: this.state,
      username: '—',
      health: 0,
      food: 0,
      position: { x: 0, y: 0, z: 0 },
      task: this.currentTask,
      track: []
    });
  }

  async goto(x, y, z) {
    if (!this.bot || !this.bot.pathfinder) {
      throw new Error('Bot is not connected or pathfinder is not loaded');
    }
    this.currentTask = { key: 'task.moving_to_xy', params: { x, y, z } };
    this.pushState();
    const goal = new GoalBlock(Math.floor(x), Math.floor(y), Math.floor(z));

    await Promise.race([
      this.bot.pathfinder.goto(goal),
      new Promise((_, reject) => {
        const check = setInterval(() => {
          if (this._abortNavigation) {
            clearInterval(check);
            this._abortNavigation = false;
            reject(Object.assign(new Error('Aborted'), { name: 'PathStopped' }));
          }
        }, 100);
      }),
      new Promise((_, reject) =>
        setTimeout(() => reject(Object.assign(
          new Error('Navigation timeout (60s)'),
          { name: 'NavigationTimeout' }
        )), 60000)
      )
    ]);
  }

  // ===== ПОВОРОТ =====

  async lookAt(x, y, z) {
    if (!this.bot || !this.bot.entity) {
      throw new Error('Bot is not connected');
    }
    try {
      const target = new Vec3(Number(x), Number(y), Number(z));
      await this.bot.lookAt(target, true);
      this.log(LOG_LEVEL.INFO, 'log.look_done', { x, y, z });
    } catch (err) {
      this.log(LOG_LEVEL.WARNING, 'log.look_fail', { error: err.message });
      this.sendEvent(EVT.ERROR, { message: err.message });
    }
  }

  // ===== КОПАНИЕ =====

  digStart(x, y, z) {
    if (!this.bot || !this.bot.entity) {
      this.log(LOG_LEVEL.WARNING, 'log.dig_not_connected');
      return;
    }

    this.digStop();

    const targetX = Number(x);
    const targetY = Number(y);
    const targetZ = Number(z);

    this._digging = true;
    this.sendEvent(EVT.DIG_STATUS, { active: true });
    this.log(LOG_LEVEL.INFO, 'log.dig_start', { x: targetX, y: targetY, z: targetZ });

    this._digTick(targetX, targetY, targetZ);
  }

  async _digTick(tx, ty, tz) {
    if (!this._digging) return;
    const bot = this.bot;
    if (!bot || !bot.entity) {
      this._stopDig();
      return;
    }

    try {
      await bot.lookAt(new Vec3(tx, ty, tz), true);

      const block = this._raycastBlock(DIG_REACH);
      if (!block) {
        this.log(LOG_LEVEL.WARNING, 'log.dig_no_block', { r: DIG_REACH });
      } else {
        const name = block.name || '';
        if (name === 'bedrock' || name === 'barrier' || name === 'end_portal_frame') {
          this.log(LOG_LEVEL.WARNING, 'log.dig_unbreakable', { name });
        } else {
          try {
            await bot.dig(block, true);
            this.log(LOG_LEVEL.INFO, 'log.dig_block_broken', {
              name,
              x: block.position.x,
              y: block.position.y,
              z: block.position.z
            });
          } catch (err) {
            this.log(LOG_LEVEL.WARNING, 'log.dig_dig_fail', { error: err.message });
          }
        }
      }
    } catch (err) {
      this.log(LOG_LEVEL.WARNING, 'log.dig_error', { error: err.message });
    }

    if (!this._digging) return;

    this._digTimer = setTimeout(() => this._digTick(tx, ty, tz), 250);
  }

  _raycastBlock(maxDist) {
    const bot = this.bot;
    if (!bot) return null;
    try {
      return bot.blockAtCursor(maxDist);
    } catch (e) {
      return null;
    }
  }

  digStop() {
    this._stopDig();
  }

  _stopDig() {
    const wasActive = this._digging;
    this._digging = false;
    if (this._digTimer) {
      clearTimeout(this._digTimer);
      this._digTimer = null;
    }
    try {
      if (this.bot && this.bot.stopDigging) this.bot.stopDigging();
    } catch (e) { /* ignore */ }
    if (wasActive) {
      this.log(LOG_LEVEL.INFO, 'log.dig_stopped');
      this.sendEvent(EVT.DIG_STATUS, { active: false });
    }
  }

  // ===== СИСТЕМНОЕ =====

  disconnect() {
    this._manualDisconnect = true;
    if (this.reconnectTimer) { clearTimeout(this.reconnectTimer); this.reconnectTimer = null; }
    if (this.stateInterval) { clearInterval(this.stateInterval); this.stateInterval = null; }
    this.lastConfig = null;
    this.reconnectAttempts = 0;
    this.track = [];

    this.routeRunner.stop();
    this.chatScheduler.stop();
    this.safety.stop();
    this.inventory.stop();
    this.autoEater.stop();
    this.combat.stop();
    this._stopDig();
    this.stats.onDisconnected();

    if (this.bot) {
      try { this.bot.quit('Manual disconnect'); } catch (e) { /* ignore */ }
      this.bot = null;
    }

    this.state = 'disconnected';
    this.currentTask = { key: 'task.idle' };
    this.log(LOG_LEVEL.INFO, 'log.disconnected');
    this.pushState();
    this.sendEvent(EVT.DISCONNECTED, { reason: 'manual' });
  }

  _sendChat(message, isAuto) {
    if (this.bot && this.state === 'connected') {
      this.bot.chat(message);
      this.stats.onChatSent();
      this.sendEvent(EVT.CHAT_SENT, { message, auto: !!isAuto });
    } else {
      this.log(LOG_LEVEL.WARNING, 'log.chat_not_connected');
    }
  }

  chat(message) {
    this._sendChat(message, false);
  }

  configureChat(config) {
    this.chatScheduler.configure(config || {});
  }

  configureSafety(config) {
    this.safety.configure(config || {});
  }

  configureAutoEat(config) {
    this.autoEater.configure(config || {});
  }

  configureCombat(config) {
    this.combat.configure(config || {});
  }

  combatStart() {
    if (!this.bot || this.state !== 'connected') {
      this.log(LOG_LEVEL.WARNING, 'log.combat_not_connected');
      return;
    }
    this.combat.start();
  }

  combatStop() {
    this.combat.stop();
  }

  resetStats() {
    this.stats.reset();
    this.log(LOG_LEVEL.INFO, 'log.stats_reset');
  }

  clearTrack() {
    this.track = [];
    this.log(LOG_LEVEL.INFO, 'log.track_cleared');
    this.pushState();
  }

  async eatItem(slotNumber) {
    try {
      await this.inventory.eat(slotNumber);
    } catch (err) {
      this.log(LOG_LEVEL.WARNING, 'log.inv_cant_eat', { error: err.message });
      this.sendEvent(EVT.ERROR, { message: err.message });
    }
  }

  async dropItem(slotNumber, count) {
    try {
      await this.inventory.drop(slotNumber, count);
    } catch (err) {
      this.log(LOG_LEVEL.WARNING, 'log.inv_cant_drop', { error: err.message });
      this.sendEvent(EVT.ERROR, { message: err.message });
    }
  }

  stop() {
    this._abortNavigation = true;
    this._stopDig();
    try {
      if (this.bot && this.bot.pathfinder) {
        this.bot.pathfinder.setGoal(null);
        this.bot.pathfinder.stop();
      }
    } catch (e) { /* ignore */ }
    this.routeRunner.stop();
    this.currentTask = { key: 'task.idle' };
    this.pushState();
  }

  pause() {
    this._abortNavigation = true;
    this._stopDig();
    try {
      if (this.bot && this.bot.pathfinder) {
        this.bot.pathfinder.setGoal(null);
        this.bot.pathfinder.stop();
      }
    } catch (e) { /* ignore */ }
    this.routeRunner.pause();
    this.currentTask = { key: 'task.paused' };
    this.pushState();
  }

  resume() {
    this.routeRunner.resume();
    this.currentTask = { key: 'task.running_route_unnamed' };
    this.pushState();
  }

  startRoute(route) {
    this.routeRunner.start(route).catch((err) => {
      this.log(LOG_LEVEL.ERROR, 'log.route_error', { error: err.message });
    });
  }
}

module.exports = BotController;