import sqlite3

import config


# create singleton
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DbSqlite(metaclass=Singleton):
    _conn = None

    def __init__(self, db_filename: str):
        self._db_filename = db_filename
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        self._conn = sqlite3.connect(self._db_filename, check_same_thread=False)

    def close(self):
        try:
            self._conn.close()
        except AttributeError:
            pass

    def commit(self):
        self._conn.commit()

    def get_sql_cursor(self, sql: str, commit: bool = False):
        cursor = self._conn.execute(sql)
        if commit:
            self.commit()
        return cursor

    def exec_select(self, sql: str, one_val: bool = False):
        cursor = self._conn.execute(sql)

        if one_val:
            try:
                data = cursor.fetchone()[0]
                return data
            except TypeError:
                return None
        else:
            data = cursor.fetchall()
            return data

    def exec_create(self, sql: str):
        cursor = self._conn.execute(sql)
        self.commit()
        return cursor.rowcount


# create object
db = DbSqlite(config.DB_FILENAME)
