"""Dashboard visualizations."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

import pandas as pd
import streamlit as st

from app.data.models import Goal, ProgressLog


def _progress_dataframe(goal: Goal) -> pd.DataFrame:
    """Convert progress logs into a DataFrame for plotting."""
    records = [
        {
            "goal": goal.title,
            "timestamp": log.logged_at,
            "value": log.value,
        }
        for log in goal.progress_logs
    ]
    return pd.DataFrame.from_records(records) if records else pd.DataFrame(columns=["goal", "timestamp", "value"])


def render_overview(goals: Iterable[Goal]) -> None:
    """Display overview metrics and charts."""
    goals = list(goals)
    st.subheader("Resumo do ano")
    col1, col2, col3 = st.columns(3)
    col1.metric("Objetivos ativos", len(goals))
    total_target = sum(goal.target_value for goal in goals)
    total_current = sum(goal.current_value for goal in goals)
    completion = 0 if total_target == 0 else int((total_current / total_target) * 100)
    col2.metric("Progresso consolidado", f"{completion}%")
    col3.metric("Última atualização", _latest_update(goals))

    chart_data = pd.concat([
        _progress_dataframe(goal) for goal in goals if goal.progress_logs
    ], ignore_index=True)
    if not chart_data.empty:
        chart_data.sort_values("timestamp", inplace=True)
        chart = chart_data.pivot_table(
            index="timestamp",
            columns="goal",
            values="value",
            aggfunc="max",
        )
        st.line_chart(chart)
    else:
        st.info("Registre progresso para visualizar seu avanço ao longo do tempo.")


def _latest_update(goals: Iterable[Goal]) -> str:
    """Return formatted timestamp of last progress log."""
    latest = max(
        (log.logged_at for goal in goals for log in goal.progress_logs),
        default=None,
    )
    if not latest:
        return "Sem registros"
    return latest.strftime("%d/%m/%Y")
