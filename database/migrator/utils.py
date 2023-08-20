from typing import Optional

from .migration import Migration


def get_migration_by_id(
    migrations: tuple[Migration, ...] | list[Migration],
    migration_id: int,
) -> Migration:
    for migration in migrations:
        if migration.id == migration_id:
            return migration

    raise ValueError("Migration not found")


def get_migrations_to_apply(
    all_migrations: tuple[Migration, ...],
    applied_migrations: tuple[Migration, ...],
    to_id: Optional[int] = None,
) -> list[Migration]:
    not_applied_migrations = [migration for migration in all_migrations if migration not in applied_migrations]
    _to_id = to_id if to_id is not None else len(not_applied_migrations) + 1

    return not_applied_migrations[: _to_id + 1]


def get_migrations_to_revert(
    applied_migrations: tuple[Migration, ...],
    to_id: Optional[int] = None,
) -> list[Migration]:
    _to_id = to_id or 0
    migrations = list(applied_migrations[_to_id:])
    migrations.reverse()

    return migrations
