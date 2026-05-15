import os

import telebot

import requests

from datetime import datetime, timedelta



# Токен берётся из переменной окружения (обязательно добавить на хостинге)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:

    raise Exception("BOT_TOKEN не задан в переменных окружения")



bot = telebot.TeleBot(TOKEN)



# Хранилище ключей Wildberries (в памяти, при перезапуске бота сбросится)

user_keys = {}



def get_sales(api_key, date_from):

    """Запрашивает продажи у Wildberries за последние сутки"""

    url = "https://statistics-api.wildberries.ru/api/v1/supplier/sales"

    headers = {"Authorization": api_key}

    params = {"dateFrom": date_from}

    try:

        resp = requests.get(url, headers=headers, params=params, timeout=15)

        if resp.status_code == 200:

            return resp.json()

        else:

            print(f"Ошибка API WB: {resp.status_code}")

            return None

    except Exception as e:

        print(f"Ошибка соединения: {e}")

        return None



@bot.message_handler(commands=['start'])

def start(message):

    bot.reply_to(message,

                 "📦 Привет! Я бот для аналитики Wildberries.\n"

                 "1. Отправь /add_key и вставь свой API-ключ\n"

                 "2. После этого используй /report для отчёта\n"

                 "Ключ можно получить в личном кабинете WB → Профиль → Интеграции по API.")



@bot.message_handler(commands=['add_key'])

def ask_for_key(message):

    msg = bot.reply_to(message, "✏️ Отправь свой API-ключ Wildberries (токен).")

    bot.register_next_step_handler(msg, save_key)



def save_key(message):

    api_key = message.text.strip()

    user_id = message.chat.id

    user_keys[user_id] = api_key

    bot.reply_to(message, "✅ API-ключ сохранён! Теперь используй /report.")



@bot.message_handler(commands=['report'])

def report(message):

    user_id = message.chat.id

    if user_id not in user_keys:

        bot.reply_to(message, "❌ Сначала добавь API-ключ командой /add_key")

        return



    api_key = user_keys[user_id]

    bot.reply_to(message, "⏳ Запрашиваю данные за последние 24 часа...")



    # Дата начала – вчера

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000Z")

    sales = get_sales(api_key, yesterday)



    if sales is None:

        bot.reply_to(message, "⚠️ Ошибка при обращении к Wildberries. Проверь API-ключ или попробуй позже.")

        return

    if not sales:

        bot.reply_to(message, "📭 За последние сутки продаж нет.")

        return



    total_revenue = 0.0

    for item in sales:

        # priceWithDiscount – итоговая цена за единицу с учётом скидки

        total_revenue += float(item.get('priceWithDiscount', 0))



    # Упрощённый расчёт чистой прибыли: 85% от выручки (средняя комиссия + логистика ≈15%)

    net_profit = total_revenue * 0.85



    reply = (f"📊 Отчёт за последние 24 часа:\n"

             f"💰 Выручка: {total_revenue:,.2f} ₽\n"

             f"📦 Количество продаж: {len(sales)}\n"

             f"⭐ Чистая прибыль (приблизительно): {net_profit:,.2f} ₽\n"

             f"_(Без учёта возвратов и точной логистики)_")

    bot.reply_to(message, reply, parse_mode='Markdown')



# Эхо-заглушка

@bot.message_handler(func=lambda m: True)

def fallback(message):

    bot.reply_to(message, "🤖 Используй /start, /add_key или /report")



print("✅ Бот запущен и слушает сообщения...")

bot.infinity_polling()
