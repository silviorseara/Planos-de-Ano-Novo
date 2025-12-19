"""Streamlit dashboard page."""
from __future__ import annotations

import streamlit as st

from app.auth import session
from app.data.database import get_session
from app.data.models import Goal
from app.ui.dashboard import render_overview


def _load_goals(user_id: int) -> list[Goal]:
    """Fetch goals for the signed-in user."""
    with get_session() as db:
        return list(db.query(Goal).filter(Goal.owner_id == user_id).all())


def main() -> None:
    """Render page content."""
    user = session.get_current_user()
    if not user:
        st.warning("Faça login com sua conta Google para acessar o dashboard.")
        st.stop()

    st.header("Dashboard")
    goals = _load_goals(user_id=user["id"])
    if goals:
        render_overview(goals)
    else:
        st.info("Cadastre seu primeiro objetivo para começar a acompanhar seu ano.")


main()
