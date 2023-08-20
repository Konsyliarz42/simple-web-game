import re
from pathlib import Path

from ..database import Database
from .constants import Constants
from .migration import Migration
from .utils import get_migration_by_id


class Migrator:
    def __init__(
        self,
        database: Database,
        migrations_directory: str | Path = Constants.MIGRATIONS_DIRECTORY,
    ) -> None:
        """
        Simple migration management.
        """
        self.db = database
        self.directory = Path(migrations_directory).absolute()

        if not self.directory.exists():
            raise ValueError("Migrations directory not found")

        if not self.directory.is_dir():
            raise ValueError("Migration directory path is not a directory")

        if not self.get_all_migrations():
            self._create_initial_migration()

    def _create_initial_migration(self) -> None:
        migration = self.create_migration(Constants.INITIAL_MIGRATION_NAME)
        sql = Constants.INITIAL_MIGRATION_TEMPLATE_PATH.read_text("utf-8").format(
            table_name=Constants.MIGRATION_TABLE,
            separator=Constants.MIGRATION_SEPARATOR,
        )
        migration.file_path.write_text(sql, "utf-8")
        self.run_migration(migration.id)

    def _insert_migration(self, migration: Migration) -> None:
        """
        Add row to the migration table.
        """
        sql = "INSERT INTO {table_name}\nVALUES ({migration_id}, '{migration_name}');".format(
            table_name=Constants.MIGRATION_TABLE,
            migration_id=migration.id,
            migration_name=migration.name,
        )
        self.db.execute(sql)

    def _delete_migration(self, migration: Migration) -> None:
        """
        Remove row from the migration table.
        """
        if migration.id == 0:
            return

        sql = "DELETE from {table_name}\nWHERE id={migration_id};".format(
            table_name=Constants.MIGRATION_TABLE,
            migration_id=migration.id,
        )
        self.db.execute(sql)

    def get_applied_migrations(self) -> tuple[Migration, ...]:
        """
        Get all applied migrations.
        """
        sql = "SELECT id, name FROM {table_name}".format(table_name=Constants.MIGRATION_TABLE)
        result = self.db.single_execute(sql)
        migrations = [
            Migration(migration_id, migration_name, self.directory) for migration_id, migration_name in result  # type: ignore
        ]

        return tuple(migrations)

    def get_all_migrations(self) -> tuple[Migration, ...]:
        """
        Get all local migrations.
        """
        migration_files = self.directory.glob("*.sql")
        migrations = []

        for file in migration_files:
            _id, name = file.stem.split("-")
            migrations.append(Migration(int(_id), name, self.directory))

        return tuple(migrations)

    def create_migration(self, migration_name: str) -> Migration:
        """
        Create a new migration from the template.
        """
        if not re.match(re.compile(Constants.ALPHANUMERIC_PATTERN), migration_name):
            raise ValueError("Name of migration must be alphanumeric")

        migrations = self.get_all_migrations()

        if migration_name in [migration.name for migration in migrations]:
            raise ValueError("Migration name must be unique")

        migration_content = Path(Constants.MIGRATION_TEMPLATE_PATH).read_text("utf-8")
        migration_content = migration_content.format(separator=Constants.MIGRATION_SEPARATOR)
        migration_id = len(migrations) if migrations else 0

        migration = Migration(migration_id, migration_name, self.directory)
        migration.file_path.write_text(migration_content, "utf-8")

        return migration

    def run_migration(self, migration_id: int) -> None:
        """
        Apply migration and set migration as applied.
        """
        migrations = self.get_all_migrations()
        migration = get_migration_by_id(migrations, migration_id)

        self.db.connect()
        self.db.execute(migration.up_sql)
        self._insert_migration(migration)
        self.db.commit()
        self.db.close()

    def revert_migration(self, migration_id: int) -> None:
        """
        Revert migration changes and set migration as unapplied.
        """
        migrations = self.get_applied_migrations()
        migration = get_migration_by_id(migrations, migration_id)

        self.db.connect()
        self.db.execute(migration.down_sql)
        self._delete_migration(migration)
        self.db.commit()
        self.db.close()
