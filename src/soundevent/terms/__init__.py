"""Terms module.

This module provides pre-defined [`Term`][soundevent.data.Term] objects for
working with soundevent data. These terms are aligned with established metadata
standards whenever possible, promoting consistency and interoperability across
projects.
"""

from soundevent.data import Term
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
    "accuracy",
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
    "genus",
    "high_freq",
    "jaccard_index",
    "location_id",
    "low_freq",
    "mean_average_precision",
    "num_segments",
    "order",
    "scientific_name",
    "state_province",
    "taxonomic_class",
    "top_3_accuracy",
    "true_class_probability",
]
