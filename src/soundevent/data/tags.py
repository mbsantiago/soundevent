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
    """Find a tag by its key.

    This function searches for a tag with the given term or term label within
    the provided sequence of tags. If the tag is found, its corresponding Tag
    object is returned. If not found, and a default Tag object is provided, the
    default tag is returned. If neither the tag is found nor a default tag is
    provided, None is returned.

    Parameters
    ----------
    tags
        The sequence of Tag objects to search within.
    term
        The term object to search for.
    label
        The label of the term to search for.
    default
        The default Tag object to return if the tag is not found. Defaults to
        None.

    Returns
    -------
    tag
        The Tag object if found, or the default Tag object if provided. Returns
        None if the tag is not found and no default is provided.

    Notes
    -----
    If there are multiple tags with the same term or term label, the first one
    is returned.
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
            "At most one of term, key, term_name, term_label can be provided. If you used `label` argument this was copied over to `term_label` and could be causing this error."
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
    Raises
    ------
    ValueError
        If neither the term nor the label is provided.
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
