
import streamlit as st
import pandas as pd
from src.database import get_dashboard_kpis, get_kanban_cards, create_kanban_card, update_kanban_card, delete_kanban_card

def render_dashboard():
    st.markdown("## Painel de Controle")
    
    # --- KPIs ---
    kpis = get_dashboard_kpis()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Devedores Ativos", kpis["total_debtors"])
    with col2:
        st.metric("Dívidas Cadastradas", kpis["total_debts"])
    with col3:
        st.metric("Taxa de Recuperação", f"{kpis['recovery_rate']:.1f}%")
    with col4:
        st.metric("Total Recuperado", f"R$ {kpis['total_recovered']:,.2f}")

    st.divider()

    # --- KANBAN BOARD ---
    st.markdown("### Quadro de Tarefas")
    
    # Add Task Form
    with st.expander("➕ Nova Tarefa"):
        with st.form("new_task_form"):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                title = st.text_input("Título da Tarefa")
                desc = st.text_area("Descrição", height=68)
            with col_b:
                status = st.selectbox("Status Inicial", ["todo", "in_progress", "done"], format_func=lambda x: {"todo": "A Fazer", "in_progress": "Em Progresso", "done": "Concluído"}[x])
                submit = st.form_submit_button("Adicionar")
                
            if submit and title:
                create_kanban_card(title, desc, status)
                st.success("Tarefa adicionada!")
                st.rerun()

    # Columns
    col_todo, col_prog, col_done = st.columns(3)
    
    # Fetch cards
    todo_cards = get_kanban_cards('todo')
    prog_cards = get_kanban_cards('in_progress')
    done_cards = get_kanban_cards('done')
    
    def render_card(card, current_status):
        with st.container():
            st.markdown(f"""
            <div class="kanban-card">
                <strong>{card['title']}</strong>
                <div class="card-desc">{card['description'] or ''}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons (Tiny)
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                # Move Left
                if current_status == 'in_progress':
                    if st.button("⬅️", key=f"l_{card['id']}", help="Mover para A Fazer"):
                        update_kanban_card(card['id'], status='todo')
                        st.rerun()
                elif current_status == 'done':
                    if st.button("⬅️", key=f"l_{card['id']}", help="Mover para Em Progresso"):
                        update_kanban_card(card['id'], status='in_progress')
                        st.rerun()
            
            with c2:
                # Delete
                if st.button("🗑️", key=f"d_{card['id']}", help="Excluir"):
                    delete_kanban_card(card['id'])
                    st.rerun()
            
            with c3:
                # Move Right
                if current_status == 'todo':
                    if st.button("➡️", key=f"r_{card['id']}", help="Mover para Em Progresso"):
                        update_kanban_card(card['id'], status='in_progress')
                        st.rerun()
                elif current_status == 'in_progress':
                    if st.button("➡️", key=f"r_{card['id']}", help="Mover para Concluído"):
                        update_kanban_card(card['id'], status='done')
                        st.rerun()

    with col_todo:
        st.info(f"A Fazer ({len(todo_cards)})")
        for card in todo_cards:
            render_card(card, 'todo')
            
    with col_prog:
        st.warning(f"Em Progresso ({len(prog_cards)})")
        for card in prog_cards:
            render_card(card, 'in_progress')
            
    with col_done:
        st.success(f"Concluído ({len(done_cards)})")
        for card in done_cards:
            render_card(card, 'done')
