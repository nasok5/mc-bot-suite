const { EVT } = require('./protocol');

class StatsTracker {
  /**
   * @param {object} deps
   * @param {(type,payload)=>void} deps.send
   * @param {()=>object|null} deps.getBot
   */
  constructor({ send, getBot }) {
    this.send = send;
    this.getBot = getBot;

    // Базовые (накопленные ранее, из statistics.json)
    this.base = {
      total_uptime_sec: 0,
      total_connection_sec: 0,
      reconnect_count: 0,
      distance_traveled: 0,
      messages_sent: 0,
      routes_completed: 0,
      damage_taken: 0
    };

    // Текущая сессия Node-процесса
    this.session = {
      startedAt: Date.now(),
      connectedSince: null
    };

    // Счётчики текущей сессии
    this.reconnectCount = 0;
    this.distance = 0;
    this.messagesSent = 0;
    this.routesCompleted = 0;
    this.damageTaken = 0;

    this.lastPos = null;

    // Тик раз в секунду — снапшот в UI
    this.timer = setInterval(() => this.push(), 1000);
  }

  /** Установить базовые значения из statistics.json (вызывается при connect). */
  setBase(base) {
    if (!base || typeof base !== 'object') return;
    this.base = {
      total_uptime_sec: Number(base.total_uptime_sec) || 0,
      total_connection_sec: Number(base.total_connection_sec) || 0,
      reconnect_count: Number(base.reconnect_count) || 0,
      distance_traveled: Number(base.distance_traveled) || 0,
      messages_sent: Number(base.messages_sent) || 0,
      routes_completed: Number(base.routes_completed) || 0,
      damage_taken: Number(base.damage_taken) || 0
    };
  }

  reset() {
    this.base = {
      total_uptime_sec: 0,
      total_connection_sec: 0,
      reconnect_count: 0,
      distance_traveled: 0,
      messages_sent: 0,
      routes_completed: 0,
      damage_taken: 0
    };
    this.session.startedAt = Date.now();
    this.session.connectedSince = null;
    this.reconnectCount = 0;
    this.distance = 0;
    this.messagesSent = 0;
    this.routesCompleted = 0;
    this.damageTaken = 0;
    this.lastPos = null;
    this.push();
  }

  onConnected() {
    if (this.session.connectedSince === null) {
      this.session.connectedSince = Date.now();
    }
  }

  onDisconnected() {
    if (this.session.connectedSince !== null) {
      const delta = (Date.now() - this.session.connectedSince) / 1000;
      this.base.total_connection_sec += Math.floor(delta);
      this.session.connectedSince = null;
    }
    this.lastPos = null;
  }

  onReconnect() {
    this.reconnectCount++;
  }

  onState(payload) {
    const pos = payload && payload.position;
    if (!pos) return;
    const cur = [pos.x, pos.y, pos.z];
    if (this.lastPos) {
      const dx = cur[0] - this.lastPos[0];
      const dy = cur[1] - this.lastPos[1];
      const dz = cur[2] - this.lastPos[2];
      const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (d > 0 && d < 30) this.distance += d;
    }
    this.lastPos = cur;
  }

  onChatSent() {
    this.messagesSent++;
  }

  onRouteCompleted() {
    this.routesCompleted++;
  }

  onDamage(amount) {
    this.damageTaken += Number(amount) || 0;
  }

  snapshot() {
    const uptimeSession = (Date.now() - this.session.startedAt) / 1000;
    const connSession =
      this.session.connectedSince !== null
        ? (Date.now() - this.session.connectedSince) / 1000
        : 0;

    return {
      total_uptime_sec: Math.floor(this.base.total_uptime_sec + uptimeSession),
      total_connection_sec: Math.floor(
        this.base.total_connection_sec + connSession
      ),
      reconnect_count: this.base.reconnect_count + this.reconnectCount,
      distance_traveled: Number(
        (this.base.distance_traveled + this.distance).toFixed(2)
      ),
      messages_sent: this.base.messages_sent + this.messagesSent,
      routes_completed: this.base.routes_completed + this.routesCompleted,
      damage_taken: Number(
        (this.base.damage_taken + this.damageTaken).toFixed(1)
      )
    };
  }

  push() {
    this.send(EVT.STAT_SNAPSHOT, this.snapshot());
  }

  stop() {
    if (this.timer) clearInterval(this.timer);
  }
}

module.exports = StatsTracker;