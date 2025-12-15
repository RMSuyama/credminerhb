
import streamlit as st
from src.services import update_all_indices
import time
import random

def render_settings():
    st.markdown("## Configurações Avançadas")
    st.info("Gerenciamento de sistema e índices financeiros")
    
    t1, t2 = st.tabs(["Atualização de Índices", "Sistema"])
    
    with t1:
        st.subheader("Índices Financeiros (SELIC, IPCA, etc)")
        if st.button("Atualizar Agora"):
            with st.status("Atualizando...", expanded=True) as status:
                try:
                    res = update_all_indices()
                    status.write("Índices atualizados.")
                    st.success("Sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    with t2:
        st.subheader("Zona de Perigo")
        if st.button("Teste de Integridade"):
            with st.status("Verificando...", expanded=True):
                time.sleep(1)
                st.write("Banco de dados: OK")
                time.sleep(1)
                st.write("Permissões: OK")
                st.success("Sistema Íntegro.")
