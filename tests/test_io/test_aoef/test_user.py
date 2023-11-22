"""Test suite for AOEF User Adapter."""

from soundevent import data
from soundevent.io.aoef.user import UserAdapter, UserObject


def test_user_can_be_converted_to_aoef(
    user: data.User,
    user_adapter: UserAdapter,
):
    """Test that a user can be converted to AOEF."""
    aoef = user_adapter.to_aoef(user)
    assert isinstance(aoef, UserObject)


def test_user_is_recovered(
    user: data.User,
    user_adapter: UserAdapter,
):
    """Test that a user is recovered."""
    aoef = user_adapter.to_aoef(user)
    recovered = user_adapter.to_soundevent(aoef)
    assert user == recovered
