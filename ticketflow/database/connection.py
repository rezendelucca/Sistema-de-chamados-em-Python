import os

import psycopg2
from psycopg2.extras import RealDictCursor

# Forca PostgreSQL a enviar mensagens de erro em UTF-8
os.environ.setdefault('PGCLIENTENCODING', 'UTF8')


class DatabaseConnection:
    _instance = None

    def __init__(self):
        self._connection = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseConnection()
        return cls._instance

    def connect(self, host='localhost', database='ticketflow', user='postgres', password='postgres', port=5432):
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )
        return self._connection

    def get_cursor(self):
        return self._connection.cursor(cursor_factory=RealDictCursor)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        if self._connection and not self._connection.closed:
            self._connection.close()
