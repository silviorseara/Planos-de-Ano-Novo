"""Session helpers for Streamlit."""
from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from app.auth.google import AUTH_COOKIE_NAME

USER_SESSION_KEY = "planos_user"


def get_current_user() -> Dict[str, Any] | None:
    """Retrieve current user data from session state."""
    return st.session_state.get(USER_SESSION_KEY)


def set_current_user(user_data: Dict[str, Any]) -> None:
    """Store user data in session state."""
    st.session_state[USER_SESSION_KEY] = user_data


def clear_session() -> None:
    """Clear session user and auth token."""
    st.session_state.pop(USER_SESSION_KEY, None)
    st.session_state.pop(AUTH_COOKIE_NAME, None)
