"""Module for accessing local database"""
import os
from pathlib import Path
import sqlite3

class Db:
    """Database wrapper around sqlite3 for summary report"""
    def __init__(self, path=None):
        self.__connection = None
        self.__connections = {}
        self.__dbs = self.__scan_folder(path)

    def __scan_folder(self, path):
        if path is None:
            path = '/script-db'
        
        db_files = []
        if os.path.exists(path):
           db_files = [entry for entry in os.scandir(path) if entry.is_file() and Path(entry).suffix == '.db'] 
        else:
            exit('Defined path doesn\'t exist')

        return db_files

    def connect(self, db_name):
        """
        Wrapper around default connect function
        Args:
            db_file: local database file *.db
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

    def select(self, query, query_params=None):
        """
        Wrapper around default fetch function
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

    def __exit__(self, *args):
        """Close connection on exit"""
        self.connection.close()
