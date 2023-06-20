import sqlite3


class Database:
    def __init__(self, path, name):
        self.name = name
        self.path = path
        self.connection = sqlite3.connect(path + name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def execute(self, query):
        try:
            result = self.connection.execute(query)
            self.connection.commit()
            return result
        except sqlite3.Error as e:
            print(e)
            return None

    def executemany(self, query, params):
        try:
            result = self.connection.executemany(query, params)
            self.connection.commit()
            return result
        except sqlite3.Error as e:
            print(e)
            return None

    def executescript(self, query):
        try:
            result = self.connection.executescript(query)
            self.connection.commit()
            return result
        except sqlite3.Error as e:
            print(e)
            return None
