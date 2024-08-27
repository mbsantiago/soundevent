"""Test suite for terms."""

from soundevent import terms


def test_term_fields_only_show_the_label_in_the_repr():
    assert repr(terms.scientific_name) == "Term(label='Scientific Taxon Name')"
