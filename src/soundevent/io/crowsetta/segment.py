"""crowsetta.segment module."""

from typing import List, Optional, Tuple

import crowsetta

from soundevent import data
from soundevent.geometry import compute_bounds
from soundevent.io.crowsetta.labels import label_from_tags, label_to_tags

__all__ = [
    "segment_from_annotation",
    "segment_to_annotation",
]


def convert_geometry_to_interval(
    geometry: data.Geometry,
    cast_to_segment: bool = False,
) -> Tuple[float, float]:
    if geometry.type != "TimeInterval":
        if not cast_to_segment:
            raise ValueError(
                "Cannot convert to a crowsetta segment "
                "because the sound event geometry is not a TimeInterval."
            )

        start_time, _, end_time, _ = compute_bounds(geometry)
        geometry = data.TimeInterval(coordinates=[start_time, end_time])

    start_time, end_time = geometry.coordinates
    return start_time, end_time


def convert_time_to_sample(recording: data.Recording, time: float) -> int:
    return int(time * recording.samplerate)


crowsetta_version = crowsetta.__version__[0]

if crowsetta_version == "4":

    def create_crowsetta_segment(
        onset_s: Optional[float] = None,
        offset_s: Optional[float] = None,
        onset_sample: Optional[int] = None,
        offset_sample: Optional[int] = None,
        label: Optional[str] = None,
    ) -> crowsetta.Segment:
        return crowsetta.Segment.from_keyword(
            label=label,
            onset_s=onset_s,
            offset_s=offset_s,
            onset_sample=onset_sample,
            offset_sample=offset_sample,
        )

else:

    def create_crowsetta_segment(
        onset_s: Optional[float] = None,
        offset_s: Optional[float] = None,
        onset_sample: Optional[int] = None,
        offset_sample: Optional[int] = None,
        label: Optional[str] = None,
    ) -> crowsetta.Segment:
        return crowsetta.Segment(
            onset_s=onset_s,  # type: ignore
            offset_s=offset_s,  # type: ignore
            onset_sample=onset_sample,  # type: ignore
            offset_sample=offset_sample,  # type: ignore
            label=label,  # type: ignore
        )


def segment_from_annotation(
    obj: data.SoundEventAnnotation,
    cast_to_segment: bool = True,
    **kwargs,
) -> crowsetta.Segment:
    """Convert a soundevent annotation to a crowsetta segment.

    This function transforms a SoundEventAnnotation object into a Crowsetta
    segment. The SoundEvent's geometry is used to determine the onset and
    offset times of the segment, and the associated tags are converted into a
    Crowsetta label using the `convert_tags_to_label` function.

    Parameters
    ----------
    obj : data.SoundEventAnnotation
        The SoundEventAnnotation object to convert.
    cast_to_segment : bool, optional
        If True, any geometry that is not a TimeInterval will be cast to a
        TimeInterval, otherwise a ValueError will be raised. By default True.
    **kwargs
        Additional keyword arguments passed to the `convert_tags_to_label`
        function.

    Returns
    -------
    Segment
        A Crowsetta Segment representing the converted soundevent segment,
        with onset and offset times, sample indices, and associated label.

    Raises
    ------
    ValueError
        If the sound event has no geometry, or if the geometry is not a
        TimeInterval and `cast_to_segment` is False.
    """
    sound_event = obj.sound_event
    geometry = sound_event.geometry

    if geometry is None:
        raise ValueError(
            "Cannot convert to a crowsetta segment "
            "because the sound event has no geometry."
        )

    start_time, end_time = convert_geometry_to_interval(
        geometry,
        cast_to_segment,
    )

    start_sample = convert_time_to_sample(sound_event.recording, start_time)
    end_sample = convert_time_to_sample(sound_event.recording, end_time)
    label = label_from_tags(obj.tags, **kwargs)

    return create_crowsetta_segment(
        onset_s=start_time,
        offset_s=end_time,
        onset_sample=start_sample,
        offset_sample=end_sample,
        label=label,
    )


def segment_to_annotation(
    segment: crowsetta.Segment,
    recording: data.Recording,
    adjust_time_expansion: bool = True,
    notes: Optional[List[data.Note]] = None,
    created_by: Optional[data.User] = None,
    **kwargs,
) -> data.SoundEventAnnotation:
    """Convert a crowsetta segment to a soundevent time interval annotation.

    This function transforms a Crowsetta segment into a SoundEvent time
    interval annotation. The segment's onset and offset times are used to
    create a time interval, and the label is converted into a list of
    soundevent tags using the `convert_label_to_tags` function.

    Parameters
    ----------
    segment : Segment
        The Crowsetta segment to convert.
    recording : data.Recording
        The original recording associated with the segment.
    adjust_time_expansion : bool, optional
        If True, adjust the segment's onset and offset times based on the
        recording's time expansion factor, by default True.
    notes : List[data.Note], optional
        Additional notes associated with the converted time interval, by
        default None.
    created_by : data.User, optional
        User information representing the creator of annotation. By default
        None.
    **kwargs
        Additional keyword arguments passed to the `convert_label_to_tags`
        function.

    Returns
    -------
    data.SoundEventAnnotation
        A SoundEventAnnotation object representing the converted time interval,
        containing a SoundEvent with the time interval, associated tags,
        notes, and creator information.
    """
    if notes is None:
        notes = []

    start_time = segment.onset_s
    end_time = segment.offset_s

    if start_time is None:
        samplerate = recording.samplerate / recording.time_expansion

        if segment.onset_sample is None:
            raise ValueError(
                "Cannot convert to a soundevent annotation "
                "because the segment has no onset time."
            )

        start_time = segment.onset_sample / samplerate

    if end_time is None:
        samplerate = recording.samplerate / recording.time_expansion

        if segment.offset_sample is None:
            raise ValueError(
                "Cannot convert to a soundevent annotation "
                "because the segment has no offset time."
            )

        end_time = segment.offset_sample / samplerate

    if adjust_time_expansion and recording.time_expansion != 1:
        # NOTE: The time expansion factor is applied to the segment's onset and
        # offset times to convert them to the original recording's time scale.
        # This is necessary because the segment's onset and offset times are
        # stored in the time scale of the expanded recording.
        start_time = start_time / recording.time_expansion
        end_time = end_time / recording.time_expansion

    geometry = data.TimeInterval(coordinates=[start_time, end_time])

    tags = label_to_tags(segment.label, **kwargs)

    sound_event = data.SoundEvent(
        geometry=geometry,
        recording=recording,
    )

    return data.SoundEventAnnotation(
        sound_event=sound_event,
        tags=tags,
        notes=notes,
        created_by=created_by,
    )
