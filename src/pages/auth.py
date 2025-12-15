
import streamlit as st
import bcrypt
from src.database import get_connection 
# Note: create_session_token might need to be imported from auth util if not in db. 
# Checking imports: app.py imported it from src.auth. Let's use that.
from src.auth import check_credentials, create_session_token, validate_session_token

def render_login():
    # Logo Area
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 2rem;">
        <div style="background: linear-gradient(135deg, #ff5e00 0%, #ff8c00 100%); padding: 20px; border-radius: 16px; box-shadow: 0 0 20px rgba(255,94,0,0.3);">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="width: 48px; height: 48px; fill: black;">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
        </div>
        <h1 style="margin-top: 1rem; color: #ff5e00; font-size: 2.5rem;">CredMiner <span style="color: white;">HB</span></h1>
        <p style="color: #666;">Sistema de Recuperação de Crédito</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### Acesso ao Sistema")
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("ENTRAR", use_container_width=True)
            
            if submit:
                if check_credentials(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    
                    # Token generation
                    token = create_session_token(username)
                    st.query_params["token"] = token
                    
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")

    # Footer
    st.markdown("""
    <div style="position: fixed; bottom: 20px; width: 100%; text-align: center; color: #444; font-size: 0.8rem;">
        &copy; 2025 HalfBlood Solutions. All rights reserved.
    </div>
    """, unsafe_allow_html=True)
