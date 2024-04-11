#Weather bot
Инструкция по запуску в режиме разработки:

Python версия 3.11 и PyCharm в качестве IDE.

Иметь установленный Postgress версия 16 или выше, библиотека для использования в python psycopg2
pip install psycopg2

Библиотеки Telebot и requests для работы с телеграмм-ботом.
pip install pyTelegramBotAPI
pip install requests

Библиотеки pandas, numpy, joblib и sklearn для обработки данных и обучения модели.
pip install numpy
pip install joblib
pip install scikit-learn

Geopy для определения местоположения пользователя. Yandex для работы с Яндекс API (проверка эффективности работы модели)
pip install geopy
Необходимо иметь API Яндекса и Telegram.

Для запуска проета в режиме разработки нужно установить среду разработки(например PyCharm), а также все вышеперечисленные библиотеки, после чего запустить файл telegb_bot.py на исполнение. Для получения более подробной информации запустить на исполнение файл yandex.py
