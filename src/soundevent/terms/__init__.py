"""Terms module.

This module provides tools for creating and managing standardized terms.

In the soundevent ecosystem, metadata is stored in `Tag` objects, which are
pairs of a `Term` and a `value`. The `Term` provides a standardized
definition that gives context and meaning to the `value`. For example, the
`Term` `scientific_name` gives meaning to the `value` `"Turdus migratorius"`.
Using standardized terms makes data understandable, shareable, and interoperable.

This module provides three main features:

1.  **Pre-defined Terms**: A collection of standard terms for common concepts
    in bioacoustics (e.g., `scientific_name`, `f1_score`).
2.  **Global API**: A set of functions (`find_term`, `add_term`, etc.) for
    managing terms in a global registry.
3.  **`TermRegistry` Class**: The underlying class for creating and managing
    custom term collections.

Example
-------
>>> from soundevent.data import Tag, Term
>>> from soundevent.terms import scientific_name, add_term, find_term
>>>
>>> # A list of tags that might be attached to a sound event
>>> tags = []
>>>
>>> # Use a pre-defined term to create a Tag
>>> species_tag = Tag(term=scientific_name, value="Turdus migratorius")
>>> tags.append(species_tag)
>>>
>>> print(f"{tags[0].term.label}: {tags[0].value}")
Scientific Name: Turdus migratorius
>>>
>>> # Create and use a custom term for a new Tag
>>> add_term(
...     Term(
...         name="custom:quality",
...         label="Quality",
...         definition="The quality of the recording, from 1 (poor) to 5 (excellent).",
...     )
... )
>>> quality_term = find_term(q="quality")[0]
>>> quality_tag = Tag(term=quality_term, value="4")
>>> tags.append(quality_tag)
>>>
>>> print(f"{tags[1].term.label}: {tags[1].value}")
Quality: 4
"""

from soundevent.data import Term
from soundevent.terms.api import (
    add_term,
    find_term,
    get_global_term_registry,
    get_term,
    get_term_by,
    has_term,
    remove_term,
    set_global_term_registry,
)
from soundevent.terms.devices import capture_device
from soundevent.terms.geography import (
    country,
    county,
    elevation,
    location_id,
    state_province,
)
from soundevent.terms.metrics import (
    accuracy,
    average_precision,
    balanced_accuracy,
    f1_score,
    jaccard_index,
    mean_average_precision,
    top_3_accuracy,
    true_class_probability,
)
from soundevent.terms.registry import (
    MultipleTermsFoundError,
    TermNotFoundError,
    TermRegistry,
)
from soundevent.terms.roi import (
    bandwidth,
    duration,
    high_freq,
    low_freq,
    num_segments,
)
from soundevent.terms.taxonomy import (
    common_name,
    family,
    genus,
    order,
    scientific_name,
    taxonomic_class,
)

alternative = Term(
    uri="http://purl.org/dc/terms/alternative",
    name="dcterms:alternative",
    label="Alternative",
    definition="An alternative name for the resource.",
    scope_note="Can be used to reference an identifier from an external source for a resource within a new collection, acting as a cross-reference.",
)

__all__ = [
    "MultipleTermsFoundError",
    "TermNotFoundError",
    "TermRegistry",
    "accuracy",
    "add_term",
    "alternative",
    "average_precision",
    "balanced_accuracy",
    "bandwidth",
    "capture_device",
    "common_name",
    "country",
    "county",
    "duration",
    "elevation",
    "f1_score",
    "family",
    "find_term",
    "genus",
    "get_global_term_registry",
    "get_term",
    "get_term_by",
    "has_term",
    "high_freq",
    "jaccard_index",
    "location_id",
    "low_freq",
    "mean_average_precision",
    "num_segments",
    "order",
    "remove_term",
    "scientific_name",
    "set_global_term_registry",
    "state_province",
    "taxonomic_class",
    "top_3_accuracy",
    "true_class_probability",
]
