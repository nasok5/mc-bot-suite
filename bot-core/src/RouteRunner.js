const { EVT, LOG_LEVEL } = require('./protocol');
const { t } = require('./i18n');

const LOOP_MAX = 50;

class RouteRunner {
  constructor({ getBot, log, send, goto }) {
    this.getBot = getBot;
    this.log = log;
    this.send = send;
    this.goto = goto;

    this.route = null;
    this.index = 0;
    this.state = 'idle';
    this.homePoint = null;

    this._interruptedByPause = false;
    this._interruptedByStop = false;
    this._loopDepth = 0;
  }

  isActive() {
    return this.state === 'running' || this.state === 'paused';
  }

  async start(route) {
    if (this.isActive()) {
      this.log(LOG_LEVEL.WARNING, 'log.route_running');
      return;
    }
    if (!route || !Array.isArray(route.points) || route.points.length === 0) {
      this.log(LOG_LEVEL.WARNING, 'log.route_empty');
      return;
    }

    this._loopDepth = (this._loopDepth || 0) + 1;
    if (this._loopDepth > LOOP_MAX) {
      this.log(LOG_LEVEL.ERROR, 'log.loop_protection', { n: LOOP_MAX });
      this._loopDepth = 0;
      this._finish();
      return;
    }

    this.route = route;
    this.index = 0;
    this.state = 'running';
    this._interruptedByPause = false;
    this._interruptedByStop = false;

    const bot = this.getBot();
    if (bot && bot.entity) {
      const p = bot.entity.position;
      this.homePoint = { x: Math.round(p.x), y: Math.round(p.y), z: Math.round(p.z) };
    }

    this.log(LOG_LEVEL.INFO, 'log.route_starting', {
      name: route.name || 'unnamed',
      n: route.points.length
    });

    this.send(EVT.STATE, {
      task: route.name
        ? { key: 'task.running_route', params: { name: route.name } }
        : { key: 'task.running_route_unnamed' }
    });

    try {
      while (this.state === 'running' || this.state === 'paused') {
        if (this.state === 'paused') {
          await this._sleep(100);
          continue;
        }

        const point = this.route.points[this.index];
        if (!point) break;

        const label = point.name ? `«${point.name}»` : `#${this.index + 1}`;
        this.log(LOG_LEVEL.INFO, 'log.route_moving', {
          label,
          x: point.x,
          y: point.y,
          z: point.z
        });

        this.send(EVT.ROUTE_PROGRESS, {
          index: this.index,
          total: this.route.points.length,
          point
        });

        this._interruptedByPause = false;
        this._interruptedByStop = false;

        try {
          await this.goto(point.x, point.y, point.z);
        } catch (err) {
          if (err && err.name === 'PathStopped') {
            if (this._interruptedByStop) {
              // Ждём финальной обработки
            } else if (this._interruptedByPause) {
              continue;
            }
          } else if (err && err.name === 'NavigationTimeout') {
            this.log(LOG_LEVEL.WARNING, 'log.route_timeout', { label });
          } else {
            this.log(LOG_LEVEL.WARNING, 'log.route_reach_fail', {
              label,
              error: err.message
            });
          }
        }

        if (this._interruptedByPause) continue;
        if (this.state === 'stopping') break;
        this.index++;
      }

      if (this.state === 'stopping') {
        this.log(LOG_LEVEL.INFO, 'log.route_stopped');
        this._finish();
        return;
      }

      if (this.route.return_home && this.homePoint) {
        this.log(LOG_LEVEL.INFO, 'log.route_return_home', {
          x: this.homePoint.x,
          y: this.homePoint.y,
          z: this.homePoint.z
        });
        try {
          await this.goto(this.homePoint.x, this.homePoint.y, this.homePoint.z);
        } catch (err) {
          if (err && err.name === 'PathStopped' && this.state === 'stopping') {
            this._finish();
            return;
          }
          this.log(LOG_LEVEL.WARNING, 'log.route_home_fail', { error: err.message });
        }
      }

      if (this.route.loop) {
        this.log(LOG_LEVEL.INFO, 'log.route_looping');
        this.state = 'idle';
        this.index = 0;
        const savedRoute = this.route;
        this.route = null;
        await this._sleep(500);
        if (this._loopDepth >= LOOP_MAX) {
          this.log(LOG_LEVEL.ERROR, 'log.route_loop_limit');
          this._loopDepth = 0;
          this._finish();
          return;
        }
        return this.start(savedRoute);
      }

      this.log(LOG_LEVEL.INFO, 'log.route_completed', {
        name: this.route.name || 'unnamed'
      });
      this.send(EVT.ROUTE_COMPLETED, {
        route: this.route.name,
        count: this.route.points.length
      });
      this._finish();
    } catch (err) {
      this.log(LOG_LEVEL.ERROR, 'log.route_error', { error: err.message });
      this._finish();
    }
  }

  pause() {
    if (this.state === 'running') {
      this.state = 'paused';
      this._interruptedByPause = true;
      const bot = this.getBot();
      if (bot && bot.pathfinder) {
        try { bot.pathfinder.setGoal(null); bot.pathfinder.stop(); } catch (e) {}
      }
      this.log(LOG_LEVEL.INFO, 'log.route_paused');
      this.send(EVT.STATE, { task: { key: 'task.paused' } });
    }
  }

  resume() {
    if (this.state === 'paused') {
      this.state = 'running';
      this._interruptedByPause = false;
      this.log(LOG_LEVEL.INFO, 'log.route_resumed');
      const name = this.route ? this.route.name : null;
      this.send(EVT.STATE, {
        task: name
          ? { key: 'task.running_route', params: { name } }
          : { key: 'task.running_route_unnamed' }
      });
    }
  }

  stop() {
    if (this.state === 'running' || this.state === 'paused') {
      this.state = 'stopping';
      this._interruptedByStop = true;
      const bot = this.getBot();
      if (bot && bot.pathfinder) {
        try { bot.pathfinder.setGoal(null); bot.pathfinder.stop(); } catch (e) {}
      }
      this.log(LOG_LEVEL.INFO, 'log.route_stopping');
      this.send(EVT.STATE, { task: { key: 'task.idle' } });
    }
  }

  _finish() {
    this.state = 'idle';
    this.route = null;
    this.index = 0;
    this._interruptedByPause = false;
    this._interruptedByStop = false;
    this._loopDepth = 0;
    this.send(EVT.STATE, { task: { key: 'task.idle' } });
  }

  _sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }
}

module.exports = RouteRunner;