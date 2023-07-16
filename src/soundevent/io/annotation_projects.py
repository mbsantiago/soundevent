"""Save and loading functions for annotation projects."""
from pathlib import Path
from typing import Dict, Optional

from soundevent import data
from soundevent.io.formats import aoef, infer_format
from soundevent.io.types import Loader, PathLike, Saver

SAVE_FORMATS: Dict[str, Saver[data.AnnotationProject]] = {}
LOAD_FORMATS: Dict[str, Loader[data.AnnotationProject]] = {}


def load_annotation_project(
    path: PathLike,
    audio_dir: Optional[PathLike] = None,
) -> data.AnnotationProject:
    """Load annotation project from path.

    Parameters
    ----------
    path: PathLike
        Path to the file with the annotation project.

    audio_dir: PathLike, optional
        Path to the directory containing the audio files. If provided, the
        audio file paths in the annotation project will be relative to this
        directory. By default None.

    Returns
    -------
    annotation_project: data.AnnotationProject
        The loaded annotation project.

    Raises
    ------
    FileNotFoundError
        If the path does not exist.

    NotImplementedError
        If the format of the file is not supported.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist.")

    try:
        format_ = infer_format(path)
    except ValueError as e:
        raise NotImplementedError(f"File {path} format not supported.") from e

    loader = LOAD_FORMATS[format_]
    return loader(path, audio_dir=audio_dir)


def save_annotation_project(
    project: data.AnnotationProject,
    path: PathLike,
    audio_dir: Optional[PathLike] = None,
    format: str = "aoef",
) -> None:
    """Save annotation project to path.

    Parameters
    ----------
    project: data.AnnotationProject
        Annotation project to save.

    path: PathLike
        Path to save annotation project to.

    audio_dir: PathLike, optional
        Path to the directory containing the audio files. If provided, the
        audio file paths in the annotation project will be relative to this
        directory. By default None.

    format: str, optional
        Format to save the annotation project in, by default "aoef".

    Raises
    ------
    NotImplementedError
        If the format is not supported.

    """
    path = Path(path)

    try:
        saver = SAVE_FORMATS[format]
    except KeyError as e:
        raise NotImplementedError(f"Format {format} not supported.") from e

    saver(project, path, audio_dir=audio_dir)


def save_annotation_project_in_aoef_format(
    obj: data.AnnotationProject,
    path: PathLike,
    audio_dir: Optional[PathLike] = None,
) -> None:
    """Save annotation project to path in AOEF format."""
    path = Path(path)

    if audio_dir is not None:
        audio_dir = Path(audio_dir).resolve()

    annotation_project_object = (
        aoef.AnnotationProjectObject.from_annotation_project(
            obj,
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
    audio_dir: Optional[PathLike] = None,
) -> data.AnnotationProject:
    """Load annotation project from path in AOEF format."""
    path = Path(path)

    if audio_dir is not None:
        audio_dir = Path(audio_dir).resolve()

    annotation_project_object = (
        aoef.AnnotationProjectObject.model_validate_json(path.read_text())
    )
    return annotation_project_object.to_annotation_project(audio_dir=audio_dir)


SAVE_FORMATS["aoef"] = save_annotation_project_in_aoef_format
LOAD_FORMATS["aoef"] = load_annotation_project_in_aoef_format
