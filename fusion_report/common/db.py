"""Database wrapper"""
import os
import sqlite3

from typing import List

from fusion_report.common.exceptions.db import DbException
from fusion_report.settings import Settings


class Db:
    """The class implements core methods.

    Attributes:
        name: Database name
        schema: Schema defining database structure (sql file)
        database: Database file *.db
        connection: Established connection to the database
    """

    def __init__(self, path: str, name: str, schema: str) -> None:
        self.name: str = name
        self._schema: str = schema
        self.database: str = f'{name.lower()}.db'
        self.connection = self.connect(path, self.database)

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
            self.create_database()

            # import all data files except .sql files
            for file in filter(lambda x: not x.endswith('.sql'), files):
                with open(file, 'r', encoding=encoding) as resource:
                    if skip_header:
                        next(resource)
                    first_line: List[str] = resource.readline().split(delimiter)
                    rows: List[List[str]] = [first_line]
                    for line in resource:
                        row = line.split(delimiter)
                        rows.append(row + ['' for _ in range(len(row), len(first_line))])
                    self.connection.executemany(
                        f'''INSERT INTO {file.split('.')[0].lower()}
                            VALUES ({','.join(['?' for _ in range(0, len(first_line))])})''',
                        rows
                    )
                    self.connection.commit()
        except (IOError, sqlite3.Error) as ex:
            raise DbException(ex)

    def create_database(self):
        """ Build database from schema file."""
        with open(self.schema, 'r', encoding='utf-8') as schema:
            self.connection.executescript(schema.read().lower())

    def select(self, query: str, params: List[str] = None):
        """Select data from table.

        Raises:
            DbException
        """
        try:
            with self.connection as conn:
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
            with self.connection as conn:
                cur = conn.cursor()
                if not params:
                    cur.execute(query)
                else:
                    cur.execute(query, params)
                self.connection.commit()
        except sqlite3.Error as ex:
            raise DbException(ex)

    @property
    def schema(self):
        """Returns database schema."""
        return os.path.join(Settings.ROOT_DIR, f'data/schema/{self._schema}')

    @classmethod
    def __dict_factory(cls, cursor, row):
        """Helper class for converting SQL results into dictionary"""
        tmp_dictionary = {}
        for idx, col in enumerate(cursor.description):
            tmp_dictionary[col[0]] = row[idx]
        return tmp_dictionary
