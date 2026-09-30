from __future__ import annotations
import requests
import streamlit as st

API_URL = "http://127.0.0.1:5000/api/v1"

class APIError(Exception):
    def __init__(self, detail: str):
        self.detail = detail

def _get_headers() -> dict[str, str]:
    token = st.session_state.get("auth_token")
    tenant_id = st.session_state.get("tenant_id", "demo_ms")
    headers = {"X-Tenant-Id": str(tenant_id)}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def login(email: str, senha: str):
    try:
        res = requests.post(f"{API_URL}/auth/login", json={"email": email, "senha": senha})
        if res.status_code == 200:
            data = res.json()
            st.session_state["auth_token"] = data["access_token"]
            st.session_state["usuario"] = data["usuario"]
            st.session_state["tenant_id"] = data["tenant_id"]
            return data
        raise APIError("Credenciais inválidas")
    except Exception as e:
        raise APIError(str(e))

def dashboard_resumo():
    return requests.get(f"{API_URL}/dashboard/resumo", headers=_get_headers()).json()

def precificacao_listar():
    return requests.get(f"{API_URL}/precificacao", headers=_get_headers()).json()

def curva_abc():
    return requests.get(f"{API_URL}/curva-abc", headers=_get_headers()).json()

def esg_indicadores():
    return requests.get(f"{API_URL}/esg/indicadores", headers=_get_headers()).json()

def auditoria_eventos():
    return requests.get(f"{API_URL}/auditoria/eventos", headers=_get_headers()).json()
