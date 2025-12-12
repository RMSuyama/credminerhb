"""PDF Generation Module for CredMiner HB - Generates various reports and calculations."""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, date
from decimal import Decimal
import io

class PDFGenerator:
    """Generate professional PDFs for CredMiner HB."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a3a52'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2d5a7b'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1a3a52'),
            spaceAfter=6,
            spaceBefore=6,
            fontName='Helvetica-Bold'
        ))
        
        # Label style
        self.styles.add(ParagraphStyle(
            name='Label',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a3a52'),
            fontName='Helvetica-Bold'
        ))

    def generate_debt_memory(self, debtor_name, debtor_cpf, debts_data, calculations_data):
        """
        Generate a "Memória de Cálculo" (Calculation Memory) PDF for debt details.
        
        Args:
            debtor_name: str - Name of debtor
            debtor_cpf: str - CPF of debtor
            debts_data: list of dicts - Debt information
            calculations_data: dict - Calculation details (SELIC, IPCA, fines, etc)
        
        Returns:
            bytes - PDF content
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        elements = []
        
        # Header
        elements.append(Paragraph("MEMÓRIA DE CÁLCULO", self.styles['CustomTitle']))
        elements.append(Paragraph("CredMiner HB - Recuperação de Crédito", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Debtor Info
        debtor_data = [
            ['DEVEDOR:', debtor_name],
            ['CPF/CNPJ:', debtor_cpf],
            ['DATA DO CÁLCULO:', datetime.now().strftime('%d/%m/%Y às %H:%M')],
        ]
        
        debtor_table = Table(debtor_data, colWidths=[1.5*inch, 4*inch])
        debtor_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a3a52')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(debtor_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Debts
        elements.append(Paragraph("RELAÇÃO DE DÍVIDAS", self.styles['CustomHeader']))
        elements.append(Spacer(1, 0.1*inch))
        
        debt_table_data = [['ID', 'Descrição', 'Vencimento', 'Valor Original', 'Status']]
        
        for debt in debts_data:
            debt_table_data.append([
                str(debt.get('id', '-')),
                debt.get('description', '-')[:30],
                debt.get('due_date', '-'),
                f"R$ {float(debt.get('original_value', 0)):,.2f}",
                debt.get('status', 'Aberta')
            ])
        
        debt_table = Table(debt_table_data, colWidths=[0.6*inch, 2.2*inch, 1.2*inch, 1.3*inch, 0.7*inch])
        debt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a7b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ]))
        
        elements.append(debt_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Calculations
        if calculations_data:
            elements.append(Paragraph("DETALHES DO CÁLCULO", self.styles['CustomHeader']))
            elements.append(Spacer(1, 0.1*inch))
            
            calc_data = [
                ['Conceito', 'Valor/Taxa'],
                ['Índice SELIC', calculations_data.get('selic_rate', '0.00%')],
                ['Índice IPCA', calculations_data.get('ipca_rate', '0.00%')],
                ['Taxa de Juros', calculations_data.get('interest_rate', '0.00%')],
                ['Multa por Atraso', calculations_data.get('fine_amount', 'R$ 0,00')],
                ['Total Atualizado', calculations_data.get('total_updated', 'R$ 0,00')],
            ]
            
            calc_table = Table(calc_data, colWidths=[2.5*inch, 1.5*inch])
            calc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a7b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(calc_table)
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = f"CredMiner HB | NASA, Washington D.C., USA | hb.solutions@gmail.com | halfblood. 2018"
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
            borderPadding=10,
        )))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_agreement_report(self, debtor_name, debtor_cpf, agreement_data, payments_data=None):
        """
        Generate an Agreement Report PDF.
        
        Args:
            debtor_name: str
            debtor_cpf: str
            agreement_data: dict with agreement details
            payments_data: list of dicts with payment history
        
        Returns:
            bytes - PDF content
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        elements = []
        
        # Header
        elements.append(Paragraph("RELATÓRIO DE ACORDO", self.styles['CustomTitle']))
        elements.append(Paragraph("CredMiner HB - Recuperação de Crédito", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Debtor & Agreement Info
        info_data = [
            ['DEVEDOR:', debtor_name],
            ['CPF/CNPJ:', debtor_cpf],
            ['STATUS DO ACORDO:', agreement_data.get('status', 'N/A').upper()],
            ['DATA DO ACORDO:', agreement_data.get('agreement_date', '-')],
            ['VALOR ACORDADO:', f"R$ {float(agreement_data.get('agreed_value', 0)):,.2f}"],
            ['TOTAL DE PARCELAS:', str(agreement_data.get('total_installments', 1))],
            ['VALOR DA PARCELA:', f"R$ {float(agreement_data.get('installment_value', 0)):,.2f}"],
            ['PRIMEIRA PARCELA:', agreement_data.get('first_installment_date', '-')],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a3a52')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Payment Schedule
        if payments_data:
            elements.append(Paragraph("HISTÓRICO DE PAGAMENTOS", self.styles['CustomHeader']))
            elements.append(Spacer(1, 0.1*inch))
            
            payment_table_data = [['# Parcela', 'Data Prevista', 'Data Pagamento', 'Valor', 'Status']]
            
            for i, payment in enumerate(payments_data, 1):
                payment_table_data.append([
                    str(i),
                    payment.get('scheduled_date', '-'),
                    payment.get('payment_date', '-'),
                    f"R$ {float(payment.get('amount', 0)):,.2f}",
                    payment.get('status', 'Pendente')
                ])
            
            payment_table = Table(payment_table_data, colWidths=[0.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a7b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(payment_table)
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = f"CredMiner HB | NASA, Washington D.C., USA | hb.solutions@gmail.com | halfblood. 2018"
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
            borderPadding=10,
        )))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_payment_extract(self, debtor_name, debtor_cpf, period_start, period_end, payments_data):
        """
        Generate a Payment Extract PDF.
        
        Args:
            debtor_name: str
            debtor_cpf: str
            period_start: date
            period_end: date
            payments_data: list of dicts
        
        Returns:
            bytes - PDF content
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        elements = []
        
        # Header
        elements.append(Paragraph("EXTRATO DE PAGAMENTOS", self.styles['CustomTitle']))
        elements.append(Paragraph("CredMiner HB - Recuperação de Crédito", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Info
        info_text = f"<b>Devedor:</b> {debtor_name} | <b>CPF/CNPJ:</b> {debtor_cpf}<br/><b>Período:</b> {period_start} a {period_end}"
        elements.append(Paragraph(info_text, self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Payments table
        if payments_data:
            payment_table_data = [['Data', 'Descrição', 'Método', 'Valor']]
            total = 0
            
            for payment in payments_data:
                payment_table_data.append([
                    payment.get('payment_date', '-'),
                    payment.get('description', '-')[:30],
                    payment.get('payment_method', '-'),
                    f"R$ {float(payment.get('amount', 0)):,.2f}"
                ])
                total += float(payment.get('amount', 0))
            
            # Total row
            payment_table_data.append([
                '',
                '',
                'TOTAL',
                f"R$ {total:,.2f}"
            ])
            
            payment_table = Table(payment_table_data, colWidths=[1.2*inch, 2*inch, 1.3*inch, 1.5*inch])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a7b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2d5a7b')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f5f5')]),
                ('FONTSIZE', (0, 1), (-1, -2), 9),
            ]))
            
            elements.append(payment_table)
        else:
            elements.append(Paragraph("Nenhum pagamento registrado no período.", self.styles['Normal']))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = f"CredMiner HB | NASA, Washington D.C., USA | hb.solutions@gmail.com | halfblood. 2018"
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
            borderPadding=10,
        )))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
