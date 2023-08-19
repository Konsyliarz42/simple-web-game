from database.migrator.constants import Constants as MigratorConstants
from tests import Constants as PytestConstants


class SqlScripts:
    GET_ALL_USERS = "SELECT * FROM user;"
    GET_ALL_TABLES = (
        "SELECT tablename, tableowner "
        "FROM pg_catalog.pg_tables "
        "WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
    )
    GET_ALL_MIGRATION_ROWS = f"SELECT * FROM {MigratorConstants.MIGRATION_TABLE};"
    CREATE_TEST_TABLE = f"CREATE TABLE {PytestConstants.TEST_TABLE_NAME}(id INTEGER, test_column TEXT);"
    DROP_TEST_TABLE = f"DROP TABLE {PytestConstants.TEST_TABLE_NAME};"
