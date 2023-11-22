from typing import Dict, Optional

from soundevent import data
from soundevent.io.aoef import save as aoef_save
from soundevent.io.formats import infer_format
from soundevent.io.types import DataObject, Saver


def save(
    obj: DataObject,
    path: data.PathLike,
    audio_dir: Optional[data.PathLike] = None,
    format: str = "aoef",
) -> None:
    """Save a dataset from a file."""
    if format is None:
        format = infer_format(path)

    saver = SAVERS.get(format)
    if saver is None:
        raise ValueError(f"Unknown format {format}")

    return saver(obj, path, audio_dir)


SAVERS: Dict[str, Saver] = {
    "aoef": aoef_save,
}
