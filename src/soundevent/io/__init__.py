"""The IO module of the soundevent package.

This module contains the classes and functions for reading and writing
sound event data.
"""
from soundevent.io.export import save
from soundevent.io.load import load

__all__ = [
    "save",
    "load",
]
