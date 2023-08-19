import argparse
from typing import Optional

from .. import db
from . import Migration, Migrator


def show_migration_list(migrator: Migrator) -> None:
    all_migrations = migrator.get_all_migrations()
    applied_migrations = migrator.get_applied_migrations()

    for migration in all_migrations:
        is_applied = migration in applied_migrations
        print(f" - [{'x' if is_applied else ' '}] - {migration._id_str} | {migration.name}")


def apply_migrations(
    migrator: Migrator,
    to_id: Optional[int] = None,
    all_migrations: Optional[tuple[Migration, ...]] = None,
    applied_migrations: Optional[tuple[Migration, ...]] = None,
) -> None:
    all_migrations = all_migrations or migrator.get_all_migrations()
    applied_migrations = applied_migrations or migrator.get_applied_migrations()
    not_applied_migrations = [migration for migration in all_migrations if migration not in applied_migrations]

    if to_id is None:
        to_id = len(applied_migrations) + 1

    for migration in not_applied_migrations[: to_id + 1]:
        print(f"- {migration._id_str} | {migration.name}")
        migrator.run_migration(migration.id)


def revert_migrations(
    migrator: Migrator,
    to_id: Optional[int] = None,
    applied_migrations: Optional[tuple[Migration, ...]] = None,
) -> None:
    applied_migrations = applied_migrations or migrator.get_applied_migrations()

    if to_id is None:
        to_id = 0

    for migration in reversed(applied_migrations[to_id:]):
        print(f"- {migration._id_str} | {migration.name}")
        migrator.revert_migration(migration.id)


def set_migration(migrator: Migrator, migration_id: int) -> None:
    applied_migrations = migrator.get_applied_migrations()

    if not applied_migrations:
        apply_migrations(migrator, migration_id, applied_migrations=applied_migrations)
        return

    all_migrations = migrator.get_all_migrations()
    last_applied_migration_id = applied_migrations[-1].id

    if migration_id > last_applied_migration_id:
        apply_migrations(migrator, migration_id, all_migrations, applied_migrations)
    elif migration_id == last_applied_migration_id:
        return
    else:
        revert_migrations(migrator, migration_id + 1, applied_migrations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Migrator",
        description="Simple migration management",
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    commands = parser.add_mutually_exclusive_group()
    commands.add_argument("-l", "--list", help="Get list of all migrations", action="store_true")
    commands.add_argument("-c", "--create", help="Create a new migration", type=str)
    commands.add_argument("-r", "--run", help="Apply or revert all to specific migration id", type=int)
    commands.add_argument("-u", "--up", help="Apply all migrations", action="store_true")
    commands.add_argument("-d", "--down", help="Revert all migrations", action="store_true")

    args = parser.parse_args()
    migrator = Migrator(db)

    if args.list:
        show_migration_list(migrator)
    elif args.create:
        migrator.create_migration(args.create)
    elif args.up:
        apply_migrations(migrator)
    elif args.down:
        revert_migrations(migrator)
    elif args.run is not None:
        set_migration(migrator, args.run)
    else:
        parser.print_help()
