const { EVT, LOG_LEVEL } = require('./protocol');
const { t } = require('./i18n');
const mcDataLoader = require('minecraft-data');

const ARMOR_SLOTS = [5, 6, 7, 8];
const INVENTORY_SLOTS = [];
for (let i = 9; i <= 35; i++) INVENTORY_SLOTS.push(i);
const HOTBAR_SLOTS = [];
for (let i = 36; i <= 44; i++) HOTBAR_SLOTS.push(i);

const ARMOR_NAMES = {
  5: 'Шлем',
  6: 'Нагрудник',
  7: 'Штаны',
  8: 'Ботинки',
};

// Жёсткий список еды (не зависит от версии minecraft-data)
const FOOD_NAMES = new Set([
  'apple', 'golden_apple', 'enchanted_golden_apple',
  'carrot', 'golden_carrot',
  'potato', 'baked_potato', 'poisonous_potato',
  'beetroot',
  'melon_slice', 'pumpkin_pie',
  'sweet_berries', 'glow_berries',
  'chorus_fruit',
  'bread', 'cookie', 'cake',
  'beetroot_soup', 'mushroom_stew', 'rabbit_stew', 'suspicious_stew',
  'beef', 'cooked_beef', 'steak',
  'porkchop', 'cooked_porkchop',
  'chicken', 'cooked_chicken',
  'mutton', 'cooked_mutton',
  'rabbit', 'cooked_rabbit',
  'cod', 'cooked_cod',
  'salmon', 'cooked_salmon',
  'tropical_fish', 'pufferfish',
  'dried_kelp',
  'honey_bottle',
  'milk_bucket',
  'rotten_flesh',
  'spider_eye',
]);

class InventoryManager {
  constructor({ getBot, log, send }) {
    this.getBot = getBot;
    this.log = log;
    this.send = send;
    this._interval = null;
    this._lastHash = '';
    this._mcData = null;
  }

  start() {
    this.stop();
    this._interval = setInterval(() => this.push(), 2000);
    setTimeout(() => this.push(), 500);
  }

  stop() {
    if (this._interval) {
      clearInterval(this._interval);
      this._interval = null;
    }
    this._lastHash = '';
    this._mcData = null;
  }

  push() {
    const bot = this.getBot();
    if (!bot || !bot.inventory) return;

    const snapshot = this._collect(bot);
    const hash = JSON.stringify(snapshot);
    if (hash === this._lastHash) return;
    this._lastHash = hash;
    this.send(EVT.INVENTORY, snapshot);
  }

  forcePush() {
    this._lastHash = '';
    this.push();
  }

  _getMcData(bot) {
    if (this._mcData) return this._mcData;
    try {
      this._mcData = mcDataLoader(bot.version);
    } catch (e) {
      this._mcData = null;
    }
    return this._mcData;
  }

  _isFood(item, bot) {
    if (!item || !item.name) return 0;
    if (FOOD_NAMES.has(item.name)) return 1;
    if (typeof item.foodPoints === 'number' && item.foodPoints > 0) {
      return item.foodPoints;
    }
    if (item.food && typeof item.food.foodPoints === 'number' && item.food.foodPoints > 0) {
      return item.food.foodPoints;
    }
    const mcData = this._getMcData(bot);
    if (mcData) {
      const itemData = mcData.itemsByName[item.name];
      if (itemData && typeof itemData.foodPoints === 'number' && itemData.foodPoints > 0) {
        return itemData.foodPoints;
      }
    }
    return 0;
  }

  _collect(bot) {
    const items = bot.inventory.slots;
    const out = [];

    const push = (slotIndex, slotType) => {
      const item = items[slotIndex];
      if (!item) {
        out.push({
          slot: slotIndex, slotType,
          name: null, displayName: null, count: 0, isFood: false,
        });
        return;
      }
      const foodPoints = this._isFood(item, bot);
      out.push({
        slot: slotIndex, slotType,
        name: item.name,
        displayName: item.displayName || item.name,
        count: item.count,
        isFood: foodPoints > 0,
        foodPoints,
      });
    };

    for (const s of ARMOR_SLOTS) push(s, ARMOR_NAMES[s] || `Armor ${s}`);
    for (let i = 0; i < INVENTORY_SLOTS.length; i++) {
      push(INVENTORY_SLOTS[i], `Inv. ${i + 1}`);
    }
    for (let i = 0; i < HOTBAR_SLOTS.length; i++) {
      push(HOTBAR_SLOTS[i], `Hotbar ${i + 1}`);
    }

    return { items: out, timestamp: Date.now() };
  }

  async eat(slotNumber) {
    const bot = this.getBot();
    if (!bot) throw new Error('Bot is not connected');

    const items = bot.inventory.slots;
    const item = items[slotNumber];
    if (!item) throw new Error(t('log.inv_slot_empty', { slot: slotNumber }));

    const foodPoints = this._isFood(item, bot);
    if (foodPoints <= 0) {
      throw new Error(t('log.inv_not_food', { name: item.displayName || item.name }));
    }

    if (bot.food >= 20) {
      throw new Error(t('log.inv_hungry'));
    }

    const countBefore = item.count;

    try {
      await bot.equip(item, 'hand');
    } catch (err) {
      throw new Error(t('log.inv_equip_fail', { error: err.message }));
    }

    const eatenPromise = new Promise((resolve) => {
      let resolved = false;
      const onHeldChange = () => {
        if (resolved) return;
        resolved = true;
        bot.removeListener('heldItemChanged', onHeldChange);
        resolve(true);
      };
      bot.on('heldItemChanged', onHeldChange);
      setTimeout(() => {
        if (resolved) return;
        resolved = true;
        bot.removeListener('heldItemChanged', onHeldChange);
        resolve(false);
      }, 3000);
    });

    bot.activateItem();
    await eatenPromise;
    bot.deactivateItem();

    await new Promise((r) => setTimeout(r, 300));

    const itemAfter = bot.inventory.slots[slotNumber];
    const countAfter = itemAfter ? itemAfter.count : 0;
    const delta = countBefore - countAfter;

    if (delta > 0) {
      this.log(LOG_LEVEL.INFO, 'log.inv_eaten', {
        name: item.displayName || item.name,
        n: delta,
        slot: slotNumber,
        left: countAfter
      });
    } else {
      this.log(LOG_LEVEL.WARNING, 'log.inv_eat_fail', {
        name: item.displayName || item.name
      });
    }

    this.forcePush();
  }

  async drop(slotNumber, count) {
    const bot = this.getBot();
    if (!bot) throw new Error('Bot is not connected');

    const items = bot.inventory.slots;
    const item = items[slotNumber];
    if (!item) throw new Error(t('log.inv_slot_empty', { slot: slotNumber }));

    const available = item.count || 1;
    if (count > available) {
      throw new Error(t('log.inv_drop_too_many', { n: available }));
    }
    if (count < 1) {
      throw new Error(t('log.inv_drop_min'));
    }

    const displayName = item.displayName || item.name;

    try {
      await bot.equip(item, 'hand');
      await new Promise((r) => setTimeout(r, 200));

      if (count >= available) {
        await bot.tossStack(item);
      } else {
        await bot.toss(item.type, null, count);
      }

      this.log(LOG_LEVEL.INFO, 'log.inv_dropped', {
        name: displayName,
        n: count,
        slot: slotNumber
      });
      setTimeout(() => this.forcePush(), 400);
    } catch (err) {
      throw new Error(t('log.inv_drop_fail', { error: err.message }));
    }
  }
}

module.exports = InventoryManager;