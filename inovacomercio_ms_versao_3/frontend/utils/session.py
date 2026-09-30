from __future__ import annotations
import streamlit as st

def init_session():
    for k in ("auth_token", "usuario", "tenant_id", "modulo_atual"):
        st.session_state.setdefault(k, None)

def is_authenticated():
    return bool(st.session_state.get("auth_token"))

def current_user():
    return st.session_state.get("usuario") or {}

def get_token():
    return st.session_state.get("auth_token")

def current_role():
    return current_user().get("role", "admin")

def current_tenant():
    return st.session_state.get("tenant_id") or "demo_ms"

def clear_auth():
    for k in ("auth_token", "usuario", "tenant_id", "modulo_atual"):
        st.session_state[k] = None
