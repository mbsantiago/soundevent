"""Storage formats for soundevent objects."""
from soundevent.io.formats.aoef import is_json
from soundevent.io.types import PathLike

__all__ = [
    "infer_format",
]

FORMATS = {
    "aoef": is_json,
}


def infer_format(path: PathLike) -> str:
    """Infer the format of a file.

    Parameters
    ----------
    path : Path
        Path to the file to infer the format of.

    Returns
    -------
    format : str
        The inferred format of the file.

    Raises
    ------
    ValueError
        If the format of the file cannot be inferred.

    """
    for format_, inferrer in FORMATS.items():
        if inferrer(path):
            return format_

    raise ValueError(
        f"Cannot infer format of file {path}, or format not supported."
    )
