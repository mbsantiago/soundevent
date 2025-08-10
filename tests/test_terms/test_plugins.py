import logging
from unittest.mock import MagicMock, patch

import pytest

from soundevent.data import Term
from soundevent.terms.api import get_term, has_term
from soundevent.terms.io import TermSet
from soundevent.terms.plugins import (
    _plugins_status,
    discover_and_load_plugins,
    plugins_enabled,
    plugins_loaded,
)
from soundevent.terms.registry import TermRegistry


@pytest.fixture(autouse=True)
def setup():
    _plugins_status["loaded"] = False


@pytest.fixture
def mock_entry_point():
    def _mock_entry_point(name, load_func_return_value):
        mock_ep = MagicMock()
        mock_ep.name = name
        mock_ep.load.return_value = MagicMock(
            return_value=load_func_return_value
        )
        return mock_ep

    return _mock_entry_point


def test_plugin_loading_is_disabled_in_testing_by_default():
    assert not plugins_enabled()


def test_default_is_true(monkeypatch):
    monkeypatch.delenv("SOUNDEVENT_LOAD_TERM_PLUGINS", raising=False)
    assert plugins_enabled()


@pytest.mark.parametrize("env_value", ("false", "0", "no", "FaLsE"))
def test_false_values(monkeypatch, env_value):
    monkeypatch.setenv("SOUNDEVENT_LOAD_TERM_PLUGINS", env_value)
    assert not plugins_enabled()


@pytest.mark.parametrize(
    "env_value", ["true", "1", "yes", "TrUe", "anything_else"]
)
def test_true_values(monkeypatch, env_value):
    monkeypatch.setenv("SOUNDEVENT_LOAD_TERM_PLUGINS", env_value)
    assert plugins_enabled()


def test_no_plugins_found(monkeypatch):
    monkeypatch.setenv("SOUNDEVENT_LOAD_TERM_PLUGINS", True)

    with patch("soundevent.terms.plugins.entry_points") as mock_entry_points:
        mock_entry_points.return_value = []
        mock_register_term_set = MagicMock()
        with patch(
            "soundevent.terms.plugins.register_term_set",
            mock_register_term_set,
        ):
            assert not plugins_loaded()
            discover_and_load_plugins()
            assert plugins_loaded()
            mock_register_term_set.assert_not_called()


def test_plugins_loaded_successfully(monkeypatch, mock_entry_point):
    # Turn on term loading
    monkeypatch.setenv("SOUNDEVENT_LOAD_TERM_PLUGINS", True)

    mock_term_set_1 = TermSet(
        terms=[
            Term(
                name="plugin:term1",
                label="Plugin Term 1",
                definition="Term 1",
            )
        ]
    )
    mock_term_set_2 = TermSet(
        terms=[
            Term(
                name="plugin:term2",
                label="Plugin Term 2",
                definition="Term 2",
            )
        ]
    )

    mock_ep1 = mock_entry_point("plugin_a", mock_term_set_1)
    mock_ep2 = mock_entry_point("plugin_b", mock_term_set_2)

    with patch(
        "soundevent.terms.plugins.discover_plugins"
    ) as mock_entry_points:
        mock_entry_points.return_value = [mock_ep1, mock_ep2]
        mock_register_term_set = MagicMock()

        with patch(
            "soundevent.terms.plugins.register_term_set",
            mock_register_term_set,
        ):
            mock_term_registry = TermRegistry()
            discover_and_load_plugins(term_registry=mock_term_registry)

            assert plugins_loaded()
            assert mock_ep1.load.called
            assert mock_ep2.load.called

            mock_register_term_set.assert_any_call(
                mock_term_set_1,
                term_registry=mock_term_registry,
            )
            mock_register_term_set.assert_any_call(
                mock_term_set_2,
                term_registry=mock_term_registry,
            )
            assert mock_register_term_set.call_count == 2


