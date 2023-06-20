# Инициализируем библиотеки
from io import open
from threading import Thread
from requests import request
from sqlite import Database

# Инициализируем пути и имена
db_path = 'db/'
db_name = 'Tinkoff.sqlite'
db = Database(db_path, db_name)

# Инициализируем запросы
sql_select_sleep = 'SELECT msec FROM sleep'
sql_select_time = 'SELECT time FROM time_current'
sql_select_links = 'SELECT route_id, urn_id, url, method, security, headers, body FROM requests_on_timer'
sql_insert_response = 'INSERT OR IGNORE INTO response(route_id, urn_id, time, code, header, body) VALUES(?,?,?,?,?,?)'

# Функция для работы с файлами
def readfile(path, filename, codepage):
    with open(path + filename, encoding=codepage) as file:
        return file.read()

# Инициализируем базу
try:
    file_sql = readfile('db/', 'sdk.sql', 'ANSI')
    db.executescript(file_sql)
except IOError:
    print('file: sdk.sql has a problem')

# Инициализируем параметры базы
try:
    file_json = readfile('db/', 'input.json', 'utf-8')
    query = f"UPDATE m_input SET value = json('{file_json}') WHERE name = 'inputJson'"
    db.executescript(query)
except IOError:
    print('file: input.json has a problem')

class Program:
    # Функция проверки активности потоков
    def _threads_check(self, threads):
        for item in threads:
            if item.isAlive():
                return True
        return False
    
    # Основная функция программы
    def execute(self):
        responses = []
        # Получаем текущее время от БД
        time = db.execute(sql_select_time).fetchone()[0]
        # Получаем запросы, которые нужно выполнить от БД
        for item in db.execute(sql_select_links):
            # Инициализируем запросы по потокам
            response = Response(
                item[0], 
                item[1], 
                item[2], 
                item[3], 
                item[4], 
                item[5], 
                item[6],
                time,
                responses)
            responses.append(response)

        # Запускаем потоки
        for item in responses:
            item.execute()

        # Ждем завершения всех потоков
        for item in responses:
            item.join()

        # Записываем результат выполнения запросов в БД
        db.executeMany(sql_insert_response, responses)
        # Обновляем список результатов запросов
        responses[:] = []

# Создаем класс запросов-ответов, наследуемся от потоков
class Response(Thread):
    def __init__(self, route_id, urn_id, url, method, security, headers, body, time, responses):
        super().__init__()
        self.url = url
        self.route_id = route_id
        self.urn_id = urn_id
        self.time = time
        self.method = method
        self.security = security
        self.headers = headers
        self.body = body
        self.name = f'Thread: {route_id}{urn_id}'
        self.responses = responses

    # Выполнение потока
    def execute(self):
        if self.headers != '':
            # Формируем заголовки для запросов
            self.headers = dict(header.split(':') for header in self.headers.split('rn'))
            # Выполняем запрос с заголовками
            maindata = request(
                self.method, 
                self.url, 
                headers=self.headers, 
                data=self.body)
        else:
            # Выполняем запрос без заголовков
            maindata = request(self.method, self.url)

        # Формируем данные для БД
        self.responses.append([
            self.route_id, 
            self.urn_id, 
            self.time, 
            maindata.status_code, 
            repr(maindata.headers), 
            repr(maindata.text)])
        print(f'[{maindata.status_code}] {self.url}')