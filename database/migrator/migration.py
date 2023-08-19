from dataclasses import dataclass
from pathlib import Path

from .constants import Constants
from .exceptions import MigrationError


@dataclass
class Migration:
    id: int
    name: str
    directory_path: Path

    @property
    def _id(self) -> str:
        return str(self.id).zfill(Constants.MIGRATION_ZFILL)

    @property
    def file_path(self) -> Path:
        return self.directory_path.joinpath(f"{self._id}-{self.name}.sql").absolute()

    @property
    def up_sql(self) -> str:
        sql, _ = self._migration_content()

        return sql.strip()

    @property
    def down_sql(self) -> str:
        _, sql = self._migration_content()

        return sql.strip()

    def _migration_content(self) -> tuple[str, str]:
        file_content = self.file_path.read_text()

        if Constants.MIGRATION_SEPARATOR not in file_content:
            raise MigrationError("Migration file has not required separator")

        up_sql, down_sql = file_content.split(Constants.MIGRATION_SEPARATOR, 1)

        return (up_sql, down_sql)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Migration):
            return NotImplemented

        return self.id == other.id

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Migration):
            return NotImplemented

        return self.id < other.id
