import pytest

from soundevent.data.terms import Term
from soundevent.terms.registry import (
    MultipleTermsFoundError,
    TermNotFoundError,
    TermOverrideError,
    TermRegistry,
)

test_term = Term(name="test", label="Test", definition="test")


@pytest.fixture
def term1() -> Term:
    return Term(
        name="test1",
        uri="http://terms.org/category/color/blue",
        label="Color Blue",
        definition="Blue is the color of the sky and the oceans, best color overall.",
    )


@pytest.fixture
def term2() -> Term:
    return Term(
        name="test2",
        uri="http://terms.org/category/animal/cat",
        label="Animal (Cat)",
        definition="Cats are humans best friends.",
    )


@pytest.fixture
def example_registry(term1: Term, term2: Term) -> TermRegistry:
    registry = TermRegistry()
    registry.add_term(term=term1, key="key1")
    registry.add_term(term=term2, key="key2")
    return registry


def test_term_registry_initialization():
    registry = TermRegistry()
    assert len(registry) == 0
    assert test_term not in registry

    initial_terms = {"test_term": test_term}
    registry = TermRegistry(terms=initial_terms)
    assert len(registry) == 1
    assert "test_term" in registry
    assert registry["test_term"] is test_term


def test_term_registry_add_term_term():
    registry = TermRegistry()
    registry.add_term(key="test_key", term=test_term)
    assert "test_key" in registry
    assert len(registry) == 1
    assert registry["test_key"] is test_term


def test_term_registry_set_term_key():
    registry = TermRegistry()
    registry["test_key"] = test_term
    assert "test_key" in registry
    assert len(registry) == 1
    assert registry["test_key"] is test_term


def test_term_registry_set_term_fails_if_not_term():
    registry = TermRegistry()
    with pytest.raises(TypeError):
        registry["test"] = "not a term"  # type: ignore


def test_term_registry_delete_term():
    registry = TermRegistry()
    registry.add_term(key="test_key", term=test_term)

    del registry["test_key"]
    assert "test_key" not in registry
    assert len(registry) == 0


def test_term_registry_remove_term():
    registry = TermRegistry()
    registry.add_term(key="test_key", term=test_term)

    registry.remove("test_key")
    assert "test_key" not in registry
    assert len(registry) == 0


def test_term_registry_remove_term_fails_if_not_found(
    example_registry: TermRegistry,
):
    with pytest.raises(KeyError):
        example_registry.remove("key3")


def test_term_registry_get_term():
    registry = TermRegistry()
    registry.add_term(key="test_key", term=test_term)
    assert "test_key" in registry
    retrieved_term = registry["test_key"]
    assert retrieved_term is test_term


def test_term_registry_get_fails_if_not_found(example_registry: TermRegistry):
    with pytest.raises(KeyError):
        example_registry["key3"]


def test_term_registry_get_term_via_method(
    example_registry: TermRegistry,
    term1: Term,
):
    retrieved_term = example_registry.get("key1")
    assert retrieved_term is term1


def test_term_registry_get_returns_none_if_not_found_by_default(
    example_registry: TermRegistry,
):
    assert example_registry.get("key3") is None


def test_term_registry_get_returns_custom_default_if_not_found(
    example_registry: TermRegistry,
    term2: Term,
):
    assert example_registry.get("key3", default=term2) is term2


def test_term_registry_get_fails_if_custom_default_is_not_a_term(
    example_registry: TermRegistry,
):
    with pytest.raises(ValueError):
        example_registry.get("key3", default="string")  # type: ignore


def test_term_registry_can_iterate(
    example_registry: TermRegistry,
    term1: Term,
    term2: Term,
):
    raw_dict = {key: term for key, term in example_registry.items()}
    assert "key1" in raw_dict
    assert raw_dict["key1"] is term1
    assert "key2" in raw_dict
    assert raw_dict["key2"] is term2


def test_term_registry_defaults_to_term_name_as_key():
    registry = TermRegistry()
    registry.add_term(term=test_term)
    assert "test" in registry
    assert registry["test"] is test_term


def test_term_registry_add_term_duplicate_term():
    registry = TermRegistry()
    registry.add_term(key="test_key", term=test_term)

    with pytest.raises(TermOverrideError):
        registry.add_term(key="test_key", term=test_term)


def test_add_term_override_with_force(
    example_registry: TermRegistry, term1: Term
):
    """Test that add_term can override a term with force=True."""
    new_term = Term(name="new", label="New", definition="New term.")

    # Check that we cannot override by default
    with pytest.raises(
        TermOverrideError,
        match="Cannot override existing term",
    ) as excinfo:
        example_registry.add_term(new_term, key="key1")

    assert excinfo.value.key == "key1"
    assert excinfo.value.term == term1

    # Now, use force=True to override
    example_registry.add_term(new_term, key="key1", force=True)

    # Check that the term has been overridden
    assert example_registry["key1"] is new_term


