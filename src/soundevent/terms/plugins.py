"""Plugin management for soundevent terms.

This module handles the discovery and loading of external term sets provided
by third-party Python packages. These packages can act as "plugins" to extend
the default set of terms available in `soundevent`.

How to Create a Term Plugin
--------------------------
To create a term plugin, you need to:

1.  **Create a Python package:** This is a standard Python project (like any
    library you might install with `pip`).
2.  **Define your terms:** Create a function within your package that loads
    your term definitions (e.g., from a JSON or CSV file) and returns them
    as a `soundevent.terms.io.TermSet` object. You can use
    `soundevent.terms.io.load_term_set_from_file` for this.
    If your terms are in a file inside your package, you can access it using
    `importlib.resources.files`.

    Example `my_plugin_package/__init__.py`:
    ```python
    from importlib.resources import files
    from soundevent.terms.io import load_term_set_from_file


    def load_my_terms():
        # Assuming terms.json is in my_plugin_package/data/
        path = files("my_plugin_package").joinpath("data/terms.json")
        return load_term_set_from_file(path)
    ```

3.  **Declare an entry point:** In your package's `pyproject.toml` file,
    add an entry point under the `[project.entry-points."soundevent.terms"]`
    section. This tells `soundevent` where to find your term-loading function.

    Example `pyproject.toml`:
    ```toml
    [project]
    name = "my-plugin-package"
    version = "0.1.0"
    # ... other project metadata ...

    [project.entry-points."soundevent.terms"]
    my_unique_plugin_name = "my_plugin_package:load_my_terms"
    ```
    Replace `my_unique_plugin_name` with a unique identifier for your plugin,
    and `my_plugin_package:load_my_terms` with the actual path to your
    term-loading function.

Once your plugin package is installed (e.g., `pip install my-plugin-package`),
`soundevent` will automatically discover and load its terms when the
`soundevent.terms` module is first used.

You can disable plugin loading by setting the environment variable
`SOUNDEVENT_LOAD_TERM_PLUGINS` to `false`, `0`, or `no`.
"""

import logging
import os
import sys
from typing import Optional

from soundevent.terms.api import get_global_term_registry
from soundevent.terms.io import register_term_set
from soundevent.terms.registry import TermRegistry

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

__all__ = [
    "discover_and_load_plugins",
]


logger = logging.getLogger(__name__)


_plugins_status = {"loaded": False}


def plugins_loaded() -> bool:
    return _plugins_status["loaded"]


def plugins_enabled() -> bool:
    """Check if term plugin loading is enabled via environment variable.

    The environment variable `SOUNDEVENT_LOAD_TERM_PLUGINS` controls
    whether plugins are loaded.

    Returns
    -------
    bool
        True if plugin loading is enabled, False otherwise.
        It is enabled by default. To disable, set the environment variable
        to "false", "0", or "no" (case-insensitive).
    """
    env = os.getenv("SOUNDEVENT_LOAD_TERM_PLUGINS", "true").lower()
    return env not in ("false", "0", "no")


def discover_plugins():
    try:
        # Python 3.10+ recommended API
        eps = entry_points()

        if hasattr(eps, "select"):
            return eps.select(group="soundevent.terms")

        # Some backports may return a mapping
        if isinstance(eps, dict):
            return eps.get("soundevent.terms", [])

        # Fallback: filter sequence by group attribute
        return [
            ep
            for ep in eps
            if getattr(ep, "group", None) == "soundevent.terms"
        ]

    except TypeError:
        # Older API supporting the `group=` kwarg
        return list(entry_points(group="soundevent.terms"))


def discover_and_load_plugins(term_registry: Optional[TermRegistry] = None):
    """Discover and load term sets from installed plugins.

    This function scans for Python packages that have registered themselves
    as `soundevent` term plugins using entry points. It then loads the
    term sets provided by these plugins and registers them with the
    specified (or global) term registry.

    Parameters
    ----------
    term_registry : Optional[TermRegistry], optional
        The term registry to add the discovered terms to. If None, the
        global term registry (`soundevent.terms.api.get_global_term_registry()`)
        will be used. By default, None.

    Notes
    -----
    *   This function is designed to be called only once per application
        session. Subsequent calls will be ignored.
    *   Any errors encountered while loading terms from a specific plugin
        will be logged, but will not prevent other plugins from being loaded.
    """
    if not plugins_enabled():
        return

    if plugins_loaded():
        return

    if term_registry is None:
        term_registry = get_global_term_registry()

    discovered_plugins = discover_plugins()

    if not discovered_plugins:
        _plugins_status["loaded"] = True
        return

    logger.debug(f"Found {len(discovered_plugins)} soundevent term plugins.")

    for entry_point in discovered_plugins:
        try:
            logger.debug(f"Loading terms from plugin: '{entry_point.name}'")

            load_func = entry_point.load()

            term_set = load_func()
            register_term_set(term_set, term_registry=term_registry)
        except Exception:
            logger.exception(
                f"Failed to load terms from plugin: '{entry_point.name}'"
            )

    _plugins_status["loaded"] = True
