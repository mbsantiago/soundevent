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
    """Find the first matching feature based on a single criterion.

    Searches an iterable of Feature objects and returns the first one that
    matches the *single* specified search criterion. Users must provide
    exactly one search method: feature name, Term object, Term name, or
    Term label.

    Parameters
    ----------
    features
        A sequence of Feature objects to search within.
    term
        The Term object associated with the feature to search for.
    term_name
        The name of the Term associated with the feature to search for.
    term_label
        The label of the Term associated with the feature to search for.
    name
        The name of the feature to search for.
    label
        (Deprecated) The label of the term to search for. Use `term_label`
        instead. If used, it counts as providing `term_label`.
    default
        A default Feature object to return if no matching feature is
        found. Defaults to None.
    raises
        If True, raises a ValueError if no matching feature is found and
        no default is provided. Defaults to False.

    Returns
    -------
    Optional[Feature]
        The first matching Feature object found, or the `default` value
        if no match is found (and `raises` is False). Returns None if no
        match is found and no `default` is provided.

    Raises
    ------
    ValueError
        If none of `name`, `term`, `term_name`, or `term_label` are
        provided.
    ValueError
        If more than one of `name`, `term`, `term_name`, or `term_label`
        are provided.
    ValueError
        If `raises` is True and no matching feature is found.

    Notes
    -----
    - Only *one* search criterion (`name`, `term`, `term_name`, or
      `term_label`) can be provided per call.
    - If multiple features match the chosen criterion, the first one
      encountered in the `features` sequence is returned.
    - The `label` parameter is deprecated. Use `term_label`.

    Examples
    --------
    >>> t_energy = Term(
    ...     name="energy",
    ...     label="Signal Energy",
    ...     definition="Total energy (J) contained in the audio signal",
    ... )
    >>> t_pitch = Term(
    ...     name="pitch",
    ...     label="Fundamental Frequency",
    ...     definition="Frequency that contains the highest concentration of energy.",
    ... )
    >>> feat1 = Feature(value=0.85, term=t_energy)
    >>> feat2 = Feature(value=440.0, term=t_pitch)
    >>> feat_list = [feat1, feat2]
    >>> # Find by feature name (defaults to term label if does not exist)
    >>> find_feature(feat_list, name="Fundamental Frequency") is feat2
    True
    >>> # Find by term name
    >>> find_feature(feat_list, term_name="energy") is feat1
    True
    >>> # Find by term label
    >>> find_feature(feat_list, term_label="Fundamental Frequency") is feat2
    True
    >>> # No match, return default
    >>> find_feature(feat_list, name="zcr", default=feat1) is feat1
    True
    >>> # No match, raises error
    >>> try:
    ...     find_feature(feat_list, name="zcr", raises=True)
    ... except ValueError as e:
    ...     print(e)
    No feature found matching the criteria.
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
    default: Optional[float] = None,
    raises: bool = False,
) -> Optional[float]:
    """Find the value of the first matching feature.

    Searches a sequence of [Feature][soundevent.data.Feature] objects using
    [`find_feature`][soundevent.data.find_feature] and returns the float
    `value` attribute of the first matching feature found.

    Parameters
    ----------
    features
        A sequence of Feature objects to search within.
    term
        The Term object to search for.
    term_name
        The name of the Term to search for.
    term_label
        The label of the Term to search for.
    name
        The name of the feature to search for.
    default
        A default float value to return if no matching feature is found.
        Defaults to None.
    raises
        If True, raises a ValueError if no matching feature is found and
        no default is provided. Defaults to False.

    Returns
    -------
    Optional[float]
        The float `value` of the matching Feature object, or the `default`
        value if no match is found (and `raises` is False). Returns None
        if no match is found and no `default` is provided.

    Raises
    ------
    ValueError
        If `raises` is True and no feature is found, or if multiple search
        criteria are provided (via `find_feature`).

    See Also
    --------
    [find_feature][soundevent.data.find_feature] : The underlying function used
        to find the Feature object.

    Examples
    --------
    >>> t_energy = Term(
    ...     name="energy",
    ...     label="Signal Energy",
    ...     definition="Total energy (J) contained in the audio signal",
    ... )
    >>> t_pitch = Term(
    ...     name="pitch",
    ...     label="Fundamental Frequency",
    ...     definition="Frequency that contains the highest concentration of energy.",
    ... )
    >>> feat1 = Feature(value=0.85, term=t_energy)
    >>> feat2 = Feature(value=440.0, term=t_pitch, name="f0")
    >>> feat_list = [feat1, feat2]
    >>> # Find value by name (defaults to label if name not provided)
    >>> find_feature_value(feat_list, name="Fundamental Frequency")
    440.0
    >>> # Find value by term name
    >>> find_feature_value(feat_list, term_name="energy")
    0.85
    >>> # No match, return default
    >>> find_feature_value(feat_list, name="zcr", default=0.0)
    0.0
    """
    feat = find_feature(
        features,
        term=term,
        term_name=term_name,
        term_label=term_label,
        name=name,
        raises=raises,
    )

    if feat is not None:
        return feat.value

    return default
