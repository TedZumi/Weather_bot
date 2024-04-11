import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.impute import SimpleImputer
import joblib
import numpy as np
import WeatherBD as bd

import teleg_bot as tb



def group_time():
    data = pd.read_csv('output.csv', delimiter=';',  encoding='ansi')

    data['Time'] = pd.to_datetime(data['Time']).dt.hour

    data['Period'] = pd.cut(data['Time'], bins=[0, 6, 12, 18, 24], labels=['Ночь', 'Утро', 'День', 'Вечер'])



    grouped_data = data.groupby(['Date', 'Period'], observed=False).agg(
        {'T': 'mean', 'U': 'mean', 'WW': lambda x: x.mode().iloc[0]}).round(1)
    grouped_data.reset_index(inplace=True)

    grouped_data['T'] = grouped_data['T'].replace('', np.nan).astype(float).fillna(method='ffill')
    grouped_data['U'] = grouped_data['U'].replace('', np.nan).astype(float).fillna(method='ffill')
    grouped_data['WW'] = grouped_data['WW'].replace('', np.nan).fillna(method='ffill')

    grouped_data['T'] = grouped_data['T'].astype(str).str.replace('.', ',')


    grouped_data.to_csv('weather_data_grouped.csv', sep=';', columns=['Date', 'Period', 'T', 'U', 'WW'],  encoding='ansi', index=False)

def replace_empty(row):

    if  pd.isnull(row['WW']) or row['WW'] == ' ':
        if any(word in str(row['c']) for word in ['Нет существенной облачности', 'Облаков нет']):
            return 4
        elif any(word in str(row['c']) for word in ['Незначительная', 'Рассеянная']):
            return 5
        elif any(word in str(row['c']) for word in ['Сплошная', 'Разорванная']):
            return 6
        else:
            return 4
    else:

        return 2 if any(word in str(row['WW']) for word in ['Снег', 'снег', 'иглы', 'крупа', 'зерна', 'морось', 'Морось']) else (
            3 if any(word in str(row['WW']) for word in ['дождь', 'ливень', 'Дождь', 'Ливень', 'Гроза', 'Шквалы']) else (
                1 if any(word in str(row['WW']) for word in ['туман', 'дымка', 'Туман', 'пыль', 'Дымка', 'Дым', 'Мгла']) else 4
            )
        )


def edit_weather():
    df = pd.read_csv('csv не формат/Санкт-Петербург 2014-2024.csv', delimiter=';',  encoding='ansi')

    #df['Date'] = df['Date'].apply(lambda x: x.split(' ')[0])

    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y %H:%M')
   # df = df.drop_duplicates(['Date'])

    #df['Date'] = df['Date'].astype(str)
   # df['Date'] = df['Date'].str.replace('-', '')

    #df['Time'] = df['Time'].str.replace(':', '')
    df['U'] = df['U'].apply(lambda x: round(x / 100, 2)).astype(float)

    df['WW'] = df.apply(replace_empty, axis=1)

    df.drop(df.columns[-1], axis=1, inplace=True)

    df['T'].ffill(inplace=True)
   # df['U'].ffill(inplace=True)
    print(df['T'].dtype)

    df['T'] = pd.to_numeric(df['T'], errors='coerce')

    df.to_csv('output.csv',  sep=';', encoding='ansi', index=False)

    print("CSV файл успешно обработан.")

def convert_weather(code):
    weather_dict = {1: "Туман", 2: "Снег", 3: "Дождь", 4: "Ясно", 5: "Облачно с прояснениями", 6: "Пасмурно"}
    return weather_dict.get(code, "Неверное значение")

def make_date(date):

    new_date = (date.strftime('%m%d'))  # Преобразование datetime.date
    return new_date

def train(city, period):

    X = []
    y = []
    result = bd.selectWeather(city, period)


    for r in result:
        date_without_dash = make_date(r[0])

        X.append([date_without_dash, r[2], r[3]])  # Добавляем дату и влажность в список X
        y.append(r[1])  # Добавляем темп в список y



    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=123)

    tree_model = DecisionTreeRegressor()

    tree_model.fit(X_train, y_train)

    joblib.dump(tree_model, f"{city}_{period}_temp.pkl")

    print("-" * 48)
    print("\nОбучение завершено\n")
    print("-" * 48)


