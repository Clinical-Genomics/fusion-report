"""Database wrapper"""

import os
import sqlite3
from typing import List

from fusion_report.common.exceptions.db import DbException


class Db:
    """The class implements core methods.

    Attributes:
        __path: Path to databases
        __name: Database name
        __schema: Schema defining database structure (sql file)
        __database: Database file *.db
        __connection: Established connection to the database
    """
    def __init__(self, path: str, name: str, schema: str) -> None:
        self.__name: str = name
        self.__schema: str = schema
        self.__database: str = f'{name.lower()}.db'
        self.__connection = self.connect(path, self.__database)

    def connect(self, path: str, database: str):
        """Method for establishing connection to the database.

        Returns:
            connection object

        Raises:
            DbException
        """
        try:
            connection = sqlite3.connect(os.path.join(path, database))
            connection.row_factory = self.__dict_factory
            return connection
        except sqlite3.DatabaseError as ex:
            raise DbException(ex)

    def setup(self, files: List[str], delimiter: str = '',
              skip_header=False, encoding='utf-8') -> None:
        """Sets up database. For most databases there is available schema and text files which
           contain all the data. This methods builds database using it's schema and imports
           all provided data files.

            Args:
                files: all necessary files required to be imported
                delimiter: separator used in data files
                skip_header: ignore header when importing files, default: False
                encoding: data file encoding, some files are not using utf-8 as default (Mitelman)

            Raises:
                DbException
        """
        try:
            # build database schema
            with open(self.get_schema(), 'r', encoding='utf-8') as schema:
                self.__connection.executescript(schema.read().lower())

            # import all data files
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
        except (IOError, sqlite3.Error) as ex:
            raise DbException(ex)

    def select(self, query: str, params: List[str] = None):
        """Select data from table.

        Raises:
            DbException
        """
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
            raise DbException(ex)

    def execute(self, query: str, params: List[str] = None):
        """Execute SQL statement. Can be anything like INSERT/UPDATE/DELETE ...

        Raises:
            DbException
        """
        try:
            with self.__connection as conn:
                cur = conn.cursor()
                if not params:
                    cur.execute(query)
                else:
                    cur.execute(query, params)
                self.__connection.commit()
        except sqlite3.Error as ex:
            raise DbException(ex)

    def get_name(self):
        """Returns database name."""
        return self.__name

    def get_schema(self):
        """Returns database schema."""
        return f'{os.path.join(os.path.dirname(__file__))}/../data/schema/{self.__schema}'

    def get_database(self):
        """Returns database file."""
        return self.__database

    @classmethod
    def __dict_factory(cls, cursor, row):
        """Helper class for converting SQL results into dictionary"""
        tmp_dictionary = {}
        for idx, col in enumerate(cursor.description):
            tmp_dictionary[col[0]] = row[idx]
        return tmp_dictionary
