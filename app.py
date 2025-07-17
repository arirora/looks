import os
import telebot
from flask import Flask, request

TOKEN = os.environ.get('TELEGRAM_TOKEN')
APP_URL = os.environ.get('RENDER_EXTERNAL_URL')

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        
        # Мы больше не используем @bot.message_handler, а обрабатываем всё здесь
        if update.message and update.message.text:
            message = update.message
            chat_id = message.chat.id
            text = message.text
            
            # Логика для /start
            if text == '/start':
                reply = "Привет! Это новая версия эхо-бота. Отправь мне что-нибудь."
                bot.send_message(chat_id, reply)
            # Логика для эхо
            else:
                bot.send_message(chat_id, text)
                
    except Exception as e:
        print(f"Что-то пошло не так: {e}")
        
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
