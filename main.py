import telebot as tb
import time as t

print('🙌 Я работаю 🙌')

# Токен
TOKEN = ''

# Создание бота
bot = tb.TeleBot(TOKEN)

all_commands = [
    tb.types.BotCommand('start', 'Запуск бота')

]

admin_commands = [
    tb.types.BotCommand('ban', '(В ответ сообщения) забанить участника'),
    tb.types.BotCommand('unban', 'Разбанить участника [ID]')
]

# Создание клавиатуры

markup = tb.types.InlineKeyboardMarkup(row_width=2)
btn_yes = tb.types.InlineKeyboardButton('Да! 🤜🤛', callback_data='yes')
btn_no = tb.types.InlineKeyboardButton('Нет! 👌', callback_data='no')
markup.add(btn_yes, btn_no)
    

# Список забаненных пользователей
banned_users = set()

# Обработка /start
@bot.message_handler(commands=['start'])
def send_hello(message):
    user = message.from_user
    bot.reply_to(
        message,
        f"Привет, {user.first_name}! Я бот-модератор. Вот что я умею:\n"
        "/ban [id] - заблокировать пользователя\n"
        "/unban [id] - разблокировать пользователя"
    )
    bot.send_message(
        message.chat.id,
        'Нужна инструкция по добавлению меня в канал?',
        reply_markup=markup
    )

    bot.set_my_commands(all_commands)

    try: # Попробуй сделать проверку админа
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status in ['administrator', 'creator']:
            bot.set_my_commands(admin_commands + all_commands)
    except Exception as e: # Если не получится отправь DEBUG
        print(f"Ошибка при получении информации о члене чата: {e}")

# Обработка инлайн-кнопок
@bot.callback_query_handler(func=lambda call: True)
def call_reaction(call):
    if call.data == 'yes':
        bot.answer_callback_query(call.id)  # Убираем часики загрузки

        # Отправляем сообщение с часами
        msg_with_clock = bot.send_message(call.message.chat.id, '⏳')
        bot.send_chat_action(call.message.chat.id, 'typing')  # Имитация печати

        t.sleep(10)  # Задержка

        # Удаляем сообщение с часами
        bot.delete_message(chat_id=call.message.chat.id, message_id=msg_with_clock.message_id)

        # Отправляем новое сообщение с инструкцией
        bot.send_message(
            call.message.chat.id,
            'Инструкция:\n'
            '1. Зайти в свою группу.\n'
            '2. Зайти в настройки группы.\n'
            '3. Выбрать пункт "Администраторы".\n'
            '4. Нажать "Добавить".\n'
            '5. В поиске написать @Moder_Helperobot.\n'
            '6. Включить все галочки и нажать "Готово".'
        )
    else:
        bot.send_message(call.message.chat.id, 'Хорошо')

    # Удаляем сообщение с инлайн-кнопками
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

# Обработка /ban
@bot.message_handler(commands=['ban'])
def com_ban(message):
    try: # Попробуй сделать проверку админа для бана 
        if not message.reply_to_message or not message.reply_to_message.from_user:
            bot.reply_to(message, 'Эта команда должна быть отправлена в ответ на сообщение пользователя.')
            chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ['administrator', '']:
            user = message.from_user
            bot.send_message(message.chat.id, f'{user.first_name}, у вас нет прав на использование этой команды')
        # Расстрелять! (БАН!)
        target_user = message.reply_to_message.from_user
        banned_users.add(target_user.id)
        bot.reply_to(message, f"Пользователь {target_user.first_name} ({target_user.id}) заблокирован.")

    except Exception as e: # Если не получится отправь DEBUG
        bot.reply_to(message, "Произошла ошибка при выполнении команды.")
        print(f"Ошибка при блокировке пользователя: {e}")

# Обработка /unban
@bot.message_handler(commands=['unban'])
def unban(message):
    try:
        user_id = int(message.text.split()[1])
        if user_id in banned_users:
            banned_users.remove(user_id)
            bot.reply_to(message, f'Пользователь с ID {user_id} разблокирован ✅')
        else:
            bot.reply_to(message, f'Пользователь с ID {user_id} не был заблокирован 😊')
    except (IndexError, ValueError):
        bot.reply_to(message, 'Используйте: /unban [ID]')

# Проверка сообщений на наличие бана или запрещённых слов
@bot.message_handler(func=lambda message: True)
def message_moder(message):
    user = message.from_user

    if user.id in banned_users:
        try:
            # Проверяем, является ли бот администратором
            chat_member = bot.get_chat_member(message.chat.id, bot.get_me().id)
            if chat_member.status in ['administrator']:
                bot.reply_to(message, f"{user.first_name}, вы заблокированы и не можете писать.")
                bot.delete_message(message.chat.id, message.message_id)
            else:
                bot.reply_to(message, f"{user.first_name}, вы заблокированы и не можете писать. Попробуйте связаться с администратором.")
        except Exception as e:
            bot.reply_to(message, f"{user.first_name}, вы заблокированы и не можете писать. Попробуйте связаться с администратором.")
            print(f"Ошибка при удалении сообщения заблокированного пользователя: {e}")
        return

    # Проверка сообщения на наличие запрещённых слов
    bad_words = ['мат']
    for word in bad_words:
        if word in message.text.lower():
            try:
                # Проверяем, является ли бот администратором
                chat_member = bot.get_chat_member(message.chat.id, bot.get_me().id)
                if chat_member.status in ['administrator']:
                    bot.reply_to(message, "⚠️ Найдено запрещённое слово. Сообщение удалено.")
                    bot.delete_message(message.chat.id, message.message_id)
                else:
                    bot.reply_to(message, "⚠️ Найдено запрещённое слово. Попробуйте связаться с администратором.")
            except Exception as e:
                bot.reply_to(message, "⚠️ Найдено запрещённое слово. Попробуйте связаться с администратором.")
                print(f"Ошибка при удалении запрещённого слова: {e}")
            return

    print(f"[{user.first_name}] написал: {message.text}")

# RUN
bot.polling()
