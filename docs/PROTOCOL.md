### set_language
```json
{ "type": "set_language", "payload": { "lang": "en" } }




{ "type": "combat_config", "payload": { "interval_ms": 600, "radius": 3, "ignore_players": true } }
{ "type": "combat_start" }
{ "type": "combat_stop" }
Управление авто-ударом (только 1.20.4-).

look_at:
{ "type": "look_at", "payload": { "x": 100, "y": 64, "z": 200 } }


dig_start / dig_stop:
{ "type": "dig_start", "payload": { "x": 100, "y": 64, "z": 200 } }
{ "type": "dig_stop" }


eat_item / drop_item / refresh_inventory:
{ "type": "eat_item", "payload": { "slot": 36 } }
{ "type": "drop_item", "payload": { "slot": 36, "count": 1 } }
{ "type": "refresh_inventory" }