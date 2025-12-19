"""Page for managing goals."""
from __future__ import annotations

import streamlit as st

from app.auth import session
from app.data.database import get_session
from app.data.models import Goal
from app.ui.forms import goal_form


def _create_goal(user_id: int, form_data: dict) -> None:
    """Persist a new goal to the database."""
    with get_session() as db:
        goal = Goal(
            owner_id=user_id,
            title=form_data["title"],
            description=form_data["description"],
            target_metric=form_data["target_metric"],
            target_value=form_data["target_value"],
            current_value=form_data["current_value"],
            unit=form_data["unit"],
            category=form_data["category"],
            start_date=form_data["start_date"],
            end_date=form_data["end_date"],
        )
        db.add(goal)


def _list_goals(user_id: int) -> list[Goal]:
    with get_session() as db:
        return list(db.query(Goal).filter(Goal.owner_id == user_id).order_by(Goal.created_at.desc()).all())


def main() -> None:
    user = session.get_current_user()
    if not user:
        st.warning("Faça login para criar e acompanhar objetivos.")
        st.stop()

    st.header("Objetivos e metas")
    st.write("Defina objetivos SMART para impulsionar seu ano.")

    form_data = goal_form()
    if form_data["submitted"]:
        _create_goal(user_id=user["id"], form_data=form_data)
        st.success("Objetivo cadastrado com sucesso!")

    st.subheader("Objetivos cadastrados")
    goals = _list_goals(user_id=user["id"])
    if not goals:
        st.info("Nenhum objetivo cadastrado ainda.")
        return

    for goal in goals:
        with st.expander(goal.title, expanded=False):
            st.write(goal.description or "Sem descrição")
            st.write(f"Meta: {goal.target_value} {goal.unit or goal.target_metric}")
            st.write(f"Atual: {goal.current_value} {goal.unit or goal.target_metric}")
            st.write(f"Período: {goal.start_date} → {goal.end_date}")


main()
