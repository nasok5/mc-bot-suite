from modules.storage import Storage

s = Storage()

# 1. Первый запуск: файлы создаются с дефолтами
settings = s.load("settings")
print("host:", settings["minecraft"]["host"])
print("messages items:", s.load("messages")["items"])

# 2. Изменим и сохраним
settings["minecraft"]["host"] = "test.example.com"
s.save("settings", settings)

# 3. Перечитаем — должны увидеть изменение
print("после save:", s.load("settings")["minecraft"]["host"])

# 4. Обновим только часть
s.update("statistics", {"messages_sent": 42})
print("messages_sent:", s.load("statistics")["messages_sent"])