from pathlib import Path

from soundevent.data import PathLike


def is_json(path: PathLike) -> bool:
    """Check if a file is a JSON file."""
    path = Path(path)
    return path.suffix == ".json"
