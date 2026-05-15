import os

import telebot



TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:

    raise Exception("BOT_TOKEN not found in environment variables")



bot = telebot.TeleBot(TOKEN)



@bot.message_handler(commands=['start'])

def start(message):

    bot.reply_to(message, "✅ Бот работает на Railway!")



@bot.message_handler(func=lambda message: True)

def echo(message):

    bot.reply_to(message, f"Ты написал: {message.text}")



print("Бот запущен и слушает...")

bot.infinity_polling()
