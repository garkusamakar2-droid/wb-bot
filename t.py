import telebot



TOKEN = "8980119127:AAFqYyXfgQdoAsMbR88YPN08tyP3ST5IWcE"



bot = telebot.TeleBot(TOKEN)



@bot.message_handler(commands=['start'])

def start(message):

    bot.reply_to(message, "✅ Бот работает через telebot!")



@bot.message_handler(func=lambda message: True)

def echo(message):

    bot.reply_to(message, f"Ты написал: {message.text}")



print("Бот запущен...")

bot.infinity_polling()