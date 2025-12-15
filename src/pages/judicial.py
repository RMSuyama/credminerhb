
import streamlit as st
import pandas as pd
from datetime import date
from src.database import (
    get_connection, 
    get_debtors, 
    get_clients,
    create_petition_template, 
    update_petition_template, 
    delete_petition_template, 
    get_template_by_id
)
from src.pdf_generator import PDFGenerator
from src.petition_templates.template_engine import render_template_text

# --- JUDICIAL PAGE ---
def render_judicial():
    st.markdown("## Judicialização")
    st.info("Gestão de Custas e Processos Judiciais")
    
    conn = get_connection()
    try:
        debtors = get_debtors()
        
        if debtors.empty:
            st.warning("Cadastre devedores primeiro.")
        else:
            debtor_opts = {row['id']: f"{row['name']} ({row['cpf_cnpj']})" for i, row in debtors.iterrows()}
            selected_debtor_id = st.selectbox("Selecione o Devedor", options=debtor_opts.keys(), format_func=lambda x: debtor_opts[x], key="jud_debtor_sel")
            
            st.divider()
            
            tab_expenses, tab_processes = st.tabs(["Custas Judiciais", "Processos"])
            
            # --- LEGAL EXPENSES ---
            with tab_expenses:
                st.subheader("Custas Processuais")
                
                # Form to add expense
                with st.expander("Adicionar Nova Custa"):
                    with st.form("add_legal_expense"):
                        desc = st.text_input("Descrição (Ex: Taxa de Mandato)")
                        val = st.number_input("Valor (R$)", min_value=0.01)
                        dt = st.date_input("Data do Pagamento")
                        
                        if st.form_submit_button("Salvar Custa"):
                            cursor = conn.cursor()
                            try:
                                # Get client_id
                                d_info = pd.read_sql_query("SELECT client_id FROM debtors WHERE id = ?", conn, params=(selected_debtor_id,))
                                client_id = d_info.iloc[0]['client_id'] if not d_info.empty else None
                                
                                cursor.execute("""
                                    INSERT INTO legal_expenses (debtor_id, client_id, description, value, date)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (selected_debtor_id, client_id, desc, val, dt.strftime('%Y-%m-%d')))
                                conn.commit()
                                st.success("Custa adicionada!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")

                # List expenses
                expenses = pd.read_sql_query("SELECT * FROM legal_expenses WHERE debtor_id = ? ORDER BY date DESC", conn, params=(selected_debtor_id,))
                if not expenses.empty:
                    st.dataframe(expenses[['date', 'description', 'value']], use_container_width=True)
                    st.metric("Total em Custas", f"R$ {expenses['value'].sum():,.2f}")
                else:
                    st.info("Nenhuma custa registrada.")

            # --- PROCESSES ---
            with tab_processes:
                st.subheader("Processos Judiciais")
                
                # Add Process
                with st.expander("Cadastrar Novo Processo"):
                    with st.form("new_process"):
                        proc_number = st.text_input("Número do Processo")
                        court = st.text_input("Vara/Foro")
                        status = st.selectbox("Status", ["Ativo", "Suspenso", "Arquivado", "Acordo"])
                        
                        if st.form_submit_button("Salvar Processo"):
                            cursor = conn.cursor()
                            try:
                                d_info = pd.read_sql_query("SELECT client_id FROM debtors WHERE id = ?", conn, params=(selected_debtor_id,))
                                client_id = d_info.iloc[0]['client_id'] if not d_info.empty else None
                                
                                cursor.execute("""
                                    INSERT INTO judicial_processes (debtor_id, client_id, process_number, court, status)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (selected_debtor_id, client_id, proc_number, court, status))
                                conn.commit()
                                st.success("Processo cadastrado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                
                # List processes
                procs = pd.read_sql_query("SELECT * FROM judicial_processes WHERE debtor_id = ?", conn, params=(selected_debtor_id,))
                if not procs.empty:
                    st.dataframe(procs[['process_number', 'court', 'status']], use_container_width=True)
                else:
                    st.info("Nenhum processo cadastrado.")

    finally:
        conn.close()

# --- PETITIONS PAGE ---
def render_petitions():
    st.markdown("## Modelos de Petição")
    st.info("Gerencie modelos e gere procurações/substabelecimentos")
    
    conn = get_connection()
    try:
        templates_df = pd.read_sql_query('SELECT id, name, process_type, description FROM petition_templates ORDER BY created_at DESC', conn)
        
        st.subheader('Modelos Cadastrados')
        if templates_df.empty:
            st.info('Ainda não há modelos cadastrados.')
        else:
            st.dataframe(templates_df[['name', 'process_type', 'description']], use_container_width=True)

        st.divider()
        st.subheader("Editor de Modelos")
        
        # Select for edit
        tpl_choices = [None] + templates_df['id'].tolist() if not templates_df.empty else [None]
        
        # Simplified Editor Logic
        with st.form('template_form'):
            tpl_id = st.selectbox('Editar existente ou Novo', options=tpl_choices, format_func=lambda x: 'Novo Modelo' if x is None else f"{x} - {templates_df.loc[templates_df['id']==x, 'name'].values[0]}")
            
            # Load data if editing
            pre_name, pre_type, pre_desc, pre_cont = "", "inicial", "", ""
            if tpl_id:
                t = get_template_by_id(tpl_id)
                if t:
                    pre_name, pre_type, pre_desc, pre_cont = t['name'], t['process_type'], t['description'], t['template_content']
            
            name = st.text_input("Nome", value=pre_name)
            p_type = st.selectbox("Tipo", ["inicial", "cumprimento", "outros"], index=["inicial", "cumprimento", "outros"].index(pre_type) if pre_type in ["inicial", "cumprimento", "outros"] else 0)
            desc = st.text_input("Descrição", value=pre_desc)
            content = st.text_area("Conteúdo (Use {{placeholders}})", value=pre_cont, height=300)
            
            if st.form_submit_button("Salvar Modelo"):
                if tpl_id:
                    update_petition_template(tpl_id, name=name, process_type=p_type, description=desc, template_content=content)
                    st.success("Atualizado!")
                else:
                    create_petition_template(name, p_type, desc, content)
                    st.success("Criado!")
                st.rerun()
        
        st.divider()
        st.subheader("Geração Rápida")
        
        t1, t2 = st.tabs(["Procuração", "Substabelecimento"])
        
        with t1:
            st.write("Gerador de Procuração Rápida")
            # Procuration Logic simplified
            if st.button("Gerar Procuração Exemplo"):
                pdf_bytes = PDFGenerator().generate_petition_pdf("Procuração", "Texto da procuração aqui...", {})
                st.download_button("Baixar PDF", pdf_bytes, "procuracao.pdf", "application/pdf")

        with t2:
            st.write("Gerador de Substabelecimento Rápido")
            # Substab logic simplified
            pass
            
    finally:
        conn.close()
