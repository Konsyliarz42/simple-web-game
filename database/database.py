from typing import Any, Optional

import psycopg2


class Database:
    def __init__(
        self,
        password: str,
        database: str = "postgres",
        user: str = "postgres",
        host: str = "localhost",
        port: int = 5432,
    ) -> None:
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection: Optional[psycopg2.connection] = None
        self.cursor: Optional[psycopg2.cursor] = None

    def connect(self) -> None:
        self.connection = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self.cursor = self.connection.cursor()

    def close(self) -> None:
        self.cursor.close()
        self.cursor = None

        self.connection.close()
        self.connection = None

    def execute(self, sql: str) -> Optional[list[tuple[Any, ...]]]:
        if not self.connection or not self.cursor:
            raise psycopg2.DatabaseError(
                "You need to start connection before executing SQL script"
            )

        self.cursor.execute(sql)

        if "SELECT" in sql.upper():
            return self.cursor.fetchall()
        
    def commit(self) -> None:
        self.connection.commit()

    def single_execute(self, sql: str) -> Optional[list[tuple[Any, ...]]]:
        self.connect()
        result = self.execute(sql)
        self.commit()
        self.close()

        return result
