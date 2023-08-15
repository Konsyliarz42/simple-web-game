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
        """
        Implementation of the Postgres database.
        """
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self._connection: Optional[psycopg2.connection] = None
        self._cursor: Optional[psycopg2.cursor] = None

    def connect(self) -> None:
        """
        Start the connection to the Postgres database.\n
        Remember to close the connection after executing the scripts!
        """
        self._connection = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self._cursor = self._connection.cursor()

    def close(self) -> None:
        """
        Close connection with the database.
        """
        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None

        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute(self, sql: str) -> Optional[list[tuple[Any, ...]]]:
        """
        Execute the SQL script and return all records if possible.\n
        Remember to start the connection before executing the scripts and commit the changes!
        """
        if not self._connection or not self._cursor:
            raise psycopg2.DatabaseError("You need to start connection before executing SQL script")

        self._cursor.execute(sql)

        if "SELECT" in sql.upper():
            return self._cursor.fetchall()

        return None

    def commit(self) -> None:
        """
        Commit your changes.\n
        Remember to start the connection before committing!
        """
        if not self._connection or not self._cursor:
            raise psycopg2.DatabaseError("You need to start connection before start committing changes")

        self._connection.commit()

    def single_execute(self, sql: str) -> Optional[list[tuple[Any, ...]]]:
        """
        Start connection, execute SQL script, commit changes and close connection.
        """
        self.connect()
        result = self.execute(sql)
        self.commit()
        self.close()

        return result
