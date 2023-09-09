"""Raw Audio module.

This module contains the RawData class which is a
file-like object that wraps the data buffer of a
WAV file and is meant to replicate the structure
of a RAW audio file.

A RAW audio file is a file that contains only the
contents of the data chunk of a WAV file without
any of the other chunks.

Handling RAW audio files is useful as WAV files
can come with various chunks that are not standard,
such as the Guano metadata chunk. This unexpected
chunks can sometimes cause problems when reading
the WAV file with other libraries and so it is
useful to be able to read only the data chunk of
a WAV file.
"""

import os
from io import BufferedIOBase, RawIOBase
from typing import Optional

from soundevent.audio.chunks import Chunk


class RawData(RawIOBase):
    """A file-like object that wraps a the data buffer of a WAV file.

    This file-like object only contains the data buffer of a WAV without any
    of the other chunks.
    """

    chunk: Chunk
    """The chunk that is being read."""

    initial_position: int
    """The initial position of the file pointer.

    Should point to the start of the data chunk.
    """

    fp: BufferedIOBase
    """The file pointer to the WAV file."""

    size: int
    """The size of the data chunk in bytes."""

    def __init__(self, fp: BufferedIOBase, chunk: Chunk):
        """Initialize a new RawData object."""
        self.chunk = chunk
        self.fp = fp
        self.size = chunk.size

        # Position the file pointer at the start of the data chunk.
        # We add 8 to the position to account for the chunk id and
        # chunk size.
        self.initial_position = chunk.position + 8

        # Position the file pointer at the start of the data chunk.
        self.fp.seek(self.initial_position)

        assert self.fp.tell() == self.initial_position

    def close(self) -> None:
        """Close the file."""
        self.fp.close()

    @property
    def closed(self) -> bool:
        """Return True if the file is closed."""
        return self.fp.closed

    def fileno(self) -> int:
        """Return the file descriptor."""
        return self.fp.fileno()

    def flush(self) -> None:
        """Flush the file."""

    def isatty(self) -> bool:
        """Return True if the file is a tty."""
        return False

    def readable(self) -> bool:
        """Return True if the file is readable."""
        return True

    def seek(self, offset: int, whence: int = os.SEEK_SET, /) -> int:
        """Seek the file pointer."""
        if whence == os.SEEK_SET:
            return self.fp.seek(
                self.initial_position + offset,
                os.SEEK_SET,
            )

        if whence == os.SEEK_END:
            return self.fp.seek(
                self.initial_position + self.size + offset,
                os.SEEK_SET,
            )

        return self.fp.seek(offset, whence)

    def seekable(self) -> bool:
        """Return True if the file is seekable."""
        return True

    def tell(self) -> int:
        """Return the file pointer position."""
        return self.fp.tell() - self.initial_position

    def truncate(self, size: Optional[int] = None, /) -> int:
        """Truncate the file."""
        if size is None:
            size = self.tell()
        return self.fp.truncate(size)

    def writable(self) -> bool:
        """Return True if the file is writable."""
        return False

    def read(self, size: int = -1, /) -> bytes:
        """Read bytes from the file."""
        if size == -1:
            size = self.size - self.tell()
        return self.fp.read(size)

    def readall(self, /) -> bytes:
        """Read all bytes from the file."""
        return self.fp.read(self.size - self.tell())

    def readinto(self, b, /):
        """Read bytes into a buffer."""
        return self.fp.readinto(b)
