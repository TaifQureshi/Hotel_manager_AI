import mysql.connector as mysql
from typing import List
import os
from dotenv import load_dotenv
load_dotenv(override=True)


class DBConnector(object):
    db_client = None

    def __init__(self) -> None:
        self.connection = mysql.connect(
            host=os.getenv("SQL_HOST", ''),
            user=os.getenv("SQL_USER", ''),
            password=os.getenv("SQL_PASSWORD", ''),
            database=os.getenv("SQL_DB", '')
        )
        self.cursor = self.connection.cursor()

    @staticmethod
    def instance():
        if DBConnector.db_client is None:
            DBConnector.db_client = DBConnector()

        return DBConnector.db_client

    def query(self, sql_query: str) -> List[dict]:
        self.cursor.execute(sql_query)
        result = self.cursor.fetchall()
        return result

    def __dm_query(self, sql_query: str) -> bool:
        try:
            self.cursor.execute(sql_query)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Problem running the query {sql_query} into db: {str(e)}")
        return False

    def insert(self, sql_query: str) -> bool:
        return self.__dm_query(sql_query)

    def delete(self, sql_query: str) -> bool:
        return self.__dm_query(sql_query)

    def update(self, sql_query: str) -> bool:
        return self.__dm_query(sql_query)
