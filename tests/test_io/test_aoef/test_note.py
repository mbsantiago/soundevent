"""Test suite for AOEF Note Adapter."""

from soundevent import data
from soundevent.io.aoef.note import NoteAdapter, NoteObject


def test_note_can_be_converted_to_aoef(
    note: data.Note,
    note_adapter: NoteAdapter,
):
    """Test that a note can be converted to AOEF."""
    aoef = note_adapter.to_aoef(note)
    assert isinstance(aoef, NoteObject)


def test_note_is_recovered(
    note: data.Note,
    note_adapter: NoteAdapter,
):
    """Test that a note is recovered."""
    aoef = note_adapter.to_aoef(note)
    recovered = note_adapter.to_soundevent(aoef)
    assert note == recovered
