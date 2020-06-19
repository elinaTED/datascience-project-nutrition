import telebot
import sqlite3
import requests
import json
import re

from sqlite3 import connect
from telebot import types

bot = telebot.TeleBot('Тут API key, но не хочется, чтобы бот крашнулся')

__connection = None

# Коннектим базу данных
def get_connection():
    global __connection
    if __connection is None:
        __connection = sqlite3.connect("bot.db")
    return __connection


conn = get_connection()
c = conn.cursor()

# Команда 'start'. Приветствуем пользователя.
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Welcome, {0.first_name}!\n<b>{1.first_name}</b> will show you something!"
                     .format(message.from_user, bot.get_me()),
                     parse_mode='html')
    bot.send_message(message.chat.id,
                     "First of all, check the investigation about food consumption in different countries.\nHere is a link to the website:\nhttps://safe-mesa-93489.herokuapp.com"
                     .format(message.from_user, bot.get_me()),
                     parse_mode='html')
    bot.send_message(message.chat.id,
                     "However, the bot is created to help you improve your body. \nThe bot can\n❣️ count your BMI\n❣️ tell you information about meal\n❣️ tell you about importance of vitamins\n❣️ provide you with the sources of vitamins"
                     .format(message.from_user, bot.get_me()),
                     parse_mode='html')
    sti = open('sticker.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id,
                     "<i>Use backslash to see all commands.</i>"
                     .format(message.from_user, bot.get_me()),
                     parse_mode='html')

# Команда 'link'. Скидываем ссылку на сайт с графичками.
@bot.message_handler(commands=['link'])
def get_vitamin(message):
    bot.send_message(message.chat.id,
                     "Oh, you want to get the link. Here it is:\nhttps://safe-mesa-93489.herokuapp.com"
                     .format(message.from_user, bot.get_me()),
                     parse_mode='html')

# Здесь мы добавляем данные о пользователе, используя SQL (используется чуть ниже).
@bot.message_handler(commands=['adddata'])
def add_data(message):
    bot.send_message(message.chat.id,
                     "So, {0.first_name}, send me the current information about yourself.\n"
                     "If you don't finish the procedure, the bot won't save any information about you."
                     .format(message.from_user, bot.get_me()),
                     parse_mode='html')
    bot.send_message(message.chat.id,
                     "Sorry for the question, {0.first_name}. What is your weight?\n"
                     "Please, send me just a number with a decimal point, if needed, and without \'kg\' and etc"
                     .format(message.from_user, bot.get_me()),
                     parse_mode='html')
    bot.register_next_step_handler(message, get_weight)

