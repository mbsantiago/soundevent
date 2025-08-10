"""Provides tools for managing and accessing standardized Term objects.

This module introduces the `TermRegistry`, a specialized collection designed
to store and retrieve `Term` objects using unique keys. It facilitates
consistency in terminology across projects by providing a central, searchable
repository for standardized terms. It also defines custom exceptions for
registry-specific error handling.
"""

from collections.abc import Callable, MutableMapping
from functools import partial
from typing import Dict, Optional

from soundevent.data import Term

__all__ = [
    "MultipleTermsFoundError",
    "TermNotFoundError",
    "TermOverrideError",
    "TermRegistry",
    "TermRegistryError",
]


class TermRegistryError(Exception):
    """Base exception for all TermRegistry related errors."""


class TermOverrideError(KeyError, TermRegistryError):
    """Raised when attempting to override an existing term.

    This error occurs when adding a term to the registry with a key that
    already exists, and the operation is not forced.

    Attributes
    ----------
    key : Optional[str]
        The key that caused the override error.
    term : Optional[Term]
        The existing term associated with the key.
    """

    def __init__(
        self,
        message: str,
        key: Optional[str] = None,
        term: Optional[Term] = None,
    ):
        super().__init__(message)
        self.key = key
        self.term = term

    def __str__(self) -> str:
        """Return a user-friendly string representation of the error."""
        message = self.args[0]
        details = []
        if self.key:
            details.append(f"key='{self.key}'")
        if self.term:
            details.append(f"existing_term={self.term!r}")
        if details:
            return f"{message} ({', '.join(details)})"
        return message


class TermNotFoundError(KeyError, TermRegistryError):
    """Raised when a term cannot be found in the registry.

    This is either by key or specific criteria.

    Inherits from KeyError for compatibility with dictionary-like access.
    """

    def __init__(
        self,
        message: str,
        key: Optional[str] = None,
        criteria: Optional[dict] = None,
    ):
        super().__init__(message)
        self.key = key
        self.criteria = criteria if criteria is not None else {}

    def __str__(self) -> str:
        message = self.args[0]

        if self.key:
            return f"{message}: Key='{self.key}'"

        if self.criteria:
            crit_str = ", ".join(
                f"{k}='{v}'" for k, v in self.criteria.items()
            )
            return f"{message}: Criteria={{{crit_str}}}"

        return message  # pragma: no cover


class MultipleTermsFoundError(LookupError, TermRegistryError):
    """Raised when get_by finds multiple terms matching the provided criteria.

    Inherits from LookupError as it's an issue during a lookup process.
    """

    def __init__(
        self,
        message: str,
        criteria: dict,
        count: int,
        matches: Optional[list[Term]] = None,
    ):
        super().__init__(message)
        self.criteria = criteria
        self.count = count
        self.matches = matches or []

    def __str__(self) -> str:
        message = self.args[0]
        crit_str = ", ".join(f"{k}='{v}'" for k, v in self.criteria.items())
        return f"{message}: Found {self.count} terms matching {{{crit_str}}}."


