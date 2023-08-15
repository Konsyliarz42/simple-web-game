from dataclasses import dataclass
from pathlib import Path

from .constants import MIGRATION_SEPARATOR
from .exceptions import MigrationError


@dataclass
class Migration:
    id: int
    name: str
    path: Path

    @property
    def up_sql(self) -> str:
        sql, _ = self._migration_content()

        return sql.strip()

    @property
    def down_sql(self) -> str:
        _, sql = self._migration_content()

        return sql.strip()

    def _migration_content(self) -> tuple[str, str]:
        file_content = self.path.read_text()

        if MIGRATION_SEPARATOR not in file_content:
            raise MigrationError("Migration file has not required separator")

        up_sql, down_sql = file_content.split(MIGRATION_SEPARATOR, 1)

        return (up_sql, down_sql)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Migration):
            return NotImplemented

        return self.id == other.id

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Migration):
            return NotImplemented

        return self.id < other.id
