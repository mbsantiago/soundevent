"""Operations Module.

This module provides generic operations for manipulating sound event data.
"""

import math
import uuid
from collections.abc import Generator
from typing import Optional

from soundevent import data
from soundevent.constants import uuid_namespace


def segment_clip(
    clip: data.Clip,
    duration: float,
    hop: Optional[float] = None,
    include_incomplete: bool = False,
) -> Generator[data.Clip, None, None]:
    """Segments a clip into smaller clips of a specified duration.

    This function iterates yields segments of a given duration, with a
    specified hop size between segments. It can optionally include the last
    segment even if it is shorter than the specified duration.

    Parameters
    ----------
    clip
        The input audio clip to be segmented.
    duration
        The duration of each segment in seconds.
    hop
        The hop size between segments in seconds. If None (default),
        the hop size is set equal to the duration, resulting in
        non-overlapping segments.
    include_incomplete
        Whether to include the last segment if it is shorter than
        the specified duration. Defaults to False.

    Yields
    ------
    data.Clip
        A segmented clip with a unique UUID, start time, end time,
        and the same recording as the input clip.

    Raises
    ------
    ValueError
        If the duration or hop size is negative or zero.

    Notes
    -----
    If `include_incomplete` is True, the last segment might be shorter
    than the specified duration, as its end time is clamped to the end
    time of the input clip.

    Examples
    --------
    >>> from soundevent import data
    >>> clip = data.Clip(
    ...     start_time=0.0,
    ...     end_time=10.0,
    ...     recording="...",
    ... )
    >>> segments = segment_clip(clip, duration=2.0, hop=1.0)
    >>> for segment in segments:
    ...     print(segment.start_time, segment.end_time)
    0.0 2.0
    1.0 3.0
    2.0 4.0
    3.0 5.0
    4.0 6.0
    5.0 7.0
    6.0 8.0
    7.0 9.0
    8.0 10.0

    """
    if hop is None:
        hop = duration

    if duration <= 0:
        raise ValueError("Duration must be positive.")

    if hop <= 0:
        raise ValueError("Hop size must be positive.")

    num_segments = math.floor(clip.duration / hop)
    for i in range(num_segments):
        start_time = clip.start_time + i * hop
        end_time = start_time + duration

        if start_time >= clip.end_time:
            break

        if end_time > clip.end_time and not include_incomplete:
            break

        end_time = min(end_time, clip.end_time)

        yield data.Clip(
            uuid=uuid.uuid5(
                uuid_namespace,
                f"segment_clip:{clip.uuid}:{start_time}:{end_time}",
            ),
            start_time=start_time,
            end_time=end_time,
            recording=clip.recording,
        )
