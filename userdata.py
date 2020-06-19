# Тут мы создаем базу данных, к которой потом и будем подключать бота
from sqlite3 import connect

conn = connect("bot.db")
c = conn.cursor()

c.execute("""
CREATE TABLE users (chat_id, weight, height)
""")