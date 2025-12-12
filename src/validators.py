import re
from typing import Tuple, Optional

class ContactValidator:
    """Valida e formata dados de contato usando regex"""
    
    @staticmethod
    def validate_cpf(cpf: str) -> Tuple[bool, str]:
        """
        Valida CPF usando regex e algoritmo de verificação.
        Retorna (is_valid, formatted_cpf)
        """
        # Remover caracteres especiais
        cpf_clean = re.sub(r'\D', '', cpf)
        
        # Verificar formato (11 dígitos)
        if not re.match(r'^\d{11}$', cpf_clean):
            return False, "CPF deve conter 11 dígitos"
        
        # Verificar se todos os dígitos são iguais (inválido)
        if len(set(cpf_clean)) == 1:
            return False, "CPF inválido (dígitos iguais)"
        
        # Validar com algoritmo de dígito verificador
        cpf_list = [int(digit) for digit in cpf_clean]
        
        # Primeiro dígito verificador
        sum1 = sum(cpf_list[i] * (10 - i) for i in range(9))
        digit1 = 11 - (sum1 % 11)
        digit1 = 0 if digit1 > 9 else digit1
        
        # Segundo dígito verificador
        sum2 = sum(cpf_list[i] * (11 - i) for i in range(10))
        digit2 = 11 - (sum2 % 11)
        digit2 = 0 if digit2 > 9 else digit2
        
        # Verificar dígitos
        if cpf_list[9] != digit1 or cpf_list[10] != digit2:
            return False, "CPF inválido (dígitos verificadores incorretos)"
        
        # Formatar: XXX.XXX.XXX-XX
        formatted = f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"
        return True, formatted
    
    @staticmethod
    def validate_rg(rg: str) -> Tuple[bool, str]:
        """
        Valida RG usando regex simples.
        Aceita formatos: XXXXXXXX, XX.XXX.XXX-X, etc
        Retorna (is_valid, formatted_rg)
        """
        # Remover caracteres especiais
        rg_clean = re.sub(r'\D', '', rg)
        
        # RG deve ter entre 7 e 9 dígitos
        if not re.match(r'^\d{7,9}$', rg_clean):
            return False, "RG deve conter entre 7 e 9 dígitos"
        
        # Formatar: XX.XXX.XXX-X (se tiver 9 dígitos)
        if len(rg_clean) == 9:
            formatted = f"{rg_clean[:2]}.{rg_clean[2:5]}.{rg_clean[5:8]}-{rg_clean[8]}"
        else:
            formatted = rg_clean
        
        return True, formatted
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Valida número de telefone brasileiro.
        Aceita: (XX) XXXXX-XXXX, (XX)XXXXX-XXXX, XX9XXXX-XXXX, etc
        Retorna (is_valid, formatted_phone)
        """
        # Remover caracteres especiais
        phone_clean = re.sub(r'\D', '', phone)
        
        # Telefone deve ter 10 ou 11 dígitos (com 9º dígito 9 para celulares)
        if not re.match(r'^(\d{10}|\d{11})$', phone_clean):
            return False, "Telefone deve conter 10 ou 11 dígitos"
        
        # Verificar se começa com DDD válido (11-99)
        ddd = int(phone_clean[:2])
        if ddd < 11 or ddd > 99:
            return False, "DDD inválido (deve ser entre 11 e 99)"
        
        # Formatação: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
        if len(phone_clean) == 11:
            # Celular: (XX) 9XXXX-XXXX
            formatted = f"({phone_clean[:2]}) 9{phone_clean[3:7]}-{phone_clean[7:]}"
        else:
            # Fixo: (XX) XXXX-XXXX
            formatted = f"({phone_clean[:2]}) {phone_clean[2:6]}-{phone_clean[6:]}"
        
        return True, formatted
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Valida email usando regex.
        Retorna (is_valid, email_normalized)
        """
        # Regex simples para email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Email inválido"
        
        # Normalizar: lowercase
        normalized = email.lower().strip()
        return True, normalized
    
    @staticmethod
    def normalize_contact(contact: str, contact_type: str) -> Optional[str]:
        """
        Normaliza um contato removendo caracteres especiais.
        Útil para comparação e detecção de duplicatas.
        """
        if contact_type.lower() in ['cpf', 'cnpj']:
            return re.sub(r'\D', '', contact)
        elif contact_type.lower() == 'rg':
            return re.sub(r'\D', '', contact)
        elif contact_type.lower() in ['phone', 'telefone', 'celular']:
            return re.sub(r'\D', '', contact)
        elif contact_type.lower() == 'email':
            return contact.lower().strip()
        return contact

# Status de contatos
CONTACT_STATUS = {
    'ativo': 'Contato ativo e funcional',
    'consultado': 'Já foi consultado',
    'invalido': 'Contato não funciona',
    'duplicado': 'Duplicado (não usar)',
    'obsoleto': 'Dados desatualizados',
    'nao_confirmar': 'Não confirmar contato'
}

CONTACT_STATUS_LIST = list(CONTACT_STATUS.keys())
