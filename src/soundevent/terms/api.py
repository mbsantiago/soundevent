"""
Global term registry functions.

This module provides a set of functions that operate on a global instance of
a `TermRegistry`. This allows for a simple, function-based API for managing
terms throughout an application.

The global registry can be replaced with a custom one using the
`set_global_term_registry` function. All functions in this module will then
operate on the new registry.

Alternatively, most functions accept an optional `term_registry` argument,
allowing them to operate on a specific `TermRegistry` instance for a single
call, without affecting the global state.
"""

from typing import List, Optional

from soundevent import data
from soundevent.terms.registry import TermRegistry

__all__ = [
    "add_term",
    "find_term",
    "get_global_term_registry",
    "get_term",
    "get_term_by",
    "has_term",
    "remove_term",
    "set_global_term_registry",
]

_registry = TermRegistry()


def get_global_term_registry() -> TermRegistry:
    """
    Return the current global term registry.

    Returns
    -------
    TermRegistry
        The active global `TermRegistry` instance.
    """
    return _registry


def set_global_term_registry(term_registry: TermRegistry) -> None:
    """
    Set a new global term registry.

    This function replaces the existing global registry with a new one. All
    subsequent calls to functions in this module will operate on the new
    registry.

    Parameters
    ----------
    term_registry : TermRegistry
        The new `TermRegistry` instance to set as the global registry.
    """
    global _registry
    _registry = term_registry


def has_term(key: str, term_registry: Optional[TermRegistry] = None) -> bool:
    """
    Check if a term exists in the registry.

    Parameters
    ----------
    key : str
        The key of the term to check.
    term_registry : Optional[TermRegistry], default=None
        If provided, the check is performed on this registry instead of the
        global one.

    Returns
    -------
    bool
        True if the term exists, False otherwise.
    """
    if term_registry is None:
        term_registry = get_global_term_registry()

    return key in term_registry


def get_term(
    key: str,
    default: Optional[data.Term] = None,
    term_registry: Optional[TermRegistry] = None,
) -> Optional[data.Term]:
    """
    Retrieve a term by its key.

    Parameters
    ----------
    key : str
        The key of the term to retrieve.
    default : Optional[data.Term], default=None
        The value to return if the key is not found.
    term_registry : Optional[TermRegistry], default=None
        If provided, the term is retrieved from this registry instead of the
        global one.

    Returns
    -------
    Optional[data.Term]
        The `Term` object or the `default` value if not found.
    """
    if term_registry is None:
        term_registry = get_global_term_registry()

    return term_registry.get(key, default=default)


def add_term(
    term: data.Term,
    key: Optional[str] = None,
    term_registry: Optional[TermRegistry] = None,
    force: bool = False,
) -> None:
    """
    Register a term.

    By default, the key is derived from `term.name`.

    Parameters
    ----------
    term : data.Term
        The `Term` object to add.
    key : Optional[str], default=None
        The key to use for registration. If None, `term.name` is used.
    term_registry : Optional[TermRegistry], default=None
        If provided, the term is added to this registry instead of the
        global one.
    force : bool, default=False
        If True, overwrite any existing term with the same key.

    Raises
    ------
    KeyError
        If `force` is False and the key already exists.
    """
    if term_registry is None:
        term_registry = get_global_term_registry()

    term_registry.add_term(term=term, key=key, force=force)


def remove_term(
    key: str,
    term_registry: Optional[TermRegistry] = None,
) -> None:
    """
    Remove a term from the registry by its key.

    Parameters
    ----------
    key : str
        The key of the term to remove.
    term_registry : Optional[TermRegistry], default=None
        If provided, the term is removed from this registry instead of the
        global one.

    Raises
    ------
    KeyError
        If no term is found with the given key.
    """
    if term_registry is None:
        term_registry = get_global_term_registry()

    del term_registry[key]


def get_term_by(
    label: Optional[str] = None,
    name: Optional[str] = None,
    uri: Optional[str] = None,
    term_registry: Optional[TermRegistry] = None,
) -> data.Term:
    """
    Retrieve one term by an exact match on a single attribute.

    Requires exactly one search criterion and expects exactly one match.

    Parameters
    ----------
    label : Optional[str], default=None
        The exact label to match.
    name : Optional[str], default=None
        The exact name to match.
    uri : Optional[str], default=None
        The exact URI to match.
    term_registry : Optional[TermRegistry], default=None
        If provided, the search is performed on this registry instead of the
        global one.

    Returns
    -------
    data.Term
        The single `Term` object that matches.

    Raises
    ------
    ValueError
        If zero or more than one criterion is provided.
    TermNotFoundError
        If no term matches the criterion.
    MultipleTermsFoundError
        If more than one term matches the criterion.
    """
    if term_registry is None:
        term_registry = get_global_term_registry()

    return term_registry.get_by(
        label=label,
        name=name,
        uri=uri,
    )


def find_term(
    label: Optional[str] = None,
    name: Optional[str] = None,
    uri: Optional[str] = None,
    definition: Optional[str] = None,
    q: Optional[str] = None,
    ignore_case: bool = True,
    term_registry: Optional[TermRegistry] = None,
) -> List[data.Term]:
    """
    Find terms by substring match.

    If `q` is provided, it searches `label`, `name`, `uri`, and
    `definition` for a match (OR logic).
    If `q` is not provided, it searches using the specific fields,
    requiring all provided fields to match (AND logic).
    If no arguments are given, all terms are returned.

    Parameters
    ----------
    label : Optional[str], default=None
        Substring to search for in labels.
    name : Optional[str], default=None
        Substring to search for in names.
    uri : Optional[str], default=None
        Substring to search for in URIs.
    definition : Optional[str], default=None
        Substring to search for in definitions.
    q : Optional[str], default=None
        General query string (searches all fields, OR logic).
    ignore_case : bool, default=True
        Perform case-insensitive search.
    term_registry : Optional[TermRegistry], default=None
        If provided, the search is performed on this registry instead of the
        global one.

    Returns
    -------
    List[data.Term]
        A list of matching `Term` objects.
    """
    if term_registry is None:
        term_registry = get_global_term_registry()

    return term_registry.find(
        label=label,
        name=name,
        uri=uri,
        definition=definition,
        q=q,
        ignore_case=ignore_case,
    )
