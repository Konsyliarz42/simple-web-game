from pathlib import Path
from time import sleep

import docker
import pytest
from docker.models.containers import Container

from database import Database, Migration, Migrator
from database.migrator import constants as migration_constants

from . import Constants
from .database import SqlScripts


@pytest.fixture
def postgres() -> Container:
    client = docker.DockerClient()
    container_env = {
        "POSTGRES_DB": Constants.POSTGRES_DATABASE,
        "POSTGRES_PORT": Constants.POSTGRES_PORT,
        "POSTGRES_USER": Constants.POSTGRES_USER,
        "POSTGRES_PASSWORD": Constants.POSTGRES_PASSWORD,
    }
    container: Container = client.containers.run(
        image=f"postgres:{Constants.POSTGRES_VERSION}",
        environment=container_env,
        ports={"5432/tcp": container_env["POSTGRES_PORT"]},
        name="pytest-db",
        detach=True,
    )

    sleep(2)  # For full initialize container

    yield container

    container.stop()
    container.remove()


@pytest.fixture
def db(postgres: Container) -> Database:
    db_env = {
        "database": Constants.POSTGRES_DATABASE,
        "port": Constants.POSTGRES_PORT,
        "user": Constants.POSTGRES_USER,
        "password": Constants.POSTGRES_PASSWORD,
    }
    db = Database(**db_env)

    return db


@pytest.fixture
def migrator(db: Database) -> Migrator:
    migrator = Migrator(db, Constants.MIGRATIONS_DIRECTORY)

    return migrator


@pytest.fixture(autouse=True)
def remove_migration_files() -> None:
    yield None

    migrations = Constants.MIGRATIONS_DIRECTORY.glob("*.sql")

    for migration in migrations:
        migration.unlink()


@pytest.fixture
def migration() -> Migration:
    migration_id = 1
    migration_id_str = str(migration_id).zfill(migration_constants.MIGRATION_ZFILL)
    migration_name = "fake_migration_0"
    migration_path = Path(f"{Constants.MIGRATIONS_DIRECTORY}/{migration_id_str}-{migration_name}.sql")

    migration_content = (
        f"{SqlScripts.CREATE_TEST_TABLE}\n"
        f"\n{migration_constants.MIGRATION_SEPARATOR}\n"
        f"\n{SqlScripts.DROP_TEST_TABLE}\n"
    )
    migration_path.write_text(migration_content, "utf-8")

    return Migration(migration_id, migration_name, migration_path)
