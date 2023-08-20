from pathlib import Path


class Constants:
    POSTGRES_VERSION = "15.4"
    POSTGRES_DATABASE = "testdatabase"
    POSTGRES_PORT = 5433
    POSTGRES_USER = "testuser"
    POSTGRES_PASSWORD = "testpassword"
    MIGRATIONS_DIRECTORY = Path("tests/database/migrations")
    TEST_TABLE_NAME = "testtable"
