from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.api import client

def render():
    st.title("📦 Curva ABC de Produtos — InovaComércio MS")
    dados = client.curva_abc()
    df = pd.DataFrame(dados.get("top10", []))

    if not df.empty:
        fig = px.bar(df, x="produto", y="faturamento", color="curva", title="Faturamento por Produto e Curva ABC")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)
