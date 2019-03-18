"""Module for accessing local database"""
import os
from pathlib import Path
import sqlite3

class Db:
    """Database wrapper around sqlite3 for summary report"""
    def __init__(self, path=None):
        self.__connection = None
        self.__connections = {}
        self.__dbs = self.scan_folder(path)

    def connect(self, db_name):
        """
        Wrapper around default connect function, sets connections.

        Args:
            db_name: name of the database file
        """
        try:
            if db_name in self.__connections:
                self.__connection = self.__connections[db_name]
            else:
                db_file = [db_file for db_file in self.__dbs if db_file.name == f'{db_name}.db'][0]
                connection = sqlite3.connect(db_file.path)
                connection.row_factory = self.__dict_factory
                self.__connections[db_file.name] = connection
                self.__connection = connection
        except sqlite3.Error as error:
            exit(error)

    def get_db_names(self):
        """Return all filename databases."""
        return [x.name.split('.')[0] for x in self.__dbs]

    def select(self, query, query_params=None):
        """
        Wrapper around default fetch function.

        Args:
            query (string): SQL statement
            query_params (list): list of all parameters, SQL statement should be sanitized
        """
        try:
            cur = self.__connection.cursor()
            if query_params is None:
                cur.execute(query)
            else:
                cur.execute(query, query_params)
            res = cur.fetchall()
            cur.close()
            return res
        except sqlite3.Error as error:
            exit(error)

    @classmethod
    def __dict_factory(cls, cursor, row):
        """Helper class for converting SQL results into dictionary"""
        tmp_dictionary = {}
        for idx, col in enumerate(cursor.description):
            tmp_dictionary[col[0]] = row[idx]
        return tmp_dictionary

    @staticmethod
    def scan_folder(path=None, extension='.db'):
        """
        Function scans defined path and searches for files with an extention ".db". If path is not
        defined search in a path /script-db.

        Args:
            path (str): Path
        Returns:
            list: List of all found database files
        """
        if path is None:
            path = '/script-db'

        db_files = []
        if os.path.exists(path):
            db_files = [entry for entry in os.scandir(path)
                        if entry.is_file() and Path(entry).suffix == extension]
        else:
            exit('Defined path doesn\'t exist')

        return db_files

    def __exit__(self, *args):
        """Close all open connections on exit"""
        for _, con in self.__connections.items():
            con.close()
        self.__connection.close()
