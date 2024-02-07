"""The IO module of the soundevent package.

This module contains the classes and functions for reading and writing
sound event data.
"""

from soundevent.io.loader import load
from soundevent.io.saver import save
from soundevent.io.types import DataCollections

__all__ = [
    "save",
    "load",
    "DataCollections",
]
