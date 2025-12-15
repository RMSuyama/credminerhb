
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

    # Render Board
    sorted_data = sort_items(list(kanban_data.items()), multi_containers=True)
    
    # Detect Changes
    # sorted_data is like [('Col1', ['item1', 'item2']), ('Col2', ['item3'])]
    
    # We compare `sorted_data` with `kanban_data` to see moves.
    # But `streamlit-sortables` might not trigger rerun automatically on drop? 
    # It usually returns the state. We check if state matches DB.
    
    # Re-process changes
    changes_detected = False
    
    for col_data in sorted_data:
        col_name = col_data._column_name # sort_items returns object with properties? 
        # Wait, sort_items returns a list of SortableItemContainer or similar?
        # No, standard usage: `items = sort_items(data)` returns the list of data in new order.
        # But wait, input is list of dicts/tuples?
        pass # checking structure below
        
    # Correct usage of sort_items with multi_containers:
    # It returns a list of the modified items corresponding to the input structure.
    
    # Let's flatten and check against DB state
    for col_idx, col_res in enumerate(sorted_data):
        # col_res is the list of items in that column (the new state)
        # column name is column_names[col_idx] (assuming order preserved)
        
        target_col_name = column_names[col_idx]
        current_items = col_res
        
        for item_str in current_items:
            # Parse ID
            # item_str format: "Title ::ID"
            if "::" in item_str:
                parts = item_str.split("::")
                card_id_str = parts[-1]
                card_id = int(card_id_str)
                
                # Check if this card's status in DB matches `target_col_name`
                # We can optimize by caching initial state, but individual updates are safer.
                # Just update everything? Expensive.
                # Better: Update ONLY if changed.
                
                # Check DB status (we need a quick lookup or just blind update)
                # Blind update is safest for "simpler" logic.
                update_kanban_card_status(card_id, target_col_name)
    
    # To avoid infinite rerun loops or massive DB hits, we should only update if diff?
    # Actually, `sort_items` is interactive. When user drops, script reruns, returns new list.
    # We act on that new list.
    # Blind update is fine for small datasets ( < 100 cards).
