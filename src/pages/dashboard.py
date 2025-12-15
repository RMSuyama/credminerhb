
import streamlit as st
import pandas as pd

from src.database import (
    get_dashboard_kpis, 
    get_kanban_cards, 
    get_kanban_columns, 
    create_kanban_card, 
    update_kanban_card_status, 
    delete_kanban_card,
    create_kanban_column,
    delete_kanban_column
)

def render_dashboard():
    st.markdown("## Painel de Controle")
    
    # --- KPIs ---
    kpis = get_dashboard_kpis()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Devedores Ativos", kpis["total_debtors"])
    with col2: st.metric("Dívidas Cadastradas", kpis["total_debts"])
    with col3: st.metric("Taxa de Recuperação", f"{kpis['recovery_rate']:.1f}%")
    with col4: st.metric("Total Recuperado", f"R$ {kpis['total_recovered']:,.2f}")

    st.divider()

    # --- KANBAN BOARD MANAGEMENT ---
    st.markdown("### Quadro de Tarefas")
    
    # Fetch dynamic columns
    columns_df = get_kanban_columns()
    if columns_df.empty:
        # Fallback if DB empty
        st.error("Erro ao carregar colunas do Kanban. Reinicie o banco de dados se necessário.")
        column_names = ["Todo", "Done"]
    else:
        column_names = columns_df['name'].tolist()

    # Expanders for Actions
    c_act1, c_act2 = st.columns([1, 1])
    
    with c_act1:
        with st.expander("➕ Nova Tarefa"):
            with st.form("new_task_form"):
                title = st.text_input("Título")
                desc = st.text_area("Descrição", height=68)
                # Default to first column
                init_status = column_names[0] if column_names else "Todo"
                if st.form_submit_button("Adicionar"):
                    if title:
                        create_kanban_card(title, desc, init_status)
                        st.success("Adicionada!")
                        st.rerun()
                    else:
                        st.warning("Título obrigatório")

    with c_act2:
        with st.expander("⚙️ Gerenciar Colunas"):
            # Add Column
            new_col = st.text_input("Nova Coluna", placeholder="Ex: Em Análise")
            if st.button("Adicionar Coluna"):
                if new_col and new_col not in column_names:
                    create_kanban_column(new_col)
                    st.rerun()
            
            st.divider()
            # Delete Column
            col_to_del = st.selectbox("Excluir Coluna", [""] + column_names)
            if st.button("Excluir"):
                if col_to_del:
                    # Find ID
                    cid = columns_df[columns_df['name'] == col_to_del].iloc[0]['id']
                    delete_kanban_column(cid)
                    st.rerun()

    # --- DRAG AND DROP BOARD (NATIVE REPLACEMENT) ---
    # Using columns and custom HTML for total control over styling.
    # Trade-off: No drag and drop, but perfect visual "Blue Box" fix.
    
    # 1. Fetch Data
    kanban_data = {name: [] for name in column_names}
    
    for col_name in column_names:
        kanban_data[col_name] = get_kanban_cards(col_name)

    # 2. Render Columns
    st_cols = st.columns(len(column_names))
    
    for i, col_name in enumerate(column_names):
        with st_cols[i]:
            # Column Header
            st.markdown(f"##### {col_name}")
            # Thick colorful line for header
            st.markdown(f"<div style='background-color: #262730; height: 2px; margin-bottom: 10px;'></div>", unsafe_allow_html=True)
            
            # Cards
            cards = kanban_data[col_name]
            for card in cards:
                # Render Card Container
                with st.container():
                    # Custom HTML for Card Look
                    st.markdown(f"""
                    <div style="
                        background-color: #2C2C2C;
                        border: 1px solid #444;
                        border-left: 4px solid #E67E22;
                        border-radius: 6px;
                        padding: 10px;
                        margin-bottom: 8px;
                        color: #ECEFF1;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                    ">
                        <strong style="font-size: 0.95rem; display: block; margin-bottom: 4px;">{card['title']}</strong>
                        <p style="font-size: 0.8rem; color: #B0BEC5; margin: 0;">#{card['id']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Move Buttons (Tiny)
                    c_left, c_right = st.columns([1, 1])
                    
                    prev_col = column_names[i-1] if i > 0 else None
                    next_col = column_names[i+1] if i < len(column_names) - 1 else None
                    
                    with c_left:
                        if prev_col:
                            if st.button("⬅️", key=f"prev_{card['id']}", use_container_width=True, help=f"Mover para {prev_col}"):
                                update_kanban_card_status(card['id'], prev_col)
                                st.rerun()
                                
                    with c_right:
                        if next_col:
                            if st.button("➡️", key=f"next_{card['id']}", use_container_width=True, help=f"Mover para {next_col}"):
                                update_kanban_card_status(card['id'], next_col)
                                st.rerun()
                    
                st.divider() # Visual separation
