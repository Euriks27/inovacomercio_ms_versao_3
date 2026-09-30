from __future__ import annotations
import streamlit as st
import requests
import pandas as pd

def render():
    st.title("💲 Gestão de Precificação & Produtos")
    st.caption("Módulo de cálculo de custos, margens e markups para o comércio de Campo Grande – MS.")

    API_URL = "http://127.0.0.1:5000/api/v1"

    # Validação de sessão ativa
    if not st.session_state.get("auth_token"):
        st.warning("Por favor, faça login na página principal para aceder a este módulo.")
        st.stop()

    headers = {"Authorization": f"Bearer {st.session_state['auth_token']}"}

    try:
        res = requests.get(f"{API_URL}/precificacao", headers=headers)
        if res.status_code == 200:
            produtos = res.json()
            if produtos:
                df = pd.DataFrame(produtos)
                st.subheader("Tabela de Produtos Cadastrados")
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.subheader("Simulador Rápido de Markup")
                with st.form("form_simulador"):
                    custo_base = st.number_input("Custo de Aquisição (R$)", min_value=0.0, value=20.0, step=0.5)
                    markup_aplicado = st.number_input("Markup Pretendido", min_value=1.0, value=1.6, step=0.05)
                    
                    calcular = st.form_submit_button("Calcular Projeção")
                    if calcular:
                        preco_sugerido = custo_base * markup_aplicado
                        margem_est = (preco_sugerido - custo_base) / preco_sugerido if preco_sugerido > 0 else 0
                        st.success(f"Preço de Venda Sugerido: R$ {preco_sugerido:.2f} | Margem de Lucro: {margem_est*100:.1f}%")
            else:
                st.info("Nenhum produto registado na base de dados.")
        else:
            st.error("Erro ao obter dados de precificação da API.")
    except Exception as e:
        st.error(f"Erro de conexão com o backend: {e}")