"""Module for converting between SoundEvent annotations and Crowsetta bounding boxes.

This module provides functions to seamlessly convert between
`SoundEventAnnotation` objects, containing sound event information with
bounding box geometries, and `crowsetta.BBox` objects used by the Crowsetta
tool.
"""

from typing import List, Optional, Tuple

from crowsetta import BBox

from soundevent import data
from soundevent.geometry import compute_bounds
from soundevent.io.crowsetta.labels import label_from_tags, label_to_tags

__all__ = [
    "bbox_from_annotation",
    "bbox_to_annotation",
]


def convert_geometry_to_bbox(
    geometry: data.Geometry,
    cast_to_bbox: bool = True,
    raise_on_time_geometries: bool = False,
) -> Tuple[float, float, float, float]:
    if geometry.type != "BoundingBox" and not cast_to_bbox:
        raise ValueError(
            "Cannot convert to a crowsetta bbox "
            "because the sound event geometry is not a BoundingBox."
        )

    if (
        geometry.type in ["TimeInterval", "TimeStamp"]
        and raise_on_time_geometries
    ):
        raise ValueError(
            "Cannot convert to a crowsetta bbox because "
            "the sound event geometry is a TimeInterval or TimeStamp "
            "and does not have frequency information."
        )

    return compute_bounds(geometry)


def bbox_from_annotation(
    obj: data.SoundEventAnnotation,
    cast_to_bbox: bool = True,
    raise_on_time_geometries: bool = True,
    **kwargs,
) -> BBox:
    """Convert a soundevent annotation to a Crowsetta bounding box.

    This function transforms a SoundEventAnnotation object into a Crowsetta
    bounding box (`BBox`). The SoundEvent's geometry is used to determine the
    onset, offset, low frequency, and high frequency values of the bounding box,
    and the associated tags are converted into a Crowsetta label using the
    `convert_tags_to_label` function.

    Parameters
    ----------
    obj : data.SoundEventAnnotation
        The SoundEventAnnotation object to convert.
    cast_to_bbox : bool, optional
        If True, cast the geometry to a bounding box, otherwise, keep it as is,
        by default True.
    raise_on_time_geometries : bool, optional
        If True, raise an exception if the geometry is a TimeInterval or
        TimeStamp, otherwise, cast it to a bounding box with a lowest frequency
        of 0 and a highest frequency of the recording's Nyquist frequency. By
        default True.
    **kwargs
        Additional keyword arguments passed to the `convert_tags_to_label`
        function.

    Returns
    -------
    BBox
        A Crowsetta bounding box representing the converted soundevent
        annotation, with onset, offset, low frequency, high frequency, and
        associated label.
    """
    sound_event = obj.sound_event
    geometry = sound_event.geometry

    if geometry is None:
        raise ValueError(
            "Cannot convert to a crowsetta bbox because the sound event "
            "has no geometry."
        )

    start_time, low_freq, end_time, high_freq = convert_geometry_to_bbox(
        geometry,
        cast_to_bbox=cast_to_bbox,
        raise_on_time_geometries=raise_on_time_geometries,
    )

    nyquist_freq = sound_event.recording.samplerate / 2
    high_freq = min(high_freq, nyquist_freq)

    label = label_from_tags(
        obj.tags,
        **kwargs,
    )

    return BBox(
        onset=start_time,
        offset=end_time,
        low_freq=low_freq,
        high_freq=high_freq,
        label=label,
    )


def bbox_to_annotation(
    bbox: BBox,
    recording: data.Recording,
    adjust_time_expansion: bool = True,
    notes: Optional[List[data.Note]] = None,
    created_by: Optional[data.User] = None,
    **kwargs,
) -> data.SoundEventAnnotation:
    """Convert a crowsetta bounding box annotation to a soundevent annotation.

    This function transforms a crowsetta bounding box annotation (`BBox`) into
    a `SoundEventAnnotation` object. The onset, offset, low frequency, and high
    frequency values of the bounding box are used to create a `BoundingBox`
    geometry. The label associated with the bounding box is converted into a
    list of soundevent tags using the `convert_label_to_tags` function.

    Parameters
    ----------
    bbox : BBox
        The bounding box annotation to convert.
    recording : data.Recording
        The original recording from which the bounding box annotation was
        derived.
    adjust_time_expansion : bool, optional
        If True, adjust the onset, offset, and frequency values based on the
        recording's time expansion factor, by default True.
    notes : List[data.Note], optional
        Additional notes associated with the converted soundevent annotation,
        by default None.
    created_by : data.User, optional
        User information representing the creator of the converted soundevent
        annotation, by default None.
    **kwargs
        Additional keyword arguments passed to the `convert_label_to_tags`
        function.

    Returns
    -------
    data.SoundEventAnnotation
        A SoundEventAnnotation object representing the converted bounding box
        annotation, containing a SoundEvent with the bounding box geometry,
        associated tags, notes, and creator information.
    """
    if notes is None:
        notes = []

    start_time = bbox.onset
    end_time = bbox.offset
    low_freq = bbox.low_freq
    high_freq = bbox.high_freq

    if adjust_time_expansion and recording.time_expansion != 1:
        start_time = start_time / recording.time_expansion
        end_time = end_time / recording.time_expansion
        low_freq = low_freq * recording.time_expansion
        high_freq = high_freq * recording.time_expansion

    geometry = data.BoundingBox(
        coordinates=[start_time, low_freq, end_time, high_freq]
    )

    tags = label_to_tags(bbox.label, **kwargs)

    sound_event = data.SoundEvent(
        recording=recording,
        geometry=geometry,
    )

    return data.SoundEventAnnotation(
        sound_event=sound_event,
        tags=tags,
        notes=notes,
        created_by=created_by,
    )
