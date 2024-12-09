import mysql.connector

from invoice_reader.core.database.data_connection import data_connection


class Database():

    def __init__(self) -> None:
        self.connection = mysql.connector.connect(
            user=data_connection['user'],
            password=data_connection['password'],
            host=data_connection['host'],
            port=data_connection['port'],
            database=data_connection['database'],
            connection_timeout=data_connection['connection_timeout'],
            autocommit=data_connection['autocommit']
        )
        self.cursor = self.connection.cursor()

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
