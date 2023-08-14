MIGRATION_TABLE = "migration"
MIGRATION_SEPARATOR = f"-- {'='*64} --"
MIGRATION_ZFILL = 3

INITIAL_MIGRATION_NAME = "initial_migration"
INITIAL_MIGRATION_TEMPLATE_PATH = f"database/migrator/templates/{INITIAL_MIGRATION_NAME}.template"
MIGRATION_TEMPLATE_PATH = "database/migrator/templates/migration.template"

ALPHANUMERIC_PATTERN = r"^[A-Za-z0-9_]+$"
