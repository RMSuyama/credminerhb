
import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items
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

    # --- DRAG AND DROP BOARD ---
    # Prepare data for sort_items
    # Structure: {'Column Name': [{'text': 'Title', 'id': 1}, ...]}
    kanban_data = {col: [] for col in column_names}
    
    # helper to get all cards
    # We need a way to get ALL cards efficiently or iterate columns. 
    # Current DB `get_kanban_cards` filters by status.
    # To avoid N queries, we should ideally fetch all. 
    # But for now, we iterate.
    
    original_cards = {} # Map id -> card data for lookup
    
    for col in column_names:
        cards = get_kanban_cards(col) # Status = Column Name
        for c in cards:
            # item formatted for sortables
            # We use a custom string format or dict if supported. 
            # sort_items supports list of strings. complex objects are trickier.
            # WORKAROUND: Use string "ID: Title" and parse it back, or just Title if unique (unsafe).
            # Better: "Title [id:X]"
            label = f"{c['title']}" 
            # We can't easily hide metadata in sort_items string list without parsing.
            # Let's try to map indices. 
            # unique_key strategy: f"{c['id']}_{c['title']}"
            
            # Actually, `sort_items` returns the new order of items.
            kanban_data[col].append(f"{c['title']} ::{c['id']}") 

    # Prepare data for sort_items
    # Structure for multi_containers=True: [{'header': 'Column Name', 'items': ['Item 1', 'Item 2']}]
    kanban_items = []
    
    for col in column_names:
        cards = get_kanban_cards(col) # Status = Column Name
        items_list = []
        for c in cards:
            # item formatted: "#{id} {title}" for cleaner look
            # We use a separator that is unlikely to be in title or regex
            items_list.append(f"#{c['id']} {c['title']}")
        
        kanban_items.append({'header': col, 'items': items_list})

    # Render Board
    # Returns the updated list of dicts
    sorted_items = sort_items(kanban_items, multi_containers=True)
    
    # Process Changes
    for col_data in sorted_items:
        # col_data is {'header': 'ColName', 'items': ['Item...', ...]}
        target_status = col_data['header']
        current_items = col_data['items']
        
        for item_str in current_items:
            # Parse ID from "#{id} {title}"
            # We look for the first space
            if item_str.startswith("#"):
                try:
                    # Split only on first space
                    parts = item_str.split(" ", 1)
                    card_id_str = parts[0].replace("#", "")
                    card_id = int(card_id_str)
                    
                    # Update status
                    update_kanban_card_status(card_id, target_status)
                except (ValueError, IndexError):
                    pass
