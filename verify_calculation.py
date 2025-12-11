
import sys
import os
from decimal import Decimal
import pandas as pd
from datetime import date

# Add current directory to path so we can import src
sys.path.append(os.getcwd())

from src.calculator import Calculator
from src.rules import RuleFactory

def verify():
    print("--- Verificando Lógica de Cálculo de Multa ---")
    
    # Setup parameters
    contract_type = "CESU" # Uses INPC, 20% Fine
    original_val = 1000.00
    due_date = date(2023, 1, 1) # Jan 1st, 2023
    calc_date = date(2024, 1, 1) # Jan 1st, 2024
    
    # 1. Run Calculator
    print(f"Calculando: Valor Original R${original_val}, Vencimento {due_date}, Data Cálculo {calc_date}")
    
    result = Calculator.calculate(
        contract_type=contract_type,
        original_value=original_val,
        due_date=due_date,
        calc_date=calc_date,
        fine_type=None
    )
    
    # 2. Extract results
    res_original = result['original']
    res_corrected = result['corrected']
    res_fine = result['fine']
    
    print(f"Resultado Original: R$ {res_original}")
    print(f"Resultado Corrigido: R$ {res_corrected}")
    print(f"Resultado Multa: R$ {res_fine}")
    
    # 3. Verify Fine Calculation
    # Rule CESU = 20% Fine
    fine_pct = Decimal("0.20")
    
    expected_fine_on_corrected = res_corrected * fine_pct
    expected_fine_on_original = res_original * fine_pct
    
    print(f"\n--- Validação ---")
    print(f"Multa esperada (sobre CORRIGIDO): R$ {expected_fine_on_corrected:.2f}")
    print(f"Multa esperada (sobre ORIGINAL): R$ {expected_fine_on_original:.2f}")
    
    if abs(res_fine - expected_fine_on_corrected) < Decimal("0.02"):
        print("\n✅ SUCESSO: A multa foi calculada sobre o valor CORRIGIDO.")
    elif abs(res_fine - expected_fine_on_original) < Decimal("0.02"):
        print("\n❌ FALHA: A multa foi calculada sobre o valor ORIGINAL.")
    else:
        print("\n⚠️ INDEFINIDO: O cálculo da multa não bateu com nenhum dos esperados.")

if __name__ == "__main__":
    verify()
