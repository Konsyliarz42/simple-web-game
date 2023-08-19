import os

from .constants import Constants

os.environ["POSTGRES_PASSWORD"] = Constants.POSTGRES_PASSWORD

__all__ = ["Constants"]
