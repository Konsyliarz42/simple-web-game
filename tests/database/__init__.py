from database.migrator import constants as migration_constants
from tests import Constants


class SqlScripts:
    GET_ALL_USERS = "SELECT * FROM user;"
    GET_ALL_TABLES = (
        "SELECT tablename, tableowner "
        "FROM pg_catalog.pg_tables "
        "WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
    )
    GET_ALL_MIGRATION_ROWS = f"SELECT * FROM {migration_constants.MIGRATION_TABLE};"
    CREATE_TEST_TABLE = f"CREATE TABLE {Constants.TEST_TABLE_NAME}(id INTEGER, test_column TEXT);"
    DROP_TEST_TABLE = f"DROP TABLE {Constants.TEST_TABLE_NAME};"
