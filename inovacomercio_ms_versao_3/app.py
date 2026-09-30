from __future__ import annotations
import streamlit as st
from frontend.utils import session
from frontend.api import client

st.set_page_config(page_title="InovaComércio MS | ERP", page_icon="🏢", layout="wide")
session.init_session()

if not session.is_authenticated():
    st.title("🔐 InovaComércio MS — Login Colab")
    with st.form("login"):
        email = st.text_input("E-mail", value="gestor@inovacomercio.ms")
        senha = st.text_input("Senha", type="password", value="123456")
        if st.form_submit_button("Entrar"):
            try:
                client.login(email, senha)
                st.success("Logado com sucesso!")
                st.rerun()
            except client.APIError as e:
                st.error(f"Erro: {e.detail}")
    st.stop()

st.sidebar.title("🏢 InovaComércio MS")
if st.sidebar.button("Sair"):
    session.clear_auth()
    st.rerun()

st.sidebar.divider()
modulo = st.sidebar.radio(
    "Navegação", 
    ["Painel Executivo", "Terminal Scanner", "Precificação", "Curva ABC", "Crédito Verde", "Auditoria"]
)

if modulo == "Painel Executivo":
    from frontend.pages import painel
    painel.render()
elif modulo == "Terminal Scanner":
    from frontend.pages import scanner
    scanner.render()
elif modulo == "Precificação":
    from frontend.pages import precificacao
    precificacao.render()
elif modulo == "Curva ABC":
    from frontend.pages import curva_abc
    curva_abc.render()
elif modulo == "Crédito Verde":
    from frontend.pages import credito_verde
    credito_verde.render()
elif modulo == "Auditoria":
    from frontend.pages import auditoria
    auditoria.render()
