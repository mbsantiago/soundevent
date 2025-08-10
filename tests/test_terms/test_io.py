import json
import shutil
from pathlib import Path

import pytest

from soundevent.data import Term
from soundevent.terms.api import (
    add_term,
    get_global_term_registry,
    get_term,
    has_term,
)
from soundevent.terms.io import (
    TermSet,
    add_terms_from_file,
    infer_term_set_format,
    load_term_set_from_csv,
    load_term_set_from_file,
    load_term_set_from_json,
    register_term_set,
)
from soundevent.terms.registry import (
    TermNotFoundError,
    TermOverrideError,
    TermRegistry,
)


@pytest.fixture
def sample_term_1() -> Term:
    return Term(
        name="scientificName",
        label="Scientific Name",
        definition="The full scientific name.",
        uri="http://example.com/scientificName",
    )


@pytest.fixture
def sample_term_2() -> Term:
    return Term(
        name="captureDevice",
        label="Capture Device",
        definition="The device used to create the resource.",
        uri="http://example.com/captureDevice",
    )


@pytest.fixture
def sample_term_3() -> Term:
    return Term(
        name="habitat",
        label="Habitat",
        definition="The natural environment of an organism.",
        uri="http://example.com/habitat",
    )


@pytest.fixture
def term_json_file_simple_list(
    tmp_path: Path, sample_term_1: Term, sample_term_2: Term
) -> Path:
    content = [
        sample_term_1.model_dump(exclude_unset=True),
        sample_term_2.model_dump(exclude_unset=True),
    ]
    file_path = tmp_path / "terms_simple.json"
    with open(file_path, "w") as f:
        json.dump(content, f)
    return file_path


@pytest.fixture
def term_json_file_structured(
    tmp_path: Path, sample_term_1: Term, sample_term_2: Term
) -> Path:
    content = {
        "terms": [
            sample_term_1.model_dump(exclude_unset=True),
            sample_term_2.model_dump(exclude_unset=True),
        ],
        "aliases": {
            "species": "scientificName",
            "device": "captureDevice",
        },
    }
    file_path = tmp_path / "terms_structured.json"
    with open(file_path, "w") as f:
        json.dump(content, f)
    return file_path


@pytest.fixture
def term_json_file_invalid(tmp_path: Path) -> Path:
    file_path = tmp_path / "terms_invalid.json"
    with open(file_path, "w") as f:
        f.write("This is not valid JSON.")
    return file_path


@pytest.fixture
def term_csv_file_no_aliases(tmp_path: Path) -> Path:
    content = """name,label,definition,uri
scientificName,Scientific Name,The full scientific name.,http://example.com/scientificName
captureDevice,Capture Device,The device used to create the resource.,http://example.com/captureDevice
"""
    file_path = tmp_path / "terms_no_aliases.csv"
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def term_csv_file_with_aliases(tmp_path: Path) -> Path:
    content = """name,label,definition,uri,alias
scientificName,Scientific Name,The full scientific name.,http://example.com/scientificName,species
captureDevice,Capture Device,The device used to create the resource.,http://example.com/captureDevice,device
"""
    file_path = tmp_path / "terms_with_aliases.csv"
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def term_csv_file_empty_fields(tmp_path: Path) -> Path:
    content = """name,label,definition,uri
scientificName,Scientific Name,The full scientific name.,http://example.com/scientificName
captureDevice,Capture Device,The device used to create the resource.,
"""
    file_path = tmp_path / "terms_empty_fields.csv"
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def term_csv_file_missing_name(tmp_path: Path) -> Path:
    content = """label,definition,uri
Scientific Name,The full scientific name.,http://example.com/scientificName
"""
    file_path = tmp_path / "terms_missing_name.csv"
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def term_set_simple(sample_term_1: Term, sample_term_2: Term) -> TermSet:
    return TermSet(terms=[sample_term_1, sample_term_2])


@pytest.fixture
def term_set_with_aliases(sample_term_1: Term, sample_term_2: Term) -> TermSet:
    return TermSet(
        terms=[sample_term_1, sample_term_2],
        aliases={
            "species": "scientificName",
            "device": "captureDevice",
        },
    )


def test_load_from_json_simple_list(
    term_json_file_simple_list: Path,
    sample_term_1: Term,
    sample_term_2: Term,
):
    term_set = load_term_set_from_json(term_json_file_simple_list)
    assert len(term_set.terms) == 2
    assert term_set.terms[0] == sample_term_1
    assert term_set.terms[1] == sample_term_2
    assert not term_set.aliases


