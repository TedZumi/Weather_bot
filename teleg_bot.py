import time
from datetime import datetime, timedelta
import telebot
from telebot import State
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import yandex
import edit_scv
from geopy.geocoders import Nominatim

import clothes
token = "6763518151:AAGdfUXGud7gYcgA6CvNaGH-5Bc5J9P20BA"



def get_geo(city):
    try:
        geolocator = Nominatim(user_agent="telebot")
        location = geolocator.geocode(city)

        if location:
            return location.address, location.latitude, location.longitude
        else:
            return "Location not found", 0, 0
    except Exception as e:
        return "Error occurred: {}".format(str(e))

def telegram_bot(token):
    bot = telebot.TeleBot(token)
    clothes_result=dict.fromkeys(["Пол","Температура","Осадки"])
    city_date = dict.fromkeys(["Город", "Дата", "Сутки"])
    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Привет! Я рад приветствовать тебя! Я могу помочь тебе узнать погоду.")


    @bot.message_handler(commands=["temperature"])
    def send_text(message):
          bot.send_message(message.chat.id, "Напишите название города")
          bot.register_next_step_handler(message,temperature)
    def temperature(message):
          if message.text.lower() != "":
              try:
                  bot.send_message(message.chat.id, "------")
                  address, latitude, longitude = yandex.get_geo(message.text)

                  bot.send_message(message.chat.id, address)
                  bot.send_message(message.chat.id, str(latitude)+"  " + str(longitude))

                  weather = yandex.curr_weath(latitude, longitude)
                  for key, value in weather.items():
                      bot.send_message(message.chat.id, f"{key}: {value}")

              except Exception as ex:
                  print(ex)
                  bot.send_message(message.chat.id, "Что-то пошло не так, попробуйте еще раз")
          else:
              bot.send_message(message.chat.id, "Ошибка. Попробуйте ввести еще раз")

    @bot.message_handler(commands=["clothes"])
    def clothes_info(message):
        keyboard = [
            [InlineKeyboardButton(text="М", callback_data="М"),
             InlineKeyboardButton(text="Ж", callback_data="Ж")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(message.chat.id ,text='Ваш пол:', reply_markup=reply_markup)
        sent = bot.reply_to(message, "Напишите название города")
        bot.register_next_step_handler(sent, city_in)

    @bot.callback_query_handler(func=lambda call:True)
    def callback_inline(call):
        if call.message:
            if call.data =="М":

                clothes_result["Пол"] = "m"
            if call.data =="Ж":

                clothes_result["Пол"] = "f"
            if call.data == "specific_date":

                bot.send_message(call.message.chat.id, "Пожалуйста, введите дату (например, 01.01.2023):")

                bot.register_next_step_handler(call.message, date_in)

            elif call.data == "today":
                city_date["Дата"] = datetime.now().strftime("%d.%m.%Y")
                print(city_date["Дата"])
            elif call.data == "tomorrow":
                city_date["Дата"] = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
                print(city_date["Дата"])


            elif call.data == "morning":
                city_date["Сутки"] = "Утро"
                day_info(call.message)

            elif call.data == "afternoon":
                city_date["Сутки"] = "День"
                day_info(call.message)
            elif call.data == "evening":
                city_date["Сутки"] = "Вечер"
                day_info(call.message)
            elif call.data == "night":
                city_date["Сутки"] = "Ночь"
                day_info(call.message)

    def date_in(message):
        user_date = message.text
        city_date["Дата"] = user_date
        print(city_date["Дата"])


    def city_in(message):
        address, latitude, longitude = get_geo(message.text)
        bot.send_message(message.chat.id, f'Твоя геолокация: {address}, {latitude}, {longitude}')
        city_name = address.split(',')[0].strip()
        city_date["Город"] = city_name
        keyboard = [
            [InlineKeyboardButton(text="Сегодня", callback_data="today"),
             InlineKeyboardButton(text="Завтра", callback_data="tomorrow"),
             InlineKeyboardButton(text="Конкретная дата", callback_data="specific_date")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)


        bot.send_message(message.chat.id, "Выберите дату:", reply_markup=reply_markup)
        time.sleep(5)

        keyboard1 = [
            [InlineKeyboardButton(text="Утро", callback_data="morning"),
             InlineKeyboardButton(text="День", callback_data="afternoon"),
             InlineKeyboardButton(text="Вечер", callback_data="evening"),
             InlineKeyboardButton(text="Ночь", callback_data="night")]
        ]
        reply_markup1 = InlineKeyboardMarkup(keyboard1)

        bot.send_message(message.chat.id, "Выберите время суток:", reply_markup=reply_markup1)


    def day_info(message):
        print(city_date)
        temp_v, weat_v = edit_scv.predict_weather(bot, message.chat.id, city_date)
        print(temp_v, weat_v)
        if city_date["Сутки"] == "Утро":
            clothes_result["Температура"], clothes_result["Осадки"] = temp_v[0], weat_v[0]
        elif city_date["Сутки"] == "День":
            clothes_result["Температура"], clothes_result["Осадки"] = temp_v[1], weat_v[1]
        elif city_date["Сутки"] == "Вечер":
            clothes_result["Температура"], clothes_result["Осадки"] = temp_v[2], weat_v[2]
        elif city_date["Сутки"] == "Ночь":
            clothes_result["Температура"], clothes_result["Осадки"] = temp_v[3], weat_v[3]

        print(clothes_result["Температура"], clothes_result["Осадки"])
        print(clothes_result)
        precipitation = clothes.precipitation_is(clothes_result['Осадки'])
        image_path = clothes.get_data(clothes_result['Температура'],clothes_result['Пол'], precipitation)
        img = open(image_path[1:], 'rb')
        bot.send_photo(message.chat.id, img)

    @bot.message_handler(commands=["weather"])
    def send_text(message):
          sent=bot.reply_to(message, "Напишите название города")
          bot.register_next_step_handler(sent, city_info)

    def city_info(message):
        keyboard = [
            [InlineKeyboardButton(text="Сегодня", callback_data="today"),
             InlineKeyboardButton(text="Завтра", callback_data="tomorrow"),
             InlineKeyboardButton(text="Конкретная дата", callback_data="specific_date")]
        ]
        address, latitude, longitude = get_geo(message.text)
        bot.send_message(message.chat.id, f'Твоя геолокация: {address}, {latitude}, {longitude}')
        city_name = address.split(',')[0].strip()
        city_date["Город"] = city_name

        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(message.chat.id, "Выберите дату:", reply_markup=reply_markup)
        print(city_date)
        temp_v, weat_v = edit_scv.predict_weather(bot, message.chat.id, city_date)


    def date_in(message):
            city_date["Дата"] = message.text
            print(city_date["Дата"])

    bot.polling(none_stop=True, interval=0)

telegram_bot(token)