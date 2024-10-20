"""Package wide constants."""

import uuid

__all__ = [
    "uuid_namespace",
]

uuid_namespace = uuid.uuid5(uuid.NAMESPACE_DNS, "soundevent")
"""UUID namespace for soundevent data."""
