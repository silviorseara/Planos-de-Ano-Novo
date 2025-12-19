"""Page for monthly reviews and exports."""
from __future__ import annotations

import io
from datetime import date

import pandas as pd
import streamlit as st

from app.auth import session
from app.data.database import get_session
from app.data.models import Goal, ProgressLog


def _load_progress(user_id: int) -> pd.DataFrame:
    with get_session() as db:
        query = (
            db.query(Goal.title, ProgressLog.logged_at, ProgressLog.value, ProgressLog.note)
            .join(ProgressLog, ProgressLog.goal_id == Goal.id)
            .filter(Goal.owner_id == user_id)
        )
        rows = [
            {
                "Objetivo": title,
                "Registrado em": logged_at,
                "Valor": value,
                "Observação": note,
            }
            for title, logged_at, value, note in query.all()
        ]
    return pd.DataFrame(rows)


def main() -> None:
    user = session.get_current_user()
    if not user:
        st.warning("Faça login para acessar suas revisões.")
        st.stop()

    st.header("Revisões e exportações")
    st.write("Anote aprendizados mensais e exporte seus dados para análise externa.")

    review_date = st.date_input("Mês de referência", value=date.today())
    reflections = st.text_area("Reflexões do período", placeholder="O que funcionou bem? O que precisa mudar?")
    if st.button("Salvar revisão"):
        st.info("Persistência de revisões será implementada na próxima etapa.")

    st.subheader("Exportar progresso")
    progress_df = _load_progress(user_id=user["id"])
    if progress_df.empty:
        st.info("Ainda não há registros de progresso para exportar.")
        return

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        progress_df.to_excel(writer, sheet_name="Progresso", index=False)
    st.download_button(
        label="Baixar em Excel",
        data=buffer.getvalue(),
        file_name="progresso_planos_ano_novo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


main()
