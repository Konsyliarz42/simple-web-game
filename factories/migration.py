from pathlib import Path

import factory

from database.migrator import Migration
from database.migrator.constants import Constants as MigratorConstants
from tests import Constants as PytestConstants

MIGRATION_TEMPLATE = Path("factories/migration.template").read_text("utf-8")


class MigrationFactory(factory.Factory):
    """
    THIS FACTORY CREATES ALSO MIGRATION FILES!\n
    The default path is defined in tests constants as `MIGRATIONS_DIRECTORY`
    """

    class Meta:
        model = Migration

    id = factory.Sequence(lambda index: index + 1)
    name = factory.LazyAttribute(lambda self: f"fake_migration_{self.id}")
    directory_path = PytestConstants.MIGRATIONS_DIRECTORY.absolute()

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> Migration:
        obj: Migration = super()._create(model_class, *args, **kwargs)

        sql = MIGRATION_TEMPLATE.format(
            id=obj.id,
            separator=MigratorConstants.MIGRATION_SEPARATOR,
        )
        obj.file_path.write_text(sql, "utf-8")

        return obj
