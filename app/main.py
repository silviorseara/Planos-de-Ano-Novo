"""Main entry point for the Streamlit app."""
from __future__ import annotations

import secrets
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import streamlit as st

if __package__ is None:  # Ensure repository root is importable when run as script
    repo_root = Path(__file__).resolve().parent.parent
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.append(repo_root_str)

from app.auth import google, session
from app.data.database import get_session, init_db
from app.data.models import User
from app.ui.layout import app_header, sidebar_menu

STATE_KEY = "oauth_state"


def _ensure_oauth_state() -> str:
    """Generate and memoize an OAuth state token."""
    if STATE_KEY not in st.session_state:
        st.session_state[STATE_KEY] = secrets.token_urlsafe(16)
    return st.session_state[STATE_KEY]


def _handle_oauth_callback() -> dict[str, Any] | None:
    """Process Google OAuth callback if present."""
    raw_params = st.experimental_get_query_params()
    params = {key: values[0] for key, values in raw_params.items() if values}
    if "code" not in params or "state" not in params:
        return None

    state = params["state"]
    expected_state = st.session_state.get(STATE_KEY)
    if state != expected_state:
        st.warning("Token de estado inválido. Tente novamente.")
        return None

    flow = google.build_flow(state=state)
    redirect_uri = flow.redirect_uri
    current_url = f"{redirect_uri}?{urlencode(params)}"
    user_info = google.fetch_user_info(flow, authorization_response=current_url)
    google.store_token(token_json=user_info.pop("token"))
    st.experimental_set_query_params()
    return user_info


def _render_login() -> None:
    """Show Google login button and status."""
    st.info("Conecte-se com sua conta Google para acessar seus planos.")
    if st.button("Entrar com Google"):
        state = _ensure_oauth_state()
        flow = google.build_flow(state=state)
        auth_url, _ = google.get_authorization_url(flow)
        st.markdown(f"[Continuar com Google]({auth_url})")
        st.stop()


def _ensure_guest_user() -> dict[str, Any]:
    """Provide a guest user for local testing when OAuth is skipped."""
    with get_session() as db:
        guest = db.query(User).filter(User.email == "guest@local").one_or_none()
        if not guest:
            guest = User(
                google_sub="guest",
                email="guest@local",
                full_name="Modo convidado",
                picture_url=None,
            )
            db.add(guest)
            db.flush()

        return {
            "id": guest.id,
            "google_sub": guest.google_sub,
            "email": guest.email,
            "full_name": guest.full_name,
            "picture_url": guest.picture_url,
        }


def main() -> None:
    """Run Streamlit application."""
    init_db()
    app_header()
    sidebar_menu()

    user = session.get_current_user()
    if not user:
        callback_user = _handle_oauth_callback()
        if callback_user:
            session.set_current_user(callback_user)
            user = callback_user

    if not user:
        disable_oauth = False
        has_oauth_credentials = False

        try:
            secrets_dict = st.secrets
        except Exception:  # pragma: no cover - Streamlit raises if secrets unset
            secrets_dict = None

        if secrets_dict:
            feature_flags = secrets_dict.get("feature_flags", {})
            if feature_flags:
                flag_value = feature_flags.get("disable_oauth")
                if isinstance(flag_value, str):
                    disable_oauth = flag_value.strip().lower() in {"1", "true", "yes"}
                else:
                    disable_oauth = bool(flag_value)

            google_oauth_cfg = secrets_dict.get("google_oauth")
            if google_oauth_cfg and not disable_oauth:
                required_keys = ("client_id", "client_secret")
                has_oauth_credentials = all(google_oauth_cfg.get(key) for key in required_keys)

        if has_oauth_credentials and not disable_oauth:
            _render_login()
            return

        user = _ensure_guest_user()
        session.set_current_user(user)
        st.info("Executando em modo convidado. Configure o OAuth para habilitar login Google.")

    st.success(f"Bem-vindo, {user['full_name']}!")
    st.write("Selecione uma das páginas na barra lateral para gerenciar seus planos.")

    if st.button("Sair"):
        session.clear_session()
        google.clear_token()
        st.rerun()