class TermRegistry(MutableMapping[str, Term]):
    """A mutable mapping for managing, storing, and retrieving `Term` objects.

    Provides dictionary-like access (getting, setting, deleting by key) along
    with specialized methods for finding terms based on their attributes.
    It serves as a central point to manage and access standardized `Term`
    objects within a project.

    Attributes
    ----------
    _terms : Dict[str, Term]
        The internal dictionary holding the registered terms.
    """

    def __init__(self, terms: Optional[Dict[str, Term]] = None):
        """Initialize the TermRegistry.

        Parameters
        ----------
        terms : Optional[Dict[str, Term]], optional
            A dictionary of initial terms {key: term} to populate the
            registry. Defaults to an empty registry.
        """
        self._terms: Dict[str, Term] = terms or {}

    def __getitem__(self, key: str) -> Term:
        """Retrieve a term by its key.

        Parameters
        ----------
        key : str
            The key of the term to retrieve.

        Returns
        -------
        Term
            The `Term` object associated with the key.

        Raises
        ------
        TermNotFoundError
            If no term is found with the given key.
        """
        try:
            return self._terms[key]
        except KeyError as err:
            raise TermNotFoundError(
                "No term found for key "
                f"'{key}'. Ensure it is registered or loaded. "
                f"Available keys: {', '.join(self._terms.keys())}",
                key=key,
            ) from err

    def __len__(self) -> int:
        """Return the number of registered terms."""
        return len(self._terms)

    def __iter__(self):
        """Return an iterator over the keys of the registry."""
        return iter(self._terms)

    def __setitem__(self, key: str, term: Term) -> None:
        """Register a term with a specific key.

        Parameters
        ----------
        key : str
            The key to register the term under.
        term : Term
            The `Term` object to register.

        Raises
        ------
        KeyError
            If a term with the provided key already exists.
        TypeError
            If the value provided is not a `Term` object.
        """
        if not isinstance(term, Term):
            raise TypeError("Value must be a Term object.")

        if key in self._terms:
            raise TermOverrideError(
                "Cannot override existing term",
                key=key,
                term=self[key],
            )

        self._terms[key] = term

    def __delitem__(self, key: str) -> None:
        """Remove a term by its key.

        Parameters
        ----------
        key : str
            The key of the term to remove.

        Raises
        ------
        KeyError
            If no term is found with the given key.
        """
        try:
            del self._terms[key]
        except KeyError as err:
            raise TermNotFoundError(
                "No term found for key "
                f"'{key}'. Available keys: {', '.join(self._terms.keys())}",
                key=key,
            ) from err

    def add_term(
        self,
        term: Term,
        key: Optional[str] = None,
        force: bool = False,
    ) -> None:
        """Register a term, optionally defaulting the key to `term.name`.

        Parameters
        ----------
        term : Term
            The `Term` object to add.
        key : Optional[str], optional
            The key to use for registration. If None, `term.name` is used.
            Defaults to None.
        force : bool, default=False
            If True, allows overriding an existing term with the same key.
            If False, raises `TermOverrideError` if the key already exists.

        Raises
        ------
        TermOverrideError
            If `force` is False and a term with the same key already exists.
        """
        key = key or term.name

        if not isinstance(term, Term):
            raise TypeError("Value must be a Term object.")

        if key in self and not force:
            raise TermOverrideError(
                "Cannot override existing term",
                key=key,
                term=self[key],
            )

        self._terms[key] = term

    def get(self, key: str, default: Optional[Term] = None) -> Optional[Term]:  # type: ignore
        """Retrieve a term by key, returning a default if not found.

        Mimics `dict.get()`. Returns `None` by default if the key is not
        found, or a specified default value.

        Parameters
        ----------
        key : str
            The key of the term to retrieve.
        default : Any, optional
            The value to return if the key is not found. Defaults to None.

        Returns
        -------
        Optional[Term]
            The `Term` object or the `default` value.

        Raises
        ------
        ValueError
            If `default` is provided and is not `None` or a `Term`.
        """
        if default is not None and not isinstance(default, Term):
            raise ValueError("Default value must be a Term object or None.")

        term = self._terms.get(key)
        return term or default

    def remove(self, key: str) -> None:
        """Remove a term from the registry by its key.

        Parameters
        ----------
        key : str
            The key of the term to remove.

        Raises
        ------
        KeyError
            If no term is found with the given key.
        """
        self.__delitem__(key)

    def get_by(
        self,
        label: Optional[str] = None,
        name: Optional[str] = None,
        uri: Optional[str] = None,
    ) -> Term:
        """Retrieve one term by an exact match on a single attribute.

        Requires exactly one search criterion and expects exactly one match.

        Parameters
        ----------
        label : Optional[str], optional
            The exact label to match.
        name : Optional[str], optional
            The exact name to match.
        uri : Optional[str], optional
            The exact URI to match.

        Returns
        -------
        Term
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
        criteria = {"label": label, "name": name, "uri": uri}
        criteria = {k: v for k, v in criteria.items() if v is not None}

        if not criteria:
            raise ValueError("At least one search criterion must be provided.")

        if len(criteria) > 1:
            raise ValueError("Only one search criterion can be provided.")

        field, value = next(iter(criteria.items()))

        matches = [
            term
            for term in self._terms.values()
            if getattr(term, field) == value
        ]

        if not matches:
            raise TermNotFoundError(
                "Term not found with the specified criteria",
                criteria=criteria,
            )

        if len(matches) > 1:
            raise MultipleTermsFoundError(
                "Multiple terms found; expected only one",
                criteria=criteria,
                count=len(matches),
                matches=matches,
            )

        return matches[0]

    def find(
        self,
        label: Optional[str] = None,
        name: Optional[str] = None,
        uri: Optional[str] = None,
        definition: Optional[str] = None,
        q: Optional[str] = None,
        ignore_case: bool = True,
    ) -> list[Term]:
        """Find terms by substring match; returns multiple terms.

        If `q` is provided, it searches `label`, `name`, `uri`, and
        `definition` for a match (OR logic).
        If `q` is not provided, it searches using the specific fields,
        requiring all provided fields to match (AND logic).
        If no arguments are given, all terms are returned.

        Parameters
        ----------
        label : Optional[str], optional
            Substring to search for in labels.
        name : Optional[str], optional
            Substring to search for in names.
        uri : Optional[str], optional
            Substring to search for in URIs.
        definition : Optional[str], optional
            Substring to search for in definitions.
        q : Optional[str], optional
            General query string (searches all fields, OR logic).
        ignore_case : bool, optional
            Perform case-insensitive search. Defaults to True.

        Returns
        -------
        list[Term]
            A list of matching `Term` objects.

        Raises
        ------
        ValueError
            If `q` is used with other specific criteria.
        """
        num_criteria = sum(
            [
                label is not None,
                name is not None,
                uri is not None,
                definition is not None,
            ]
        )

        if q is not None and num_criteria > 0:
            raise ValueError(
                "If 'q' is provided, no other specific search criteria can be used."
            )

        if q is not None:
            search_func = _build_search_func(
                ignore_case=ignore_case,
                match_any=True,
                label=q,
                name=q,
                definition=q,
                uri=q,
            )
        else:
            search_func = _build_search_func(
                ignore_case=ignore_case,
                label=label,
                name=name,
                definition=definition,
                uri=uri,
            )

        return [term for term in self._terms.values() if search_func(term)]


def _build_search_func(
    ignore_case: bool = True,
    match_any: bool = False,
    **kwargs,
) -> Callable[[Term], bool]:
    criteria = [
        partial(_query_term_field, field=f, query=v, ignore_case=ignore_case)
        for f, v in kwargs.items()
        if v is not None
    ]

    if match_any:
        return lambda term: any(func(term) for func in criteria)

    return lambda term: all(func(term) for func in criteria)


def _query_term_field(
    term: Term,
    field: str,
    query: str,
    ignore_case: bool = True,
) -> bool:
    value = getattr(term, field, None)

    if value is None:
        return False  # pragma: no cover

    if ignore_case:
        return query.lower() in value.lower()

    return query in value
