import psycopg2

def createWeatherBD():  #Создание бд с табличками
    con = psycopg2.connect(dbname="postgres", user="postgres", password="tedzumi", host="127.0.0.1")
    cursor = con.cursor()
    con.autocommit = True
    cursor.execute("CREATE DATABASE weatherbd")
    cursor.close()
    con.close()

    con = psycopg2.connect(dbname="weatherbd", user="postgres", password="tedzumi", host="127.0.0.1")
    cursor = con.cursor()
    con.autocommit = True
    cursor.execute("""CREATE TABLE Moscow (
            date date, 
            period varchar(6), 
            temperature real, 
            humidity real, 
            current_weather int, 
            Primary key (date, period))""")
    cursor.execute("""CREATE TABLE N_Novgorod (
                date date, 
                period varchar(6), 
                temperature real, 
                humidity real, 
                current_weather int, 
                Primary key (date, period));""")
    cursor.close()
    con.close()


def addData():  # Добавление данных из архива
    con = psycopg2.connect(dbname="weatherbd", user="postgres", password="tedzumi", host="127.0.0.1")
    cursor = con.cursor()
    cursor.execute("""COPY N_Novgorod FROM 'csvform/N_Novgorod.csv' WITH (format csv, header, delimiter ';', encoding 'WIN1251')""")
    cursor.execute("""COPY Moscow FROM  'csvform/Moscow.csv'
            WITH (format csv, header, delimiter ';', encoding 'WIN1251')""")
    cursor.close()
    con.close()


def selectWeather(city, period): # Достаём данные
    con = psycopg2.connect(dbname="weatherbd", user="postgres", password="tedzumi", host="127.0.0.1")
    cursor = con.cursor()
    if period != "all": # Проверяем какой период нужен или берём всё
        cursor.execute("SELECT date, temperature, humidity, current_weather FROM "+city+" WHERE period = %s", (period, ))
    else:
        cursor.execute("SELECT date, temperature, humidity, current_weather FROM "+city+"",)
    result = cursor.fetchall()
    cursor.close()
    con.close()
    return result

#print(selectWeather('Moscow', 'День'))

