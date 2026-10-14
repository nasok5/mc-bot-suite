const WebSocket = require('ws');
const BotController = require('./BotController');
const { CMD, EVT } = require('./protocol');
const { setLanguage } = require('./i18n');

const WS_PORT = 34567;
const wss = new WebSocket.Server({ port: WS_PORT });
let controller = null;

function broadcast(type, payload) {
  const msg = JSON.stringify({ type, payload });
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) client.send(msg);
  });
}

wss.on('connection', (ws) => {
  console.log('[WS] Python-клиент подключился');
  if (!controller) {
    controller = new BotController((type, payload) => broadcast(type, payload));
  }

  ws.on('message', (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw);
    } catch (e) {
      broadcast(EVT.ERROR, { message: 'Invalid JSON from Python' });
      return;
    }
    const { type, payload } = msg;
    console.log('[CMD]', type, payload || '');

    switch (type) {
      case CMD.CONNECT: controller.connect(payload); break;
      case CMD.DISCONNECT: controller.disconnect(); break;
      case CMD.GOTO:
        controller.goto(payload.x, payload.y, payload.z).catch((err) => {
          broadcast(EVT.ERROR, { message: `Navigation failed: ${err.message}` });
        });
        break;
      case CMD.ROUTE: controller.startRoute(payload); break;
      case CMD.CHAT: controller.chat(payload.message); break;
      case CMD.CHAT_CONFIG: controller.configureChat(payload); break;
      case CMD.SAFETY_CONFIG: controller.configureSafety(payload); break;
      case CMD.AUTO_EAT_CONFIG: controller.configureAutoEat(payload); break;
      case CMD.COMBAT_CONFIG: controller.configureCombat(payload); break;
      case CMD.COMBAT_START: controller.combatStart(); break;
      case CMD.COMBAT_STOP: controller.combatStop(); break;
      case CMD.LOOK_AT:
        controller.lookAt(payload.x, payload.y, payload.z);
        break;
      case CMD.DIG_START:
        controller.digStart(payload.x, payload.y, payload.z);
        break;
      case CMD.DIG_STOP:
        controller.digStop();
        break;
      case CMD.SET_LANGUAGE:
        setLanguage(payload.lang || 'ru');
        console.log('[CMD] language set to', payload.lang);
        break;
      case CMD.STAT_RESET: controller.resetStats(); break;
      case CMD.CLEAR_TRACK: controller.clearTrack(); break;
      case CMD.EAT_ITEM: controller.eatItem(payload.slot); break;
      case CMD.DROP_ITEM: controller.dropItem(payload.slot, payload.count); break;
      case CMD.REFRESH_INVENTORY:
        if (controller.inventory) controller.inventory.forcePush();
        break;
      case CMD.STOP: controller.stop(); break;
      case CMD.PAUSE: controller.pause(); break;
      case CMD.RESUME: controller.resume(); break;
      default:
        broadcast(EVT.ERROR, { message: `Unknown command: ${type}` });
    }
  });

  ws.on('close', () => console.log('[WS] Python-клиент отключился'));
});

console.log(`[bot-core] WebSocket сервер запущен на ws://127.0.0.1:${WS_PORT}`);