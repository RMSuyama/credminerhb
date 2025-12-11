import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def send_proposal_email(sender_email, sender_password, to_email, debtor_name, proposal_details, total_value):
    """
    Sends a proposal email to the debtor.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = f"Proposta de Acordo - {debtor_name}"

        body = f"""
        <html>
        <body>
            <h2>Olá, {debtor_name}</h2>
            <p>Segue abaixo o detalhamento dos seus débitos atualizados para negociação:</p>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th>Descrição</th>
                    <th>Vencimento</th>
                    <th>Valor Original</th>
                    <th>Total Atualizado</th>
                </tr>
                {proposal_details}
            </table>
            <h3>Total Geral Atualizado: R$ {total_value:,.2f}</h3>
            <p>Entre em contato para regularizar sua situação.</p>
            <p>Atenciosamente,<br>Departamento Financeiro</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))

        # Connect to Gmail SMTP (defaulting to Gmail for now, can be configurable)
        # Using port 587 for TLS
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        return True, "E-mail enviado com sucesso!"
    except Exception as e:
        return False, f"Erro ao enviar e-mail: {e}"
