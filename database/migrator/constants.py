from pathlib import Path


class Constants:
    MIGRATION_TABLE = "migration"
    MIGRATION_SEPARATOR = f"-- {'='*64} --"
    MIGRATION_ZFILL = 3

    MIGRATIONS_DIRECTORY = Path("migrations")
    MIGRATION_TEMPLATE_PATH = Path("database/migrator/templates/new_migration.template")

    INITIAL_MIGRATION_NAME = "initial_migration"
    INITIAL_MIGRATION_TEMPLATE_PATH = Path(f"database/migrator/templates/{INITIAL_MIGRATION_NAME}.template")

    ALPHANUMERIC_PATTERN = r"^[A-Za-z0-9_]+$"
