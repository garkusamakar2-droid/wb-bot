import os

import telebot

import requests

from datetime import datetime, timedelta



TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:

    raise Exception("BOT_TOKEN не задан")



bot = telebot.TeleBot(TOKEN)

user_keys = {}



def get_sales(api_key, date_from):

    url = "https://statistics-api.wildberries.ru/api/v1/supplier/sales"

    headers = {"Authorization": api_key}

    params = {"dateFrom": date_from}

    try:

        resp = requests.get(url, headers=headers, params=params, timeout=15)

        if resp.status_code == 200:

            return resp.json()

        else:

            return None

    except:

        return None



@bot.message_handler(commands=['start'])

def start(message):

    bot.reply_to(message, "Привет! Отправь /add_key для добавления API-ключа Wildberries, затем /report")



@bot.message_handler(commands=['add_key'])

def ask_for_key(message):

    msg = bot.reply_to(message, "Отправь свой API-ключ Wildberries")

    bot.register_next_step_handler(msg, save_key)



def save_key(message):

    user_keys[message.chat.id] = message.text.strip()

    bot.reply_to(message, "Ключ сохранён! Теперь /report")



@bot.message_handler(commands=['report'])

def report(message):

    uid = message.chat.id

    if uid not in user_keys:

        bot.reply_to(message, "Сначала /add_key")

        return

    api_key = user_keys[uid]

    bot.reply_to(message, "Запрашиваю данные...")

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000Z")

    sales = get_sales(api_key, yesterday)

    if sales is None:

        bot.reply_to(message, "Ошибка API, проверь ключ")

        return

    if not sales:

        bot.reply_to(message, "Продаж за сутки нет")

        return

    total = sum(float(item.get('priceWithDiscount', 0)) for item in sales)

    profit = total * 0.85

    bot.reply_to(message, f"Выручка: {total:.2f} ₽\nПрибыль (~85%): {profit:.2f} ₽\nПродаж: {len(sales)}")



@bot.message_handler(func=lambda m: True)

def fallback(message):

    bot.reply_to(message, "Используй /start, /add_key, /report")



print("Бот запущен")

bot.infinity_polling()
