from os import environ

from .database import Database

# db = Database(environ["POSTGRES_PASSWORD"])
db = Database("postgres")

__all__ = ["Database", "db"]
