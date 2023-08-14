from pathlib import Path

from .constants import (
    INITIAL_MIGRATION_TEMPLATE_PATH,
    MIGRATION_SEPARATOR,
    MIGRATION_TABLE,
)
from .migration import Migration


def get_initial_migration() -> tuple[str, str]:
    sql = Path(INITIAL_MIGRATION_TEMPLATE_PATH).read_text("utf-8")
    sql = sql.format(table_name=MIGRATION_TABLE, separator=MIGRATION_SEPARATOR)
    up, down = sql.split(MIGRATION_SEPARATOR, 1)

    return (up.strip(), down.strip())


def get_migration_by_id(migrations: tuple[Migration, ...] | list[Migration], migration_id: int) -> Migration:
    for migration in migrations:
        if migration.id == migration_id:
            return migration

    raise ValueError("Migration not found")
