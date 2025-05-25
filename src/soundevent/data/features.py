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
    "find_feature_value",
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
    term: Optional[Term] = None,
    term_name: Optional[str] = None,
    term_label: Optional[str] = None,
    name: Optional[str] = None,
    label: Optional[str] = None,
    default: Optional[Feature] = None,
    raises: bool = False,
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
    if label is not None:
        warnings.warn(
            "The `label` argument has been deprecated, please use `term_label` instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        term_label = label

    num_args = sum(
        [
            term is not None,
            name is not None,
            term_name is not None,
            term_label is not None,
        ]
    )

    if num_args == 0:
        raise ValueError(
            "Either term, name, term_name or term_label must be provided."
        )

    if num_args > 1:
        raise ValueError(
            "At most one of term, name, term_name, term_label can be"
            " provided. If you used `label` argument this was copied"
            " over to `term_label` and could be causing this error."
        )

    ret = None

    if name is not None:
        ret = next(
            (feature for feature in features if feature.name == name), None
        )

    if term is not None:
        ret = next(
            (feature for feature in features if feature.term == term), None
        )

    if term_label is not None:
        ret = next(
            (
                feature
                for feature in features
                if feature.term.label == term_label
            ),
            None,
        )

    if term_name is not None:
        ret = next(
            (
                feature
                for feature in features
                if feature.term.name == term_name
            ),
            None,
        )

    if ret is not None:
        return ret

    if raises:
        raise ValueError("No feature found matching the criteria.")

    return default


def find_feature_value(
    features: Sequence[Feature],
    term: Optional[Term] = None,
    term_name: Optional[str] = None,
    term_label: Optional[str] = None,
    name: Optional[str] = None,
    label: Optional[str] = None,
    default: Optional[float] = None,
    raises: bool = False,
) -> Optional[float]:
    feat = find_feature(
        features,
        term=term,
        term_name=term_name,
        term_label=term_label,
        name=name,
        label=label,
        raises=raises,
    )

    if feat is not None:
        return feat.value

    return default
