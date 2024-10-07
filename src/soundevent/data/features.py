"""Features.

Features are numerical values associated with sound events, clips, and
recordings, providing additional metadata. They enable searching, organizing,
and analyzing bioacoustic data. Each feature consists of a term (providing
context and meaning) and a corresponding numeric value.

**Sound Events**: Features attached to sound events offer various information,
from basic characteristics (e.g., duration, bandwidth) to intricate details
extracted using deep learning models.

**Clips**: Features associated with clips describe the overall acoustic content
(e.g., signal-to-noise ratio, acoustic indices).

**Recordings**: Features attached to recordings provide contextual information
(e.g., temperature, wind speed, recorder height).

Multiple features on sound events, clips, and recordings enable comprehensive
data exploration and analysis, including outlier identification, understanding
characteristic distributions, and statistical analysis.
"""

import warnings
from collections.abc import Sequence
from typing import Optional

from pydantic import BaseModel, model_validator

from soundevent.data.compat import key_from_term, term_from_key
from soundevent.data.terms import Term

__all__ = [
    "Feature",
    "find_feature",
]


class Feature(BaseModel):
    """Feature Class.

    Features are numerical values associated with sound events, clips, and
    recordings, providing additional metadata. These numerical descriptors
    enable searching, organizing, and analyzing bioacoustic data.

    Attributes
    ----------
    term
        The standardized term associated with the feature, providing context
        and meaning.
    value : float
        The numeric value quantifying the feature, enabling precise comparison
        and analysis.
    """

    term: Term

    value: float

    def __hash__(self):
        """Hash the Feature object."""
        return hash((self.term, self.value))

    @property
    def name(self) -> str:
        """Return the name of the feature."""
        warnings.warn(
            "The 'name' attribute is deprecated. Use 'term' instead.",
            DeprecationWarning,
            stacklevel=1,
        )
        return key_from_term(self.term)

    @model_validator(mode="before")
    @classmethod
    def handle_deprecated_name(cls, values):
        if "name" in values:
            warnings.warn(
                "The 'name' field is deprecated. Please use 'term' instead.",
                DeprecationWarning,
                stacklevel=1,
            )

            if "term" not in values:
                values["term"] = term_from_key(values["name"])

            del values["name"]
        return values


def find_feature(
    features: Sequence[Feature],
    label: Optional[str] = None,
    term: Optional[Term] = None,
    default: Optional[Feature] = None,
) -> Optional[Feature]:
    """Find a feature by its name.

    This function searches for a feature with the given name within the
    provided sequence of features. If the feature is found, its corresponding
    Feature object is returned. If not found, and a default Feature object is
    provided, the default feature is returned. If neither the feature is found
    nor a default feature is provided, None is returned.

    Parameters
    ----------
    features
        The sequence of Feature objects to search within.
    name
        The name of the feature to search for.
    default
        The default Feature object to return if the feature is not found.
        Defaults to None.

    Returns
    -------
    feature: Optional[Feature]
        The Feature object if found, or the default Feature object if provided.
        Returns None if the feature is not found and no default is provided.

    Notes
    -----
    If there are multiple features with the same name, the first one is
    returned.
    """
    if term is not None:
        return next(
            (f for f in features if f.term == term),
            default,
        )

    if label is not None:
        return next(
            (f for f in features if f.term.label == label),
            default,
        )

    raise ValueError("Either 'term' or 'label' must be provided.")
