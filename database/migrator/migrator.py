import re
from pathlib import Path

from ..database import Database
from .constants import (
    ALPHANUMERIC_PATTERN,
    INITIAL_MIGRATION_NAME,
    MIGRATION_SEPARATOR,
    MIGRATION_TABLE,
    MIGRATION_TEMPLATE_PATH,
    MIGRATION_ZFILL,
)
from .migration import Migration
from .utils import get_initial_migration, get_migration_by_id


class Migrator:
    def __init__(self, database: Database, migrations_directory: str | Path) -> None:
        self.db = database
        self.directory = Path(migrations_directory)

        if not self.directory.exists():
            raise ValueError("Migrations directory not found")

        if not self.directory.is_dir():
            raise ValueError("Migration directory path is not a directory")

        up_sql, down_sql = get_initial_migration()
        self.db.single_execute(up_sql)

        if not self.get_all_migrations():
            initial_migration = self.create_migration(INITIAL_MIGRATION_NAME)
            initial_migration.path.write_text(f"{up_sql}\n\n{MIGRATION_SEPARATOR}\n\n{down_sql}\n")

    def _insert_migration(self, migration: Migration) -> None:
        sql = "INSERT INTO {table_name}\nVALUES ({migration_id}, '{migration_name}');".format(
            table_name=MIGRATION_TABLE,
            migration_id=migration.id,
            migration_name=migration.name,
        )
        self.db.single_execute(sql)

    def _delete_migration(self, migration: Migration) -> None:
        sql = "DELETE from {table_name}\nWHERE id={migration_id};".format(
            table_name=MIGRATION_TABLE,
            migration_id=migration.id,
        )
        self.db.single_execute(sql)

    def get_applied_migrations(self) -> tuple[Migration, ...]:
        sql = "SELECT id, name FROM {table_name}".format(table_name=MIGRATION_TABLE)
        result = self.db.single_execute(sql)
        migrations = []

        for migration_id, migration_name in result:  # type: ignore
            migration_id_str = str(migration_id).zfill(MIGRATION_ZFILL)
            migration_path = Path(f"{self.directory}/{migration_id_str}-{migration_name}.sql")
            migrations.append(Migration(migration_id, migration_name, migration_path.absolute()))

        return tuple(migrations)

    def get_all_migrations(self) -> tuple[Migration, ...]:
        migration_files = self.directory.glob("*.sql")
        migrations = []

        for file in migration_files:
            _id, name = file.stem.split("-")
            migrations.append(Migration(int(_id), name, file.absolute()))

        return tuple(migrations)

    def create_migration(self, migration_name: str) -> Migration:
        if not re.match(re.compile(ALPHANUMERIC_PATTERN), migration_name):
            raise ValueError("Name of migration must be alphanumeric")

        migrations = self.get_all_migrations()

        if migration_name in [migration.name for migration in migrations]:
            raise ValueError("Migration name must be unique")

        migration_content = Path(MIGRATION_TEMPLATE_PATH).read_text("utf-8")
        migration_content = migration_content.format(separator=MIGRATION_SEPARATOR)
        migration_id = len(migrations) if migrations else 0
        migration_id_str = str(migration_id).zfill(MIGRATION_ZFILL)
        migration_file = Path(f"{self.directory}/{migration_id_str}-{migration_name}.sql").absolute()

        migration_file.write_text(migration_content, "utf-8")

        return Migration(migration_id, migration_name, migration_file)

    def run_migration(self, migration_id: int) -> None:
        migrations = self.get_all_migrations()
        migration = get_migration_by_id(migrations, migration_id)
        self._insert_migration(migration)

    def revert_migration(self, migration_id: int) -> None:
        migrations = self.get_applied_migrations()
        migration = get_migration_by_id(migrations, migration_id)
        self._delete_migration(migration)
