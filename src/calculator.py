import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
from src.rules import RuleFactory

DATA_DIR = os.path.join("data")

class IndicesManager:
    _cache = {}

    @staticmethod
    def get_indices(index_name):
        if index_name in IndicesManager._cache:
            return IndicesManager._cache[index_name]
        
        filename = f"indices_{index_name.lower().replace('-', '_')}.csv"
        path = os.path.join(DATA_DIR, filename)
        
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Ensure date format
            df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
            df = df.set_index('data')
            IndicesManager._cache[index_name] = df
            return df
        return None

    @staticmethod
    def get_selic():
        path = os.path.join(DATA_DIR, "selic.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
            df = df.set_index('data')
            return df
        return None

class Calculator:
    @staticmethod
    def calculate(contract_type, original_value, due_date, calc_date, fine_type=None):
        rule = RuleFactory.get_rule(contract_type)
        
        original_value = Decimal(str(original_value))
        due_date = pd.to_datetime(due_date)
        calc_date = pd.to_datetime(calc_date)
        
        if calc_date <= due_date:
            return {
                "original": original_value,
                "corrected": original_value,
                "interest": Decimal("0.00"),
                "fine": Decimal("0.00"),
                "total": original_value
            }

        # 1. Monetary Update
        indices = IndicesManager.get_indices(rule.get_index_name())
        corrected_value = original_value
        correction_factor = Decimal("1.0")

        if indices is not None:
            # Logic: Value * (Current Index / Due Date Index) ??
            # Or Cumulative? 
            # Standard Tabela Prática logic: Value / Index(Due) * Index(Current)
            # But indices in CSV are usually monthly variations or accumulated factors?
            # Assuming the CSV contains ACCUMULATED factors (Fator Acumulado) or Fixed Base Index.
            # If it's monthly variation (%), we need to accumulate.
            # Let's assume the Scraper fetches the "Fator de Atualização" table which is usually absolute numbers.
            # Formula: Corrected = Value * (Factor_Calc_Date / Factor_Due_Date)
            # If Factor_Due_Date is missing, use closest previous.
            
            try:
                indices = indices.copy()
                if 'data' not in indices.columns and indices.index.name == 'data':
                    indices = indices.reset_index()

                # Ensure dates are datetime
                if not pd.api.types.is_datetime64_any_dtype(indices['data']):
                    indices['data'] = pd.to_datetime(indices['data'], format='%d/%m/%Y')
                
                # Filter indices: From Due Month (inclusive) until Month BEFORE Calculation (inclusive)
                # Standard practice: If due in Jan, and calc in March.
                # Correction = Value * (1 + Jan%) * (1 + Feb%). March index is not applied yet (usually).
                # Or if indices are "Index of the Month", we apply from Start to End.
                # Let's apply: indices where date >= due_date_month_start AND date < calc_date_month_start
                
                start_date = due_date.replace(day=1)
                end_date = calc_date.replace(day=1)
                
                mask = (indices['data'] >= pd.Timestamp(start_date)) & (indices['data'] < pd.Timestamp(end_date))
                relevant_indices = indices.loc[mask]
                
                if not relevant_indices.empty:
                    accumulated_factor = Decimal("1.0")
                    for val in relevant_indices['valor']:
                        # val is percentage, e.g. 0.53
                        rate = Decimal(str(val)) / Decimal("100")
                        accumulated_factor *= (1 + rate)
                    
                    correction_factor = accumulated_factor
                    corrected_value = original_value * correction_factor
                else:
                    correction_factor = Decimal("1.0")
                    corrected_value = original_value

            except Exception as e:
                print(f"Error calculating correction: {e}")
                corrected_value = original_value

        # 2. Interest
        interest_val = Decimal("0.00")
        
        if contract_type == "JUDICIAL":
            # Law 14905: Interest = SELIC - IPCA (Monthly)
            # This is complex. We need to iterate month by month.
            # For each month: Rate = Max(0, SELIC_Month - IPCA_Month)
            # Apply compound or simple? Law says "taxa legal". Usually simple accumulation of rates?
            # Or Compound? "Taxa Selic" is usually simple in civil debts, but here it replaces correction+interest?
            # Actually Law 14905 says: Correction (IPCA) + Interest (Selic - IPCA).
            # So we already corrected with IPCA above.
            # Now we add Interest.
            pass # TODO: Implement detailed Law 14905 logic
        else:
            # Standard 1% Simple Interest
            months_diff = (calc_date.year - due_date.year) * 12 + (calc_date.month - due_date.month)
            
            # Check day of month for full month calculation
            if calc_date.day < due_date.day:
                months_diff -= 1
            
            rate = rule.get_interest_rate()
            
            if rule.is_pro_rata():
                # Pro-rata logic
                # Full months
                interest_val = corrected_value * (Decimal(months_diff) * rate)
                
                # Remaining days
                # Calculate days in partial month?
                # Simplified: Total days / 30 * rate?
                # Or: (Date_Calc - Date_Due).days / 30 * rate
                
                total_days = (calc_date - due_date).days
                interest_val = corrected_value * (Decimal(total_days) / Decimal("30") * rate)
            else:
                # No Pro-rata (Full months only)
                if months_diff < 0: months_diff = 0
                interest_val = corrected_value * (Decimal(months_diff) * rate)

        # 3. Fine
        fine_pct = rule.get_fine_percentage(fine_type)
        fine_val = corrected_value * fine_pct

        total = corrected_value + interest_val + fine_val
        
        return {
            "original": original_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "corrected": corrected_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "interest": interest_val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "fine": fine_val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "total": total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "description": f"Correção: {rule.get_index_name()} | Juros: {rule.get_interest_rate()*100}% {'Pro-rata' if rule.is_pro_rata() else 'a.m.'} | Multa: {fine_pct*100}%"
        }
