"""Reusable layout components."""
from __future__ import annotations

import streamlit as st


def app_header() -> None:
    """Render top header with title and description."""
    st.title("Planos de Ano Novo")
    st.caption("Defina objetivos, acompanhe metas e celebre conquistas ao longo do ano.")


def sidebar_menu() -> None:
    """Render sidebar with navigation tips."""
    st.sidebar.header("Navegação")
    st.sidebar.write("Use as páginas para registrar metas, marcar marcos e revisar seu progresso.")
