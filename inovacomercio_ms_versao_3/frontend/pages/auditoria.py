from __future__ import annotations
import streamlit as st
import pandas as pd
from frontend.api import client

def render():
    st.title("🛡️ Trilha de Auditoria — InovaComércio MS")
    eventos = client.auditoria_eventos()
    df = pd.DataFrame(eventos)
    if not df.empty and "ts" in df.columns:
        df["Data/Hora"] = pd.to_datetime(df["ts"], unit="s")
    st.dataframe(df, use_container_width=True)
