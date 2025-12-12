import streamlit as st
import pandas as pd
from datetime import date
from decimal import Decimal
from src.database import init_db, get_connection
from src.auth import check_credentials, create_session_token, validate_session_token
from src.calculator import Calculator
from src.scraper import update_all_indices

# Initialize Database (protected so Streamlit doesn't crash on startup if DB is unreachable)
db_init_error = None
DB_AVAILABLE = True
try:
    init_db()
except Exception as e:
    # Keep the app running and report the error inside the UI later
    db_init_error = e
    DB_AVAILABLE = False
    print("Warning: database initialization failed:", e)

st.set_page_config(page_title="CredMiner HB - Sistema de Recuperação de Crédito", layout="wide", page_icon="⚖️")

# Aplicar CSS corporativo (design anos 2000 - minimalista e profissional)
st.markdown("""
<style>
    /* Fontes e cores corporativas */
    :root {
        --primary-color: #1a3a52;
        --secondary-color: #2d5a7b;
        --accent-color: #3d7cab;
        --neutral-light: #f5f5f5;
        --neutral-dark: #333333;
        --border-color: #cccccc;
    }
    
    /* Header estilo corporativo */
    h1, h2, h3 {
        color: var(--primary-color) !important;
        font-family: Arial, sans-serif !important;
        font-weight: bold !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    h1 {
        font-size: 28px !important;
        border-bottom: 2px solid var(--primary-color) !important;
        padding-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 22px !important;
    }
    
    h3 {
        font-size: 18px !important;
        margin-top: 1rem !important;
    }
    
    /* Métrica - Design corporativo */
    div[data-testid="stMetric"] {
        background-color: white !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        padding: 1.25rem !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.08) !important;
    }
    
    div[data-testid="stMetric"] label {
        color: var(--primary-color) !important;
        font-weight: bold !important;
        font-size: 12px !important;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--neutral-dark) !important;
        font-size: 24px !important;
        font-weight: bold !important;
    }
    
    /* Buttons - Corporativo */
    button {
        border-radius: 4px !important;
        border: 1px solid var(--primary-color) !important;
        font-family: Arial, sans-serif !important;
    }
    
    button[type="primary"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    button[type="secondary"] {
        background-color: transparent !important;
        color: var(--primary-color) !important;
    }
    
    /* Tabs */
    div[role="tablist"] {
        border-bottom: 2px solid var(--border-color) !important;
    }
    
    /* Containers */
    section[data-testid="stSidebar"] {
        background-color: var(--neutral-light) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    /* DataFrame/Table */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
    }
    
    /* Success/Error Messages */
    div[data-testid="stAlert"] {
        border-radius: 4px !important;
        border-left: 4px solid !important;
    }
    
    /* Form elements */
    input, select, textarea {
        border-radius: 4px !important;
        border: 1px solid var(--border-color) !important;
        padding: 0.5rem !important;
        font-family: Arial, sans-serif !important;
    }
    
    /* Divider */
    hr {
        border: none !important;
        border-top: 1px solid var(--border-color) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Text geral */
    body {
        font-family: Arial, sans-serif !important;
        color: var(--neutral-dark) !important;
    }
</style>
"""
, unsafe_allow_html=True)

# If DB initialization failed, show a non-blocking warning so the Streamlit UI still loads
if not DB_AVAILABLE:
    try:
        st.warning(
            "Atenção: não foi possível conectar ao banco de dados Supabase. "
            "O app caiu para um banco local ou está em modo degradado. Verifique suas credenciais (st.secrets ou .env).\n"
            f"Erro: {db_init_error}"
        )
    except Exception:
        # If Streamlit isn't fully ready yet, print to console as fallback
        print("DB warning: ", db_init_error)


# Session State for Login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- PERSISTENT LOGIN LOGIC ---
if not st.session_state['logged_in']:
    # Check for token in URL
    query_params = st.query_params
    token = query_params.get("token", None)
    if token:
        user = validate_session_token(token)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = user
            st.rerun()

