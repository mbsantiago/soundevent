"""The IO module of the soundevent package.

This module contains the classes and functions for reading and writing
sound event data.
"""

from soundevent.io.datasets import load_dataset, save_dataset


__all__ = [
    "load_dataset",
    "save_dataset",
]
