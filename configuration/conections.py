import mysql.connector
from mysql.connector import Error

class DatabaseConnection:

    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host 
        self.user = user 
        self.password = password
        self.database = database
        self.mydb = None

    def get_connection(self):
        try:
            if self.mydb is None or not self.mydb.is_connected():
                self.mydb = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                )
            return self.mydb
        except Error as e:
            print("Error al conectar a la base de datos MySQL:", e)
            return None
        
    def get_cursor(self, dictionary=True):
        conn = self.get_connection()
        return conn.cursor(dictionary=dictionary)