"""Data transformations for soundevent objects.

This module provides a framework for applying transformations to soundevent data
objects. The core of the framework is the `TransformBase` class, which defines
a visitor pattern for traversing the complex hierarchy of soundevent data
models.

The module also includes concrete transform classes for common data
manipulation tasks, such as modifying recording paths (`PathTransform`) or
transforming tags (`TagsTransform`).

These tools are designed to help users clean, modify, and standardize their
bioacoustic datasets in a structured and reliable way.
"""

from soundevent.transforms.base import TransformBase
from soundevent.transforms.path import PathTransform
from soundevent.transforms.tags import TagsTransform

__all__ = [
    "PathTransform",
    "TagsTransform",
    "TransformBase",
]
