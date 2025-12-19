"""Google OAuth utilities."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Tuple

import streamlit as st
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests

AUTH_COOKIE_NAME = "planos_oauth_token"


def _load_client_config() -> Dict[str, Any]:
    """Load OAuth client configuration from Streamlit secrets."""
    config = st.secrets.get("google_oauth")
    if not config:
        raise RuntimeError("Google OAuth configuration not found in secrets")
    return {
        "web": {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [config.get("redirect_uri", "http://localhost:8501")],
        }
    }


def build_flow(state: str) -> Flow:
    """Prepare Google OAuth flow instance."""
    client_config = _load_client_config()
    flow = Flow.from_client_config(
        client_config,
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
        ],
        state=state,
    )
    flow.redirect_uri = client_config["web"]["redirect_uris"][0]
    return flow


def get_authorization_url(flow: Flow) -> Tuple[str, str]:
    """Generate authorization URL and state."""
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return authorization_url, state


def fetch_user_info(flow: Flow, authorization_response: str) -> Dict[str, Any]:
    """Exchange auth code for tokens and decode the ID token."""
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(
        credentials.id_token,
        requests.Request(),
        flow.client_config["client_id"],
    )
    return {
        "google_sub": id_info["sub"],
        "email": id_info["email"],
        "full_name": id_info.get("name", ""),
        "picture_url": id_info.get("picture"),
        "token": credentials.to_json(),
    }


def store_token(token_json: str) -> None:
    """Persist token into Streamlit session state."""
    st.session_state[AUTH_COOKIE_NAME] = token_json


def clear_token() -> None:
    """Remove token from session state."""
    st.session_state.pop(AUTH_COOKIE_NAME, None)
    if AUTH_COOKIE_NAME in st.experimental_get_query_params():
        st.experimental_set_query_params()


def load_token() -> Dict[str, Any] | None:
    """Return the stored Google credentials if available."""
    token_json = st.session_state.get(AUTH_COOKIE_NAME)
    if not token_json:
        return None
    return json.loads(token_json)
