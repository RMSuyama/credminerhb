
import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from src.database import get_connection, get_debtors, get_debts
from src.calculator import Calculator
from src.pdf_generator import PDFGenerator

# --- NEGOTIATION / CALCULATION PAGE ---
def render_negotiation():
    st.markdown("## Negociação e Acordo Avançado")
    st.info("Simulação de dívidas e geração de propostas")
    
    conn = get_connection()
    try:
        debtors = get_debtors()
        if debtors.empty:
            st.warning("Cadastre devedores primeiro.")
            return

        debtor_opts = {row['id']: f"{row['name']} ({row['cpf_cnpj']})" for i, row in debtors.iterrows()}
        selected_debtor_id = st.selectbox("Selecione o Devedor", options=debtor_opts.keys(), format_func=lambda x: debtor_opts[x], key="calc_debtor_sel")
        
        calc_date = st.date_input("Data do Cálculo", value=date.today())
        
        debts = get_debts(selected_debtor_id)
        
        if debts.empty:
            st.info("Devedor sem dívidas.")
            return

        st.divider()
        st.subheader("1. Composição da Dívida")
        
        # Calculate Logic
        results = []
        # Normal Debts
        for i, debt in debts.iterrows():
            res = Calculator.calculate(
                contract_type=debt['contract_type'],
                original_value=debt['original_value'],
                due_date=debt['due_date'],
                calc_date=calc_date,
                fine_type=debt.get('fine_type')
            )
            res['description'] = debt['description']
            res['type'] = 'Dívida'
            results.append(res)
            
        # Legal Expenses
        expenses = pd.read_sql_query("SELECT * FROM legal_expenses WHERE debtor_id = ?", conn, params=(selected_debtor_id,))
        for i, exp in expenses.iterrows():
            res_exp = Calculator.calculate("CUSTAS", exp['value'], exp['date'], calc_date)
            res_exp['description'] = f"Custa: {exp['description']}"
            res_exp['type'] = 'Custa'
            results.append(res_exp)
            
        if results:
            df_res = pd.DataFrame(results)
            st.dataframe(df_res[['description', 'original', 'corrected', 'interest', 'fine', 'total']], use_container_width=True)
            
            subtotal = Decimal(str(df_res['total'].sum()))
            fees = (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
            grand_total = subtotal + fees
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Subtotal", f"R$ {subtotal:,.2f}")
            c2.metric("Honorários (5%)", f"R$ {fees:,.2f}")
            c3.metric("TOTAL GERAL", f"R$ {grand_total:,.2f}")
            
            st.divider()
            st.subheader("2. Simulação de Acordo")
            
            col1, col2 = st.columns(2)
            with col1:
                entry_mode = st.radio("Entrada", ["Valor", "%"], horizontal=True)
                if entry_mode == "Valor":
                    entry_val = st.number_input("Valor Entrada", min_value=0.0)
                else:
                    entry_pct = st.slider("% Entrada", 0, 100, 20)
                    entry_val = float(grand_total) * (entry_pct/100)
                st.write(f"Entrada: R$ {entry_val:,.2f}")

            with col2:
                inst = st.number_input("Parcelas", 1, 60, 1)
                
                # Discount Logic
                disc_pct = 0.0
                if inst <= 10: disc_pct = 0.20
                elif inst <= 15: disc_pct = 0.15
                else: disc_pct = 0.10
                
                disc_val = float(grand_total) * disc_pct
                final_total = float(grand_total) - disc_val
                st.success(f"Desconto: {disc_pct*100}% (- R$ {disc_val:,.2f})")
                st.write(f"Novo Total: R$ {final_total:,.2f}")
            
            remaining = final_total - entry_val
            if remaining < 0:
                st.error("Entrada maior que total.")
            else:
                inst_val = remaining / inst
                st.info(f"Saldo: {inst}x de R$ {inst_val:,.2f}")
                
                if st.button("Gerar Minuta (PDF)"):
                    st.success("PDF Gerado (Simulado)")

    finally:
        conn.close()


# --- PAYMENTS PAGE ---
def render_payments():
    st.markdown("## Registrar Pagamento")
    conn = get_connection()
    try:
        debtors = get_debtors()
        if debtors.empty:
            st.warning("Sem devedores.")
            return
            
        debtor_opts = {row['id']: f"{row['name']} ({row['cpf_cnpj']})" for i, row in debtors.iterrows()}
        selected_debtor_id = st.selectbox("Selecione o Devedor", options=debtor_opts.keys(), format_func=lambda x: debtor_opts[x], key="pay_debtor_sel")
        
        # Form
        with st.form("pay_form"):
            date_pay = st.date_input("Data")
            amt = st.number_input("Valor", min_value=0.01)
            method = st.selectbox("Método", ["PIX", "Boleto", "Dinheiro"])
            if st.form_submit_button("Registrar"):
                # Insert logic simplified
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO payments (debtor_id, payment_date, amount, payment_method)
                    VALUES (?, ?, ?, ?)
                """, (selected_debtor_id, date_pay, amt, method))
                conn.commit()
                st.success("Pagamento Registrado")
                st.rerun()

        # History
        st.subheader("Histórico")
        pays = pd.read_sql_query("SELECT * FROM payments WHERE debtor_id = ? ORDER BY payment_date DESC", conn, params=(selected_debtor_id,))
        if not pays.empty:
            st.dataframe(pays[['payment_date', 'amount', 'payment_method']], use_container_width=True)
            
    finally:
        conn.close()


# --- AGREEMENTS PAGE ---
def render_agreements():
    st.markdown("## Gerenciar Acordos")
    st.info("Gestão de contratos e parcelamentos")
    # Simplified Logic
    conn = get_connection()
    agreements = pd.read_sql_query("SELECT * FROM agreements", conn)
    conn.close()
    
    if not agreements.empty:
        st.dataframe(agreements, use_container_width=True)
    else:
        st.info("Nenhum acordo registrado.")
