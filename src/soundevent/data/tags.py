"""Tags.

Tags attach metadata to objects (recordings, clips, sound events) in the
soundevent package, enhancing organization and filtering.

## Structure

Each tag comprises a value (string) and a term. The term provides context and
meaning, often drawn from controlled vocabularies (e.g., "ac:duration" from the
Audiovisual Core). This ensures standard, clear tag meanings.

## Usage Examples

**Recording Tags**: Provide context (e.g., vegetation type, recording device,
protocol).

**Clip Tags**: Highlight acoustic content (e.g., species present, noise levels,
soundscape category).

**Sound Event Tags**: Describe individual sounds (e.g., species, behavior,
specific syllables).
"""

import warnings
from collections.abc import Iterable
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from soundevent.data.compat import key_from_term, term_from_key
from soundevent.data.terms import Term

__all__ = ["Tag", "find_tag", "find_tag_value"]


class Tag(BaseModel):
    """Tag Class.

    Tags annotate and categorize bioacoustic research components. Each tag is a
    `term-value` pair. The `term` provides context and enables categorization.

    Attributes
    ----------
    term
        The standardized term associated with the tag, providing context and meaning.
    value
        The value associated with the tag, offering specific information.

    Notes
    -----
    The `key` attribute is deprecated. Use `term` instead.
    """

    term: Term = Field(
        title="Term",
        description="The standardised term associated with the tag.",
        repr=True,
    )

    value: str = Field(
        title="Value",
        description="The value associated with the tag.",
        repr=True,
    )

    def __hash__(self):
        """Hash the Tag object."""
        return hash((self.term, self.value))

    @property
    def key(self) -> str:
        """Return the key of the tag."""
        warnings.warn(
            "The 'key' attribute is deprecated. Use 'term' instead.",
            DeprecationWarning,
            stacklevel=1,
        )
        return key_from_term(self.term)

    @model_validator(mode="before")
    @classmethod
    def handle_deprecated_key(cls, values):
        if "key" in values:
            warnings.warn(
                "The 'key' field is deprecated. Please use 'term' instead.",
                DeprecationWarning,
                stacklevel=2,
            )

            if "term" not in values:
                values["term"] = term_from_key(values["key"])

            del values["key"]
        return values


