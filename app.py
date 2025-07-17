import os
import telebot
from flask import Flask, request

# --- Настройки ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
APP_URL = os.environ.get('RENDER_EXTERNAL_URL')

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# --- Логика Бота ---

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Диагностическое сообщение
    print("Получена команда /start")
    bot.reply_to(message, "Привет! Я эхо-бот, работающий на Render. Отправь мне что-нибудь.")

# Обработчик, который повторяет все текстовые сообщения
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # ДОБАВЛЕНО ДЛЯ ДИАГНОСТИКИ:
    print(f"Получено сообщение для эхо: '{message.text}'")
    bot.reply_to(message, message.text)


# --- Веб-сервер для приема вебхуков ---

# Этот маршрут принимает обновления от Telegram
@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# Этот маршрут нужен, чтобы сообщить Telegram адрес нашего бота
@server.route("/set_webhook")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL + '/' + TOKEN)
    return "Webhook установлен!", 200

# Простой маршрут для проверки, что сервер работает
@server.route("/")
def index():
    return "Сервер бота запущен!"

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
