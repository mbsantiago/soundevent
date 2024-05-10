"""Module for converting between SoundEvent annotations and Crowsetta sequences.

This module facilitates the conversion between sequences of
`SoundEventAnnotation` objects, used within the SoundEvent library, and
`crowsetta.Sequence` objects employed by the Crowsetta tool.
"""

from typing import List, Optional, Sequence

import crowsetta

from soundevent import data
from soundevent.io.crowsetta.segment import (
    segment_from_annotation,
    segment_to_annotation,
)

__all__ = [
    "sequence_from_annotations",
    "sequence_to_annotations",
]


def sequence_from_annotations(
    annotations: Sequence[data.SoundEventAnnotation],
    cast_to_segment: bool = True,
    ignore_errors: bool = False,
    **kwargs,
) -> crowsetta.Sequence:
    """Convert a sequence of soundevent annotations to a Crowsetta sequence.

    This function transforms a sequence of `SoundEventAnnotation` objects into
    a Crowsetta sequence (`crowsetta.Sequence`). Each annotation is
    individually converted into a Crowsetta segment using the
    `to_crowsetta_segment` function.

    Parameters
    ----------
    annotations : Sequence[data.SoundEventAnnotation]
        The sequence of SoundEventAnnotation objects to convert.
    cast_to_segment : bool, optional
        If True, cast the annotations to Crowsetta segments, otherwise, keep
        them as is, by default True.
    ignore_errors : bool, optional
        If True, ignore errors during conversion and continue with the next
        annotation, otherwise this function will raise an error if an
        annotation cannot be converted, by default False.
    **kwargs
        Additional keyword arguments passed to the `to_crowsetta_segment`
        function.

    Returns
    -------
    crowsetta.Sequence
        A Crowsetta sequence representing the converted soundevent annotations.

    Raises
    ------
    ValueError
        If an annotation cannot be converted and `ignore_errors` is False.
    """
    segments = []

    for annotation in annotations:
        try:
            segment = segment_from_annotation(
                annotation,
                cast_to_segment=cast_to_segment,
                **kwargs,
            )
        except ValueError as e:
            if ignore_errors:
                continue

            raise e

        segments.append(segment)

    return crowsetta.Sequence.from_segments(segments)


def sequence_to_annotations(
    sequence: crowsetta.Sequence,
    recording: data.Recording,
    adjust_time_expansion: bool = True,
    created_by: Optional[data.User] = None,
    **kwargs,
) -> List[data.SoundEventAnnotation]:
    """Convert a Crowsetta sequence to a list of soundevent annotations.

    This function transforms a Crowsetta sequence (`crowsetta.Sequence`) into a
    list of `SoundEventAnnotation` objects. Each segment in the Crowsetta
    sequence is individually converted into a soundevent annotation using the
    `to_time_interval_annotation` function.

    Parameters
    ----------
    sequence : crowsetta.Sequence
        The Crowsetta sequence to convert.
    recording : data.Recording
        The original recording associated from which the Crowsetta sequence
        was annotated.
    adjust_time_expansion : bool, optional
        If True, adjust the onset and offset times based on the recording's
        time expansion factor, by default True.
    created_by : data.User, optional
        User information representing the creator of the converted soundevent
        annotations, by default None.
    **kwargs
        Additional keyword arguments passed to the
        `to_time_interval_annotation` function.

    Returns
    -------
    List[data.SoundEventAnnotation]
        A list of soundevent annotations representing the converted Crowsetta
        sequence.
    """
    return [
        segment_to_annotation(
            segment,
            recording,
            adjust_time_expansion=adjust_time_expansion,
            created_by=created_by,
            **kwargs,
        )
        for segment in sequence.segments
    ]
