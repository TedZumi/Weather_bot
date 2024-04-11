import psycopg2


#создание БД
def create_bd():
    connection = psycopg2.connect(dbname='clothesbase', user='postgres',
                            password='tedzumi', host='127.0.0.1', port="5432")
    cursor = connection.cursor()
    connection.autocommit = True

    cursor.execute (""" CREATE TABLE weather_clothes (
                                    weather_name VARCHAR(100),
                                    gender VARCHAR(1),
                                    precipitation VARCHAR(3),
                                    temperature_min INT,
                                    temperature_max INT,
                                    image VARCHAR(100) )"""
    )
    print("Таблица успешно создана в PostgreSQL")
    cursor.close()
    connection.close()


def add_data():
    connection = psycopg2.connect(dbname='clothesbase', user='postgres',
                                  password='tedzumi', host='127.0.0.1', port="5432")

    cursor = connection.cursor()
    # Выполнение SQL-запроса для вставки данных в таблицу
    insert_query = """ INSERT INTO weather_clothes (weather_name, gender, precipitation, temperature_min, temperature_max, image) VALUES
                                              ('very_cold', 'm', 'no', -60, -30, '/images/very_cold_no_m.jpg'),
                                              ('very_cold', 'm', 'yes', -60, -30, '/images/very_cold_yes_m.jpg'),
                                              ('very_cold', 'f', 'no', -60, -30, '/images/very_cold_no_f.jpg'),
                                              ('very_cold', 'f', 'yes', -60, -30, '/images/very_cold_yes_f.jpg'),
                                              ('cold', 'm', 'no', -29, -15, '/images/cold_no_m.jpg'),
                                              ('cold', 'm', 'yes', -29, -15, '/images/cold_yes_m.jpg'),
                                              ('cold', 'f', 'no', -29, -15, '/images/cold_no_f.jpg'),
                                              ('cold', 'f', 'yes', -29, -15, '/images/cold_yes_f.jpg'),
                                              ('cool', 'm', 'no', -14, -1, '/images/cool_no_m.jpg'),
                                              ('cool', 'm', 'yes', -14, -1, '/images/cool_yes_m.jpg'),
                                              ('cool', 'f', 'no', -14, -1, '/images/cool_no_f.jpg'),
                                              ('cool', 'f', 'yes', -14, -1, '/images/cool_yes_f.jpg'),
                                              ('warm', 'm', 'no', 0, 14, '/images/warm_no_m.jpg'),
                                              ('warm', 'm', 'yes', 0, 14, '/images/warm_yes_m.jpg'),
                                              ('warm', 'f', 'no', 0, 14, '/images/warm_no_f.jpg'),
                                              ('warm', 'f', 'yes', 0, 14, '/images/warm_yes_f.jpg'),
                                              ('hot', 'm', 'no', 15, 29, '/images/hot_no_m.jpg'),
                                              ('hot', 'm', 'yes', 15, 29, '/images/hot_yes_m.jpg'),
                                              ('hot', 'f', 'no', 15, 29, '/images/hot_no_f.jpg'),
                                              ('hot', 'f', 'yes', 15, 29, '/images/hot_yes_f.jpg'),
                                              ('very_hot', 'm', 'no', 29, 50, '/images/very_hot_no_m.jpg'),
                                              ('very_hot', 'm', 'yes', 29, 50, '/images/very_hot_yes_m.jpg'),
                                              ('very_hot', 'f', 'no', 29, 50, '/images/very_hot_no_f.jpg'),
                                              ('very_hot', 'f', 'yes', 29, 50, '/images/very_hot_yes_f.jpg')"""
    cursor.execute(insert_query)
    connection.commit()


def get_data(temp, gender, precipitation):
    # Подключиться к существующей базе данных
    connection = psycopg2.connect(dbname='clothesbase', user="postgres",
                                  password="tedzumi", host='127.0.0.1', port="5432")

    cursor = connection.cursor()
    postgreSQL_select_Query = "select * from weather_clothes WHERE temperature_min <= %s and temperature_max >= %s" \
                              " and gender = %s and precipitation = %s"

    cursor.execute(postgreSQL_select_Query, (temp, temp, gender, precipitation))
    print("Выбор строк из таблицы mobile с помощью cursor.fetchall")
    mobile_records = cursor.fetchall()
    return mobile_records[0][5]
    # print("Вывод каждой строки и ее столбцов")
    # for row in mobile_records:
    #     print("Name =", row[0], )
    #     print("Gender =", row[1])
    #     print("Precipitation =", row[2], "\n")
    #     print("Image =", row[5], "\n")

    cursor.close()
    connection.close()
    print("Соединение с PostgreSQL закрыто")

def precipitation_is(per):
    if per == 2 or 3:
        return 'yes'
    else:
        return 'no'


if __name__ == '__main__':
    temp = int(input("Введите температуру: "))
    gender = input("Введите пол: ")
    precipitation = input("Введите осадки: ")
    get_data(temp, gender, precipitation)