def testload_term_set_from_json_structured_object(
    term_json_file_structured: Path,
    sample_term_1: Term,
    sample_term_2: Term,
):
    term_set = load_term_set_from_json(term_json_file_structured)
    assert len(term_set.terms) == 2
    assert term_set.terms[0] == sample_term_1
    assert term_set.terms[1] == sample_term_2
    assert term_set.aliases == {
        "species": "scientificName",
        "device": "captureDevice",
    }


def testload_term_set_from_json_invalid_format_raises_error(
    term_json_file_invalid: Path,
):
    with pytest.raises(ValueError):
        load_term_set_from_json(term_json_file_invalid)


def testload_term_set_from_csv_no_aliases(
    term_csv_file_no_aliases: Path, sample_term_1: Term, sample_term_2: Term
):
    term_set = load_term_set_from_csv(term_csv_file_no_aliases)
    assert len(term_set.terms) == 2
    assert term_set.terms[0] == sample_term_1
    assert term_set.terms[1] == sample_term_2
    assert not term_set.aliases


def testload_term_set_from_csv_with_aliases(
    term_csv_file_with_aliases: Path, sample_term_1: Term, sample_term_2: Term
):
    term_set = load_term_set_from_csv(term_csv_file_with_aliases)
    assert len(term_set.terms) == 2
    assert term_set.terms[0] == sample_term_1
    assert term_set.terms[1] == sample_term_2
    assert term_set.aliases == {
        "species": "scientificName",
        "device": "captureDevice",
    }


def testload_term_set_from_csv_empty_fields(term_csv_file_empty_fields: Path):
    term_set = load_term_set_from_csv(term_csv_file_empty_fields)
    assert len(term_set.terms) == 2
    assert term_set.terms[0].uri == "http://example.com/scientificName"
    assert term_set.terms[1].uri is None


def testload_term_set_from_csv_missing_name_field_raises_error(
    term_csv_file_missing_name: Path,
):
    with pytest.raises(ValueError):
        load_term_set_from_csv(term_csv_file_missing_name)


def testinfer_term_set_format_json(tmp_path: Path):
    file_path = tmp_path / "test.json"
    file_path.touch()
    assert infer_term_set_format(file_path) == "json"


def testinfer_term_set_format_csv(tmp_path: Path):
    file_path = tmp_path / "test.csv"
    file_path.touch()
    assert infer_term_set_format(file_path) == "csv"


def testinfer_term_set_format_unknown_extension_raises_error(tmp_path: Path):
    file_path = tmp_path / "test.txt"
    file_path.touch()
    with pytest.raises(ValueError):
        infer_term_set_format(file_path)


def test_load_term_set_from_file_explicit_format(
    tmp_path: Path,
    term_json_file_simple_list: Path,
    sample_term_1: Term,
):
    path = tmp_path / "file_with_weird_extension.notjson"
    shutil.copy(term_json_file_simple_list, path)

    term_set = load_term_set_from_file(path, format="json")
    assert len(term_set.terms) == 2
    assert term_set.terms[0] == sample_term_1


def test_load_term_set_from_file_inferred_format(
    term_csv_file_no_aliases: Path,
    sample_term_1: Term,
):
    term_set = load_term_set_from_file(term_csv_file_no_aliases)
    assert len(term_set.terms) == 2
    assert term_set.terms[0] == sample_term_1


def test_load_term_set_from_file_explicit_format_mismatch_raises_error(
    term_csv_file_no_aliases: Path,
):
    with pytest.raises(ValueError):
        load_term_set_from_file(term_csv_file_no_aliases, format="json")


def test_load_term_set_from_file_unsupported_explicit_format_raises_error(
    term_json_file_simple_list: Path,
):
    with pytest.raises(ValueError):
        load_term_set_from_file(
            term_json_file_simple_list,
            format="xml",  # type: ignore
        )


def test_load_term_set_from_file_non_existent_file_raises_error(
    tmp_path: Path,
):
    non_existent_file = tmp_path / "non_existent.json"
    with pytest.raises(FileNotFoundError):
        load_term_set_from_file(non_existent_file)


def test_register_term_set_to_global_registry(
    term_set_simple: TermSet,
    sample_term_1: Term,
):
    register_term_set(term_set_simple)
    assert get_term("scientificName") == sample_term_1


def test_register_term_set_to_specific_registry(
    term_set_simple: TermSet, sample_term_1: Term
):
    registry = TermRegistry()
    register_term_set(term_set_simple, term_registry=registry)
    assert registry["scientificName"] == sample_term_1


def test_register_term_set_default_behavior_skips_existing_terms(
    term_set_simple: TermSet,
    sample_term_1: Term,
    sample_term_2: Term,
):
    add_term(sample_term_1)
    register_term_set(term_set_simple)
    assert get_term("scientificName") == sample_term_1
    assert get_term("captureDevice") == sample_term_2


