"""Forms and input helpers for goals and milestones."""
from __future__ import annotations

from datetime import date
from typing import Optional

import streamlit as st

from app.data.models import Goal


def goal_form(existing_goal: Goal | None = None) -> dict[str, Optional[str | float | date]]:
    """Render goal creation/editing form and return submitted values."""
    with st.form(key="goal_form"):
        title = st.text_input("Título", value=getattr(existing_goal, "title", ""))
        description = st.text_area("Descrição", value=getattr(existing_goal, "description", ""))
        target_metric = st.text_input(
            "Indicador mensurável", value=getattr(existing_goal, "target_metric", "")
        )
        unit = st.text_input("Unidade", value=getattr(existing_goal, "unit", ""))
        target_value = st.number_input(
            "Valor alvo",
            min_value=0.0,
            value=float(getattr(existing_goal, "target_value", 0.0)),
        )
        current_value = st.number_input(
            "Valor atual",
            min_value=0.0,
            value=float(getattr(existing_goal, "current_value", 0.0)),
        )
        category = st.text_input("Categoria", value=getattr(existing_goal, "category", ""))
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Data inicial",
                value=getattr(existing_goal, "start_date", date.today()),
            )
        with col2:
            end_date = st.date_input(
                "Data final",
                value=getattr(existing_goal, "end_date", date(date.today().year, 12, 31)),
            )
        submitted = st.form_submit_button("Salvar objetivo")
    return {
        "submitted": submitted,
        "title": title,
        "description": description,
        "target_metric": target_metric,
        "target_value": target_value,
        "current_value": current_value,
        "unit": unit,
        "category": category,
        "start_date": start_date,
        "end_date": end_date,
    }
