import os

from .database import Database

db = Database(os.environ["POSTGRES_PASSWORD"])

__all__ = ["Database", "db"]
