import os

import threading

from http.server import HTTPServer, BaseHTTPRequestHandler

import telebot



TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:

    raise Exception("BOT_TOKEN not set")



bot = telebot.TeleBot(TOKEN)



@bot.message_handler(commands=['start'])

def start(message):

    bot.reply_to(message, "✅ Бот работает на Render!")



@bot.message_handler(func=lambda m: True)

def echo(message):

    bot.reply_to(message, message.text)



# Простой HTTP-сервер, чтобы Render видел порт

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)

        self.end_headers()

        self.wfile.write(b"Bot is running")



def run_http():

    port = int(os.environ.get("PORT", 8080))

    server = HTTPServer(('0.0.0.0', port), Handler)

    server.serve_forever()



# Запускаем HTTP-сервер в фоновом потоке

threading.Thread(target=run_http, daemon=True).start()



print("Бот успешно запущен и слушает сообщения...")

bot.infinity_polling()
