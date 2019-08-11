import sqlite3
import os
from pathlib import Path
from os import DirEntry, scandir
from typing import Any, Dict, List
from fusion_report.common.exceptions.db import DbException


class Db:

    def connect(self, path: str, database: str):
        try:
            connection = sqlite3.connect(os.path.join(path, database))
            connection.row_factory = self.__dict_factory
            return connection
        except sqlite3.DatabaseError as ex:
            raise DbException(ex)

    @staticmethod
    def _select(connection, query, query_params=None):
        try:
            with connection as conn:
                cur = conn.cursor()
                if not query_params:
                    cur.execute(query)
                else:
                    cur.execute(query, query_params)
                res = cur.fetchall()
                cur.close()
                return res
        except sqlite3.OperationalError as ex:
            conn.close()
            raise DbException(ex)

    @staticmethod
    def _execute(connection, statement):
        try:
            with connection as conn:
                cur = conn.cursor()
                cur.execute(statement)
        except sqlite3.Error as ex:
            conn.close()
            raise DbException(ex)

    @classmethod
    def __dict_factory(cls, cursor, row):
        """Helper class for converting SQL results into dictionary"""
        tmp_dictionary = {}
        for idx, col in enumerate(cursor.description):
            tmp_dictionary[col[0]] = row[idx]
        return tmp_dictionary
