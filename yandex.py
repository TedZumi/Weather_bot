import requests
import telebot
import auth_data
import teleg_bot

import datetime
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt

def curr_weath(latitude, longitude):
    url = f'https://api.weather.yandex.ru/v2/fact?lat={latitude}&lon={longitude}'
    response = requests.get(url, headers=auth_data.headers)
    if response.status_code == 200:
        weather = response.json()

    else:
      print(f'Ошибка: {response.status_code}')
    return weather

#Москва - 55.7245371, 37.625444019985025
def forecast_weath(latitude, longitude):
 #limit = сколько дней вперед
    url = f'https://api.weather.yandex.ru/v2/forecast?lat={latitude}&lon={longitude}&limit=1'
    response = requests.get(url, headers=auth_data.headers)
    if response.status_code == 200:
        data = response.json()
        date=data['forecasts'][0]['date']
        print(f"Дата: {date}")
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%m%d')

        morning_temp = data['forecasts'][0]['parts']['morning']['temp_avg']
        day_temp = data['forecasts'][0]['parts']['day']['temp_avg']
        evening_temp = data['forecasts'][0]['parts']['evening']['temp_avg']
        night_temp = data['forecasts'][0]['parts']['night']['temp_avg']

        return formatted_date, morning_temp, day_temp, evening_temp, night_temp

    else:
      print(f'Ошибка: {response.status_code}')
    return response


def eff():
    day, y_morning_temp, y_day_temp, y_evening_temp, y_night_temp = forecast_weath(55.7245371, 37.625444019985025)
    yandex_temperatures = [y_morning_temp, y_day_temp, y_evening_temp,
                           y_night_temp]

    weather_data = joblib.load('city_union_temp.pkl')
    date = [
        [day,
         (str(int(day) + 1)),
         (day)]
    ]
    model_temperatures = []
    temp_values = [weather_data["moscow_morning"], weather_data["moscow_day"], weather_data["moscow_evening"],
                   weather_data["moscow_night"]]
    for i, time_of_day in enumerate(["Morning", "Day", "Evening", "Night"]):
        temp_model = joblib.load(temp_values[i])
        temp = temp_model.predict(date)[0]
        model_temperatures.append(temp)

    mae = mean_absolute_error(yandex_temperatures, model_temperatures)
    print(f"Средняя абсолютная ошибка для всех временных интервалов: {mae}")

    mse = mean_squared_error(yandex_temperatures, model_temperatures)
    print(f"Средняя квадратичная ошибка (MSE): {mse}")


    r2 = r2_score(yandex_temperatures, model_temperatures)
    print(f"Коэффициент детерминации (R^2): {r2}")
    hours = [6, 12, 18, 24]

    plt.figure(figsize=(10, 6))
    plt.plot(yandex_temperatures, label='Температура от Яндекса', marker='o')
    plt.plot(model_temperatures, label='Предсказанная температура моделью', marker='x')

    plt.xlabel('Временные интервалы')
    plt.xticks(range(len(hours)), hours)
    plt.ylabel('Температура')
    plt.title('Сравнение температур от Яндекса и предсказанных моделью')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    eff()
    teleg_bot.telegram_bot(auth_data.token)
    #forecast_weath(55.7245371, 37.625444019985025)