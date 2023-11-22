import requests
import telebot

bot = telebot.TeleBot('6416365019:AAEM1tvgcXngl1yH0nWfKMzusSRpg3-K9r4')

@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        response = requests.get('https://fakestoreapi.com/products')
        response.raise_for_status()
        data = response.json()
        print("Received data from external source:", data)  # Отладочное сообщение

        message_text = "Список товаров:\n"
        for item in data:
            item_text = f"Название: {item['title']}\nОписание: {item['description']}\nКатегория: {item['category']}\n\n"
            if len(message_text) + len(item_text) <= 4000:
                message_text += item_text
            else:
                bot.send_message(message.chat.id, message_text)
                message_text = item_text

        bot.send_message(message.chat.id, message_text)
    except requests.exceptions.HTTPError as errh:
        bot.send_message(message.chat.id, f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        bot.send_message(message.chat.id, f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        bot.send_message(message.chat.id, f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        bot.send_message(message.chat.id, f"Something went wrong: {err}")

bot.polling(none_stop=True)

#  и  rabbit, кастом админку, реакт страница


