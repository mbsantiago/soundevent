"""Input/output operations for terms and term sets.

This module provides functions to load term definitions from files,
supporting both JSON and CSV formats. It is designed to be flexible,
allowing for simple lists of terms or more structured definitions
that include aliases.

Supported Formats
-----------------

**JSON Format**

The JSON loader supports two structures:

1.  **Simple List**: A JSON array where each object corresponds to a
    single term definition. The object's keys should match the
    fields of the `soundevent.data.Term` model.

    *Example:*
    ```json
    [
      {
        "name": "dwc:scientificName",
        "label": "Scientific Name",
        "definition": "The full scientific name..."
      },
      {
        "name": "ac:captureDevice",
        "label": "Capture Device",
        "definition": "The device used to create the resource."
      }
    ]
    ```

2.  **Structured Object**: A JSON object with a `terms` key and an
    optional `aliases` key. This is the recommended format when you
    need to define aliases.

    - `terms` (required): A list of term definition objects.
    - `aliases` (optional): An object mapping custom, simple names
      (aliases) to the official term names defined in the `terms` list.

    *Example:*
    ```json
    {
      "terms": [
        {
          "name": "dwc:scientificName",
          "label": "Scientific Taxon Name",
          "definition": "The full scientific name..."
        }
      ],
      "aliases": {
        "species": "dwc:scientificName"
      }
    }
    ```

**CSV Format**

The CSV loader expects the first row to be a header.

-   **Columns**: Column headers should match the field names of the
    `soundevent.data.Term` model (e.g., `name`, `label`, `definition`, `uri`).
-   **Aliases**: An optional column named `alias` can be included. If a
    row has a value in this column, that value will be registered as an
    alias for the term defined in that same row.
-   **Empty Fields**: Empty cells in the CSV are ignored, and the default
    value for the corresponding field in the `Term` model will be used.

*Example:*
```csv
name,label,definition,alias
dwc:scientificName,Scientific Taxon Name,"The full scientific name...",species
ac:captureDevice,Capture Device,"The device used to create the resource.",
```
"""

import csv
import json
from pathlib import Path
from typing import Callable, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ValidationError

from soundevent.data import PathLike, Term
from soundevent.terms.api import add_term, get_global_term_registry
from soundevent.terms.registry import (
    TermNotFoundError,
    TermOverrideError,
    TermRegistry,
)

__all__ = [
    "load_term_set_from_file",
    "add_terms_from_file",
    "register_term_set",
    "TermSet",
]


class TermSet(BaseModel):
    """A collection of terms and their optional mappings."""

    terms: List[Term]
    """A list of term objects."""

    aliases: Dict[str, str] = Field(default_factory=dict)
    """A mapping from a custom key to a term name."""


def load_term_set_from_json(path: PathLike) -> TermSet:
    """Load a list of terms from a JSON file."""
    with open(path, "r") as f:
        data = json.load(f)

    if isinstance(data, list):
        return TermSet(terms=data)

    if isinstance(data, dict):
        return TermSet.model_validate(data)

    raise ValueError("Invalid JSON format for terms.")


def _normalise_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return value

    return value.strip()


def load_term_set_from_csv(path: PathLike) -> TermSet:
    """Load a list of terms from a CSV file."""
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    terms = []
    aliases = {}

    for index, row in enumerate(rows):
        alias = _normalise_value(row.pop("alias", None))
        term_name = _normalise_value(row.get("name"))

        if alias and term_name:
            aliases[alias] = term_name

        # Remove empty fields so Pydantic uses the model's defaults
        term_data = {k: v.strip() for k, v in row.items() if v != ""}
        try:
            terms.append(Term(**term_data))
        except ValidationError as err:
            raise ValueError(
                f"Invalid term at CSV row {index}: {err}"
            ) from err

    return TermSet(terms=terms, aliases=aliases)


TermFormat = Literal["json", "csv"]

TERM_LOADERS: Dict[TermFormat, Callable[[PathLike], TermSet]] = {
    "json": load_term_set_from_json,
    "csv": load_term_set_from_csv,
}


def infer_term_set_format(path: PathLike) -> TermFormat:
    """Infer the file format from the file extension."""
    suffix = Path(path).suffix.lower()

    if suffix == ".json":
        return "json"
    if suffix == ".csv":
        return "csv"

    raise ValueError(f"Could not infer format for file: {path}")


def load_term_set_from_file(
    path: PathLike,
    format: Optional[TermFormat] = None,
) -> TermSet:
    """Load terms from a file into a TermSet object.

    The format can be specified explicitly. If not, it will be
    inferred from the file extension.

    Parameters
    ----------
    path
        The path to the file.
    format
        The format of the file. If None, it will be inferred from the
        file extension.

    Returns
    -------
    TermSet
        A TermSet object containing the loaded terms and any aliases.

    Raises
    ------
    ValueError
        If the format is not specified and cannot be inferred from the
        file extension, or if the format is not supported.

    Notes
    -----
    See [soundevent.terms.io][] for detailed information on the
    supported JSON and CSV file structures.
    """
    if format is None:
        format = infer_term_set_format(path)

    loader = TERM_LOADERS.get(format)
    if loader is None:
        raise ValueError(f"Unsupported format: {format}")

    return loader(path)


