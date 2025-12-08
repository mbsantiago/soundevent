"""UUID generation logic for soundevent objects."""

import uuid

from soundevent.constants import uuid_namespace

__all__ = [
    "generate_recording_uuid",
    "generate_clip_uuid",
]

# Define namespaces for different object types
RECORDING_NAMESPACE = uuid.uuid5(uuid_namespace, "recording")
CLIP_NAMESPACE = uuid.uuid5(uuid_namespace, "clip")


def generate_recording_uuid(
    checksum: str | None = None,
) -> uuid.UUID:
    """Generate a UUID for a recording.

    If a checksum is provided, the UUID is generated deterministically
    from the checksum using the recording namespace. Otherwise, a
    random UUID is generated.

    Parameters
    ----------
    checksum
        The MD5 checksum of the recording.

    Returns
    -------
    uuid.UUID
        The generated UUID.
    """
    if checksum is not None:
        return uuid.uuid5(RECORDING_NAMESPACE, checksum)
    return uuid.uuid4()


def generate_clip_uuid(
    recording_uuid: uuid.UUID,
    start_time: float,
    end_time: float,
) -> uuid.UUID:
    """Generate a UUID for a clip.

    The UUID is generated deterministically from the recording UUID,
    start time, and end time using the clip namespace.

    Parameters
    ----------
    recording_uuid
        The UUID of the recording the clip belongs to.
    start_time
        The start time of the clip in seconds.
    end_time
        The end_time of the clip in seconds.

    Returns
    -------
    uuid.UUID
        The generated UUID.
    """
    # Create a unique string identifier for the clip
    identifier = f"{recording_uuid}:{start_time}:{end_time}"
    return uuid.uuid5(CLIP_NAMESPACE, identifier)
