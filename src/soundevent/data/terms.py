"""Terms module.

Soundevent uses a specialized object to refer to specific standardised terms.
Using standardised terms ensures it's easier to interpret tags and features as
well as sharing data with others. It makes it much clearer how to incorporate
with existing corpus of data.

"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "Term",
]


class Term(BaseModel):
    """A term class for a standardised term."""

    model_config = ConfigDict(frozen=True, extra="allow")

    # Minimal set of attributes according to the DCMI Metadata Terms

    label: str = Field(
        title="Label",
        description="The human-readable label assigned to the term.",
        repr=True,
    )

    definition: str = Field(
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
        default=None,
        title="URI",
        repr=False,
        description=(
            "The Uniform Resource Identifier used to uniquely identify a term."
        ),
        json_schema_extra={"$id": "http://purl.org/dc/terms/URI"},
    )

    type_of_term: str = Field(
        default="property",
        alias="type",
        title="Type",
        description="The nature or genre of the resource.",
        repr=False,
        json_schema_extra={"$id": "http://purl.org/dc/terms/type"},
    )

    # Additional attributes according to the DCMI Metadata

    comment: Optional[str] = Field(
        default=None,
        title="Comment",
        description="Additional information about the term or its application.",
        repr=False,
    )

    see: Optional[str] = Field(
        default=None,
        title="See",
        description="Authoritative documentation related to the term.",
        repr=False,
    )

    subproperty_of: Optional[str] = Field(
        default=None,
        serialization_alias="subpropertyOf",
        title="Subproperty Of",
        description="A property of which the described term is a sub-property.",
        repr=False,
    )

    superclass_of: Optional[str] = Field(
        default=None,
        serialization_alias="superclassOf",
        title="Superclass Of",
        description="A class of which the described term is a super-class.",
        repr=False,
    )

    subclass_of: Optional[str] = Field(
        default=None,
        serialization_alias="subclassOf",
        title="Subclass Of",
        description="A class of which the described term is a sub-class.",
        repr=False,
    )

    domain: Optional[str] = Field(
        default=None,
        title="Domain",
        description=(
            "A class of which a resource described by the term is an instance."
        ),
        repr=False,
    )

    domain_includes: Optional[str] = Field(
        default=None,
        serialization_alias="domainIncludes",
        title="Domain Includes",
        description=("A suggested class for subjects of this property."),
        repr=False,
        json_schema_extra={"$id": "http://purl.org/dc/dcam/domainIncludes"},
    )

    term_range: Optional[str] = Field(
        default=None,
        alias="range",
        title="Range",
        description=(
            "A class of which a value described by the term is an instance."
        ),
        repr=False,
    )

    range_includes: Optional[str] = Field(
        default=None,
        serialization_alias="rangeIncludes",
        title="Range Includes",
        description="A suggested class for values of this property.",
        repr=False,
        json_schema_extra={"$id": "http://purl.org/dc/dcam/rangeIncludes"},
    )

    member_of: Optional[str] = Field(
        default=None,
        serialization_alias="memberOf",
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
        serialization_alias="equivalentProperty",
        title="Equivalent Property",
        description="A property to which the described term is equivalent.",
        repr=False,
    )

    description: Optional[str] = Field(
        default=None,
        title="Description",
        description="An account of the resource.",
        repr=False,
        json_schema_extra={"$id": "http://purl.org/dc/terms/description"},
    )

    scope_note: Optional[str] = Field(
        default=None,
        serialization_alias="scopeNote",
        title="Scope Note",
        description=(
            "A note that helps to clarify the meaning and/or the "
            "use of a concept."
        ),
        repr=False,
        json_schema_extra={
            "$id": "https://www.w3.org/2012/09/odrl/semantic/draft/doco/skos_scopeNote.html"
        },
    )

    def __hash__(self):
        return hash(self.name)
