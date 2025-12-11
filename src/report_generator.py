from fpdf import FPDF
from datetime import datetime
import os

class PDFReport(FPDF):
    def header(self):
        # Logo or Title
        self.set_font('Arial', 'B', 14)
        self.set_text_color(192, 0, 0) # Dark Red like the image
        self.cell(0, 10, 'PLANILHA DE DÉBITOS', 0, 1, 'L')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(data):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- Header Info ---
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(0)
    
    debtor = data['debtor']
    calc_date = data['calc_date'].strftime("%B/%Y") # e.g. Dezembro/2025
    
    # Translate month name roughly or use babel if needed. Simple replace for now.
    months = {
        "January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril",
        "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto",
        "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"
    }
    for eng, pt in months.items():
        calc_date = calc_date.replace(eng, pt)

    pdf.cell(0, 5, f"Atualização de Cálculo - {debtor['name'].upper()}", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 5, f"Data de atualização dos valores: {calc_date}", 0, 1)
    pdf.cell(0, 5, f"Indexador utilizado: Tabela Prática (INPC/IPCA)", 0, 1) # Generic for now
    pdf.cell(0, 5, f"Juros moratórios simples de 1,00% ao mês", 0, 1)
    pdf.cell(0, 5, f"Acréscimo de multa conforme contrato.", 0, 1)
    pdf.cell(0, 5, f"Honorários advocatícios de {data['totals']['honorariums_pct']}%", 0, 1)
    pdf.ln(10)
    
    # --- Table Header ---
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 8)
    
    # Columns: ITEM, DESCRIÇÃO, DATA, VALOR SINGELO, VALOR ATUALIZADO, JUROS, MULTA, TOTAL
    # Widths: 10, 50, 20, 25, 25, 20, 20, 25
    cols = [10, 50, 20, 25, 25, 20, 20, 25]
    headers = ["ITEM", "DESCRIÇÃO", "DATA", "ORIGINAL", "CORRIGIDO", "JUROS", "MULTA", "TOTAL"]
    
    for i, h in enumerate(headers):
        pdf.cell(cols[i], 8, h, 1, 0, 'C', fill=True)
    pdf.ln()
    
    # --- Table Rows ---
    pdf.set_font('Arial', '', 8)
    
    debts = data['debts']
    for idx, debt in enumerate(debts, 1):
        pdf.cell(cols[0], 6, str(idx), 1, 0, 'C')
        pdf.cell(cols[1], 6, debt['description'][:30], 1, 0, 'L') # Truncate desc
        
        due_date = debt['due_date'].strftime("%d/%m/%Y") if hasattr(debt['due_date'], 'strftime') else str(debt['due_date'])
        pdf.cell(cols[2], 6, due_date, 1, 0, 'C')
        
        pdf.cell(cols[3], 6, f"{debt['original']:,.2f}", 1, 0, 'R')
        pdf.cell(cols[4], 6, f"{debt['corrected']:,.2f}", 1, 0, 'R')
        pdf.cell(cols[5], 6, f"{debt['interest']:,.2f}", 1, 0, 'R')
        pdf.cell(cols[6], 6, f"{debt['fine']:,.2f}", 1, 0, 'R')
        pdf.cell(cols[7], 6, f"{debt['total']:,.2f}", 1, 0, 'R')
        pdf.ln()
        
    # --- Totals ---
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 9)
    
    # Align totals to the right columns
    # Total width = 195
    # Label "TOTAIS" around middle
    
    pdf.cell(sum(cols[:3]), 8, "TOTAIS", 0, 0, 'R')
    pdf.cell(cols[3], 8, f"{data['totals']['original']:,.2f}", 0, 0, 'R')
    pdf.cell(cols[4], 8, f"{data['totals']['updated']:,.2f}", 0, 0, 'R')
    # Juros + Multa sum?
    # Just show Grand Total at the end
    pdf.cell(sum(cols[5:]), 8, f"{data['totals']['updated'] + sum(d['interest'] + d['fine'] for d in debts):,.2f}", 0, 0, 'R') # This is actually 'total' column sum
    pdf.ln(10)
    
    # --- Footer Totals ---
    # Subtotal
    # Honorarios
    # Total Geral
    
    pdf.set_fill_color(240, 240, 240)
    
    # Subtotal
    pdf.cell(140, 8, "Subtotal", 0, 0, 'R')
    pdf.cell(50, 8, f"R$ {data['totals']['updated'] + sum(d['interest'] + d['fine'] for d in debts):,.2f}", 1, 1, 'R', fill=True)
    
    # Honorarios
    pdf.cell(140, 8, f"Honorários Advocatícios ({data['totals']['honorariums_pct']}%)", 0, 0, 'R')
    pdf.cell(50, 8, f"R$ {data['totals']['honorariums_val']:,.2f}", 1, 1, 'R')
    
    # Total Geral
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(140, 10, "TOTAL GERAL", 0, 0, 'R')
    pdf.cell(50, 10, f"R$ {data['totals']['grand_total']:,.2f}", 1, 1, 'R', fill=True)
    
    return pdf.output(dest='S').encode('latin-1')
