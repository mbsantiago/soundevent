import pytest

from soundevent import terms


@pytest.fixture(autouse=True)
def global_registry() -> terms.TermRegistry:
    """Set a clean global term registry for each test."""
    registry = terms.TermRegistry()
    terms.set_global_term_registry(registry)
    return registry