def test_plugin_loading_failure(monkeypatch, mock_entry_point, caplog):
    monkeypatch.setenv("SOUNDEVENT_LOAD_TERM_PLUGINS", True)

    mock_term_set_ok = TermSet(
        terms=[
            Term(
                name="plugin:ok",
                label="Plugin OK",
                definition="Term OK",
            )
        ]
    )

    mock_ep_ok = mock_entry_point("plugin_ok", mock_term_set_ok)
    mock_ep_fail = mock_entry_point("plugin_fail", None)
    mock_ep_fail.load.return_value = MagicMock(
        side_effect=Exception("Simulated plugin error")
    )

    with patch(
        "soundevent.terms.plugins.discover_plugins"
    ) as mock_entry_points:
        mock_entry_points.return_value = [mock_ep_ok, mock_ep_fail]
        mock_register_term_set = MagicMock()
        with patch(
            "soundevent.terms.plugins.register_term_set",
            mock_register_term_set,
        ):
            mock_term_registry = TermRegistry()
            with caplog.at_level(logging.ERROR):
                discover_and_load_plugins(term_registry=mock_term_registry)

            assert plugins_loaded()
            assert mock_ep_ok.load.called
            assert mock_ep_fail.load.called

            # Make sure the OK plugin was loaded
            mock_register_term_set.assert_called_once_with(
                mock_term_set_ok,
                term_registry=mock_term_registry,
            )
            # And that an error was emited to the logs
            assert (
                "Failed to load terms from plugin: 'plugin_fail'"
                in caplog.text
            )


def test_discover_only_runs_once(monkeypatch, mock_entry_point):
    monkeypatch.setenv("SOUNDEVENT_LOAD_TERM_PLUGINS", True)

    mock_term_set = TermSet(
        terms=[
            Term(
                name="plugin:once",
                label="Plugin Once",
                definition="Term once",
            )
        ]
    )
    mock_ep = mock_entry_point("plugin_once", mock_term_set)

    with patch(
        "soundevent.terms.plugins.discover_plugins"
    ) as mock_entry_points:
        mock_entry_points.return_value = [mock_ep]
        mock_register_term_set = MagicMock()
        with patch(
            "soundevent.terms.plugins.register_term_set",
            mock_register_term_set,
        ):
            discover_and_load_plugins()
            discover_and_load_plugins()

            assert plugins_loaded()
            assert mock_entry_points.call_count == 1
            assert mock_register_term_set.call_count == 1


def test_uses_global_registry_by_default(
    monkeypatch,
    mock_entry_point,
):
    monkeypatch.setenv("SOUNDEVENT_LOAD_TERM_PLUGINS", True)

    mock_term_set = TermSet(
        terms=[
            Term(
                name="plugin:global",
                label="Plugin Global",
                definition="Term global",
            )
        ]
    )
    mock_ep = mock_entry_point("plugin_global", mock_term_set)

    with patch(
        "soundevent.terms.plugins.discover_plugins"
    ) as mock_entry_points:
        mock_entry_points.return_value = [mock_ep]
        mock_register_term_set = MagicMock()
        with patch(
            "soundevent.terms.plugins.register_term_set",
            mock_register_term_set,
        ):
            mock_global_registry = TermRegistry()
            with patch(
                "soundevent.terms.plugins.get_global_term_registry",
                return_value=mock_global_registry,
            ):
                discover_and_load_plugins()

                mock_register_term_set.assert_called_once_with(
                    mock_term_set, term_registry=mock_global_registry
                )


def test_does_not_load_if_disabled(
    monkeypatch,
):
    monkeypatch.setenv("SOUNDEVENT_LOAD_TERM_PLUGINS", "false")

    with patch("soundevent.terms.plugins.entry_points") as mock_entry_points:
        discover_and_load_plugins()
        mock_entry_points.assert_not_called()
        assert not plugins_loaded()


def test_loaded_terms_are_available(
    monkeypatch,
    mock_entry_point,
):
    monkeypatch.setenv("SOUNDEVENT_LOAD_TERM_PLUGINS", True)

    mock_term_set = TermSet(
        terms=[
            Term(
                name="plugin:global",
                label="Plugin Global",
                definition="Term global",
            )
        ],
        aliases={
            "test": "plugin:global",
        },
    )
    mock_ep = mock_entry_point("plugin_global", mock_term_set)

    with patch(
        "soundevent.terms.plugins.discover_plugins"
    ) as mock_entry_points:
        mock_entry_points.return_value = [mock_ep]

        assert not has_term("plugin:global")
        assert not has_term("test")

        discover_and_load_plugins()

        assert has_term("plugin:global")
        assert has_term("test")
        assert get_term("plugin:global") == mock_term_set.terms[0]
        assert get_term("plugin:global") == get_term("test")
