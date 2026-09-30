from __future__ import annotations
import streamlit as st
import requests
from frontend.utils import session

def render():
    st.title("📷 Terminal de Scanner & PDV — InovaComércio MS")
    st.markdown("Ponto de convergência para leitura de códigos de barras com feedback instantâneo.")

    with st.form("form_scan"):
        col1, col2 = st.columns([3, 1])
        with col1:
            codigo_input = st.text_input("Código de Barras", value="7891000100102")
        with col2:
            origem = st.selectbox("Origem", ["USB", "CAMERA", "MANUAL"], index=0)

        btn_enviar = st.form_submit_button("Processar Scan", use_container_width=True)

    if btn_enviar and codigo_input:
        token = session.get_token()
        headers = {"Authorization": f"Bearer {token}", "X-Tenant-Id": "demo_ms"}
        payload = {"codigo": codigo_input.strip(), "estabelecimento_id": 1, "pdv_id": "PDV-01", "origem": origem, "contexto": "VENDA"}

        try:
            res = requests.post("http://127.0.0.1:5000/api/v1/scanner/scan", json=payload, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                feedback = data.get("feedback", {})
                produtos = data.get("produtos", [])

                if feedback.get("tipo") == "WARNING":
                    st.warning(feedback.get("mensagem"))
                else:
                    st.success(feedback.get("mensagem"))

                if produtos:
                    st.divider()
                    st.subheader("📦 Produto Identificado")
                    for p in produtos:
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Produto", p.get("nome"))
                        c2.metric("Preço", f"R$ {p.get('preco_venda'):,.2f}")
                        c3.metric("Estoque", f"{p.get('estoque_atual')} {p.get('unidade')}")
                        c4.metric("Abaixo Mínimo", "Sim" if p.get("abaixo_minimo") else "Não")
            else:
                st.error("Erro no processamento do scan.")
        except Exception as e:
            st.error(f"Erro de conexão: {str(e)}")
