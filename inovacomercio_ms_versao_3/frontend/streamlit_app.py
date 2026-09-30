from __future__ import annotations
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="InovaComércio MS v6.0",
    page_icon="🌱",
    layout="wide"
)

# URL base da API Flask
API_URL = "http://127.0.0.1:5000/api/v1"

# Inicialização do estado de sessão para autenticação
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# --- TELA DE LOGIN ---
if not st.session_state["auth_token"]:
    st.markdown("<h2 style='text-align: center;'>🌱 InovaComércio MS v6.0</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Plataforma Inteligente de Gestão Comercial e Sustentabilidade</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Autenticação do Operador")
        email_input = st.text_input("E-mail corporativo", value="gestor@inovacomercio.ms")
        senha_input = st.text_input("Senha", type="password", value="123456")
        
        if st.button("Entrar no Sistema", use_container_width=True):
            try:
                response = requests.post(f"{API_URL}/auth/login", json={"email": email_input, "senha": senha_input})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["auth_token"] = data["access_token"]
                    st.session_state["usuario"] = data["usuario"]
                    st.success("Login efetuado com sucesso!")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Verifique os dados.")
            except Exception as e:
                st.error(f"Erro de conexão com o backend Flask: {e}")
    st.stop()

# --- HEADER E MENU LATERAL ---
headers = {"Authorization": f"Bearer {st.session_state['auth_token']}"}

st.sidebar.title("Painel de Gestão")
st.sidebar.write(f"**Operador:** {st.session_state['usuario']['nome']}")
st.sidebar.write(f"**Perfil:** {st.session_state['usuario']['role'].upper()}")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação",
    [
        "📊 Dashboard Executivo",
        "💲 Precificação & Produtos",
        "📈 Curva ABC",
        "♻️ Crédito Verde (ESG)",
        "📋 Trilha de Auditoria"
    ]
)

if st.sidebar.button("Terminar Sessão"):
    st.session_state["auth_token"] = None
    st.session_state["usuario"] = None
    st.rerun()

# --- 1. DASHBOARD EXECUTIVO ---
if menu == "📊 Dashboard Executivo":
    st.header("📊 Dashboard Executivo de Desempenho")
    st.caption("Indicadores chave de performance (KPIs) do varejo em Campo Grande – MS.")

    try:
        res = requests.get(f"{API_URL}/dashboard/resumo", headers=headers)
        if res.status_code == 200:
            kpis = res.json()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Faturamento do Mês", f"R$ {kpis['faturamento_mes']:,.2f}", f"{kpis['variacao_mom']*100:.1f}% MoM")
            c2.metric("Ticket Médio", f"R$ {kpis['ticket_medio']:.2f}")
            c3.metric("Margem Média", f"{kpis['margem_media']*100:.1f}%")
            c4.metric("Rupturas Ativas", kpis['rupturas_ativas'], delta_color="inverse")
            
            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                st.info(f"Saldo de Créditos Verdes Disponíveis: R$ {kpis['credito_verde_saldo']:,.2f}")
            with col_b:
                st.success("Integração Fiscal Ativa: NuvemFiscal / SEFAZ-MS")
        else:
            st.warning("Não foi possível carregar os dados do dashboard.")
    except Exception as e:
        st.error(f"Erro ao comunicar com a API: {e}")

# --- 2. PRECIFICAÇÃO E PRODUTOS ---
elif menu == "💲 Precificação & Produtos":
    st.header("💲 Gestão de Produtos e Precificação")
    st.caption("Tabela de custos, marcação e preços sugeridos com base no banco de dados SQLite.")

    try:
        res = requests.get(f"{API_URL}/precificacao", headers=headers)
        if res.status_code == 200:
            produtos = res.json()
            df_prod = pd.DataFrame(produtos)
            st.dataframe(df_prod, use_container_width=True, hide_index=True)
        else:
            st.error("Erro ao obter lista de produtos.")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")

# --- 3. CURVA ABC ---
elif menu == "📈 Curva ABC":
    st.header("📈 Análise de Curva ABC (Princípio de Pareto)")
    st.caption("Classificação do mix de mercadorias por relevância financeira no faturamento.")

    try:
        res = requests.get(f"{API_URL}/curva-abc", headers=headers)
        if res.status_code == 200:
            data = res.json()
            
            st.subheader("Top 10 Produtos - Curva ABC")
            df_top10 = pd.DataFrame(data["top10"])
            st.dataframe(df_top10, use_container_width=True, hide_index=True)
            
            st.subheader("Faturamento por Classe")
            df_classes = pd.DataFrame(data["classes"])
            fig = px.bar(df_classes, x="classe", y="faturamento", title="Faturamento Consolidado por Classe ABC", color="classe")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar dados da Curva ABC: {e}")

# --- 4. CRÉDITO VERDE (ESG) ---
elif menu == "♻️ Crédito Verde (ESG)":
    st.header("♻️ Logística Reversa & Sustentabilidade")
    st.caption("Monitoramento de resíduos comerciais e mitigação de emissões de carbono.")

    try:
        res = requests.get(f"{API_URL}/esg/indicadores", headers=headers)
        if res.status_code == 200:
            esg_data = res.json()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("CO₂ Evitado Acumulado", f"{esg_data['ambiental']['co2_evitado_kg']} kg")
            c2.metric("Resíduos Reciclados", f"{esg_data['ambiental']['residuos_kg']} kg")
            c3.metric("Conformidade de Governança", f"{esg_data['governança']['conformidade_pct']*100:.0f}%")
    except Exception as e:
        st.error(f"Erro ao carregar indicadores ESG: {e}")

# --- 5. TRILHA DE AUDITORIA ---
elif menu == "📋 Trilha de Auditoria":
    st.header("📋 Trilha de Auditoria Corporativa")
    st.caption("Registo imutável de eventos, acessos e operações críticas do sistema.")

    try:
        res = requests.get(f"{API_URL}/auditoria/eventos", headers=headers)
        if res.status_code == 200:
            eventos = res.json()
            df_audit = pd.DataFrame(eventos)
            st.dataframe(df_audit, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro ao carregar a trilha de auditoria: {e}")