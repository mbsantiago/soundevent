"""Test cases for the terms API."""

import pytest

from soundevent.data import Term
from soundevent.terms import (
    MultipleTermsFoundError,
    TermNotFoundError,
    TermOverrideError,
    TermRegistry,
    add_term,
    find_term,
    get_global_term_registry,
    get_term,
    get_term_by,
    has_term,
    remove_term,
    set_global_term_registry,
)


@pytest.fixture
def term1() -> Term:
    """Return a sample term for testing."""
    return Term(
        name="term1",
        label="Term 1",
        definition="This is the first term.",
        uri="http://example.com/term1",
    )


@pytest.fixture
def term2() -> Term:
    """Return another sample term for testing."""
    return Term(
        name="term2",
        label="Term 2",
        definition="This is the second term.",
        uri="http://example.com/term2",
    )


def test_get_global_term_registry(global_registry: TermRegistry):
    """Test that the global registry can be retrieved."""
    assert get_global_term_registry() is global_registry


def test_set_global_term_registry():
    """Test that a new global registry can be set."""
    new_registry = TermRegistry()
    set_global_term_registry(new_registry)
    assert get_global_term_registry() is new_registry


def test_has_term(term1: Term):
    """Test checking for a term's existence."""
    add_term(term1)
    assert has_term("term1")
    assert not has_term("non_existent")


def test_has_term_on_provided_registry(term1: Term):
    """Test checking for a term on a specific registry."""
    registry = TermRegistry()
    registry.add_term(term1)
    assert has_term("term1", term_registry=registry)
    assert not has_term("non_existent", term_registry=registry)


def test_get_term(term1: Term):
    """Test retrieving a term."""
    add_term(term1)
    assert get_term("term1") is term1
    assert get_term("non_existent") is None
    assert get_term("non_existent", default=term1) is term1


def test_get_term_on_provided_registry(term1: Term):
    """Test retrieving a term from a specific registry."""
    registry = TermRegistry()
    registry.add_term(term1)
    assert get_term("term1", term_registry=registry) is term1


def test_add_term(term1: Term):
    """Test adding a term."""
    add_term(term1)
    assert has_term("term1")


def test_add_term_with_key(term1: Term):
    """Test adding a term with a specific key."""
    add_term(term1, key="custom_key")
    assert has_term("custom_key")


def test_add_term_override_fails(term1: Term):
    """Test that overriding a term fails by default."""
    add_term(term1)
    with pytest.raises(TermOverrideError):
        add_term(term1)


def test_add_term_override_with_force(term1: Term, term2: Term):
    """Test that a term can be overridden with force=True."""
    add_term(term1)
    add_term(term2, key="term1", force=True)
    assert get_term("term1") is term2


def test_add_term_to_provided_registry(term1: Term):
    """Test adding a term to a specific registry."""
    registry = TermRegistry()
    add_term(term1, term_registry=registry)
    assert "term1" in registry


def test_remove_term(term1: Term):
    """Test removing a term."""
    add_term(term1)
    remove_term("term1")
    assert not has_term("term1")


def test_remove_term_fails_if_not_found():
    """Test that removing a non-existent term fails."""
    with pytest.raises(KeyError):
        remove_term("non_existent")


def test_remove_term_from_provided_registry(term1: Term):
    """Test removing a term from a specific registry."""
    registry = TermRegistry()
    registry.add_term(term1)
    remove_term("term1", term_registry=registry)
    assert "term1" not in registry


def test_get_term_by(term1: Term, term2: Term):
    """Test retrieving a term by its attributes."""
    add_term(term1)
    add_term(term2)
    assert get_term_by(label="Term 1") is term1
    assert get_term_by(name="term2") is term2
    assert get_term_by(uri="http://example.com/term1") is term1


def test_get_term_by_raises_errors(term1: Term, term2: Term):
    """Test errors raised by get_term_by."""
    add_term(term1)
    add_term(term2)
    term_dup = Term(name="dup", label="Term 1", definition="dup")
    add_term(term_dup)

    with pytest.raises(ValueError):
        get_term_by()

    with pytest.raises(ValueError):
        get_term_by(label="Term 1", name="term2")

    with pytest.raises(TermNotFoundError):
        get_term_by(label="non_existent")

    with pytest.raises(MultipleTermsFoundError):
        get_term_by(label="Term 1")


def test_get_term_by_on_provided_registry(term1: Term):
    """Test retrieving a term by attribute from a specific registry."""
    registry = TermRegistry()
    registry.add_term(term1)
    assert get_term_by(label="Term 1", term_registry=registry) is term1


def test_find_term(term1: Term, term2: Term):
    """Test finding terms with various criteria."""
    add_term(term1)
    add_term(term2)

    assert find_term(label="Term") == [term1, term2]
    assert find_term(label="Term 1") == [term1]
    assert find_term(name="term", definition="second") == [term2]
    assert find_term(q="second") == [term2]
    assert find_term(q="term") == [term1, term2]
    assert set(find_term()) == {term1, term2}


def test_find_term_ignore_case(term1: Term):
    """Test case-insensitivity when finding terms."""
    add_term(term1)
    assert find_term(label="term 1") == [term1]
    assert find_term(label="term 1", ignore_case=False) == []


def test_find_term_on_provided_registry(term1: Term):
    """Test finding terms on a specific registry."""
    registry = TermRegistry()
    registry.add_term(term1)
    assert find_term(label="Term 1", term_registry=registry) == [term1]


def test_find_term_with_q_and_kwargs_raises_error():
    """Test that using q with other criteria raises an error."""
    with pytest.raises(ValueError):
        find_term(q="test", name="test")
