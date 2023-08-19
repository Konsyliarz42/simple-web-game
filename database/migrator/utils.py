from pathlib import Path

from .constants import Constants
from .migration import Migration


def get_initial_migration() -> tuple[str, str]:
    sql = Path(Constants.INITIAL_MIGRATION_TEMPLATE_PATH).read_text("utf-8")
    sql = sql.format(
        table_name=Constants.MIGRATION_TABLE,
        separator=Constants.MIGRATION_SEPARATOR,
    )
    up, down = sql.split(Constants.MIGRATION_SEPARATOR, 1)

    return (up.strip(), down.strip())


def get_migration_by_id(
    migrations: tuple[Migration, ...] | list[Migration],
    migration_id: int,
) -> Migration:
    for migration in migrations:
        if migration.id == migration_id:
            return migration

    raise ValueError("Migration not found")
