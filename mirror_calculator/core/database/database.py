import mysql.connector
from mirror_calculator.core.database.database_informations import database_data


class Database():
    def __init__(self) -> None:
        self.connection = mysql.connector.connect(
            user=database_data['USER'],
            password=database_data['PASSWORD'],
            host=database_data['HOST'],
            port=database_data['PORT'],
            database=database_data['NAME'],
            connection_timeout=180,
            autocommit=False
        )
        self.cursor = self.connection.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close
        if self.connection:
            self.connection.close()