def test_term_registry_get_term_not_found():
    registry = TermRegistry()

    with pytest.raises(KeyError, match="Key='non_existent_key'"):
        registry["non_existent_key"]


def test_term_registry_get_keys(example_registry: TermRegistry):
    keys = set(example_registry.keys())
    assert keys == {"key1", "key2"}


def test_term_registry_can_get_by_label(
    term1: Term, example_registry: TermRegistry
):
    retrieved_term = example_registry.get_by(label="Color Blue")
    assert retrieved_term is term1


def test_term_registry_get_by_label_fails_if_not_found(
    example_registry: TermRegistry,
):
    with pytest.raises(TermNotFoundError, match="Criteria={label='UnLabel'}"):
        example_registry.get_by(label="UnLabel")


def test_term_registry_fails_if_multiple_matches():
    registry = TermRegistry()
    term1 = Term(name="test1", label="Test", definition="test")
    term2 = Term(name="test2", label="Test", definition="test")
    registry.add_term(term=term1, key="key1")
    registry.add_term(term=term2, key="key2")

    with pytest.raises(
        MultipleTermsFoundError,
        match="Found 2 terms matching",
    ):
        registry.get_by(label="Test")


def test_term_registry_can_get_by_name(
    term2: Term, example_registry: TermRegistry
):
    retrieved_term = example_registry.get_by(name="test2")
    assert retrieved_term is term2


def test_term_registry_get_by_name_fails_if_not_found(
    example_registry: TermRegistry,
):
    with pytest.raises(TermNotFoundError, match="Criteria={name='test3'}"):
        example_registry.get_by(name="test3")


def test_term_registry_can_get_by_uri(
    example_registry: TermRegistry, term2: Term
):
    retrieved_term = example_registry.get_by(
        uri="http://terms.org/category/animal/cat"
    )
    assert retrieved_term is term2


def test_term_registry_get_by_uri_fails_if_not_found(
    example_registry: TermRegistry,
):
    with pytest.raises(TermNotFoundError):
        example_registry.get_by(uri="http://terms.org/test/test3")


def test_term_registry_get_by_fails_if_by_not_provided(
    example_registry: TermRegistry,
):
    with pytest.raises(ValueError):
        example_registry.get_by()


def test_term_registry_get_by_fails_with_multiple_criteria(
    example_registry: TermRegistry,
):
    with pytest.raises(ValueError):
        example_registry.get_by(name="test", label="Animal")


def test_term_registry_can_find_by_name(
    example_registry: TermRegistry,
    term1: Term,
    term2: Term,
):
    retrieved = example_registry.find(name="test")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1, term2}

    # Search is case insensitive by default
    retrieved = example_registry.find(name="TeSt")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1, term2}

    # Search is case insensitive by default
    retrieved = example_registry.find(name="TeSt", ignore_case=False)
    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


def test_term_registry_can_find_by_uri(
    example_registry: TermRegistry,
    term1: Term,
    term2: Term,
):
    retrieved = example_registry.find(uri="category")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1, term2}

    retrieved = example_registry.find(uri="color")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1}

    retrieved = example_registry.find(uri="animal")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term2}


def test_term_registry_can_find_by_label(
    example_registry: TermRegistry,
    term1: Term,
    term2: Term,
):
    retrieved = example_registry.find(label="l")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1, term2}

    retrieved = example_registry.find(label="blue")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1}

    retrieved = example_registry.find(label="z")
    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


def test_term_registry_can_find_by_definition(
    example_registry: TermRegistry,
    term1: Term,
    term2: Term,
):
    retrieved = example_registry.find(definition="best")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1, term2}

    retrieved = example_registry.find(definition="oceans")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1}

    retrieved = example_registry.find(definition="friend")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term2}


def test_term_registry_can_find_by_multiple_criteria(
    example_registry: TermRegistry,
    term1: Term,
    term2: Term,
):
    retrieved = example_registry.find(definition="best", label="color")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1}

    retrieved = example_registry.find(definition="best", uri="animal")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term2}

    retrieved = example_registry.find(label="color", uri="animal")
    assert isinstance(retrieved, list)
    assert len(retrieved) == 0


def test_term_registry_can_find_with_query(
    example_registry: TermRegistry,
    term1: Term,
    term2: Term,
):
    retrieved = example_registry.find(q="best")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1, term2}

    retrieved = example_registry.find(q="terms.org")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1, term2}

    retrieved = example_registry.find(q="test1")
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1}


def test_term_registry_find_without_criteria_returns_all_terms(
    example_registry: TermRegistry,
    term1: Term,
    term2: Term,
):
    retrieved = example_registry.find()
    assert isinstance(retrieved, list)
    assert set(retrieved) == {term1, term2}


def test_term_registry_find_fails_if_query_and_criteria_are_provided(
    example_registry: TermRegistry,
):
    with pytest.raises(ValueError):
        example_registry.find(q="test", name="Test")
