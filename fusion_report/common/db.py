import os
import sqlite3
from typing import List

from fusion_report.common.exceptions.db import DbException


class Db:

    def __init__(self, path: str, name: str, schema: str):
        self.__name: str = name
        self.__schema: str = schema
        self.__database: str = f'{name.lower()}.db'
        self.__connection = self.connect(path, self.__database)

    def connect(self, path: str, database: str):
        try:
            connection = sqlite3.connect(os.path.join(path, database))
            connection.row_factory = self.__dict_factory
            return connection
        except sqlite3.DatabaseError as ex:
            raise DbException(ex)

    def setup(self, files: List[str], delimiter: str = '', skip_header=False, encoding='utf-8'):
        try:
            with open(self.get_schema(), 'r', encoding='utf-8') as schema:
                self.__connection.executescript(schema.read().lower())

            for file in files:
                if not file.endswith('.sql'):
                    with open(file, 'r', encoding=encoding) as resource:
                        if skip_header:
                            next(resource)
                        rows: List[List[str]] = []
                        for line in resource:
                            rows.append(line.split(delimiter))
                        self.__connection.executemany(
                            f'''INSERT INTO {file.split('.')[0].lower()}
                                VALUES ({','.join(['?' for _ in range(0, len(max(rows)))])})''',
                            rows
                        )
                        self.__connection.commit()
        except Exception as ex:
            raise ex

    def select(self, query: str, params: List[str] = None):
        try:
            with self.__connection as conn:
                cur = conn.cursor()
                if not params:
                    cur.execute(query)
                else:
                    cur.execute(query, params)
                res = cur.fetchall()
                cur.close()
                return res
        except sqlite3.OperationalError as ex:
            conn.close()
            raise DbException(ex)

    def execute(self, query: str, params: List[str] = None):
        try:
            with self.__connection as conn:
                cur = conn.cursor()
                if not params:
                    cur.execute(query)
                else:
                    cur.execute(query, params)
                self.__connection.commit()
        except sqlite3.Error as ex:
            conn.close()
            raise DbException(ex)

    def get_name(self):
        return self.__name

    def get_schema(self):
        return f'{os.path.join(os.path.dirname(__file__))}/../data/schema/{self.__schema}'

    def get_database(self):
        return self.__database

    @classmethod
    def __dict_factory(cls, cursor, row):
        """Helper class for converting SQL results into dictionary"""
        tmp_dictionary = {}
        for idx, col in enumerate(cursor.description):
            tmp_dictionary[col[0]] = row[idx]
        return tmp_dictionary
