from pathlib import Path


class Constants:
    POSTGRES_VERSION = "15.4"
    POSTGRES_DATABASE = "test-database"
    POSTGRES_PORT = 5433
    POSTGRES_USER = "test-user"
    POSTGRES_PASSWORD = "test-password"
    MIGRATIONS_DIRECTORY = Path("tests/database/migrations")
    TEST_TABLE_NAME = "testtable"
