from abc import ABC, abstractmethod
from decimal import Decimal

class ContractRule(ABC):
    @abstractmethod
    def get_index_name(self):
        pass

    @abstractmethod
    def get_fine_percentage(self, debt_type=None):
        pass

    @abstractmethod
    def is_pro_rata(self):
        pass
    
    @abstractmethod
    def get_interest_rate(self):
        pass

class CESURule(ContractRule):
    def get_index_name(self):
        return "INPC"
    
    def get_fine_percentage(self, debt_type=None):
        return Decimal("0.20") # 20%
    
    def is_pro_rata(self):
        return False
    
    def get_interest_rate(self):
        return Decimal("0.01") # 1%

class PAFERule(ContractRule):
    def get_index_name(self):
        return "IPC-FIPE"
    
    def get_fine_percentage(self, debt_type=None):
        return Decimal("0.02") # 2%
    
    def is_pro_rata(self):
        return False
    
    def get_interest_rate(self):
        return Decimal("0.01") # 1%

class PPDRule(ContractRule):
    def get_index_name(self):
        return "IPCA"
    
    def get_fine_percentage(self, debt_type=None):
        return Decimal("0.02") # 2%
    
    def is_pro_rata(self):
        return False
    
    def get_interest_rate(self):
        return Decimal("0.01") # 1%

class MensalidadesRule(ContractRule):
    def get_index_name(self):
        return "INPC"
    
    def get_fine_percentage(self, debt_type="Físico"):
        if debt_type == "Digital":
            return Decimal("0.25") # 25%
        return Decimal("0.02") # 2% (Default Physical)
    
    def is_pro_rata(self):
        return True
    
    def get_interest_rate(self):
        return Decimal("0.01") # 1%

class JudicialRule(ContractRule):
    def get_index_name(self):
        return "IPCA"
    
    def get_fine_percentage(self, debt_type=None):
        return Decimal("0.00") # Configurable, default 0
    
    def is_pro_rata(self):
        return False # Special logic for Law 14905 (SELIC-IPCA)
    
    def get_interest_rate(self):
        return Decimal("0.00") # Calculated dynamically

class LegalExpenseRule(ContractRule):
    def get_index_name(self):
        return "INPC" # Or TJSP standard
    
    def get_fine_percentage(self, debt_type=None):
        return Decimal("0.00") # 0% as per report
    
    def is_pro_rata(self):
        return False
    
    def get_interest_rate(self):
        return Decimal("0.01") # 1% a.m.

class RuleFactory:
    @staticmethod
    def get_rule(contract_type):
        if contract_type == "CESU":
            return CESURule()
        elif contract_type == "PAFE":
            return PAFERule()
        elif contract_type == "PPD":
            return PPDRule()
        elif contract_type == "MENSALIDADES":
            return MensalidadesRule()
        elif contract_type == "JUDICIAL":
            return JudicialRule()
        elif contract_type == "CUSTAS":
            return LegalExpenseRule()
        else:
            raise ValueError(f"Unknown contract type: {contract_type}")
