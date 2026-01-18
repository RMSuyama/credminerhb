import streamlit as st
from datetime import date
import pandas as pd
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

from src.database import (
    get_kanban_cards, 
    get_kanban_columns, 
    create_kanban_card, 
    update_kanban_card_status, 
    archive_kanban_card,
    restore_kanban_card,
    get_archived_cards,
    check_overdue_tasks,
    get_kanban_stats,
    get_process_stats
)

DONE_STATUS = "Done"


# =========================================================
# MAIN
# =========================================================
def render_tasks():
    # ---------- OVERDUE CHECK (1x/dia) ----------
    if "last_overdue_check" not in st.session_state:
        st.session_state.last_overdue_check = date.today()
        check_overdue_tasks()
    elif st.session_state.last_overdue_check < date.today():
        check_overdue_tasks()
        st.session_state.last_overdue_check = date.today()

    st.markdown("## Área de trabalho")

    # ---------- ADICIONAR TAREFA ----------
    col_act, _ = st.columns([0.25, 0.75])
    with col_act:
        with st.popover("➕ ADICIONAR TAREFA", use_container_width=True):
            with st.form("new_task"):
                title = st.text_input("Título")
                desc = st.text_area("Descrição")

                c1, c2 = st.columns(2)
                with c1:
                    due_date = st.date_input("Prazo", value=None)
                with c2:
                    priority = st.selectbox(
                        "Prioridade", ["Alta", "Média", "Baixa"], index=1
                    )

                cols_df = get_kanban_columns()
                all_cols = cols_df["name"].tolist() if not cols_df.empty else ["Todo"]

                if st.form_submit_button("Criar"):
                    create_kanban_card(title, desc, all_cols[0], due_date, priority)
                    st.success("Tarefa criada")
                    st.rerun()

    # ---------- DADOS ----------
    main_col, side_col = st.columns([0.75, 0.25])

    cols_df = get_kanban_columns()
    all_cols = cols_df["name"].tolist() if not cols_df.empty else ["Todo"]

    cards = get_kanban_cards()
    cards = [c for c in cards if c["status"] in all_cols]

    PRIORITY_MAP = {"Alta": 1, "Média": 2, "Baixa": 3}

    def sort_key(c):
        p = PRIORITY_MAP.get(c.get("priority"), 4)
        d = pd.to_datetime(c.get("due_date"), errors="coerce")
        d = d.date() if not pd.isna(d) else date.max
        return (d, p)

    cards.sort(key=sort_key)

    # ---------- CLASSIFICAÇÃO ----------
    overdue, pending = [], []
    today = date.today()

    for c in cards:
        is_done = c["status"] == DONE_STATUS
        d = pd.to_datetime(c.get("due_date"), errors="coerce")

        if not pd.isna(d) and d.date() < today and not is_done:
            overdue.append(c)
        elif not is_done:
            pending.append(c)

    # =====================================================
    # LISTA DE TAREFAS
    # =====================================================
    with main_col:
        if not cards:
            st.info("Nenhuma tarefa.")
        else:
            for card in cards:
                with st.container():
                    c1, c2, c3 = st.columns([0.06, 0.74, 0.2])

                    # ✔️ CHECKBOX CORRIGIDO
                    with c1:
                        key = f"done_{card['id']}"
                        if key not in st.session_state:
                            st.session_state[key] = card["status"] == DONE_STATUS

                        checked = st.checkbox("", key=key)

                        if checked and card["status"] != DONE_STATUS:
                            update_kanban_card_status(card["id"], DONE_STATUS)
                            st.rerun()

                        if not checked and card["status"] == DONE_STATUS:
                            update_kanban_card_status(card["id"], all_cols[0])
                            st.rerun()

                    with c2:
                        d = pd.to_datetime(card.get("due_date"), errors="coerce")
                        date_str = ""
                        if not pd.isna(d):
                            color = "#ff4b4b" if d.date() < today and card["status"] != DONE_STATUS else "#888"
                            date_str = f"<span style='color:{color}'> - {d.strftime('%d/%m/%Y')}</span>"

                        st.markdown(
                            f"""
                            <div style='font-size:15px;font-weight:500'>
                                {card['title']}{date_str}
                            </div>
                            <div style='font-size:12px;color:#888'>
                                {card.get('priority','')}
                                <span style='background:#eee;padding:2px 6px;
                                border-radius:4px;margin-left:6px'>
                                {card['status']}
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with c3:
                        if st.button("🗑️", key=f"del_{card['id']}"):
                            archive_kanban_card(card["id"])
                            st.rerun()

                    st.divider()

    # =====================================================
    # SIDEBAR
    # =====================================================
    with side_col:
        st.markdown("#### Minhas atividades")

        stats = get_kanban_stats()
        a, b, c = st.columns(3)
        a.metric("Concluídas", stats["completed"])
        b.metric("Atrasadas", stats["overdue"])
        c.metric("Pendentes", stats["todo"])

        st.divider()

        # ---------- RELATÓRIO EM PDF ----------
        st.markdown("##### Relatório em PDF")

        pdf_bytes = build_pdf_report(overdue, pending)

        st.download_button(
            "📄 Baixar relatório (PDF)",
            data=pdf_bytes,
            file_name=f"relatorio_tarefas_{date.today().strftime('%d_%m_%Y')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.caption("PDF pronto para anexar em e-mail ou WhatsApp.")

        st.divider()

        st.markdown("##### Processos (30 dias)")
        proc = get_process_stats(30)
        st.write(f"🟢 {proc['moved']} movimentados")
        st.write(f"⚪ {proc['not_moved']} sem movimentação")

    # ---------- ARQUIVO ----------
    with st.expander("🗑️ Lixeira / Arquivo"):
        archived = get_archived_cards()
        if not archived.empty:
            for _, row in archived.iterrows():
                x1, x2 = st.columns([0.8, 0.2])
                x1.write(row["title"])
                if x2.button("Restaurar", key=f"res_{row['id']}"):
                    restore_kanban_card(row["id"])
                    st.rerun()
        else:
            st.write("Vazio.")


# =========================================================
# PDF
# =========================================================
def build_pdf_report(overdue, pending):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(
        f"<b>Relatório de Tarefas</b><br/>{date.today().strftime('%d/%m/%Y')}",
        styles["Title"]
    ))
    elements.append(Spacer(1, 12))

    # Atrasadas
    elements.append(Paragraph("<b>🔴 Tarefas Atrasadas</b>", styles["Heading2"]))
    if overdue:
        items = [
            ListItem(
                Paragraph(f"{t['title']} (Venc: {t.get('due_date')})", styles["Normal"])
            )
            for t in overdue
        ]
        elements.append(ListFlowable(items, bulletType="bullet"))
    else:
        elements.append(Paragraph("Nenhuma tarefa atrasada.", styles["Normal"]))

    elements.append(Spacer(1, 12))

    # Pendentes
    elements.append(Paragraph("<b>🟡 Tarefas Pendentes</b>", styles["Heading2"]))
    if pending:
        items = [
            ListItem(
                Paragraph(f"{t['title']} (Venc: {t.get('due_date','')})", styles["Normal"])
            )
            for t in pending
        ]
        elements.append(ListFlowable(items, bulletType="bullet"))
    else:
        elements.append(Paragraph("Nenhuma tarefa pendente.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