def test_register_term_set_raises_error_on_override_if_not_ignored(
    term_set_simple: TermSet,
    sample_term_1: Term,
):
    add_term(sample_term_1)
    with pytest.raises(TermOverrideError):
        register_term_set(term_set_simple, ignore_overrides=False)


def test_register_term_set_overwrites_existing_terms(
    term_set_simple: TermSet,
    sample_term_1: Term,
    sample_term_2: Term,
):
    add_term(sample_term_1)
    register_term_set(term_set_simple, override_existing=True)
    assert get_term("scientificName") == sample_term_1
    assert get_term("captureDevice") == sample_term_2


def test_register_term_set_aliases_skipped_if_target_missing_and_ignored(
    sample_term_1: Term,
    sample_term_2: Term,
):
    assert not has_term("non-existent")
    term_set = TermSet(
        terms=[sample_term_1, sample_term_2],
        aliases={
            "key": "non-existent",
        },
    )

    register_term_set(term_set)
    assert not has_term("key")


def test_register_term_set_raises_error_if_alias_target_missing_and_not_ignored(
    sample_term_1: Term,
    sample_term_2: Term,
):
    assert not has_term("non-existent")
    term_set = TermSet(
        terms=[sample_term_1, sample_term_2],
        aliases={
            "key": "non-existent",
        },
    )

    with pytest.raises(TermNotFoundError):
        register_term_set(term_set, ignore_missing_key=False)


def test_register_term_set_aliases_overwritten_with_force(
    sample_term_1: Term,
    sample_term_2: Term,
    sample_term_3: Term,
):
    # Add term with species key
    add_term(sample_term_3, key="species")
    assert has_term("species")

    term_set = TermSet(
        terms=[sample_term_1, sample_term_2],
        aliases={
            "species": sample_term_1.name,
        },
    )

    register_term_set(term_set, override_existing=True)
    assert get_term("species") == sample_term_1


def test_register_term_set_aliases_raise_error_on_override_if_not_ignored(
    term_set_with_aliases: TermSet,
    sample_term_1: Term,
):
    add_term(sample_term_1, key="species")
    with pytest.raises(TermOverrideError):
        register_term_set(term_set_with_aliases, ignore_overrides=False)


def test_register_term_set_aliases_skipped_on_override_if_ignored(
    term_set_with_aliases: TermSet,
    sample_term_1: Term,
):
    add_term(sample_term_1, key="species")
    register_term_set(term_set_with_aliases, ignore_overrides=True)
    assert get_term("species") == sample_term_1


def test_register_term_set_with_mixed_terms_and_aliases(
    sample_term_1: Term,
    sample_term_2: Term,
    sample_term_3: Term,
):
    add_term(sample_term_1)
    add_term(sample_term_2, key="existing_alias")

    term_set = TermSet(
        terms=[
            sample_term_1,
            sample_term_3,
        ],
        aliases={
            "species": "scientificName",
            "existing_alias": "captureDevice",
            "non_existent_target": "unknownTerm",
        },
    )

    register_term_set(term_set)

    registry = get_global_term_registry()
    assert registry["scientificName"] == sample_term_1
    assert registry["habitat"] == sample_term_3
    assert registry["species"] == sample_term_1
    assert registry["existing_alias"] == sample_term_2
    assert "non_existent_target" not in registry


def test_register_term_set_with_alias_referencing_term_in_same_set(
    sample_term_1: Term,
):
    term_set = TermSet(
        terms=[
            sample_term_1,
        ],
        aliases={
            "species": "scientificName",
        },
    )

    register_term_set(term_set)
    registry = get_global_term_registry()
    assert registry["scientificName"] == sample_term_1
    assert registry["species"] == sample_term_1


def test_add_terms_from_file_to_global_registry_integration(
    term_json_file_simple_list: Path,
    sample_term_1: Term,
):
    add_terms_from_file(term_json_file_simple_list)
    assert get_term("scientificName") == sample_term_1


def test_add_terms_from_file_to_specific_registry_integration(
    term_json_file_simple_list: Path, sample_term_1: Term
):
    registry = TermRegistry()
    add_terms_from_file(term_json_file_simple_list, term_registry=registry)
    assert registry["scientificName"] == sample_term_1


def test_add_terms_from_file_json_and_csv_integration(
    term_json_file_simple_list: Path,
    term_csv_file_with_aliases: Path,
):
    add_terms_from_file(term_json_file_simple_list)
    add_terms_from_file(term_csv_file_with_aliases)
    assert get_term("scientificName")
    assert get_term("species")
    assert get_term("species") == get_term("scientificName")