def predict_weather(bot, chat_id, data):
    weather_data = joblib.load('city_union_temp.pkl')
    weather_weath = joblib.load('city_union_weath.pkl')
    time_of_day_dict = {
        "Morning": {"text": "Утро", "emoji": "☀️"},
        "Day": {"text": "День", "emoji": "🌞"},
        "Evening": {"text": "Вечер", "emoji": "🌆"},
        "Night": {"text": "Ночь", "emoji": "🌙"}
    }

    city = ''
    date = ''


    if data['Город'] == 'Москва':
        city = 'Moscow'
    elif data['Город'] == 'Нижний Новгород':
        city = 'N_Novgorod'

    print(data)
    if data['Дата'] != None:
        date_parts = data['Дата'].split('.')
        day = date_parts[1] + date_parts[0]

    print(city)
    print(date)


    date = [
        [day,
         (str(int(day) + 1)),
         (day)]
    ]

    temp_values = []
    weath_values = []
    if city == "Moscow":
        temp_values = [weather_data["moscow_morning"], weather_data["moscow_day"], weather_data["moscow_evening"],
                       weather_data["moscow_night"]]
        weath_values = [weather_weath["moscow_morning"], weather_weath["moscow_day"],
                        weather_weath["moscow_evening"], weather_weath["moscow_night"]]
    elif city == "N_Novgorod":
        temp_values = [weather_data["nn_morning"], weather_data["nn_day"], weather_data["nn_evening"],
                       weather_data["nn_night"]]
        weath_values = [weather_weath["nn_morning"], weather_weath["nn_day"],
                        weather_weath["nn_evening"], weather_weath["nn_night"]]
    else:
        message_text = f"Извините, к сожалению ваш город еще не добавлен. Следите за обновлениями. Хорошего вам дня."
        bot.send_message(chat_id, message_text)

    temp_v=[]
    weat_v=[]
    if temp_values and weath_values:
        for i, time_of_day in enumerate(["Morning", "Day", "Evening", "Night"]):
            temp_model = joblib.load(temp_values[i])
            temp = temp_model.predict(date)[0]

            weath_model = joblib.load(weath_values[i])
            weath = weath_model.predict(date)[0]
            weather_text = convert_weather(weath)
            #print(f"{time_of_day} temperature prediction: {temp}°C weather prediction: {weather_text} ")
            russian_time_of_day = time_of_day_dict[time_of_day]["text"]
            emoji = time_of_day_dict[time_of_day]["emoji"]
            message_text = f"{russian_time_of_day}{emoji} предсказание температуры: {temp}°C предсказание погоды: {weather_text} "
            #bot.send_message(chat_id, message_text)
            temp_v.append(int(temp))
            weat_v.append(int(weath))
    return temp_v, weat_v




def union_all():
    weather_data = {
        "moscow_morning": "models/temp/Moscow/Moscow_Утро_temp.pkl",
        "moscow_day": "models/temp/Moscow/Moscow_День_temp.pkl",
        "moscow_evening": "models/temp/Moscow/Moscow_Вечер_temp.pkl",
        "moscow_night": "models/temp/Moscow/Moscow_Ночь_temp.pkl",
        "nn_morning": "models/temp/N_Novgorod/N_Novgorod_Утро_temp.pkl",
        "nn_day": "models/temp/N_Novgorod/N_Novgorod_День_temp.pkl",
        "nn_evening": "models/temp/N_Novgorod/N_Novgorod_Вечер_temp.pkl",
        "nn_night": "models/temp/N_Novgorod/N_Novgorod_Ночь_temp.pkl"
    }

    # Сохранение всех прогнозов в один файл
    joblib.dump(weather_data, "city_union_temp.pkl")

    weather_value = {
        "moscow_morning": "models/weath/Moscow/Moscow_Утро_weath.pkl",
        "moscow_day": "models/weath/Moscow/Moscow_День_weath.pkl",
        "moscow_evening": "models/weath/Moscow/Moscow_Вечер_weath.pkl",
        "moscow_night": "models/weath/Moscow/Moscow_Ночь_weath.pkl",
        "nn_morning": "models/weath/N_Novgorod/N_Novgorod_Утро_weath.pkl",
        "nn_day": "models/weath/N_Novgorod/N_Novgorod_День_weath.pkl",
        "nn_evening": "models/weath/N_Novgorod/N_Novgorod_Вечер_weath.pkl",
        "nn_night": "models/weath/N_Novgorod/N_Novgorod_Ночь_weath.pkl"
    }

    # Сохранение всех прогнозов в один файл
    joblib.dump(weather_value, "city_union_weath.pkl")



    #union_all()
    #edit_weather()
    #group_time()
    #split_data_by_time_of_day()
    #train("Moscow", "Утро")
    #predict_weather()
    #train()