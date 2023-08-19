import psycopg2
import pytest
from docker.models.containers import Container

from database import Database

from ..constants import Constants
from . import SqlScripts


def test_database_connection(db: Database) -> None:
    db.connect()

    assert db._connection is not None
    assert db._cursor is not None


@pytest.mark.parametrize(
    ["key", "value"],
    [
        ("database", "fake-database"),
        ("host", "fake-host"),
        ("port", 1000),
        ("user", "fake-user"),
        ("password", "fake-password"),
    ],
)
def test_database_connection_with_wrong_parameters(
    postgres: Container,
    key: str,
    value: str | int,
) -> None:
    db_env = {"password": Constants.POSTGRES_PASSWORD}
    db_env[key] = value
    db = Database(**db_env)

    with pytest.raises(psycopg2.OperationalError):
        db.connect()


def test_database_close_connection(db: Database) -> None:
    db.connect()

    db.close()

    assert db._connection is None
    assert db._cursor is None


def test_execute(db: Database) -> None:
    db.connect()

    result = db.execute(SqlScripts.GET_ALL_USERS)

    assert result == [(db.user,)]


def test_execute_without_connection() -> None:
    db = Database("fake-password")

    with pytest.raises(
        psycopg2.DatabaseError,
        match="You need to start connection before executing SQL script",
    ):
        db.execute(SqlScripts.GET_ALL_USERS)


def test_commit(db: Database) -> None:
    db.connect()
    db.execute(SqlScripts.CREATE_TEST_TABLE)

    db.commit()

    result = db.execute(SqlScripts.GET_ALL_TABLES)
    assert result == [(Constants.TEST_TABLE_NAME, db.user)]


def test_commit_changes_without_connection() -> None:
    db = Database("fake-password")

    with pytest.raises(
        psycopg2.DatabaseError,
        match="You need to start connection before start committing changes",
    ):
        db.commit()


def test_single_execute(db: Database) -> None:
    db.single_execute(SqlScripts.CREATE_TEST_TABLE)

    db.connect()
    result = db.execute(SqlScripts.GET_ALL_TABLES)
    assert result == [(Constants.TEST_TABLE_NAME, db.user)]
