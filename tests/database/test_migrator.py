from datetime import datetime
from pathlib import Path

import pytest

from database import Database
from database.migrator import Migration, Migrator
from database.migrator import constants as migration_constants
from factories import MigrationFactory
from tests import Constants

from . import SqlScripts


def _round_datetime(dt: datetime) -> datetime:
    return dt.replace(microsecond=0)


def test_migrator_init(db: Database) -> None:
    migration_id = str(0).zfill(migration_constants.MIGRATION_ZFILL)
    migration_file = f"{migration_id}-{migration_constants.INITIAL_MIGRATION_NAME}.sql"

    Migrator(db, Constants.MIGRATIONS_DIRECTORY)

    assert Path(f"{Constants.MIGRATIONS_DIRECTORY}/{migration_file}").exists()

    result = db.single_execute(SqlScripts.GET_ALL_TABLES)
    assert result == [(migration_constants.MIGRATION_TABLE, Constants.POSTGRES_USER)]


def test_migrator_create_migration(migrator: Migrator) -> None:
    migration_name = "test_migration"

    migration = migrator.create_migration(migration_name)

    assert migration.id == 1
    assert migration.name == migration_name
    assert migration.path.exists()


def test_migrator_create_migration_indexes(migrator: Migrator) -> None:
    base_migration_name = "test_migration"

    for index in range(1, 3):
        migration = migrator.create_migration(f"{base_migration_name}_{index}")

        assert migration.id == index
        assert str(index).zfill(migration_constants.MIGRATION_ZFILL) in migration.path.name


@pytest.mark.parametrize(
    "migration_name",
    [
        "test-migration",
        "test migration",
        "test@migration",
    ],
)
def test_migrator_create_migration_with_not_alphanumeric_name(
    migrator: Migrator,
    migration_name: str,
) -> None:
    with pytest.raises(ValueError) as error:
        migrator.create_migration(migration_name)

    assert str(error.value) == "Name of migration must be alphanumeric"


def test_migrator_create_migration_with_not_unique_name(migrator: Migrator) -> None:
    with pytest.raises(ValueError) as error:
        migrator.create_migration(migration_constants.INITIAL_MIGRATION_NAME)

    assert str(error.value) == "Migration name must be unique"


def test_migrator_run_migration(
    db: Database,
    migrator: Migrator,
    migration_factory: MigrationFactory,
) -> None:
    current_utc_time = datetime.utcnow()
    migration: Migration = migration_factory.create()

    migrator.run_migration(migration.id)

    result = db.single_execute(SqlScripts.GET_ALL_TABLES)
    assert result == [
        (migration_constants.MIGRATION_TABLE, Constants.POSTGRES_USER),
        (f"table{migration.id}", Constants.POSTGRES_USER),
    ]

    result = db.single_execute(SqlScripts.GET_ALL_MIGRATION_ROWS)
    assert len(result) == 1

    migration_id, migration_name, applied_at = result[0]
    assert migration_id == migration.id
    assert migration_name == migration.name
    assert _round_datetime(applied_at) == _round_datetime(current_utc_time)


def test_migrator_run_migration_with_wrong_id(migrator: Migrator) -> None:
    with pytest.raises(ValueError, match="Migration not found"):
        migrator.run_migration(1)


def test_migrator_revert_migration(
    db: Database,
    migrator: Migrator,
    migration_factory: MigrationFactory,
) -> None:
    migration: Migration = migration_factory.create()
    migrator.run_migration(migration.id)

    migrator.revert_migration(migration.id)

    result = db.single_execute(SqlScripts.GET_ALL_TABLES)
    assert result == [(migration_constants.MIGRATION_TABLE, Constants.POSTGRES_USER)]

    result = db.single_execute(SqlScripts.GET_ALL_MIGRATION_ROWS)
    assert len(result) == 0


def test_migrator_revert_migration_with_wrong_id(migrator: Migrator) -> None:
    with pytest.raises(ValueError, match="Migration not found"):
        migrator.revert_migration(1)


def test_migrator_get_all_migrations(
    migrator: Migrator,
    migration_factory: MigrationFactory,
) -> None:
    migration_factory.create_batch(4)
    migration_files = Path(Constants.MIGRATIONS_DIRECTORY).glob("*.sql")

    all_migrations = migrator.get_all_migrations()

    for _migration, file in zip(all_migrations, migration_files):
        assert _migration.path == file.absolute()


def test_migrator_get_all_applied_migrations(
    migrator: Migrator,
    migration_factory: MigrationFactory,
) -> None:
    migration_factory.create_batch(4)
    migration_files = Path(Constants.MIGRATIONS_DIRECTORY).glob("*.sql")

    applied_migrations = migrator.get_applied_migrations()

    assert len(list(migration_files)) > len(applied_migrations)
