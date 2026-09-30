from __future__ import annotations
import streamlit as st
from frontend.api import client

def render():
    st.title("📊 Painel Executivo — InovaComércio MS")
    st.markdown("Visão geral em tempo real dos principais indicadores de desempenho do varejo de proximidade.")
    resumo = client.dashboard_resumo()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Faturamento", f"R$ {resumo.get('faturamento_mes', 0):,.2f}")
    col2.metric("Ticket Médio", f"R$ {resumo.get('ticket_medio', 0):,.2f}")
    col3.metric("Margem", f"{resumo.get('margem_media', 0)*100:.1f}%")
    col4.metric("Rupturas", f"{resumo.get('rupturas_ativas', 0)}")

    st.divider()
    c_inf1, c_inf2 = st.columns(2)
    c_inf1.metric("Crédito Verde", f"R$ {resumo.get('credito_verde_saldo', 0):,.2f}")
    c_inf2.metric("Crescimento MoM", f"{resumo.get('variacao_mom', 0) * 100:.2f}%")
