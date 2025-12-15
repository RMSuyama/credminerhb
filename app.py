
import streamlit as st
import importlib
import sys

# Page Configuration (MUST BE FIRST)
st.set_page_config(
    page_title="CredMiner HB",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Internal modules
from src.styles import load_custom_css
from src.database import init_db
from src.auth import validate_session_token
from src.pages.auth import render_login
from src.pages.dashboard import render_dashboard
from src.pages.administrative import render_clients, render_debtors, render_debts
from src.pages.judicial import render_judicial, render_petitions
from src.pages.calculations import render_negotiation, render_payments, render_agreements
from src.pages.settings import render_settings

# --- INITIALIZATION ---
init_db()
load_custom_css()

# --- AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Check URL token if not logged in
if not st.session_state['logged_in']:
    params = st.query_params
    token = params.get("token", None)
    if token:
        username = validate_session_token(token)
        if username:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.rerun()

# --- ROUTING ---
if not st.session_state['logged_in']:
    render_login()
else:
    # --- SIDEBAR NAV ---
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
             <h2 style="color: #E67E22; margin:0; font-weight: 800; letter-spacing: -1px;">CredMiner</h2>
             <span style="color: #B0BEC5; font-size: 0.8rem; letter-spacing: 1px;">PROFESSIONAL</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.write(f"Olá, **{st.session_state.get('username', 'Usuário')}**")
        st.divider()
        
        # Navigation
        selected_module = "Dashboard" # Default
        
        # Principal
        st.markdown("**PRINCIPAL**")
        if st.button("📊 Dashboard", use_container_width=True): st.session_state['page'] = "Dashboard"
        
        st.markdown("**ADMINISTRATIVO**")
        if st.button("🏢 Clientes e Foros", use_container_width=True): st.session_state['page'] = "Clientes"
        if st.button("👥 Cadastro de Devedores", use_container_width=True): st.session_state['page'] = "Devedores"
        if st.button("💰 Gerenciar Dívidas", use_container_width=True): st.session_state['page'] = "Dívidas"
        
        st.markdown("**JUDICIAL**")
        if st.button("⚖️ Processos e Custas", use_container_width=True): st.session_state['page'] = "Judicial"
        if st.button("📄 Modelos de Petição", use_container_width=True): st.session_state['page'] = "Petições"
        
        st.markdown("**FINANCEIRO**")
        if st.button("🧮 Negociação / Simulação", use_container_width=True): st.session_state['page'] = "Simulação"
        if st.button("🤝 Gerenciar Acordos", use_container_width=True): st.session_state['page'] = "Acordos"
        if st.button("💸 Registrar Pagamento", use_container_width=True): st.session_state['page'] = "Pagamentos"
        
        st.divider()
        if st.button("⚙️ Configurações", use_container_width=True): st.session_state['page'] = "Configurações"
        
        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state['logged_in'] = False
            st.query_params.clear()
            st.rerun()

    # --- PAGE RENDERING ---
    page = st.session_state.get('page', 'Dashboard')
    
    if page == "Dashboard":
        render_dashboard()
        
    elif page == "Clientes":
        render_clients()
        
    elif page == "Devedores":
        render_debtors()
        
    elif page == "Dívidas":
        render_debts()
        
    elif page == "Judicial":
        render_judicial()
        
    elif page == "Petições":
        render_petitions()
        
    elif page == "Simulação":
        render_negotiation()
        
    elif page == "Acordos":
        render_agreements()
        
    elif page == "Pagamentos":
        render_payments()
        
    elif page == "Configurações":
        render_settings()
        
