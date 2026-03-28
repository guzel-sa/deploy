
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

class PGDatabase:
    def __init__(self, host, database, user, password):
        """Инициализация подключения к базе данных"""
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
        self.cursor = self.connection.cursor()
        self.connection.autocommit = True
       
         
    def post(self, query, args=None):
        """Выполняет SQL запрос (INSERT, UPDATE, DELETE)"""
        try:
            if args:
                self.cursor.execute(query, args)
            else:
                self.cursor.execute(query)
            return True
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            return False