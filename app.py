import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# --- Настройки ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
APP_URL = os.environ.get('RENDER_EXTERNAL_URL')

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# --- Список ваших хэштегов ---
HASHTAGS = ["#обзор", "#ошибка", "#идея", "#вопрос", "#документация"]

# --- Логика Бота ---

# Эта функция создает саму клавиатуру с кнопками
def create_tags_keyboard():
    markup = InlineKeyboardMarkup()
    for tag in HASHTAGS:
        # Важно: callback_data - это уникальная строка, которую бот получит при нажатии
        button = InlineKeyboardButton(text=tag, callback_data=f"tag_{tag}")
        markup.add(button)
    return markup

# Обработчик команды /tags, который отправляет сообщение с кнопками
@bot.message_handler(commands=['tags'])
def send_tags(message):
    print("Получена команда /tags")
    markup = create_tags_keyboard()
    bot.send_message(message.chat.id, "Выберите хэштег:", reply_markup=markup)

# Обработчик нажатий на кнопки (колбэков)
# Он сработает, только если callback_data начинается с "tag_"
@bot.callback_query_handler(func=lambda call: call.data.startswith('tag_'))
def handle_tag_callback(call):
    # Получаем хэштег из callback_data (отрезаем "tag_")
    hashtag = call.data.replace('tag_', '')
    user = call.from_user
    
    # Отправляем сообщение в чат о том, кто и что выбрал
    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Пользователь @{user.username} выбрал: {hashtag}"
    )
    
    # Отправляем короткое уведомление "Выбран #обзор" вверху экрана
    bot.answer_callback_query(call.id, text=f"Выбран {hashtag}")


# --- Веб-сервер для приема вебхуков (остается без изменений) ---

@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    # Эта функция сама разберется, пришло сообщение или нажатие на кнопку
    bot.process_new_updates([update])
    return "!", 200

@server.route("/set_webhook")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL + '/' + TOKEN)
    return "Webhook установлен!", 200

@server.route("/")
def index():
    return "Сервер бота запущен!"

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