def login_page():
    # Styled Logo
    st.markdown("""
    <style>
    .logo-container {
        text-align: center;
        padding: 30px 0;
    }
    .logo-icon {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #0068C9 0%, #00B4D8 100%);
        border-radius: 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
        box-shadow: 0 8px 24px rgba(0, 104, 201, 0.3);
    }
    .logo-icon svg {
        width: 48px;
        height: 48px;
        fill: white;
    }
    .logo-text {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .logo-text .hb {
        color: #0068C9;
    }
    .logo-subtitle {
        font-size: 0.95rem;
        color: #666;
        margin-top: 5px;
    }
    </style>
    <div class="logo-container">
        <div class="logo-icon">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
        </div>
        <h1 class="logo-text">CredMiner <span class="hb">HB</span></h1>
        <p class="logo-subtitle">Sistema de Recuperação de Crédito</p>
    </div>
    """, unsafe_allow_html=True)

    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")
            
            if submit:
                if check_credentials(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    
                    # Set Token in URL
                    token = create_session_token(username)
                    st.query_params["token"] = token
                    
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

def get_debtors():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM debtors", conn)
    conn.close()
    return df

def get_debts(debtor_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM debts WHERE debtor_id = ?", conn, params=(debtor_id,))
    conn.close()
    return df


def main_app():
    # --- HEADER / NAVIGATION ---
    
    # Ensure active_tab is in session state
    if 'active_tab' not in st.session_state:
        st.session_state['active_tab'] = "Dashboard"

    with st.sidebar:
        st.title("Menu")
        
        # Custom CSS for "Despojado" Sidebar Buttons
        st.markdown("""
        <style>
        /* General Sidebar Button Style - Minimalist/Despojado */
        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            text-align: left;
            border: none;
            background: transparent;
            color: var(--text-color); /* Dark mode compatible */
            padding: 12px 15px;
            font-size: 16px;
            display: flex;
            justify-content: flex-start;
            border-radius: 8px;
            transition: background-color 0.2s, color 0.2s;
        }
        
        /* Hover Effect */
        section[data-testid="stSidebar"] .stButton button:hover {
            background-color: rgba(150, 150, 150, 0.1); 
            color: var(--text-color);
        }

        /* Active Button Styling (Focus) */
        section[data-testid="stSidebar"] .stButton button:focus {
            background-color: rgba(0, 104, 201, 0.15); /* Light blue tint */
            color: rgb(0, 104, 201);
            font-weight: 600;
        }

        /* Danger/Prank Button Override - RED & Centered */
        div[data-testid="stSidebar"] .stButton button[kind="primary"] { 
            /* This might target active buttons if I used kind=primary for them. 
               BUT I used type='secondary' or 'primary' depending on active state.
               Wait, the danger button is explicitly type='primary'.
               The Menu buttons: if active, also primary?
               If I make Active Menu Buttons primary, they will turn RED if I use generic primary selector.
               I MUST use the KEY selector for the danger button.
            */
        }
        
        .st-key-btn_danger button {
            background-color: #ff4b4b !important;
            color: white !important;
            border: 1px solid #ff4b4b !important;
            text-align: center !important;
            justify-content: center !important;
            font-weight: bold !important;
        }
        .st-key-btn_danger button:hover {
            background-color: #ff3333 !important;
            border-color: #ff3333 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Navigation Buttons Helper
        def nav_button(label, page_name, icon):
            is_active = st.session_state['active_tab'] == page_name
            label_with_icon = f"{icon}  {label}"
            
            # Use secondary for everything to avoid conflict with standard primary styles or my red override
            # relying on visual focus style defined in CSS above for "Active" look?
            # Or just use secondary and let the focus style handle the blue tint.
            # But focus is transient (only when clicked). Persistent active state requires logic.
            # I'll use type="secondary" always, and add a visual marker in text if active?
            # Or use a specific key-based class? Too complex for Streamlit keys.
            # I'll keep it simple: type="secondary". The user sees the page content change.
            # If they really want highlight, I'd need to inject style based on key.
            # Let's try to stick to "Despojado" -> clean.
            
            if st.button(label_with_icon, key=f"nav_{page_name}", use_container_width=True, type="secondary"):
                st.session_state['active_tab'] = page_name
                st.rerun()

        nav_button("Painel Geral", "Dashboard", "")
        nav_button("Devedores", "Cadastro de Devedores", "")
        nav_button("Dívidas", "Gerenciar Dívidas", "")
        nav_button("Judicial", "Judicialização", "")
        nav_button("Simulação", "Negociação / Simulação", "")
        nav_button("Pagamentos", "Registrar Pagamento", "")
        nav_button("Acordos", "Gerenciar Acordos", "")
        
        st.divider()
        
        # User & Config Section in Sidebar
        st.markdown(f"**Usuário:** {st.session_state.get('username', 'Admin')}")
        
        with st.expander("Configurações"):
            if st.button("Atualizar Índices (SELIC/IPCA)", help="Baixa dados do site da AASP"):
                with st.spinner("Atualizando índices..."):
                    try:
                        results = update_all_indices()
                        for k, v in results.items():
                            if v:
                                st.success(f"{k} atualizado!")
                            else:
                                st.warning(f"Falha ao atualizar {k}")
                    except Exception as e:
                        st.error(f"Erro: {e}")
            
            st.divider()
            
            # User Management Section
            st.markdown("**Gerenciar Usuários**")
            
            with st.form("create_user_form"):
                new_username = st.text_input("Novo Usuário")
                new_password = st.text_input("Senha", type="password")
                new_password_confirm = st.text_input("Confirmar Senha", type="password")
                
                if st.form_submit_button("Criar Usuário"):
                    if not new_username or not new_password:
                        st.error("Preencha todos os campos.")
                    elif new_password != new_password_confirm:
                        st.error("Senhas não conferem.")
                    else:
                        try:
                            import bcrypt
                            conn = get_connection()
                            cursor = conn.cursor()
                            
                            # Check if user exists
                            cursor.execute("SELECT username FROM users WHERE username = ?", (new_username,))
                            if cursor.fetchone():
                                st.error("Usuário já existe.")
                            else:
                                # Create user
                                password_bytes = new_password.encode('utf-8')
                                salt = bcrypt.gensalt()
                                hashed = bcrypt.hashpw(password_bytes, salt)
                                
                                cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                                             (new_username, hashed.decode('utf-8')))
                                conn.commit()
                                
                                # Generate shareable link
                                from src.auth import create_session_token
                                token = create_session_token(new_username)
                                
                                # Detect current URL base
                                # Try to get the app URL from Streamlit's context
                                try:
                                    # For Streamlit Cloud, this will return the public URL
                                    base_url = st.get_option("browser.serverAddress")
                                    if not base_url or base_url == "localhost":
                                        # Fallback for local development
                                        port = st.get_option("server.port") or 8501
                                        base_url = f"http://localhost:{port}"
                                    elif not base_url.startswith("http"):
                                        # Add https for cloud URLs
                                        base_url = f"https://{base_url}"
                                except:
                                    # Final fallback
                                    base_url = "http://localhost:8501"

                                
                                share_link = f"{base_url}?token={token}"
                                
                                st.success(f"Usuário '{new_username}' criado!")
                                st.info("Link de acesso (válido por 7 dias):")
                                st.code(share_link)
                                if "localhost" in base_url:
                                    st.warning("App rodando localmente. Para compartilhar, use a URL pública após o deploy.")

                                
                            conn.close()
                        except Exception as e:
                            st.error(f"Erro ao criar usuário: {e}")
            
            st.divider()
            
            if st.button("Sair do Sistema"):
                st.session_state['logged_in'] = False
                st.query_params.clear()
                st.rerun()

    # --- PRANK BUTTON (Hidden at bottom of Sidebar) ---
    st.sidebar.markdown("<br>" * 5, unsafe_allow_html=True) # Spacer
    if st.sidebar.button("APAGAR TUDO (PERIGO)", type="primary", key="btn_danger"):
        import random
        import time
        
        with st.sidebar.status("Iniciando destruição em massa...", expanded=True) as status:
            time.sleep(1)
            status.write("Acessando núcleo do servidor...")
            time.sleep(1)
            status.write("Aquecendo o Lança-Chamas (40%)...")
            time.sleep(1)
            status.write("Aquecendo o Lança-Chamas (80%)...")
            time.sleep(1)
            status.write("Aquecendo o Lança-Chamas (99%)...")
            time.sleep(1.5)
            status.update(label="ERRO CRÍTICO!", state="error", expanded=True)
        
        messages = [
            "ERRO: O sistema se recusou a apagar os dados pois está com apego emocional.",
            "Falha ao apagar: O banco de dados contratou um advogado.",
            "Impossível deletar: Culpado não encontrado (foi você?).",
            "Atenção: O FBI foi notificado (Brincadeira... ou não?).",
            "Erro 418: Sou um bule de chá e não apago dados.",
            "O banco de dados se escondeu debaixo da cama.",
            "Operação cancelada: Usuário muito bonito para cometer este crime.",
            "Apagando... 99%... Travou! Tente novamente em 2035.",
            "Você tem certeza? Porque eu não tenho. Cancelei por via das dúvidas."
        ]
        
        msg = random.choice(messages)
        st.sidebar.error(msg)
        st.sidebar.markdown(f"**Pegadinha!** Nada foi apagado.")
        st.balloons()

    # --- PAGE ROUTING ---
    page = st.session_state['active_tab']


    if page == "Dashboard":
        st.header("Painel de Análise")
        st.markdown("Visão geral de desempenho de cobrança e recuperação de crédito")
        
        conn = get_connection()
        try:
            # ===== QUERIES PARA ANÁLISES =====
            # Dados básicos
            total_debtors = pd.read_sql_query("SELECT count(*) as cnt FROM debtors", conn).iloc[0, 0]
            total_original_value = pd.read_sql_query("SELECT COALESCE(sum(original_value), 0) as total FROM debts", conn).iloc[0, 0]
            total_debts = pd.read_sql_query("SELECT count(*) as cnt FROM debts", conn).iloc[0, 0]
            
            # Acordos
            agreements_df = pd.read_sql_query("SELECT * FROM agreements", conn)
            active_agreements = len(agreements_df[agreements_df['status'] == 'active']) if not agreements_df.empty else 0
            total_agreed_value = agreements_df['agreed_value'].sum() if not agreements_df.empty else 0
            
            # Pagamentos realizados
            payments_df = pd.read_sql_query("SELECT * FROM payments", conn)
            total_recovered = payments_df['amount'].sum() if not payments_df.empty else 0
            total_payments = len(payments_df)
            
            # Taxa de recuperação
            recovery_rate = (total_recovered / total_original_value * 100) if total_original_value > 0 else 0
            remaining_value = total_original_value - total_recovered
            
            # KPIs principais (linha 1)
            st.markdown("### Indicadores de Desempenho")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    label="Devedores Ativos",
                    value=total_debtors,
                    delta=None,
                    help="Número total de devedores cadastrados"
                )
            
            with col2:
                st.metric(
                    label="Dívidas",
                    value=total_debts,
                    delta=None,
                    help="Número total de dívidas registradas"
                )
            
            with col3:
                st.metric(
                    label="Taxa Recuperação",
                    value=f"{recovery_rate:.1f}%",
                    delta=None,
                    help="Percentual do valor total já recuperado"
                )
            
            with col4:
                st.metric(
                    label="Acordos Ativos",
                    value=active_agreements,
                    delta=None,
                    help="Número de acordos em vigor"
                )
            
            with col5:
                st.metric(
                    label="Pagamentos",
                    value=total_payments,
                    delta=None,
                    help="Número total de pagamentos recebidos"
                )
            
            # ===== VALORES EM REAIS =====
            st.markdown("### Análise de Valores")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Valor Total em Aberto",
                    value=f"R$ {total_original_value:,.2f}",
                    help="Soma de todas as dívidas registradas"
                )
            
            with col2:
                st.metric(
                    label="Valor Recuperado",
                    value=f"R$ {total_recovered:,.2f}",
                    delta=f"{recovery_rate:.1f}%",
                    help="Total já recebido em pagamentos"
                )
            
            with col3:
                st.metric(
                    label="Valor em Aberto",
                    value=f"R$ {remaining_value:,.2f}",
                    help="Ainda a recuperar"
                )
            
            with col4:
                if active_agreements > 0:
                    avg_agreed = total_agreed_value / active_agreements if active_agreements > 0 else 0
                    st.metric(
                        label="Valor Médio/Acordo",
                        value=f"R$ {avg_agreed:,.2f}",
                        help="Valor médio dos acordos ativos"
                    )
                else:
                    st.metric(
                        label="Valor Médio/Acordo",
                        value="R$ 0,00",
                        help="Nenhum acordo ativo"
                    )
            
            # ===== GRÁFICOS ANALÍTICOS =====
            st.markdown("### Análises Detalhadas")
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Recuperação", "Acordos", "Dívidas", "Desempenho", "Detalhes"
            ])
            
            # TAB 1: Recuperação
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico: Recuperação vs Pendente
                    recovery_data = {
                        'Status': ['Recuperado', 'Pendente'],
                        'Valor (R$)': [total_recovered, remaining_value]
                    }
                    recovery_chart = pd.DataFrame(recovery_data)
                    st.bar_chart(recovery_chart.set_index('Status'), use_container_width=True)
                
                with col2:
                    # Proporção de Recuperação (Pizza)
                    if total_original_value > 0:
                        fig, ax = __import__('matplotlib.pyplot', fromlist=['pyplot']).subplots(figsize=(8, 6))
                        sizes = [total_recovered, remaining_value]
                        labels = [f'Recuperado\nR$ {total_recovered:,.0f}\n({recovery_rate:.1f}%)', 
                                 f'Pendente\nR$ {remaining_value:,.0f}\n({100-recovery_rate:.1f}%)']
                        colors = ['#2ecc71', '#e74c3c']
                        ax.pie(sizes, labels=labels, colors=colors, autopct='', startangle=90)
                        ax.set_title('Distribuição de Recuperação', fontsize=12, fontweight='bold')
                        st.pyplot(fig)
                    else:
                        st.warning("Sem dados de dívidas para exibir gráfico.")
            
            # TAB 2: Acordos
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Status dos Acordos
                    if not agreements_df.empty:
                        agreement_status = agreements_df['status'].value_counts()
                        st.bar_chart(agreement_status, use_container_width=True)
                    else:
                        st.info("Nenhum acordo registrado ainda.")
                
                with col2:
                    # Top Acordos por Valor
                    if not agreements_df.empty:
                        top_agreements = agreements_df.nlargest(5, 'agreed_value')[['debtor_id', 'agreed_value', 'status']]
                        top_agreements.columns = ['Devedor ID', 'Valor Acordo (R$)', 'Status']
                        st.dataframe(top_agreements, use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhum acordo para exibir.")
            
            # TAB 3: Distribuição de Dívidas
            with tab3:
                # Dívidas por tipo de contrato
                debts_by_type = pd.read_sql_query("""
                    SELECT contract_type, count(*) as qtd, sum(original_value) as total_value
                    FROM debts
                    GROUP BY contract_type
                    ORDER BY total_value DESC
                """, conn)
                
                if not debts_by_type.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.bar_chart(debts_by_type.set_index('contract_type')['qtd'], use_container_width=True)
                    
                    with col2:
                        st.bar_chart(debts_by_type.set_index('contract_type')['total_value'], use_container_width=True)
                    
                    st.dataframe(debts_by_type, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhuma dívida registrada.")
            
            # TAB 4: Desempenho de Pagamentos
            with tab4:
                # Evolução de pagamentos ao longo do tempo
                if not payments_df.empty:
                    payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])
                    payments_timeline = payments_df.groupby('payment_date')['amount'].sum().sort_index()
                    
                    st.line_chart(payments_timeline, use_container_width=True)
                    
                    # Estatísticas de pagamentos
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Pagamento Médio", f"R$ {payments_df['amount'].mean():,.2f}")
                    with col2:
                        st.metric("Maior Pagamento", f"R$ {payments_df['amount'].max():,.2f}")
                    with col3:
                        st.metric("Menor Pagamento", f"R$ {payments_df['amount'].min():,.2f}")
                    
                    # Tabela de últimos pagamentos
                    st.subheader("Últimos 10 Pagamentos")
                    recent_payments = payments_df.nlargest(10, 'payment_date')[['debtor_id', 'amount', 'payment_date', 'installment_number']]
                    recent_payments.columns = ['Devedor ID', 'Valor (R$)', 'Data', 'Parcela']
                    st.dataframe(recent_payments, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum pagamento registrado ainda.")
            
            # TAB 5: Detalhes por Devedor
            with tab5:
                # Devedores com maiores dívidas
                debtors_debts = pd.read_sql_query("""
                    SELECT d.id, d.name, COUNT(db.id) as num_debts, SUM(db.original_value) as total_debt
                    FROM debtors d
                    LEFT JOIN debts db ON d.id = db.debtor_id
                    GROUP BY d.id, d.name
                    ORDER BY total_debt DESC
                    LIMIT 10
                """, conn)
                
                if not debtors_debts.empty:
                    st.subheader("Top 10 Maiores Devedores")
                    debtors_debts.columns = ['ID', 'Nome', 'Nº Dívidas', 'Total Devido (R$)']
                    st.dataframe(debtors_debts, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum devedor registrado.")
            
            # ===== ATALHOS RÁPIDOS =====
            st.markdown("### Ações Rápidas")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Registrar Nova Dívida", use_container_width=True):
                    st.session_state['active_tab'] = "Gerenciar Dívidas"
                    st.rerun()
            
            with col2:
                if st.button("Registrar Novo Acordo", use_container_width=True):
                    st.session_state['active_tab'] = "Negociação / Simulação"
                    st.rerun()
            
            with col3:
                if st.button("Registrar Pagamento", use_container_width=True):
                    st.info("Esta funcionalidade será adicionada em breve.")
                
        finally:
            conn.close()

    elif page == "Judicialização":
        st.header("Gestão de Custas Judiciais")
        st.info("Aqui você lança custas processuais que serão somadas ao valor final da dívida para acordo.")
        
        debtors = get_debtors()
        if not debtors.empty:
            debtor_options = debtors.apply(lambda x: f"{x['name']} (CPF: {x['cpf_cnpj']})", axis=1).tolist()
            selected_debtor_str = st.selectbox("Selecione o Devedor", options=debtor_options)
            
            if selected_debtor_str:
                selected_debtor_cpf = selected_debtor_str.split("CPF: ")[1].replace(")", "")
                selected_debtor = debtors[debtors['cpf_cnpj'] == selected_debtor_cpf].iloc[0]
                selected_debtor_id = int(selected_debtor['id'])
                
                # Form for new expense
                with st.form("new_legal_expense"):
                    st.subheader("Lançar Nova Custa")
                    col_l1, col_l2 = st.columns([3, 1])
                    desc_custas = col_l1.text_input("Descrição (Ex: Diligência Oficial de Justiça)")
                    val_custas = col_l2.number_input("Valor (R$)", min_value=0.0, step=10.0)
                    if st.form_submit_button("Lançar Custa"):
                        conn = get_connection()
                        conn.execute("INSERT INTO legal_expenses (debtor_id, description, value, date) VALUES (?, ?, ?, ?)",
                                     (selected_debtor_id, desc_custas, val_custas, date.today().strftime('%Y-%m-%d')))
                        conn.commit()
                        conn.close()
                        st.success("Custa lançada com sucesso!")
                        st.rerun()
                
                # List existing expenses
                conn = get_connection()
                expenses = pd.read_sql_query("SELECT id, description, value, date FROM legal_expenses WHERE debtor_id = ?", conn, params=(selected_debtor_id,))
                conn.close()
                
                if not expenses.empty:
                    st.markdown("### Custas Lançadas")
                    st.dataframe(expenses, use_container_width=True)
                    st.metric("Total Custas", f"R$ {expenses['value'].sum():,.2f}")
                    
                    # Delete Legal Expenses
                    with st.expander("Excluir Custas"):
                        st.warning("Selecione as custas para excluir.")
                        
                        # Create options for multiselect
                        expense_options = {row['id']: f"{row['description']} - R$ {row['value']:.2f} ({row['date']})" for i, row in expenses.iterrows()}
                        
                        selected_expenses = st.multiselect(
                            "Selecione as custas",
                            options=list(expense_options.keys()),
                            format_func=lambda x: expense_options[x]
                        )
                        
                        if st.button("Excluir Custas Selecionadas", key="delete_expenses_btn"):
                            if selected_expenses:
                                st.session_state['confirm_delete_expenses'] = True
                                st.session_state['delete_expense_ids'] = selected_expenses
                            else:
                                st.warning("Selecione pelo menos uma custa.")
                        
                        if st.session_state.get('confirm_delete_expenses'):
                            st.error(f"Tem certeza que deseja excluir {len(st.session_state['delete_expense_ids'])} custa(s)?")
                            col_yes, col_no = st.columns(2)
                            
                            if col_yes.button("Sim, Excluir"):
                                conn = get_connection()
                                cursor = conn.cursor()
                                try:
                                    ids_to_delete = st.session_state['delete_expense_ids']
                                    if len(ids_to_delete) == 1:
                                        cursor.execute("DELETE FROM legal_expenses WHERE id = ?", (ids_to_delete[0],))
                                    else:
                                        cursor.execute(f"DELETE FROM legal_expenses WHERE id IN {tuple(ids_to_delete)}")
                                    conn.commit()
                                    st.success("Custas excluídas!")
                                    st.session_state['confirm_delete_expenses'] = False
                                    del st.session_state['delete_expense_ids']
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao excluir: {e}")
                                finally:
                                    conn.close()
                            
                            if col_no.button("Cancelar"):
                                st.session_state['confirm_delete_expenses'] = False
                                st.rerun()
                else:
                    st.info("Nenhuma custa judicial lançada para este devedor.")
        else:
            st.warning("Cadastre devedores primeiro.")

    elif page == "Cadastro de Devedores":
        st.header("Gestão de Devedores")
        
        tab1, tab2 = st.tabs(["Novo Devedor", "Gerenciar Devedores (Endereços/Fiadores)"])
        
        with tab1:
            st.subheader("Cadastrar Novo Devedor")
            with st.form("new_debtor"):
                name = st.text_input("Nome")
                cpf = st.text_input("CPF/CNPJ")
                rg = st.text_input("RG")
                email = st.text_input("Email")
                phone = st.text_input("Telefone")
                notes = st.text_area("Observações")
                submit = st.form_submit_button("Salvar Devedor")
                
                if submit:
                    conn = get_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO debtors (name, cpf_cnpj, rg, email, phone, notes) VALUES (?, ?, ?, ?, ?, ?)",
                                       (name, cpf, rg, email, phone, notes))
                        conn.commit()
                        st.success("Devedor cadastrado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")
                    finally:
                        conn.close()

        with tab2:
            st.subheader("Gerenciar Devedor Existente")
            debtors = get_debtors()
            if debtors.empty:
                st.info("Nenhum devedor cadastrado.")
            else:
                debtor_opts = {row['id']: f"{row['name']} ({row['cpf_cnpj']})" for i, row in debtors.iterrows()}
                selected_debtor_id = st.selectbox("Selecione o Devedor para Editar", options=debtor_opts.keys(), format_func=lambda x: debtor_opts[x])
                
                # Fetch selected debtor details
                conn = get_connection()
                debtor = pd.read_sql_query("SELECT * FROM debtors WHERE id = ?", conn, params=(selected_debtor_id,)).iloc[0]
                conn.close()
                
                # Editable Debtor Info
                with st.expander("Editar Dados do Devedor", expanded=True):
                    with st.form("edit_debtor_form"):
                        col_ed1, col_ed2 = st.columns(2)
                        new_name = col_ed1.text_input("Nome", value=debtor['name'])
                        new_cpf = col_ed2.text_input("CPF/CNPJ", value=debtor['cpf_cnpj'])
                        
                        col_ed3, col_ed4 = st.columns(2)
                        new_rg = col_ed3.text_input("RG", value=debtor['rg'] if debtor['rg'] else "")
                        new_email = col_ed4.text_input("Email", value=debtor['email'] if debtor['email'] else "")
                        
                        new_phone = st.text_input("Telefone", value=debtor['phone'] if debtor['phone'] else "")
                        new_notes = st.text_area("Observações", value=debtor['notes'] if debtor['notes'] else "")
                        
                        if st.form_submit_button("Salvar Alterações do Devedor"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            try:
                                cursor.execute("""
                                    UPDATE debtors 
                                    SET name = ?, cpf_cnpj = ?, rg = ?, email = ?, phone = ?, notes = ?
                                    WHERE id = ?
                                """, (new_name, new_cpf, new_rg, new_email, new_phone, new_notes, selected_debtor_id))
                                conn.commit()
                                st.success("Dados do devedor atualizados!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {e}")
                            finally:
                                conn.close()

                # --- DANGER ZONE (DELETE DEBTOR) ---
                with st.expander("Zona de Perigo - Excluir Devedor"):
                    st.error("Atenção: A exclusão do devedor removerá PERMANENTEMENTE todos os históricos, dívidas, endereços e fiadores vinculados.")
                    if st.button("Excluir Este Devedor"):
                        st.session_state['confirm_delete_debtor'] = True
                    
                    if st.session_state.get('confirm_delete_debtor'):
                        st.warning(f"Confirma a exclusão de '{debtor['name']}'? Esta ação é irreversível.")
                        col_del_yes, col_del_no = st.columns(2)
                        
                        if col_del_yes.button("SIM, EXCLUIR TUDO"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            try:
                                # 1. Delete Addresses of Guarantors (Indirect Link)
                                # Find guarantors first
                                cursor.execute("SELECT id FROM guarantors WHERE debtor_id = ?", (selected_debtor_id,))
                                g_ids = [row[0] for row in cursor.fetchall()]
                                if g_ids:
                                    cursor.execute(f"DELETE FROM addresses WHERE guarantor_id IN {tuple(g_ids) if len(g_ids) > 1 else f'({g_ids[0]})'}")

                                # 2. Delete Addresses of Debtor
                                cursor.execute("DELETE FROM addresses WHERE debtor_id = ?", (selected_debtor_id,))
                                
                                # 3. Delete Guarantors
                                cursor.execute("DELETE FROM guarantors WHERE debtor_id = ?", (selected_debtor_id,))
                                
                                # 4. Delete Debts
                                cursor.execute("DELETE FROM debts WHERE debtor_id = ?", (selected_debtor_id,))
                                
                                # 5. Delete Debtor
                                cursor.execute("DELETE FROM debtors WHERE id = ?", (selected_debtor_id,))
                                
                                conn.commit()
                                st.success("Devedor e todos os dados vinculados foram removidos.")
                                st.session_state['confirm_delete_debtor'] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir: {e}")
                            finally:
                                conn.close()

                        if col_del_no.button("Cancelar Exclusão"):
                            st.session_state['confirm_delete_debtor'] = False
                            st.rerun()
                
                man_tab1, man_tab2 = st.tabs(["Endereços", "Fiadores"])
                
                # --- ADDRESS MANAGEMENT ---
                with man_tab1:
                    st.markdown("### Endereços do Devedor")
                    
                    # Add Address Form
                    with st.expander("Adicionar Novo Endereço"):
                        col_cep, col_btn = st.columns([3, 1])
                        cep_input = col_cep.text_input("CEP")
                        if col_btn.button("Buscar CEP"):
                            from src.services import get_address_from_viacep
                            addr_data = get_address_from_viacep(cep_input)
                            if addr_data:
                                st.session_state['addr_street'] = addr_data['street']
                                st.session_state['addr_neighborhood'] = addr_data['neighborhood']
                                st.session_state['addr_city'] = addr_data['city']
                                st.session_state['addr_state'] = addr_data['state']
                            else:
                                st.error("CEP não encontrado.")
                        
                        with st.form("add_address_form"):
                            street = st.text_input("Rua", value=st.session_state.get('addr_street', ''))
                            number = st.text_input("Número")
                            neighborhood = st.text_input("Bairro", value=st.session_state.get('addr_neighborhood', ''))
                            city = st.text_input("Cidade", value=st.session_state.get('addr_city', ''))
                            state = st.text_input("Estado", value=st.session_state.get('addr_state', ''))
                            is_primary = st.checkbox("Endereço Principal?")
                            
                            submit_addr = st.form_submit_button("Salvar Endereço")
                            if submit_addr:
                                conn = get_connection()
                                cursor = conn.cursor()
                                cursor.execute("""
                                    INSERT INTO addresses (debtor_id, cep, street, number, neighborhood, city, state, is_primary)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (selected_debtor_id, cep_input, street, number, neighborhood, city, state, is_primary))
                                conn.commit()
                                conn.close()
                                st.success("Endereço adicionado!")
                                st.rerun()

                    # List Addresses
                    conn = get_connection()
                    addrs = pd.read_sql_query("SELECT * FROM addresses WHERE debtor_id = ?", conn, params=(selected_debtor_id,))
                    conn.close()
                    if not addrs.empty:
                        st.dataframe(addrs[['id', 'cep', 'street', 'number', 'neighborhood', 'city', 'state', 'is_primary']], use_container_width=True)
                        
                        # Delete Addresses
                        with st.expander("Excluir Endereços"):
                            st.warning("Selecione os endereços para excluir.")
                            
                            # Create options for multiselect
                            addr_options = {row['id']: f"{row['street']}, {row['number']} - {row['city']}/{row['state']}" for i, row in addrs.iterrows()}
                            
                            selected_addrs = st.multiselect(
                                "Selecione os endereços",
                                options=list(addr_options.keys()),
                                format_func=lambda x: addr_options[x]
                            )
                            
                            if st.button("Excluir Endereços Selecionados", key="delete_addrs_btn"):
                                if selected_addrs:
                                    st.session_state['confirm_delete_addrs'] = True
                                    st.session_state['delete_addr_ids'] = selected_addrs
                                else:
                                    st.warning("Selecione pelo menos um endereço.")
                            
                            if st.session_state.get('confirm_delete_addrs'):
                                st.error(f"Tem certeza que deseja excluir {len(st.session_state['delete_addr_ids'])} endereço(s)?")
                                col_yes, col_no = st.columns(2)
                                
                                if col_yes.button("Sim, Excluir"):
                                    conn = get_connection()
                                    cursor = conn.cursor()
                                    try:
                                        ids_to_delete = st.session_state['delete_addr_ids']
                                        if len(ids_to_delete) == 1:
                                            cursor.execute("DELETE FROM addresses WHERE id = ?", (ids_to_delete[0],))
                                        else:
                                            cursor.execute(f"DELETE FROM addresses WHERE id IN {tuple(ids_to_delete)}")
                                        conn.commit()
                                        st.success("Endereços excluídos!")
                                        st.session_state['confirm_delete_addrs'] = False
                                        del st.session_state['delete_addr_ids']
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao excluir: {e}")
                                    finally:
                                        conn.close()
                                
                                if col_no.button("Cancelar"):
                                    st.session_state['confirm_delete_addrs'] = False
                                    st.rerun()
                    else:
                        st.info("Nenhum endereço cadastrado.")

                # --- GUARANTOR MANAGEMENT ---
                with man_tab2:
                    st.markdown("### Fiadores")
                    
                    with st.expander("Adicionar Novo Fiador"):
                        with st.form("add_guarantor"):
                            g_name = st.text_input("Nome do Fiador")
                            g_cpf = st.text_input("CPF do Fiador")
                            g_rg = st.text_input("RG do Fiador")
                            g_email = st.text_input("Email")
                            g_phone = st.text_input("Telefone")
                            g_notes = st.text_area("Observações")
                            
                            submit_g = st.form_submit_button("Salvar Fiador")
                            if submit_g:
                                conn = get_connection()
                                cursor = conn.cursor()
                                cursor.execute("""
                                    INSERT INTO guarantors (debtor_id, name, cpf, rg, email, phone, notes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (selected_debtor_id, g_name, g_cpf, g_rg, g_email, g_phone, g_notes))
                                conn.commit()
                                conn.close()
                                st.success("Fiador adicionado!")
                                st.rerun()
                    
                    # List Guarantors
                    conn = get_connection()
                    guarantors = pd.read_sql_query("SELECT * FROM guarantors WHERE debtor_id = ?", conn, params=(selected_debtor_id,))
                    conn.close()
                    
                    if not guarantors.empty:
                        for i, g in guarantors.iterrows():
                            with st.expander(f"Fiador: {g['name']} ({g['cpf']})"):
                                st.write(f"**RG:** {g['rg']} | **Email:** {g['email']} | **Tel:** {g['phone']}")
                                
                                # Guarantor Addresses
                                st.markdown("#### Endereços do Fiador")
                                
                                # Add Guarantor Address Form (Nested)
                                g_cep_key = f"g_cep_{g['id']}"
                                col_g_cep, col_g_btn = st.columns([3, 1])
                                g_cep_input = col_g_cep.text_input("CEP", key=g_cep_key)
                                if col_g_btn.button("Buscar", key=f"btn_{g_cep_key}"):
                                    from src.services import get_address_from_viacep
                                    g_addr_data = get_address_from_viacep(g_cep_input)
                                    if g_addr_data:
                                        st.session_state[f'g_street_{g["id"]}'] = g_addr_data['street']
                                        st.session_state[f'g_neigh_{g["id"]}'] = g_addr_data['neighborhood']
                                        st.session_state[f'g_city_{g["id"]}'] = g_addr_data['city']
                                        st.session_state[f'g_state_{g["id"]}'] = g_addr_data['state']
                                
                                with st.form(f"add_g_addr_{g['id']}"):
                                    g_street = st.text_input("Rua", value=st.session_state.get(f'g_street_{g["id"]}', ''))
                                    g_number = st.text_input("Número")
                                    g_neigh = st.text_input("Bairro", value=st.session_state.get(f'g_neigh_{g["id"]}', ''))
                                    g_city = st.text_input("Cidade", value=st.session_state.get(f'g_city_{g["id"]}', ''))
                                    g_state = st.text_input("Estado", value=st.session_state.get(f'g_state_{g["id"]}', ''))
                                    
                                    if st.form_submit_button("Adicionar Endereço ao Fiador"):
                                        conn = get_connection()
                                        cursor = conn.cursor()
                                        cursor.execute("""
                                            INSERT INTO addresses (guarantor_id, cep, street, number, neighborhood, city, state)
                                            VALUES (?, ?, ?, ?, ?, ?, ?)
                                        """, (g['id'], g_cep_input, g_street, g_number, g_neigh, g_city, g_state))
                                        conn.commit()
                                        conn.close()
                                        st.success("Endereço do fiador salvo!")
                                        st.rerun()
                                
                                # List Guarantor Addresses
                                conn = get_connection()
                                g_addrs = pd.read_sql_query("SELECT * FROM addresses WHERE guarantor_id = ?", conn, params=(g['id'],))
                                conn.close()
                                if not g_addrs.empty:
                                    st.dataframe(g_addrs[['cep', 'street', 'number', 'neighborhood', 'city', 'state']], use_container_width=True)
                    else:
                        st.info("Nenhum fiador cadastrado.")

    elif page == "Gerenciar Dívidas":
        st.header("Gerenciar Dívidas")
        
        debtors = get_debtors()
        if debtors.empty:
            st.warning("Cadastre devedores primeiro.")
        else:
            debtor_opts = {row['id']: f"{row['name']} ({row['cpf_cnpj']})" for i, row in debtors.iterrows()}
            selected_debtor_id = st.selectbox("Selecione o Devedor", options=debtor_opts.keys(), format_func=lambda x: debtor_opts[x])
            
            st.divider()

            # --- FETCH DEBTS ---
            debts = get_debts(selected_debtor_id)
            
            # Create Visual Index 1..N
            if not debts.empty:
                debts = debts.sort_values(by='due_date').reset_index(drop=True)
                debts['Item'] = range(1, len(debts) + 1)
                
                # Metrics
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Total de Dívidas", len(debts))
                col_m2.metric("Valor Total Original", f"R$ {debts['original_value'].sum():,.2f}")
                col_m3.metric("Último Vencimento", debts['due_date'].max() if not debts['due_date'].empty else "-")

            st.subheader("Lista de Dívidas")
            
            if not debts.empty:
                # Ensure due_date is datetime for the editor
                debts['due_date'] = pd.to_datetime(debts['due_date'])
                
                # --- INLINE EDITING ---
                column_config = {
                    "Item": st.column_config.NumberColumn("#", disabled=True, width="small"),
                    # id column is hidden via column_order
                    "contract_type": st.column_config.SelectboxColumn("Tipo Contrato", options=["CESU", "PAFE", "PPD", "MENSALIDADES", "JUDICIAL"], required=True),
                    "description": st.column_config.TextColumn("Descrição", required=True),
                    "original_value": st.column_config.NumberColumn("Valor Original", min_value=0.01, step=0.01, format="R$ %.2f", required=True),
                    "due_date": st.column_config.DateColumn("Vencimento", required=True),
                    "fine_type": st.column_config.TextColumn("Tipo Multa (Mensalidade)")
                }
                
                # Reorder columns for display
                display_cols = ['Item', 'id', 'contract_type', 'description', 'original_value', 'due_date', 'fine_type']
                visible_cols = ['Item', 'contract_type', 'description', 'original_value', 'due_date', 'fine_type']
                
                edited_debts = st.data_editor(
                    debts[display_cols],
                    column_config=column_config,
                    column_order=visible_cols, # Hides 'id'
                    use_container_width=True,
                    hide_index=True,
                    key="debts_editor",
                    num_rows="dynamic" # Allows adding/deleting rows directly? No, keeping custom delete for safety
                )
                
                col_save, col_del = st.columns([1, 4])
                
                with col_save:
                    if st.button("Salvar Alterações", type="primary"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            # Iterate over edited rows and update DB
                            for index, row in edited_debts.iterrows():
                                # Convert Timestamp to date/string for SQLite
                                d_date = row['due_date']
                                if hasattr(d_date, 'date'):
                                    d_date = d_date.date()
                                    
                                cursor.execute("""
                                    UPDATE debts 
                                    SET contract_type = ?, description = ?, original_value = ?, due_date = ?, fine_type = ?
                                    WHERE id = ?
                                """, (row['contract_type'], row['description'], row['original_value'], d_date, row['fine_type'], row['id']))
                            
                            conn.commit()
                            st.success("Alterações salvas com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar alterações: {e}")
                        finally:
                            conn.close()

                # --- DELETION WITH CONFIRMATION (Using Visual Index) ---
                with st.expander("Excluir Dívidas"):
                    st.warning("Selecione os itens pelo número (#) para excluir.")
                    # Create options using the visual ITEM number
                    # Map Item # back to Real ID
                    item_map = {row['Item']: row['id'] for i, row in debts.iterrows()}
                    
                    selected_items = st.multiselect(
                        "Selecione os itens para excluir", 
                        options=debts['Item'], 
                        format_func=lambda x: f"Item {x} - {debts.loc[debts['Item']==x, 'description'].values[0]} ({debts.loc[debts['Item']==x, 'original_value'].values[0]:.2f})"
                    )
                    
                    if st.button("Excluir Selecionadas"):
                        if selected_items:
                            st.session_state['confirm_delete'] = True
                            st.session_state['delete_items'] = selected_items
                        else:
                            st.warning("Selecione pelo menos um item.")
                    
                    if st.session_state.get('confirm_delete'):
                        st.error(f"⚠️ Tem certeza que deseja excluir os itens: {st.session_state['delete_items']}?")
                        col_conf_yes, col_conf_no = st.columns(2)
                        
                        if col_conf_yes.button("Sim, Excluir Definitivamente"):
                            ids_to_delete = [item_map[i] for i in st.session_state['delete_items']]
                            conn = get_connection()
                            cursor = conn.cursor()
                            try:
                                if len(ids_to_delete) == 1:
                                    cursor.execute("DELETE FROM debts WHERE id = ?", (ids_to_delete[0],))
                                else:
                                    cursor.execute(f"DELETE FROM debts WHERE id IN {tuple(ids_to_delete)}")
                                conn.commit()
                                st.success("Dívidas excluídas!")
                                st.session_state['confirm_delete'] = False
                                del st.session_state['delete_items']
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir: {e}")
                            finally:
                                conn.close()
                        
                        if col_conf_no.button("Cancelar"):
                            st.session_state['confirm_delete'] = False
                            st.rerun()
                            
            else:
                st.info("Nenhum registro encontrado para este devedor.")

            st.divider()
            
            # --- ADD NEW DEBT (Moved to bottom/cleaner section) ---
            with st.expander("Adicionar Nova Dívida"):
                with st.form("new_debt"):
                    col_n1, col_n2 = st.columns(2)
                    contract_type = col_n1.selectbox("Tipo de Contrato", ["CESU", "PAFE", "PPD", "MENSALIDADES", "JUDICIAL"])
                    fine_type = None
                    if contract_type == "MENSALIDADES":
                        fine_type = col_n2.radio("Tipo de Contrato", ["Físico", "Digital"], horizontal=True)

                    
                    description = st.text_input("Descrição (ex: Mensalidade Maio/2023)")
                    
                    col_n3, col_n4 = st.columns(2)
                    original_value = col_n3.number_input("Valor Original (R$)", min_value=0.01, step=0.01)
                    start_due_date = col_n4.date_input("Data de Vencimento (1ª Parcela)")
                    
                    st.markdown("---")
                    is_batch = st.checkbox("Gerar em Lote (Parcelas)?")
                    num_installments = 1
                    if is_batch:
                        num_installments = st.number_input("Número de Parcelas", min_value=2, value=12, step=1)
                    
                    submit = st.form_submit_button("Adicionar Dívida(s)")
                    
                    if submit:
                        if original_value <= 0:
                            st.error("O valor deve ser maior que zero.")
                        else:
                            conn = get_connection()
                            cursor = conn.cursor()
                            try:
                                from dateutil.relativedelta import relativedelta
                                
                                for i in range(num_installments):
                                    current_due_date = start_due_date + relativedelta(months=i)
                                    
                                    if is_batch:
                                        current_desc = f"{description} ({i+1}/{num_installments})"
                                    else:
                                        current_desc = description
                                    
                                    cursor.execute("INSERT INTO debts (debtor_id, contract_type, description, original_value, due_date, fine_type) VALUES (?, ?, ?, ?, ?, ?)",
                                                   (selected_debtor_id, contract_type, current_desc, original_value, current_due_date, fine_type))
                                
                                conn.commit()
                                st.success(f"{num_installments} dívida(s) adicionada(s)!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao adicionar: {e}")
                            finally:
                                conn.close()

    elif page == "Negociação / Simulação":
        st.header("Negociação e Acordo Avançado")
        
        debtors = get_debtors()
        if debtors.empty:
            st.warning("Cadastre devedores primeiro.")
        else:
            debtor_opts = {row['id']: f"{row['name']} ({row['cpf_cnpj']})" for i, row in debtors.iterrows()}
            selected_debtor_id = st.selectbox("Selecione o Devedor", options=debtor_opts.keys(), format_func=lambda x: debtor_opts[x])
            
            calc_date = st.date_input("Data do Cálculo", value=date.today())
            
            debts = get_debts(selected_debtor_id)
            
            if debts.empty:
                st.info("Este devedor não possui dívidas cadastradas.")
            else:
                st.divider()
                st.subheader("1. Composição da Dívida (Memorial de Cálculo)")
                
                # --- CALCULATION ---
                results = []
                
                # 1. Calculate Debts
                for i, debt in debts.iterrows():
                    res = Calculator.calculate(
                        contract_type=debt['contract_type'],
                        original_value=debt['original_value'],
                        due_date=debt['due_date'],
                        calc_date=calc_date,
                        fine_type=debt['fine_type']
                    )
                    res['id'] = debt['id']
                    res['description'] = debt['description']
                    res['type'] = 'Dívida'
                    results.append(res)
                
                # 2. Calculate Legal Expenses (Custas) as Debts
                conn = get_connection()
                expenses = pd.read_sql_query("SELECT id, description, value, date FROM legal_expenses WHERE debtor_id = ?", conn, params=(selected_debtor_id,))
                conn.close()
                
                for i, exp in expenses.iterrows():
                    # Calculate using LegalExpenseRule ('CUSTAS')
                    res_exp = Calculator.calculate(
                        contract_type="CUSTAS",
                        original_value=exp['value'],
                        due_date=exp['date'],
                        calc_date=calc_date
                    )
                    res_exp['id'] = f"exp_{exp['id']}"
                    res_exp['description'] = f"Custa: {exp['description']}"
                    res_exp['type'] = 'Custa'
                    results.append(res_exp)

                if not results:
                    st.warning("Nenhuma dívida ou custa encontrada.")
                else:
                    df_res = pd.DataFrame(results)
                    
                    # Sort by Due Date (implied or need to add date to result for sorting?)
                    # Calculator output doesn't return 'date' explicitly but we have it.
                    # Let's trust the order or just list them.
                    
                    # Totals Logic
                    subtotal_corrected = df_res['total'].sum()
                    
                    # 3. Attorney Fees (5%)
                    # The report applies fees on the SUBOTAL (Correction + Interest + Fine)
                    attorney_fees_percent = Decimal("0.05")
                    attorney_fees_value = subtotal_corrected * attorney_fees_percent
                    
                    grand_total = subtotal_corrected + attorney_fees_value
                    
                    # Display Composition Table matching Report
                    st.markdown("### Detalhamento")
                    
                    # Display Table
                    display_df = df_res[['description', 'original', 'corrected', 'interest', 'fine', 'total']].copy()
                    display_df.columns = ['Descrição', 'Valor Original', 'Valor Atualizado', 'Juros', 'Multa', 'Total']
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Summary Metrics
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Subtotal (Dívida + Custas)", f"R$ {subtotal_corrected:,.2f}")
                    c2.metric("Honorários (5%)", f"R$ {attorney_fees_value:,.2f}")
                    c3.metric("TOTAL GERAL", f"R$ {grand_total:,.2f}", delta="Base para Acordo")
                    
                    # Report Button
                    if st.button("Gerar Memorial de Cálculo (Original)", help="Gera o relatório da dívida atualizada sem acordo (Cálculo Puro)."):
                         st.toast("Funcionalidade de PDF (Memorial) em desenvolvimento!", )

                st.divider()
                st.subheader("2. Proposta de Acordo")
                
                col_prop1, col_prop2 = st.columns(2)
                
                with col_prop1:
                    entry_mode = st.radio("Entrada", ["Valor Fixo (R$)", "Percentual (%)"], horizontal=True)
                    if entry_mode == "Valor Fixo (R$)":
                        entry_value = st.number_input("Valor da Entrada", min_value=0.0, max_value=float(grand_total), step=100.0)
                        if grand_total > 0:
                            entry_percent = (entry_value / float(grand_total)) * 100
                        else:
                            entry_percent = 0
                    else:
                        entry_percent = st.slider("Percentual de Entrada", 0, 100, 20)
                        entry_value = float(grand_total) * (entry_percent / 100)
                    
                    st.write(f"**Entrada:** R$ {entry_value:,.2f} ({entry_percent:.1f}%)")
                    
                with col_prop2:
                    st.subheader("Simulação")
                    
                    # Installment Selector
                    installments = st.number_input("Número de Parcelas Desejadas", min_value=1, max_value=60, value=1, step=1)
                    
                    # Discount Logic
                    # <= 10x: 20%
                    # 11-15x: 15%
                    # > 15x: 10%
                    
                    discount_rate = 0.0
                    if installments <= 10:
                        discount_rate = 0.20
                        discount_label = "20% (Até 10x)"
                    elif 11 <= installments <= 15:
                        discount_rate = 0.15
                        discount_label = "15% (11 a 15x)"
                    else:
                        discount_rate = 0.10
                        discount_label = "10% (> 15x)"
                        
                    discount_value = float(grand_total) * discount_rate
                    final_total = float(grand_total) - discount_value
                    
                    st.success(f"Desconto Aplicado: {discount_label}")
                    st.write(f"Desconto: R$ {discount_value:,.2f}")
                    st.write(f"Novo Total: R$ {final_total:,.2f}")
                    
                    st.divider()
                    
                    remaining = final_total - entry_value
                    
                    if remaining < 0:
                        st.error("O valor da entrada é maior que o total da dívida com desconto.")
                    else:
                        installment_val = remaining / installments if installments > 0 else 0
                        
                        st.info(f"Saldo a Parcelar: R$ {remaining:,.2f}")
                        st.markdown(f"### {installments}x de R$ {installment_val:,.2f}")
                        
                        if st.button("Gerar Minuta do Acordo (PDF)"):
                            st.toast("Funcionalidade de PDF em desenvolvimento!", )

    elif page == "Registrar Pagamento":
        st.header("Registrar Pagamento")
        st.markdown("Registro de pagamentos recebidos de devedores")
        
        conn = get_connection()
        try:
            # Fetch debtors
            debtors = get_debtors()
            
            if debtors.empty:
                st.warning("Nenhum devedor cadastrado.")
            else:
                debtor_opts = {row['id']: f"{row['name']} ({row['cpf_cnpj']})" for i, row in debtors.iterrows()}
                selected_debtor_id = st.selectbox("Selecione o Devedor", options=debtor_opts.keys(), format_func=lambda x: debtor_opts[x], key="payment_debtor_select")
                
                # Fetch agreements for this debtor
                agreements = pd.read_sql_query("SELECT * FROM agreements WHERE debtor_id = ? AND status = 'active'", conn, params=(selected_debtor_id,))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Registrar Novo Pagamento")
                    
                    with st.form("register_payment_form"):
                        payment_date = st.date_input("Data do Pagamento", value=date.today())
                        amount = st.number_input("Valor do Pagamento (R$)", min_value=0.01, step=10.0)
                        payment_method = st.selectbox("Método de Pagamento", ["PIX", "Transferência", "Boleto", "Cheque", "Dinheiro", "Outro"])
                        
                        if not agreements.empty:
                            agreement_opts = {row['id']: f"Acordo #{row['id']} - R$ {row['agreed_value']:.2f}" for i, row in agreements.iterrows()}
                            selected_agreement_id = st.selectbox("Vinculado a Acordo (Opcional)", options=[None] + list(agreement_opts.keys()), format_func=lambda x: "Sem acordo" if x is None else agreement_opts[x])
                        else:
                            selected_agreement_id = None
                            st.info("Nenhum acordo ativo para este devedor.")
                        
                        installment_number = st.number_input("Nº Parcela (Se aplicável)", min_value=0, step=1, value=0)
                        notes = st.text_area("Observações", height=100)
                        
                        submit_payment = st.form_submit_button("Registrar Pagamento", type="primary")
                        
                        if submit_payment:
                            cursor = conn.cursor()
                            try:
                                cursor.execute("""
                                    INSERT INTO payments 
                                    (debtor_id, debt_id, agreement_id, payment_date, amount, installment_number, payment_method, notes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    selected_debtor_id, 
                                    None, 
                                    selected_agreement_id,
                                    payment_date.strftime('%Y-%m-%d'),
                                    amount,
                                    installment_number if installment_number > 0 else None,
                                    payment_method,
                                    notes
                                ))
                                conn.commit()
                                st.success("Pagamento registrado com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao registrar pagamento: {e}")
                
                with col2:
                    st.subheader("Histórico de Pagamentos")
                    
                    # Fetch payments for this debtor
                    payments = pd.read_sql_query("""
                        SELECT id, payment_date, amount, payment_method, installment_number, agreement_id
                        FROM payments 
                        WHERE debtor_id = ? 
                        ORDER BY payment_date DESC
                    """, conn, params=(selected_debtor_id,))
                    
                    if not payments.empty:
                        payments['payment_date'] = pd.to_datetime(payments['payment_date'])
                        
                        # Summary
                        st.metric("Total Recebido", f"R$ {payments['amount'].sum():,.2f}")
                        st.metric("Nº de Pagamentos", len(payments))
                        
                        # Recent payments
                        st.write("**Últimos Pagamentos:**")
                        for i, payment in payments.head(5).iterrows():
                            with st.container(border=True):
                                col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
                                col_p1.write(f"**{payment['payment_date'].strftime('%d/%m/%Y')}**")
                                col_p2.write(f"R$ {payment['amount']:,.2f}")
                                col_p3.write(f"({payment['payment_method']})")
                        
                        # Full table
                        with st.expander("Ver todos os pagamentos"):
                            display_payments = payments[['payment_date', 'amount', 'payment_method', 'installment_number']].copy()
                            display_payments.columns = ['Data', 'Valor (R$)', 'Método', 'Parcela']
                            st.dataframe(display_payments, use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhum pagamento registrado para este devedor.")
        
        finally:
            conn.close()

    elif page == "Gerenciar Acordos":
        st.header("Gerenciar Acordos")
        st.markdown("Criar, atualizar e acompanhar acordos de pagamento")
        
        tab_new_agreement, tab_manage_agreements = st.tabs(["Novo Acordo", "Gerenciar Acordos"])
        
        conn = get_connection()
        try:
            debtors = get_debtors()
            
            if debtors.empty:
                st.warning("Nenhum devedor cadastrado.")
            else:
                # TAB: CRIAR NOVO ACORDO
                with tab_new_agreement:
                    st.subheader("Criar Novo Acordo")
                    
                    debtor_opts = {row['id']: f"{row['name']} ({row['cpf_cnpj']})" for i, row in debtors.iterrows()}
                    selected_debtor_id = st.selectbox("Selecione o Devedor", options=debtor_opts.keys(), format_func=lambda x: debtor_opts[x], key="new_agreement_debtor")
                    
                    # Fetch debts for this debtor
                    debts_for_agreement = pd.read_sql_query("SELECT id, description, original_value, due_date FROM debts WHERE debtor_id = ?", conn, params=(selected_debtor_id,))
                    
                    with st.form("new_agreement_form"):
                        agreement_date = st.date_input("Data do Acordo", value=date.today())
                        
                        st.write("**Dívida vinculada:**")
                        if not debts_for_agreement.empty:
                            debt_opts = {row['id']: f"{row['description']} - R$ {row['original_value']:.2f}" for i, row in debts_for_agreement.iterrows()}
                            selected_debt_id = st.selectbox("Selecione a dívida", options=[None] + list(debt_opts.keys()), format_func=lambda x: "Sem dívida específica" if x is None else debt_opts[x])
                        else:
                            selected_debt_id = None
                            st.info("Nenhuma dívida para este devedor.")
                        
                        col_ag1, col_ag2 = st.columns(2)
                        
                        with col_ag1:
                            agreed_value = st.number_input("Valor Total do Acordo (R$)", min_value=0.01, step=100.0)
                        
                        with col_ag2:
                            total_installments = st.number_input("Total de Parcelas", min_value=1, max_value=360, value=1, step=1)
                        
                        col_ag3, col_ag4 = st.columns(2)
                        
                        with col_ag3:
                            installment_value = agreed_value / total_installments if total_installments > 0 else 0
                            st.metric("Valor por Parcela", f"R$ {installment_value:,.2f}")
                        
                        with col_ag4:
                            interest_rate = st.number_input("Taxa de Juros Mensal (%)", min_value=0.0, max_value=100.0, step=0.1, value=0.0)
                        
                        first_installment_date = st.date_input("Data da Primeira Parcela")
                        agreement_notes = st.text_area("Observações", height=100)
                        
                        submit_agreement = st.form_submit_button("Criar Acordo", type="primary")
                        
                        if submit_agreement:
                            cursor = conn.cursor()
                            try:
                                cursor.execute("""
                                    INSERT INTO agreements 
                                    (debtor_id, debt_id, status, agreement_date, agreed_value, total_installments, installment_value, interest_rate, first_installment_date, notes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    selected_debtor_id,
                                    selected_debt_id,
                                    'active',
                                    agreement_date.strftime('%Y-%m-%d'),
                                    agreed_value,
                                    total_installments,
                                    installment_value,
                                    interest_rate,
                                    first_installment_date.strftime('%Y-%m-%d'),
                                    agreement_notes
                                ))
                                conn.commit()
                                st.success("Acordo criado com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao criar acordo: {e}")
                
                # TAB: GERENCIAR ACORDOS EXISTENTES
                with tab_manage_agreements:
                    st.subheader("Acordos Existentes")
                    
                    # Filters
                    col_filter1, col_filter2 = st.columns(2)
                    
                    with col_filter1:
                        status_filter = st.selectbox("Filtrar por Status", ["Todos", "active", "completed", "cancelled"])
                    
                    with col_filter2:
                        if status_filter == "Todos":
                            all_agreements = pd.read_sql_query("SELECT * FROM agreements ORDER BY agreement_date DESC", conn)
                        else:
                            all_agreements = pd.read_sql_query("SELECT * FROM agreements WHERE status = ? ORDER BY agreement_date DESC", conn, params=(status_filter,))
                    
                    if not all_agreements.empty:
                        st.metric("Total de Acordos", len(all_agreements))
                        st.metric("Valor Total em Acordos", f"R$ {all_agreements['agreed_value'].sum():,.2f}")
                        
                        st.dataframe(all_agreements[['id', 'debtor_id', 'status', 'agreement_date', 'agreed_value', 'total_installments']], use_container_width=True)
                        
                        # Edit/Delete Agreement
                        with st.expander("Editar ou Deletar Acordo"):
                            agreement_opts = {row['id']: f"Acordo #{row['id']} - Devedor {row['debtor_id']} - R$ {row['agreed_value']:.2f}" for i, row in all_agreements.iterrows()}
                            selected_agreement_to_edit = st.selectbox("Selecione o acordo", options=agreement_opts.keys(), format_func=lambda x: agreement_opts[x])
                            
                            selected_agreement_data = all_agreements[all_agreements['id'] == selected_agreement_to_edit].iloc[0]
                            
                            col_edit1, col_edit2 = st.columns(2)
                            
                            with col_edit1:
                                st.write("**Status Atual:**", selected_agreement_data['status'])
                                new_status = st.selectbox("Novo Status", ["active", "completed", "cancelled"], index=["active", "completed", "cancelled"].index(selected_agreement_data['status']))
                                
                                if st.button("Atualizar Status"):
                                    cursor = conn.cursor()
                                    try:
                                        cursor.execute("UPDATE agreements SET status = ? WHERE id = ?", (new_status, selected_agreement_to_edit))
                                        conn.commit()
                                        st.success(f"Status atualizado para '{new_status}'!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro: {e}")
                            
                            with col_edit2:
                                if st.button("Deletar Acordo", key="delete_agreement_btn"):
                                    st.session_state['confirm_delete_agreement'] = True
                                    st.session_state['agreement_to_delete'] = selected_agreement_to_edit
                                
                                if st.session_state.get('confirm_delete_agreement'):
                                    st.error(f"Tem certeza que deseja deletar o Acordo #{selected_agreement_to_edit}?")
                                    col_yes, col_no = st.columns(2)
                                    
                                    if col_yes.button("Sim, Deletar"):
                                        cursor = conn.cursor()
                                        try:
                                            cursor.execute("DELETE FROM agreements WHERE id = ?", (st.session_state['agreement_to_delete'],))
                                            conn.commit()
                                            st.success("Acordo deletado!")
                                            st.session_state['confirm_delete_agreement'] = False
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Erro: {e}")
                                    
                                    if col_no.button("Cancelar"):
                                        st.session_state['confirm_delete_agreement'] = False
                                        st.rerun()
                    else:
                        st.info("Nenhum acordo encontrado.")
        
        finally:
            conn.close()

if not st.session_state['logged_in']:
    login_page()
else:
    main_app()
