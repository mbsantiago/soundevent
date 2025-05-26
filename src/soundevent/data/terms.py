"""Terms module.

Soundevent uses specialized objects to refer to standardized terms.
Standardized terms make it easier to interpret tags and features,
and facilitate data sharing. This clarity helps integrate with
existing data corpora.
"""

from collections.abc import Callable, MutableMapping
from functools import partial
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "Term",
]


class Term(BaseModel):
    """A term class for a standardised term."""

    model_config = ConfigDict(frozen=True, extra="allow")

    # Minimal set of attributes according to the DCMI Metadata Terms

    label: str = Field(
        serialization_alias="rdfs:label",
        title="Label",
        description="The human-readable label assigned to the term.",
        repr=True,
        json_schema_extra={
            "$id": "https://www.w3.org/TR/rdf-schema/#ch_label"
        },
    )

    definition: str = Field(
        serialization_alias="skos:definition",
        title="Definition",
        description=(
            "The type of term: property, class, datatype, or "
            "vocabulary encoding scheme."
        ),
        repr=False,
        json_schema_extra={
            "$id": "http://www.w3.org/2004/02/skos/core#definition"
        },
    )

    name: str = Field(
        title="Name",
        description=(
            "A token appended to the URI of a DCMI namespace to "
            "create the URI of the term."
        ),
        repr=False,
    )

    uri: Optional[str] = Field(
        serialization_alias="dcterms:URI",
        default=None,
        title="URI",
        repr=False,
        description=(
            "The Uniform Resource Identifier used to uniquely identify a term."
        ),
        json_schema_extra={"$id": "http://purl.org/dc/terms/URI"},
    )

    type_of_term: str = Field(
        serialization_alias="dcterms:type",
        default="property",
        alias="type",
        title="Type",
        description="The nature or genre of the resource.",
        repr=False,
        json_schema_extra={"$id": "http://purl.org/dc/terms/type"},
    )

    # Additional attributes according to the DCMI Metadata

    comment: Optional[str] = Field(
        serialization_alias="rdfs:comment",
        default=None,
        title="Comment",
        description="Additional information about the term or its application.",
        repr=False,
        json_schema_extra={
            "$id": "https://www.w3.org/TR/rdf-schema/#ch_comment"
        },
    )

    see: Optional[str] = Field(
        default=None,
        serialization_alias="rdsf:seeAlso",
        title="See",
        description="Authoritative documentation related to the term.",
        repr=False,
        json_schema_extra={
            "$id": "https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.ttl"
        },
    )

    subproperty_of: Optional[str] = Field(
        default=None,
        serialization_alias="rdfs:subpropertyOf",
        title="Subproperty Of",
        description="A property of which the described term is a sub-property.",
        repr=False,
        json_schema_extra={
            "$id": "https://www.w3.org/TR/rdf-schema/#ch_subpropertyof"
        },
    )

    subclass_of: Optional[str] = Field(
        default=None,
        serialization_alias="rdfs:subclassOf",
        title="Subclass Of",
        description="A class of which the described term is a sub-class.",
        repr=False,
        json_schema_extra={
            "$id": "https://www.w3.org/TR/rdf-schema/#ch_subclassof"
        },
    )

    domain: Optional[str] = Field(
        default=None,
        serialization_alias="rdfs:domain",
        title="Domain",
        description=(
            "A class of which a resource described by the term is an instance."
        ),
        repr=False,
        json_schema_extra={
            "$id": "https://www.w3.org/TR/rdf-schema/#ch_domain"
        },
    )

    domain_includes: Optional[str] = Field(
        default=None,
        serialization_alias="dcam:domainIncludes",
        title="Domain Includes",
        description=("A suggested class for subjects of this property."),
        repr=False,
        json_schema_extra={"$id": "http://purl.org/dc/dcam/domainIncludes"},
    )

    term_range: Optional[str] = Field(
        default=None,
        serialization_alias="rdfs:range",
        alias="range",
        title="Range",
        description=(
            "A class of which a value described by the term is an instance."
        ),
        json_schema_extra={
            "$id": "https://www.w3.org/TR/rdf-schema/#ch_range"
        },
        repr=False,
    )

    range_includes: Optional[str] = Field(
        default=None,
        serialization_alias="dcam:rangeIncludes",
        title="Range Includes",
        description="A suggested class for values of this property.",
        repr=False,
        json_schema_extra={"$id": "http://purl.org/dc/dcam/rangeIncludes"},
    )

    member_of: Optional[str] = Field(
        default=None,
        serialization_alias="dcam:memberOf",
        title="Member Of",
        description="A collection of which the described term is a member.",
        repr=False,
        json_schema_extra={"$id": "http://purl.org/dc/dcam/memberOf"},
    )

    instance_of: Optional[str] = Field(
        default=None,
        serialization_alias="instanceOf",
        title="Instance Of",
        description="A class of which the described term is an instance.",
        repr=False,
    )

    equivalent_property: Optional[str] = Field(
        default=None,
        serialization_alias="owl:equivalentProperty",
        title="Equivalent Property",
        description="A property to which the described term is equivalent.",
        repr=False,
        json_schema_extra={
            "$id": "https://www.w3.org/TR/owl-ref/#equivalentProperty-def"
        },
    )

    description: Optional[str] = Field(
        default=None,
        serialization_alias="dcterms:description",
        title="Description",
        description="An account of the resource.",
        repr=False,
        json_schema_extra={"$id": "http://purl.org/dc/terms/description"},
    )

    scope_note: Optional[str] = Field(
        default=None,
        serialization_alias="skos:scopeNote",
        title="Scope Note",
        description=(
            "A note that helps to clarify the meaning and/or the "
            "use of a concept."
        ),
        repr=False,
        json_schema_extra={
            "$id": "https://www.w3.org/2012/09/odrl/semantic/draft/doco/skos_scopeNote"
        },
    )

    def __hash__(self):
        return hash(self.name)


class TermRegistryError(Exception):
    """Base exception for all TermRegistry related errors."""


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

        return message


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
            raise KeyError(f"A term with the key '{key}' already exists.")

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
        del self._terms[key]

    def add_term(
        self,
        term: Term,
        key: Optional[str] = None,
    ) -> None:
        """Register a term, optionally defaulting the key to `term.name`.

        Parameters
        ----------
        term : Term
            The `Term` object to add.
        key : Optional[str], optional
            The key to use for registration. If None, `term.name` is used.
            Defaults to None.

        Raises
        ------
        KeyError
            If the chosen key already exists.
        """
        key = key or term.name
        self[key] = term

    def get(self, key: str, default: Optional[Term] = None) -> Optional[Term]:
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
        del self._terms[key]

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
        return False

    if ignore_case:
        return query.lower() in value.lower()

    return query in value
