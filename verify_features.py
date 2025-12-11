import pandas as pd
from src.database import get_connection, init_db
from datetime import date

def verify_features():
    print("Verifying Legal Expenses...")
    init_db()
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Ensure table exists
    try:
        c.execute("SELECT count(*) FROM legal_expenses")
        print("✅ Table 'legal_expenses' exists.")
    except Exception as e:
        print(f"❌ Table 'legal_expenses' MISSING: {e}")
        return

    # 2. Insert dummy
    try:
        c.execute("INSERT INTO legal_expenses (debtor_id, description, value, date) VALUES (999, 'Test Expense', 150.00, '2023-01-01')")
        conn.commit()
        print("✅ Inserted test expense.")
    except Exception as e:
        print(f"❌ Insert failed: {e}")

    # 3. Read back
    try:
        val = pd.read_sql_query("SELECT SUM(value) FROM legal_expenses WHERE debtor_id = 999", conn).iloc[0, 0]
        print(f"✅ Retrieved Sum: {val} (Expected 150.0)")
    except Exception as e:
        print(f"❌ Readback failed: {e}")
        
    # Clean up
    c.execute("DELETE FROM legal_expenses WHERE debtor_id = 999")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    verify_features()
