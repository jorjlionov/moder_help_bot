import sqlite3
import telebot
from telebot import types

# Токен бота
TOKEN = '7770375433:AAHHX1_TmjrDuh7Zgk6RAvVu5qzQ5nymkLY'

# Создание бота
bot = telebot.TeleBot(TOKEN)

# Подключение к базе данных
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 0
)
''')
conn.commit()


# Обработка команды /start
@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Проверяем, есть ли пользователь в базе
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    if not user:
        # Если пользователя нет, добавляем его в базу
        cursor.execute('INSERT INTO users (user_id, username, balance) VALUES (?, ?, ?)', (user_id, username, 0))
        conn.commit()
        bot.reply_to(message, f"Привет, {username}! Твой баланс: 0")
    else:
        # Если пользователь есть, показываем его баланс
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        balance = cursor.fetchone()[0]
        bot.reply_to(message, f"Привет, {username}! Твой баланс: {balance}")


# Команда /add_balance
@bot.message_handler(commands=['add_balance'])
def add_balance(message):
    user_id = message.from_user.id
    try:
        amount = int(message.text.split()[1])  # Получаем сумму из команды
        cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()

        # Показываем новый баланс
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        new_balance = cursor.fetchone()[0]
        bot.reply_to(message, f"Баланс пополнен! Новый баланс: {new_balance}")
    except (IndexError, ValueError):
        bot.reply_to(message, "Используйте: /add_balance [сумма]")


# Команда /reg
@bot.message_handler(commands=['reg'])
def register(message):
    bot.send_message(message.chat.id, 'Введите ваше имя:')
    bot.register_next_step_handler(message, get_name)


# Получение имени
def get_name(message):
    name = message.text
    bot.send_message(message.chat.id, 'Введите свой возраст:')
    bot.register_next_step_handler(message, get_age, name)


# Получение возраста
def get_age(message, name):
    age = message.text
    bot.send_message(message.chat.id, f'Регистрация завершена! Твоё имя: {name}, твой возраст: {age}')



# Запускаем бота
bot.polling(none_stop=True)
