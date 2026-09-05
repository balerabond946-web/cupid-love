import os
import json
import telebot
from telebot import types

# Сюда мы вставим твой секретный токен из BotFather
API_TOKEN = '7669480133:AAFl69LCHBOn-T0fF9f32A5oO9k06e91mXQ' 

bot = telebot.TeleBot(API_TOKEN)

# Ловим посылку от нашей малиновой кнопки из мини-приложения
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        # Распаковываем данные (имена и готовый отчет)
        data = json.loads(message.web_app_data.data)
        
        if data.get("action") == "compatibility_invoice":
            title = data.get("title", "Расчет совместимости")
            description = data.get("description", "Полный гороскоп вашей пары")
            amount = int(data.get("amount", 5)) # Цена в Звёздах
            report = data.get("report", "Ошибка генерации прогноза")
            
            # Формируем официальный чек на оплату Telegram Stars
            prices = [types.LabeledPrice(label='Telegram Stars', amount=amount)]
            
            # Отправляем счет пользователю в чат! Посылка содержит внутри скрытый отчет
            bot.send_invoice(
                chat_id=message.chat.id,
                title=title,
                description=description,
                invoice_payload=report, # Прячем сюда текст прогноза, он выдастся после оплаты!
                provider_token='', # Для Telegram Stars тут должно быть пусто
                currency='XTR', # Официальный код валюты Telegram Stars
                prices=prices
            )
    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")

# Проверяем факт успешной оплаты Звёздами
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    # Говорим Телеграму, что всё супер, мы готовы принять Звёзды
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Как только оплата прошла — бот мгновенно выдает тот самый красивый скрытый прогноз!
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    # Достаем текст прогноза, который мы спрятали в чеке
    saved_report = message.successful_payment.invoice_payload
    
    bot.send_message(
        message.chat.id, 
        f"🎉 **Оплата успешно принята!**\n\nВот ваш персональный расчет совместимости:\n\n{saved_report}",
        parse_mode='Markdown'
    )

# Запуск постоянного прослушивания сети
if __name__ == '__main__':
    print("Умный Купидон запущен и слушает сеть...")
    bot.infinity_polling()
