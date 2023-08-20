from time import sleep

import docker
import pytest
from docker.models.containers import Container
from pytest_factoryboy import register

from database import Database
from database.migrator import Migrator
from factories import MigrationFactory

from . import Constants

register(MigrationFactory)


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

    sleep(3)  # For full initialize container

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

    yield db

    db.close()


@pytest.fixture
def migrator(db: Database) -> Migrator:
    migrator = Migrator(db, Constants.MIGRATIONS_DIRECTORY)

    yield migrator

    MigrationFactory.reset_sequence()

    for migration in Constants.MIGRATIONS_DIRECTORY.glob("*.sql"):
        migration.unlink()
