"""Save and loading functions for annotation projects."""

import os
import sys
from pathlib import Path
from typing import Callable, Dict, Union

from soundevent import data
from soundevent.io.format import AnnotationProjectObject, is_json

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol


PathLike = Union[str, os.PathLike]


class Saver(Protocol):
    """Protocol for saving annotation projects."""

    def __call__(
        self,
        project: data.AnnotationProject,
        path: PathLike,
        audio_dir: PathLike = ".",
    ) -> None:
        """Save annotation project to path."""
        ...


class Loader(Protocol):
    """Protocol for loading annotation projects."""

    def __call__(
        self, path: PathLike, audio_dir: PathLike = "."
    ) -> data.AnnotationProject:
        """Load annotation project from path."""
        ...


SAVE_FORMATS: Dict[str, Saver] = {}
LOAD_FORMATS: Dict[str, Loader] = {}
FORMATS: Dict[str, Callable[[PathLike], bool]] = {}


def load_annotation_project(path: PathLike) -> data.AnnotationProject:
    """Load annotation project from path."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist.")

    for format_name, is_format in FORMATS.items():
        if not is_format(path):
            continue

        return LOAD_FORMATS[format_name](path)

    raise NotImplementedError(
        f"Could not find a loader for {path}. "
        f"Supported formats are: {list(FORMATS.keys())}"
    )


def save_annotation_project(
    project: data.AnnotationProject,
    path: PathLike,
    audio_dir: PathLike = ".",
) -> None:
    """Save annotation project to path.

    Parameters
    ----------
    project: data.AnnotationProject
        Annotation project to save.
    path: PathLike
        Path to save annotation project to.
    """
    path = Path(path)

    for format_name, is_format in FORMATS.items():
        if not is_format(path):
            continue

        SAVE_FORMATS[format_name](project, path, audio_dir=audio_dir)
        return

    raise NotImplementedError(
        f"Could not find a saver for {path}. "
        f"Supported formats are: {list(FORMATS.keys())}"
    )


def save_annotation_project_in_aoef_format(
    project: data.AnnotationProject,
    path: PathLike,
    audio_dir: PathLike = ".",
) -> None:
    """Save annotation project to path in AOEF format."""
    path = Path(path)
    audio_dir = Path(audio_dir).resolve()
    annotation_project_object = (
        AnnotationProjectObject.from_annotation_project(
            project,
            audio_dir=audio_dir,
        )
    )
    path.write_text(
        annotation_project_object.model_dump_json(
            indent=None,
            exclude_none=True,
        )
    )


def load_annotation_project_in_aoef_format(
    path: PathLike,
    audio_dir: PathLike = ".",
) -> data.AnnotationProject:
    """Load annotation project from path in AOEF format."""
    path = Path(path)
    audio_dir = Path(audio_dir).resolve()
    annotation_project_object = AnnotationProjectObject.validate_json(
        path.read_text()
    )
    return annotation_project_object.to_annotation_project(audio_dir=audio_dir)


SAVE_FORMATS["aoef"] = save_annotation_project_in_aoef_format
LOAD_FORMATS["aoef"] = load_annotation_project_in_aoef_format
FORMATS["aoef"] = is_json
