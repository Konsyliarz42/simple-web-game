from pathlib import Path

import factory

from database.migrator import Migration, constants
from tests import Constants as TestsConstants


class MigrationFactory(factory.Factory):
    """
    THIS FACTORY CREATES ALSO MIGRATION FILES!\n
    The default path is defined in tests constants as `MIGRATIONS_DIRECTORY`
    """
    class Meta:
        model = Migration
        exclude = ["directory"]

    directory = TestsConstants.MIGRATIONS_DIRECTORY

    id = factory.Sequence(lambda index: index + 1)
    name = factory.LazyAttribute(lambda obj: f"fake_migration_{obj.id}")
    path = factory.LazyAttribute(
        lambda obj: Path(f"{obj.directory}/{str(obj.id).zfill(constants.MIGRATION_ZFILL)}-{obj.name}.sql").absolute()
    )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = super()._create(model_class, *args, **kwargs)

        sql_up = "CREATE TABLE table{id}(\n\tcolumn0 INTEGER NOT NULL,\n\tcolumn1 TEXT NOT NULL UNIQUE\n);".format(id=obj.id)
        sql_down = "DROP TABLE table{id};".format(id=obj.id)
        sql = "{up}\n\n{separator}\n\n{down}\n".format(
            up=sql_up,
            down=sql_down,
            separator=constants.MIGRATION_SEPARATOR,
        )

        obj.path.write_text(sql, "utf-8")

        return obj
