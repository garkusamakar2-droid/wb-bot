import os

import telebot

import requests

from datetime import datetime, timedelta



TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:

    raise Exception("BOT_TOKEN not set")



bot = telebot.TeleBot(TOKEN)



# Временное хранилище ключей (при перезапуске бота очистится)

user_keys = {}



# Функция получения продаж из API WB

def get_sales(api_key, date_from):

    url = "https://statistics-api.wildberries.ru/api/v1/supplier/sales"

    headers = {"Authorization": api_key}

    params = {"dateFrom": date_from}

    try:

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:

            return response.json()

        else:

            return None

    except Exception as e:

        print(f"Ошибка API: {e}")

        return None



# Обработчик команды /start

@bot.message_handler(commands=['start'])

def start(message):

    bot.reply_to(message, "Привет! Я бот для аналитики Wildberries.\n"

                          "Отправь /add_key и вставь свой API-ключ.\n"

                          "После этого используй /report для получения отчёта.")



# Обработчик команды /add_key

@bot.message_handler(commands=['add_key'])

def ask_for_key(message):

    msg = bot.reply_to(message, "Отправь свой API-ключ Wildberries. Он нужен для получения данных.")

    bot.register_next_step_handler(msg, save_key)



def save_key(message):

    api_key = message.text.strip()

    user_id = message.chat.id

    user_keys[user_id] = api_key

    bot.reply_to(message, "API-ключ сохранён! Теперь используй /report для получения отчёта.")



# Обработчик команды /report

@bot.message_handler(commands=['report'])

def report(message):

    user_id = message.chat.id

    if user_id not in user_keys:

        bot.reply_to(message, "Сначала добавь API-ключ командой /add_key")

        return

    api_key = user_keys[user_id]

    bot.reply_to(message, "Запрашиваю данные за последние сутки...")



    # Дата начала: вчера (или сегодня, но за 24 часа)

    date_from = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000Z")

    sales = get_sales(api_key, date_from)

    if sales is None:

        bot.reply_to(message, "Ошибка при запросе к Wildberries. Проверь API-ключ или попробуй позже.")

        return

    if not sales:

        bot.reply_to(message, "За последние сутки продаж нет.")

        return



    total_revenue = sum(float(item.get('priceWithDiscount', 0)) for item in sales)

    net_profit = total_revenue * 0.85  # упрощённый расчёт

    reply = f"📊 Отчёт за последние 24 часа:\n💰 Выручка: {total_revenue:.2f} ₽\n⭐ Чистая прибыль (≈85%): {net_profit:.2f} ₽\n📦 Количество продаж: {len(sales)}"

    bot.reply_to(message, reply)



# Эхо на все остальные сообщения (можно убрать)

@bot.message_handler(func=lambda m: True)

def echo(message):

    bot.reply_to(message, f"Я понимаю только команды: /start, /add_key, /report")



print("Бот запущен и слушает...")

bot.infinity_polling()