def register_term_set(
    term_set: TermSet,
    term_registry: Optional[TermRegistry] = None,
    override_existing: bool = False,
    ignore_overrides: bool = True,
    ignore_missing_key: bool = True,
):
    """Register a collection of terms and their aliases to a registry.

    This function takes a `TermSet` object, which contains a list of `Term`
    objects and an optional dictionary of aliases, and registers them to
    the specified `TermRegistry`. It provides flexible options for handling
    conflicts such as existing terms or aliases, and references to non-existent
    terms.

    Parameters
    ----------
    term_set : TermSet
        A `TermSet` object containing the terms and aliases to be registered.
    term_registry : Optional[TermRegistry], default=None
        The registry to add the terms to. If None, the global
        registry is used.
    override_existing : bool, default=False
        If True, existing terms or aliases with the same key will be
        overwritten. Defaults to False.
    ignore_overrides : bool, default=True
        If True, and `override_existing` is False, any term or alias that
        already exists in the registry will be skipped without raising an
        error. If False, a `TermOverrideError` will be raised. Defaults to True.
    ignore_missing_key : bool, default=True
        If True, any alias in the `term_set` that refers to a non-existent
        term (i.e., a term not found in the registry after all terms from
        `term_set` have been processed) will be skipped. If False, a
        `TermNotFoundError` will be raised. Defaults to True.

    Raises
    ------
    TermOverrideError
        If `override_existing` is False, `ignore_overrides` is False,
        and a term or alias being registered already exists in the registry.
    TermNotFoundError
        If `ignore_missing_key` is False and an alias in the `term_set`
        referring to a term name that is not found in the registry.
    """
    if term_registry is None:
        term_registry = get_global_term_registry()

    for term in term_set.terms:
        try:
            add_term(
                term, term_registry=term_registry, force=override_existing
            )
        except TermOverrideError as err:
            if not ignore_overrides:
                raise err
            continue

    for alias, term_name in term_set.aliases.items():
        try:
            term = term_registry[term_name]
        except KeyError as err:
            if not ignore_missing_key:
                raise TermNotFoundError(
                    f"Cannot create alias '{alias}': the target term "
                    f"'{term_name}' was not found in the registry.",
                    key=term_name,
                ) from err
            continue

        try:
            add_term(
                term,
                key=alias,
                term_registry=term_registry,
                force=override_existing,
            )
        except TermOverrideError as err:
            if not ignore_overrides:
                raise TermOverrideError(
                    f"Cannot create alias '{alias}': a term with this key "
                    f"already exists in the registry.",
                    key=alias,
                    term=err.term,
                ) from err
            continue


def add_terms_from_file(
    path: PathLike,
    term_registry: Optional[TermRegistry] = None,
    format: Optional[TermFormat] = None,
    override_existing: bool = False,
    ignore_overrides: bool = True,
    ignore_missing_key: bool = True,
) -> None:
    """Load terms from a file and add them to a registry.

    This function provides options to handle cases where a term being
    loaded already exists in the registry, or when a mapping refers
    to a non-existent term.

    The format can be specified explicitly. If not, it will be
    inferred from the file extension.

    Parameters
    ----------
    path
        The path to the file.
    term_registry
        The registry to add the terms to. If None, the global
        registry is used.
    format
        The format of the file. If None, it will be inferred from the
        file extension.
    override_existing
        If True, existing terms with the same name will be
        overwritten. Defaults to False.
    ignore_overrides
        If True, and `override_existing` is False, any term that
        already exists in the registry will be skipped without
        raising an error. If False, a `TermOverrideError` will be
        raised. Defaults to True.
    ignore_missing_key
        If True, any alias in the mapping that refers to a non-existent
        term will be skipped. If False, a `TermNotFoundError` will be
        raised. Defaults to True.

    Raises
    ------
    TermOverrideError
        If `override_existing` is False, `ignore_overrides` is False,
        and a term or alias being loaded already exists in the registry.
    TermNotFoundError
        If `ignore_missing_key` is False and an alias in the mapping
        refers to a term name that is not found in the registry.

    Notes
    -----
    See [soundevent.terms.io][] for detailed information on the
    supported JSON and CSV file structures.
    """
    term_set = load_term_set_from_file(path, format=format)

    register_term_set(
        term_set,
        term_registry=term_registry,
        override_existing=override_existing,
        ignore_overrides=ignore_overrides,
        ignore_missing_key=ignore_missing_key,
    )
