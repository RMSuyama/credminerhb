from datetime import date
import streamlit as st
import pandas as pd

from src.database import (
    get_dashboard_kpis, 
    get_kanban_cards, 
    get_kanban_columns, 
    create_kanban_card, 
    update_kanban_card,
    update_kanban_card_status, 
    delete_kanban_card,
    create_kanban_column,
    delete_kanban_column,
    archive_kanban_card,
    restore_kanban_card,
    get_archived_cards,
    check_overdue_tasks,
    get_kanban_stats,
    get_process_stats
)

def render_dashboard():
    st.markdown("## Dashboards (Indicadores)")
    
    # --- KPIs ---
    kpis = get_dashboard_kpis()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Devedores Ativos", kpis["total_debtors"])
    with col2: st.metric("Dívidas Cadastradas", kpis["total_debts"])
    with col3: st.metric("Taxa de Recuperação", f"{kpis['recovery_rate']:.1f}%")
    with col4: st.metric("Total Recuperado", f"R$ {kpis['total_recovered']:,.2f}")
    
    st.markdown("---")
    
    # Process Stats Chart (Basic)
    st.subheader("Movimentação de Processos (30 dias)")
    proc_stats = get_process_stats(30)
    
    # Create a simple df for chart
    chart_data = pd.DataFrame({
        "Status": ["Movimentados", "Sem Movimentação"],
        "Quantidade": [proc_stats['moved'], proc_stats['not_moved']]
    })
    
    st.bar_chart(chart_data.set_index("Status"))
    
    st.info("Visualização macro dos dados do sistema.")