# Получаем данные о весе, если это не текстовое сообщение (фотка например),
# то просим повторить попытку.
# А далее мы будем с помощью регулярных выражений проверять, является ли
# введенный текст числом с точкой (вроде как нет просто проверки является ли
# текст числом), но энивей дальше мы еще раз воспользуемся регулярными выражениями
# А еще пользуемся SQL
def get_weight(message):
    if message.content_type == 'text':
        if message.text.isnumeric():
            if float(message.text) < 200 and float(message.text) >30:
                weight = float(message.text)
                bot.send_message(message.chat.id,
                                 "What is your height?\nPlease, follow the same rules as with weight"
                                 .format(message.from_user, bot.get_me()),
                                 parse_mode='html')
                conn = connect("bot.db")
                c = conn.cursor()
                user_data = [f"{message.chat.id}", weight, None]
                us_id = [f"{message.chat.id}"]
                # Удаляем старую информацию о пользователе
                # с помощью SQL
                if not (c.execute('''
                                SELECT height FROM users
                                WHERE chat_id = ?
                                LIMIT 1
                                ''', tuple(us_id)).fetchone() is None):
                    c.execute('''
                                         DELETE FROM users
                                         WHERE chat_id = ?
                                         ''', tuple(us_id))
                # Добавляем новую инфу
                c.execute('''
                            INSERT INTO users (chat_id, weight, height) VALUES (?, ?, ?)
                            ''', tuple(user_data))
                conn.commit()
                bot.register_next_step_handler(message, get_height)
            else:
                bot.send_message(message.chat.id,
                                 "Are sure? Please, try again."
                                 .format(message.from_user, bot.get_me()),
                                 parse_mode='html')
                bot.register_next_step_handler(message, get_weight_abnormal)
        # Регулярные выражения (число с точкой с качестве разделителя)
        elif re.match(r"^\d+?\.\d+?$", message.text) is None:
            bot.send_message(message.chat.id,
                             "Check your data. Enter your weight again:"
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')
            bot.register_next_step_handler(message, get_weight)
        else:
            weight = float(message.text)
            # Проверяем вес на адекватность, спрашивая, не ошибся ли пользователь
            # Но затем, если снова введен нестандартный вес, то мы его записываем
            if weight < 200 and weight >30:
                bot.send_message(message.chat.id,
                                 "What is your height?\nPlease, follow the same rules as with weight"
                                 .format(message.from_user, bot.get_me()),
                                 parse_mode='html')
                conn = connect("bot.db")
                c = conn.cursor()
                user_data = [f"{message.chat.id}", weight, 0]
                c.execute('''
                                    INSERT INTO users (chat_id, weight, height) VALUES (?, ?, ?)
                                    ''', tuple(user_data))
                conn.commit()
                bot.register_next_step_handler(message, get_height)
            else:
                bot.send_message(message.chat.id,
                                 "Are sure? Please, try again."
                                 .format(message.from_user, bot.get_me()),
                                 parse_mode='html')
                bot.register_next_step_handler(message, get_weight_abnormal)
    else:
        bot.send_message(message.chat.id,
                         "Sorry, {0.first_name}, but you are supposed to send a text message.\nDon't send me garbage, please.\nTry again."
                         .format(message.from_user, bot.get_me()),
                         parse_mode='html')
        bot.register_next_step_handler(message, get_weight)

# Тут как раз даем вторую попытку, если вес нестандартный
def get_weight_abnormal(message):
    if message.content_type == 'text':
        if message.text.isnumeric():
            weight = float(message.text)
            bot.send_message(message.chat.id,
                             "What is your height?\nPlease, follow the same rules as with weight"
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')
            conn = connect("bot.db")
            c = conn.cursor()
            user_data = [f"{message.chat.id}", weight, None]
            us_id = [f"{message.chat.id}"]
            # Delete information if it exists
            if not (c.execute('''
                            SELECT height FROM users
                            WHERE chat_id = ?
                            LIMIT 1
                            ''', tuple(us_id)).fetchone() is None):
                c.execute('''
                                     DELETE FROM users
                                     WHERE chat_id = ?
                                     ''', tuple(us_id))
            # Add new info
            c.execute('''
                        INSERT INTO users (chat_id, weight, height) VALUES (?, ?, ?)
                        ''', tuple(user_data))
            conn.commit()
            bot.register_next_step_handler(message, get_height)

        elif re.match(r"^\d+?\.\d+?$", message.text) is None:
            bot.send_message(message.chat.id,
                             "Check your data. Enter your weight again:"
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')
            bot.register_next_step_handler(message, get_weight)
        else:
            weight = float(message.text)
            bot.send_message(message.chat.id,
                             "What is your height?\nPlease, follow the same rules as with weight"
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')
            conn = connect("bot.db")
            c = conn.cursor()
            user_data = [f"{message.chat.id}", weight, 0]
            c.execute('''
                                INSERT INTO users (chat_id, weight, height) VALUES (?, ?, ?)
                                ''', tuple(user_data))
            conn.commit()
            bot.register_next_step_handler(message, get_height)
    else:
        bot.send_message(message.chat.id,
                         "Sorry, {0.first_name}, but you are supposed to send a text message.\nDon't send me garbage, please.\nTry again."
                         .format(message.from_user, bot.get_me()),
                         parse_mode='html')
        bot.register_next_step_handler(message, get_weight)

# Аналогично весу, пользуемся SQL и регулярными выражениями
def get_height(message):
    if message.content_type == 'text':
        if message.text.isnumeric():
            if float(message.text) < 210 and float(message.text) > 150:
                height = float(message.text)
                bot.send_message(message.chat.id,
                                 "Thank you! We got all required information."
                                 .format(message.from_user, bot.get_me()),
                                 parse_mode='html')
                us_id = [f"{message.chat.id}"]
                conn = connect("bot.db")
                c = conn.cursor()
                c.execute('''
                                        SELECT weight FROM users
                                        WHERE chat_id = ?
                                        LIMIT 1
                                        ''', tuple(us_id))
                (weight,) = c.fetchone()
                c.execute('''
                             DELETE FROM users
                             WHERE chat_id = ?
                             ''', tuple(us_id))
                user_data = [f"{message.chat.id}", weight, height]
                c.execute('''
                                    INSERT INTO users (chat_id, weight, height) VALUES (?, ?, ?)
                                    ''', tuple(user_data))
                conn.commit()
            else:
                bot.send_message(message.chat.id,
                                 "Are sure? Please, try again."
                                 .format(message.from_user, bot.get_me()),
                                 parse_mode='html')
                bot.register_next_step_handler(message, get_height_abnormal)
        elif re.match(r"^\d+?\.\d+?$", message.text) is None:
            bot.send_message(message.chat.id,
                             "Check your data. Enter your height again:"
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')
            bot.register_next_step_handler(message, get_height)
        else:
            height = float(message.text)
            if height < 210 and height > 150:
                bot.send_message(message.chat.id,
                                 "Thank you! We got all required information."
                                 .format(message.from_user, bot.get_me()),
                                 parse_mode='html')
                us_id = [f"{message.chat.id}"]
                conn = connect("bot.db")
                c = conn.cursor()
                c.execute('''
                                SELECT weight FROM users
                                WHERE chat_id = ?
                                LIMIT 1
                                ''', tuple(us_id))
                (weight,) = c.fetchone()
                user_data = [f"{message.chat.id}", weight, height]
                c.execute('''
                            INSERT INTO users (chat_id, weight, height) VALUES (?, ?, ?)
                            ''', tuple(user_data))
                conn.commit()
            else:
                bot.send_message(message.chat.id,
                                 "Are sure? Please, try again."
                                 .format(message.from_user, bot.get_me()),
                                 parse_mode='html')
                bot.register_next_step_handler(message, get_height_abnormal)
    else:
        bot.send_message(message.chat.id,
                         "Sorry, {0.first_name}, but you are supposed to send a text message.\nDon't send me garbage, please.\nTry again."
                         .format(message.from_user, bot.get_me()),
                         parse_mode='html')
        bot.register_next_step_handler(message, get_height)

# Обрабатываем нестандартный рост
def get_height_abnormal(message):
    if message.content_type == 'text':
        if message.text.isnumeric():
            height = float(message.text)
            bot.send_message(message.chat.id,
                             "Thank you! We got all required information."
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')
            us_id = [f"{message.chat.id}"]
            conn = connect("bot.db")
            c = conn.cursor()
            c.execute('''
                                    SELECT weight FROM users
                                    WHERE chat_id = ?
                                    LIMIT 1
                                    ''', tuple(us_id))
            (weight,) = c.fetchone()
            c.execute('''
                         DELETE FROM users
                         WHERE chat_id = ?
                         ''', tuple(us_id))
            user_data = [f"{message.chat.id}", weight, height]
            c.execute('''
                                INSERT INTO users (chat_id, weight, height) VALUES (?, ?, ?)
                                ''', tuple(user_data))
            conn.commit()
        elif re.match(r"^\d+?\.\d+?$", message.text) is None:
            bot.send_message(message.chat.id,
                             "Check your data. Enter your height again:"
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')
            bot.register_next_step_handler(message, get_height)
        else:
            height = float(message.text)
            bot.send_message(message.chat.id,
                             "Thank you! We got all required information."
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')
            us_id = [f"{message.chat.id}"]
            conn = connect("bot.db")
            c = conn.cursor()
            c.execute('''
                            SELECT weight FROM users
                            WHERE chat_id = ?
                            LIMIT 1
                            ''', tuple(us_id))
            (weight,) = c.fetchone()
            user_data = [f"{message.chat.id}", weight, height]
            c.execute('''
                        INSERT INTO users (chat_id, weight, height) VALUES (?, ?, ?)
                        ''', tuple(user_data))
            conn.commit()
    else:
        bot.send_message(message.chat.id,
                         "Sorry, {0.first_name}, but you are supposed to send a text message.\nDon't send me garbage, please.\nTry again."
                         .format(message.from_user, bot.get_me()),
                         parse_mode='html')
        bot.register_next_step_handler(message, get_height)

# Считаем BMI, используя SQL
@bot.message_handler(commands=['bmi'])
def countBMI(message):

    us_id = [f"{message.chat.id}"]

    conn = connect("bot.db")
    c = conn.cursor()

    if c.execute('''
                SELECT height FROM users
                WHERE chat_id = ?
                LIMIT 1
                ''', tuple(us_id)).fetchone() is None:
        bot.send_message(message.chat.id, "Sorry, but you should provide the bot with the data about yourself.")
        conn.commit()
    else:
        bot.send_message(message.chat.id,
                         "Body mass index (BMI) is a measure of body fat based on height and weight that applies to adult men and women.".format(
                             message.from_user, bot.get_me()),
                         parse_mode='html')

        # SQL
        conn.commit()
        conn = connect("bot.db")
        c = conn.cursor()
        c.execute('''
                    SELECT height, weight FROM users
                    WHERE chat_id = ?
                    LIMIT 1
                    ''', tuple(us_id))
        (h,w) = c.fetchone()
        conn.commit()
        BMI = open('BMI.png', 'rb')
        bot.send_photo(message.chat.id, photo=BMI)
        bmi = round(float(w) / (float(h) / 100) ** 2, 1)
        bot.send_message(message.chat.id, f"Your BMI is {bmi}")
        if bmi < 16:
            bot.send_message(message.chat.id,
                             "Your BMI is less than 18.5 and it indicates you are underweight. You may need to gain weight.")
        elif bmi > 25:
            bot.send_message(message.chat.id,
                             "Your BMI is greater than 25 and it is defined as overweight. It's a good idea to lose some weight for your health's sake, or at least aim to prevent further weight gain.")
        else:
            bot.send_message(message.chat.id, "You're in a healthy weight, and should aim to stay that way 💪")

# Тут мы используем уже полученную базу данных, с помощью selenium и SQL
# Выдаем клавиатуру для выбора витамина и ответа на вопрос
# "Зачем мне его есть?"
@bot.message_handler(commands=['why'])
def get_vitamin(message):
    chat_id = message.chat.id
    bot.send_message(message.chat.id,
                     "Choose a vitamin from the following list and the bot will tell you <b>why</b> your body needs it."
                     .format(message.from_user, bot.get_me()), reply_markup=keyboard_vitamins_why(chat_id),
                     parse_mode='html')

# "А как я могу получить витамин?" (опять выдаем клавиатуру)
@bot.message_handler(commands=['how'])
def get_source(message):
    chat_id = message.chat.id
    bot.send_message(message.chat.id,
                     "Choose a vitamin from the following list and the bot will tell you <b>how</b> can get it."
                     .format(message.from_user, bot.get_me()), reply_markup=keyboard_vitamins_how(chat_id),
                     parse_mode='html')

# "Что находится в еде?"
@bot.message_handler(commands=['what'])
def meal(message):
    bot.send_message(message.chat.id,
                     "Seems like you want to check composition of your meal"
                     .format(message.from_user, bot.get_me()),
                     parse_mode='html')
    bot.send_message(message.chat.id,
                     "Send the name of the specified dish and the bot will provide you with a choice from a few variants."
                     .format(message.from_user, bot.get_me()),
                     parse_mode='html')
    bot.send_message(message.chat.id,
                     "<i>Choose the most appropriate option.</i>"
                     .format(message.from_user, bot.get_me()),
                     parse_mode='html')
    bot.register_next_step_handler(message, send_var)

# Тут мы обрабатываем то, на какую клавишу нажал
# пользователь и какой у него был запрос
@bot.callback_query_handler(func=lambda message:True)
def callback_inline(message):
    chat_id = message.message.chat.id
    conn = connect("minerals.db")
    c = conn.cursor()
    minerals_raw = c.execute("""
        SELECT mineral FROM min_info;
        """).fetchall()
    list_of_vitamins = []
    for i in minerals_raw:
        (j,) = i
        list_of_vitamins.append(j)
    conn.commit()
    info = message.data.split(':')
    f = info[0]
    vitamin = info[1]
    # "Зачем нужен?"
    if f == 'why':
        if vitamin in list_of_vitamins:
            vit_upd = (vitamin,)
            conn = connect("minerals.db")
            c = conn.cursor()
            c.execute('''
                                 SELECT cause1, cause2 FROM min_info
                                 WHERE mineral = ?
                                 LIMIT 1
                                 ''', vit_upd)
            (c1, c2) = c.fetchone()
            conn.commit()

            bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id, text=f"You chose {vitamin}.\nHere is info about it:",
                                  reply_markup=None)

            bot.send_message(chat_id,
                             "⬇⬇⬇"
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')


            bot.send_message(chat_id,
                             f"{c1}\n\n{c2}"
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')

    # "Как получить?"
    elif f == 'how':
        if vitamin in list_of_vitamins:
            vit_upd = (vitamin,)
            conn = connect("minerals.db")
            c = conn.cursor()
            c.execute('''
                                 SELECT how, get1, get2, get3 FROM min_info
                                 WHERE mineral = ?
                                 LIMIT 1
                                 ''', vit_upd)
            (how, g1, g2, g3) = c.fetchone()
            conn.commit()

            bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                                  text=f"You chose {vitamin}.\nHere is info about it:",
                                  reply_markup=None)

            bot.send_message(chat_id,
                             "⬇⬇⬇"
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')

            bot.send_message(chat_id,
                             f"{how}\n✓ {g1}\n✓ {g2}\n✓ {g3}"
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')

    # "Что содержится в моей еде?"
    # Тут мы используем API, чтобы получить состав продуктов
    elif f == 'what':
        entrypoint = 'https://api.nal.usda.gov/fdc/v1/foods/search'
        service_key = 'iWevvaM8g3wDoY8u3J9MBS3i4wlN58yP4OdxLT2U'
        num = int(info[1])-1
        req = info[2]

        r = requests.get(entrypoint, {'api_key': service_key, 'query': req, 'format': 'json'})
        response = json.loads(r.text)

        food_info = response['foods'][num]['foodNutrients']
        all_nutr = ""

        for i in range(0, len(food_info)):
            # C помощью регулярных выражений мы проверяем тип содержимого
            # не выводим непонятное содержимое, такое как "14:3 vitamin"
            if (re.match(r"\d+?\:\d+?", response['foods'][num]['foodNutrients'][i]['nutrientName']) is None):
                all_nutr = all_nutr + f"\n✓ {response['foods'][num]['foodNutrients'][i]['nutrientName']} – {response['foods'][num]['foodNutrients'][i]['value']} {response['foods'][num]['foodNutrients'][i]['unitName']}"

        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                            text=f"You chose #{num+1}.\nHere is info about its composition per 100g",
                            reply_markup=None)

        bot.send_message(chat_id,
                             "⬇⬇⬇"
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')

        bot.send_message(chat_id,
                             all_nutr
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')


# Задаем клавиатуру для "Зачем?"
def keyboard_vitamins_why(chat_id):
    conn = connect("minerals.db")
    c = conn.cursor()
    minerals_raw = c.execute("""
    SELECT mineral FROM min_info;
    """).fetchall()
    list_of_vitamins = []
    for i in minerals_raw:
        (j,) = i
        list_of_vitamins.append(j)
    conn.commit()

    keyboard = types.InlineKeyboardMarkup()
    for vit in list_of_vitamins:
        callback_vit = f'why:{vit}'
        keyboard.add(types.InlineKeyboardButton(text = vit, callback_data=callback_vit))

    return keyboard

# Задаем клавиатуру для "Как получить?"
def keyboard_vitamins_how(chat_id):
    conn = connect("minerals.db")
    c = conn.cursor()
    minerals_raw = c.execute("""
    SELECT mineral FROM min_info;
    """).fetchall()
    list_of_vitamins = []
    for i in minerals_raw:
        (j,) = i
        list_of_vitamins.append(j)
    conn.commit()

    keyboard = types.InlineKeyboardMarkup()
    for vit in list_of_vitamins:
        callback_vit = f'how:{vit}'
        keyboard.add(types.InlineKeyboardButton(text=vit, callback_data=callback_vit))

    return keyboard

# Проверяем с помощью API корректность введенного блюда
# Иногда API говорит, что произошла ошибка и это первый случай
# Иногда просто говорит, что таких блюд нет и это второй случай
# Как и всегда проверяем, чтобы нам отправили именно текст
def send_var(message):
    if message.content_type == 'text':
        entrypoint = 'https://api.nal.usda.gov/fdc/v1/foods/search'
        service_key = 'iWevvaM8g3wDoY8u3J9MBS3i4wlN58yP4OdxLT2U'
        selected_prod = message.text
        r = requests.get(entrypoint, {'api_key': service_key, 'query': selected_prod, 'format': 'json'})
        response = json.loads(r.text)
        if 'error' in response:
            bot.send_message(message.chat.id,
                             "Check your input and try again."
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')
            bot.register_next_step_handler(message, send_var)
        elif response['totalHits'] == 0:
            bot.send_message(message.chat.id,
                             "Check your input and try again."
                             .format(message.from_user, bot.get_me()),
                             parse_mode='html')
            bot.register_next_step_handler(message, send_var)
        else:
            bot.send_message(message.chat.id,
                         f"Okay, you chose \'{message.text}\'. Chose one variant from the following list:"
                         .format(message.from_user, bot.get_me()), reply_markup=keyboard_vitamins_what(message.text),
                         parse_mode='html')
    else:
        bot.send_message(message.chat.id,
                         "Sorry, {0.first_name}, but you are supposed to send a text message.\nDon't send me garbage, please.\nTry again."
                         .format(message.from_user, bot.get_me()),
                         parse_mode='html')
        bot.register_next_step_handler(message, send_var)

# С помощью API выдаем несколько вариантов на запрос
# (5 или столько, сколько есть, иногда
# блюдо специфическое и там мало вариантов)
def keyboard_vitamins_what(text_from_mes):
    entrypoint = 'https://api.nal.usda.gov/fdc/v1/foods/search'
    service_key = 'iWevvaM8g3wDoY8u3J9MBS3i4wlN58yP4OdxLT2U'
    selected_prod = text_from_mes
    r = requests.get(entrypoint, {'api_key': service_key, 'query': selected_prod, 'format': 'json'})
    response = json.loads(r.text)
    list_prod = []
    for i in range(0,min(5, response['totalHits'])):
        list_prod.append(f"{i+1}. {response['foods'][i]['description']}")

    keyboard = types.InlineKeyboardMarkup()
    for prod in list_prod:
        num_raw = prod.split('. ')
        num = num_raw[0]
        callback_pr = f"what:{num}:{selected_prod}"
        keyboard.add(types.InlineKeyboardButton(text=prod, callback_data=callback_pr))

    return keyboard

# На все другие запросы просто просим пользователя изучить
# имеющиеся команды бота
@bot.message_handler(content_types=['text'])
def actions(message):
        bot.send_message(message.chat.id, "Please, choose a command.\nUse backslash to see all of them ❤")

# Запускаем бота
bot.polling(none_stop=True)