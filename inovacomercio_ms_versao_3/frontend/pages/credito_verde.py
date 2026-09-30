from __future__ import annotations
import streamlit as st
import requests

st.title("♻️ Crédito Verde & Logística Reversa (ESG)")
st.caption("Monitoramento de sustentabilidade e compensação de pegada de carbono no ecossistema comercial.")

API_URL = "http://127.0.0.1:5000/api/v1"

if not st.session_state.get("auth_token"):
    st.warning("Por favor, efetue o login na página principal.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['auth_token']}"}

try:
    res = requests.get(f"{API_URL}/esg/indicadores", headers=headers)
    if res.status_code == 200:
        data = res.json()
        ambiental = data.get("ambiental", {})
        social = data.get("social", {})
        governanca = data.get("governança", {})
        
        c1, c2, c3 = st.columns(3)
        c1.metric("CO₂ Evitado", f"{ambiental.get('co2_evitado_kg', 0)} kg")
        c2.metric("Resíduos Reciclados", f"{ambiental.get('residuos_kg', 0)} kg")
        c3.metric("Equipa / Colaboradores", social.get('colaboradores', 0))
        
        st.markdown("---")
        st.subheader("Índice de Conformidade e Governança")
        pct_gov = governanca.get('conformidade_pct', 0.0)
        st.progress(pct_gov)
        st.write(f"Nível de Adequação Regulatória: **{pct_gov*100:.1f}%**")
    else:
        st.error("Não foi possível carregar os indicadores ESG.")
except Exception as e:
    st.error(f"Erro de conexão: {e}")