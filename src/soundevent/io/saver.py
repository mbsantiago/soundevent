from typing import Dict, Optional

from soundevent import data
from soundevent.io.aoef import save as aoef_save
from soundevent.io.formats import infer_format
from soundevent.io.types import DataCollections, Saver


def save(
    obj: DataCollections,
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: str = "aoef",
) -> None:
    """Save a data object to a file.

    This function saves a data object to a file in a format that can be loaded
    by the [`load`][soundevent.io.load] function. The following object types
    are supported:

    - [`RecordingSet`][soundevent.data.RecordingSet]
    - [`Dataset`][soundevent.data.Dataset]
    - [`AnnotationSet`][soundevent.data.AnnotationSet]
    - [`AnnotationProject`][soundevent.data.AnnotationProject]
    - [`EvaluationSet`][soundevent.data.EvaluationSet]
    - [`PredictionSet`][soundevent.data.PredictionSet]
    - [`ModelRun`][soundevent.data.ModelRun]
    - [`Evaluation`][soundevent.data.Evaluation]

    Parameters
    ----------
    obj
        The data object to save.
    path
        Path to the file to save to.
    audio_dir
        All path to audio files will be stored relative to this directory.
        This is useful to avoid storing absolute paths which are not portable.
        If `None`, audio paths will be stored as absolute paths.
    format
        Format to save the data in. If `None`, the format will be inferred
        from the file extension.
    """

    if format is None:
        format = infer_format(path)

    saver = SAVERS.get(format)
    if saver is None:
        raise ValueError(f"Unknown format {format}")

    return saver(obj, path, audio_dir)


SAVERS: Dict[str, Saver] = {
    "aoef": aoef_save,
}