def find_tag(
    tags: Iterable[Tag],
    term: Optional[Term] = None,
    term_name: Optional[str] = None,
    term_label: Optional[str] = None,
    label: Optional[str] = None,
    key: Optional[str] = None,
    default: Optional[Tag] = None,
    raises: bool = False,
) -> Optional[Tag]:
    """Find the first matching tag based on provided criteria.

    Searches an iterable of Tag objects and returns the first one that
    matches the *single* specified search criterion. Users must provide
    exactly one search method: tag key, Term object, Term name, or Term
    label.

    Parameters
    ----------
    tags
        An iterable of Tag objects to search within.
    term
        The Term object associated with the tag to search for.
    term_name
        The name of the Term associated with the tag to search for.
    term_label
        The label of the Term associated with the tag to search for.
    key
        The key of the tag to search for.
    label
        (Deprecated) The label of the term to search for. Use `term_label`
        instead.
    default
        A default Tag object to return if no matching tag is found.
        Defaults to None.
    raises
        If True, raises a ValueError if no matching tag is found and no
        default is provided. Defaults to False.

    Returns
    -------
    Optional[Tag]
        The first matching Tag object found, or the `default` value if no
        match is found (and `raises` is False). Returns None if no match
        is found and no `default` is provided.

    Raises
    ------
    ValueError
        If none of `key`, `term`, `term_name`, or `term_label` are
        provided.
    ValueError
        If more than one of `key`, `term`, `term_name`, or `term_label`
        are provided.
    ValueError
        If `raises` is True and no matching tag is found.

    Notes
    -----
    - Only *one* search criterion (`key`, `term`, `term_name`, or
      `term_label`) can be provided per call.
    - If multiple tags match the chosen criterion, the first one
      encountered in the `tags` iterable is returned.
    - The `label` parameter is deprecated and will be removed in a future
      version. Please use `term_label`. Using `label` counts as using
      `term_label` regarding the one-criterion rule.

    Examples
    --------
    >>> t1 = Term(
    ...     name="instrument",
    ...     label="Instrument Type",
    ...     definition="Type of musical instrument.",
    ... )
    >>> t2 = Term(
    ...     name="scene",
    ...     label="Acoustic Scene",
    ...     definition="Class of acoustic scene as defined by the AudioSet ontology",
    ... )
    >>> tag1 = Tag(term=t1, value="guitar")
    >>> tag2 = Tag(term=t2, value="park")
    >>> tag_list = [tag1, tag2]
    >>> # Find by term name
    >>> find_tag(tag_list, term_name="scene") is tag2
    True
    >>> # Find by term label
    >>> find_tag(tag_list, term_label="Instrument Type") is tag1
    True
    >>> # Find by key (if tag does not have a key will default to its label)
    >>> find_tag(tag_list, key="Instrument Type") is tag1
    True
    >>> # No match, return default
    >>> find_tag(tag_list, term_name="weather", default=tag1) is tag1
    True
    >>> # No match, return None
    >>> find_tag(tag_list, term_name="weather") is None
    True
    """
    if label is not None:
        warnings.warn(
            "The `label` argument has been deprecated, please use"
            "`term_label` instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        term_label = label

    num_args = sum(
        [
            term is not None,
            key is not None,
            term_name is not None,
            term_label is not None,
        ]
    )

    if num_args == 0:
        raise ValueError(
            "Either term, key, term_name or term_label must be provided."
        )

    if num_args > 1:
        raise ValueError(
            "At most one of term, key, term_name, term_label can be"
            " provided. If you used `label` argument this was copied"
            " over to `term_label` and could be causing this error."
        )

    ret = None

    if key is not None:
        ret = next((tag for tag in tags if tag.key == key), None)

    if term is not None:
        ret = next((tag for tag in tags if tag.term == term), None)

    if term_label is not None:
        ret = next((tag for tag in tags if tag.term.label == term_label), None)

    if term_name is not None:
        ret = next((tag for tag in tags if tag.term.name == term_name), None)

    if ret is not None:
        return ret

    if raises:
        raise ValueError("No tag found matching the criteria.")

    return default


def find_tag_value(
    tags: Iterable[Tag],
    key: Optional[str] = None,
    term: Optional[Term] = None,
    term_name: Optional[str] = None,
    term_label: Optional[str] = None,
    default: Optional[str] = None,
    raises: bool = False,
) -> Optional[str]:
    """Find the value of the first matching tag.

    Searches an iterable of [Tag][soundevent.data.Tag] objects using
    [`find_tag`][soundevent.data.find_tag] and returns the `value` attribute
    of the first matching tag found.

    Parameters
    ----------
    tags
        An iterable of Tag objects to search within.
    key
        The key of the tag to search for.
    term
        The Term object associated with the tag to search for.
    term_name
        The name of the Term associated with the tag to search for.
    term_label
        The label of the Term associated with the tag to search for.
    default
        A default string value to return if no matching tag is found.
        Defaults to None.
    raises
        If True, raises a ValueError if no matching tag is found and no
        default is provided. Defaults to False.

    Returns
    -------
    Optional[str]
        The string `value` of the first matching Tag object, or the
        `default` value if no match is found (and `raises` is False).
        Returns None if no match is found and no `default` is provided.

    Raises
    ------
    ValueError
        If `raises` is True and no matching tag is found.
        Also raised if no search criteria are provided (via `find_tag`).

    See Also
    --------
    [find_tag][soundevent.data.find_tag] : The underlying function used to find
        the Tag object itself.

    Examples
    --------
    >>> t1 = Term(
    ...     name="instrument",
    ...     label="Instrument Type",
    ...     definition="Type of musical instrument.",
    ... )
    >>> t2 = Term(
    ...     name="tau2019:scene",
    ...     label="Acoustic Scene",
    ...     definition="Type of acoustic scene according to TAU Urban Acoustic Scenes dataset.",
    ... )
    >>> tag1 = Tag(term=t1, value="guitar")
    >>> tag2 = Tag(term=t2, value="park")
    >>> tag_list = [tag1, tag2]
    >>> # Find value by term name
    >>> find_tag_value(tag_list, term_name="tau2019:scene")
    'park'
    >>> # Find value by key
    >>> find_tag_value(tag_list, key="Instrument Type")
    'guitar'
    >>> # No match, return default
    >>> find_tag_value(tag_list, term_name="weather", default="unknown")
    'unknown'
    """
    tag = find_tag(
        tags,
        key=key,
        term=term,
        term_name=term_name,
        term_label=term_label,
        raises=raises,
    )

    if tag is not None:
        return tag.value

    return default
