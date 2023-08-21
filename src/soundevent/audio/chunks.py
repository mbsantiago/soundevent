"""Parse a RIFF file into chunks and subchunks.

This module is based on the RIFF specification:
https://www.loc.gov/preservation/digital/formats/fdd/fdd000001.shtml

The RIFF file format is a container format for storing data in tagged chunks.
Each chunk consists of a 4-byte chunk ID, a 4-byte little-endian chunk size,
and the chunk data. The chunk data is padded with a null byte if the chunk
size is odd.

The RIFF file format is used for storing audio and video data. The RIFF file
format is also used for storing other types of data, such as text, images,
and metadata.

"""
import os
from dataclasses import dataclass, field
from typing import BinaryIO, Dict, List, Optional

CHUNKS_WITH_SUBCHUNKS = ["RIFF", "LIST"]

__all__ = [
    "Chunk",
    "parse_into_chunks",
]


@dataclass
class Chunk:
    """A chunk of a RIFF file.

    Parameters
    ----------
    chunk_id : str
        The chunk ID.
    position: int
        The position of the chunk in the file.
    chunk_size : int
        The chunk size.
    subchunks : Dict[Chunk]
        A dictionary holding the subchunks of the chunk.
    """

    chunk_id: str
    size: int
    position: int
    identifier: Optional[str] = None
    subchunks: Dict[str, "Chunk"] = field(default_factory=dict)


def _get_subchunks(riff: BinaryIO, size: int) -> List[Chunk]:
    """Return the subchunks of a RIFF chunk.

    Assume the file pointer is at the beginning of the subchunks.

    Parameters
    ----------
    riff : BinaryIO

    size : int
        The size of the chunk.

    Returns
    -------
    list

    """
    start_position = riff.tell()

    subchunks = []
    while riff.tell() < start_position + size - 1:
        subchunk = _read_chunk(riff)

        if subchunk is None:
            break

        subchunks.append(subchunk)
    return subchunks


def _read_chunk(riff: BinaryIO) -> Optional[Chunk]:
    """Read a chunk from a RIFF file at current pointer position.

    We assume the file pointer is at the beginning of the chunk.

    Parameters
    ----------
    riff : BinaryIO

    Returns
    -------
    Chunk
    """
    position = riff.tell()
    chunk_id = riff.read(4).decode("ascii")
    size = int.from_bytes(riff.read(4), "little")

    if size == 0:
        # Make sure we don't get stuck in an infinite loop.
        return None

    identifier = None
    if chunk_id in CHUNKS_WITH_SUBCHUNKS:
        identifier = riff.read(4).decode("ascii")

    chunk = Chunk(
        chunk_id=chunk_id,
        size=size,
        position=position,
        identifier=identifier,
    )

    if chunk_id in CHUNKS_WITH_SUBCHUNKS:
        chunk.subchunks = {
            subchunk.chunk_id: subchunk
            for subchunk in _get_subchunks(riff, size - 4)
        }
    else:
        riff.seek(size, os.SEEK_CUR)

    return chunk


def parse_into_chunks(riff: BinaryIO) -> Chunk:
    """Return the RIFF file chunk and subchunks.

    Parameters
    ----------
    riff : BinaryIO
        Open file object of the RIFF file.

    Returns
    -------
    Chunk

    Raises
    ------
    ValueError
        If the RIFF file is empty.
    """
    riff.seek(0)
    chunk = _read_chunk(riff)

    if chunk is None:
        raise ValueError("RIFF file is empty")

    return chunk
