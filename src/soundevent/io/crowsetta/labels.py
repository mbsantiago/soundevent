"""Crowsetta label conversion functions.

This module provides functions for converting between **Crowsetta** labels and
`soundevent` tags. Crowsetta labels are represented as strings, while
soundevent tags are instances of a custom class
[`data.Tag`][soundevent.data.Tag], which contains a term-value pair rather than
a single string. The conversion functions provided in this module facilitate
the conversion of labels to tags and vice versa, and they allow users to
customize the conversion process using various options.
"""

from typing import Callable, Dict, List, Optional, Sequence, Union

from soundevent import data

__all__ = [
    "label_to_tags",
    "label_from_tags",
]


EMPTY_LABEL = "__empty__"


LabelToTagFn = Callable[[str], Union[List[data.Tag], data.Tag]]
LabelToTagMap = Dict[str, Union[List[data.Tag], data.Tag]]


def label_to_tags(
    label: str,
    tag_fn: Optional[LabelToTagFn] = None,
    tag_mapping: Optional[LabelToTagMap] = None,
    term_mapping: Optional[Dict[str, data.Term]] = None,
    key_mapping: Optional[Dict[str, str]] = None,
    key: Optional[str] = None,
    term: Optional[data.Term] = None,
    fallback: str = "crowsetta",
    empty_labels: Sequence[str] = (EMPTY_LABEL,),
) -> List[data.Tag]:
    """Convert a crowsetta label to a list of soundevent tags.

    Parameters
    ----------
    label
        The Crowsetta label to convert.
    tag_fn
        A function to directly convert labels to a list of tags.
    tag_mapping
        A dictionary mapping labels to lists of tags or a single tag.
    term_mapping
        A dictionary mapping labels directly to `soundevent.data.Term` objects
    key_mapping
        A dictionary mapping labels to keys (deprecated, use `term_mapping`
        instead).
    key
        The key to use for the tag (deprecated, use `term` instead).
    term
        The `soundevent.data.Term` to use for the tag
    fallback
        The key to use if no other key is provided (deprecated, use `term`
        instead).
    empty_labels
        Labels considered empty, resulting in an empty list of tags.

    Returns
    -------
    List[data.Tag]
        The list of soundevent tags corresponding to the Crowsetta label.

    Notes
    -----
    This is the default conversion process:

    1. If `label` is in `empty_labels`, return an empty list.
    2. If `tag_fn` is provided, use it to convert the label.
    3. If `term_mapping` is provided and the label is found, use the corresponding term.
    4. If `tag_mapping` is provided and the label is found, return the corresponding tags.
    5. If `key_mapping` is provided and the label is found, use the corresponding key (deprecated).
    6. If `key` is provided, use it (deprecated). Otherwise, use `fallback` (deprecated).
    7. If `term` is not yet set, derive it from the `key` (deprecated).
    8. Return a list containing a single `Tag` with the determined `term` and the original `label` as the `value`.
    """
    if label in empty_labels:
        return []

    if tag_fn is not None:
        try:
            tags = tag_fn(label)
            return tags if isinstance(tags, list) else [tags]
        except ValueError:
            pass

    if term_mapping is not None:
        if label in term_mapping:
            term = term_mapping[label]

    if term is None and tag_mapping is not None:
        if label in tag_mapping:
            tags = tag_mapping[label]
            return tags if isinstance(tags, list) else [tags]

    if term is None and key_mapping is not None:
        key = key_mapping.get(label)

    if key is None:
        key = fallback

    if term is None:
        term = data.term_from_key(key)

    return [data.Tag(term=term, value=label)]


def label_from_tag(
    tag: data.Tag,
    label_fn: Optional[Callable[[data.Tag], str]] = None,
    label_mapping: Optional[Dict[data.Tag, str]] = None,
    value_only: bool = False,
    separator: str = ":",
) -> str:
    """Convert a soundevent tag to a crowsetta label.

    This function facilitates the conversion of a soundevent tag into a
    crowsetta label. Users can customize this conversion using the following
    options:

    1. If a custom mapping function (`label_fn` argument) is provided, it will
    be used to directly convert the tag to a label.
    2. If a mapping dictionary (`label_mapping` argument) is provided, the
    function will attempt to look up the label for the tag in the mapping. If
    found, it returns the label; otherwise, it proceeds to the next option.
    3. If the `value_only` argument is set to True, the function returns only
    the value of the tag.
    4. If none of the above conditions are met, the function constructs the
    label by combining the tag's key and value with the specified separator.

    Parameters
    ----------
    tag
        The soundevent tag to convert to a label.
    label_fn
        A function to convert tags to labels.
    label_mapping
        A dictionary mapping tags to labels.
    value_only
        If True, return only the value of the tag, by default False.
    separator
        The separator to use between the key and value when constructing the
        label, by default ":".

    Returns
    -------
    str
        The crowsetta label corresponding to the soundevent tag.
    """
    if label_fn is not None:
        return label_fn(tag)

    if label_mapping is not None:
        label = label_mapping.get(tag)

        if label is not None:
            return label

    if value_only:
        return tag.value

    return f"{data.key_from_term(tag.term)}{separator}{tag.value}"


def label_from_tags(
    tags: Sequence[data.Tag],
    seq_label_fn: Optional[Callable[[Sequence[data.Tag]], str]] = None,
    select_by_key: Optional[str] = None,
    index: Optional[int] = None,
    separator: str = ",",
    empty_label: str = EMPTY_LABEL,
    **kwargs,
) -> str:
    """Convert a sequence of soundevent tags to a crowsetta label.

    This function facilitates the conversion of a sequence of soundevent tags
    into a Crowsetta label. Users can customize the conversion process using
    the following options:

    1. If a custom sequence label function (`seq_label_fn` argument) is
    provided, it will be used to directly convert the sequence of tags to a
    label.
    2. If the sequence of tags is empty, the function returns the specified
    `empty_label`.
    3. If the `select_by_key` argument is provided, the function will
    attempt to find the first tag in the sequence with a matching key. If
    found, it returns the label converted from that tag using
    `convert_tag_to_label`, otherwise it returns the `empty_label`.
    4. If the `index` argument is provided, it will be used to select a tag
    from the sequence based on the index. If the index is out of bounds, it
    wraps around to the valid range. The label converted from the selected
    tag is then returned.
    5. If none of the above conditions are met, the function constructs a
    label by joining the labels of all tags in the sequence with the
    specified separator.

    Parameters
    ----------
    tags
        The sequence of soundevent tags to convert to a label.
    seq_label_fn
        A function to convert sequences of tags to labels.
    select_by_key
        If provided, select the first tag with a matching key for label
        conversion.
    index
        If provided, use it as the index to select a tag from the sequence for
        label conversion. The index is wrapped around if it exceeds the bounds.
    separator
        The separator to use between the labels when constructing the final
        label.
    empty_label
        The label to return when the sequence of tags is empty. By default
        "__empty__".
    **kwargs
        Additional keyword arguments passed to the `convert_tag_to_label`
        function.

    Returns
    -------
    str
        The Crowsetta label corresponding to the sequence of soundevent tags.
    """
    if seq_label_fn is not None:
        return seq_label_fn(tags)

    if not tags:
        return empty_label

    if select_by_key is not None:
        tag = next(
            (t for t in tags if data.key_from_term(t.term) == select_by_key),
            None,
        )

        if tag is None:
            return empty_label

        return label_from_tag(tag, value_only=True, **kwargs)

    if index is not None:
        index = index % len(tags)
        return label_from_tag(tags[index], **kwargs)

    return separator.join([label_from_tag(tag, **kwargs) for tag in tags])
