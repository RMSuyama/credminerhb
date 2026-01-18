
import sqlite3
import os

DB_PATH = os.path.join("data", "debtors.db")
print(f"Connecting to {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(kanban_cards)")
    cols = [info[1] for info in cursor.fetchall()]
    print(f"Current columns: {cols}")

    if 'due_date' not in cols:
        print("Adding due_date...")
        cursor.execute("ALTER TABLE kanban_cards ADD COLUMN due_date TEXT")
    
    if 'priority' not in cols:
        print("Adding priority...")
        cursor.execute("ALTER TABLE kanban_cards ADD COLUMN priority TEXT DEFAULT 'Medium'")
        
    if 'is_archived' not in cols:
        print("Adding is_archived...")
        cursor.execute("ALTER TABLE kanban_cards ADD COLUMN is_archived BOOLEAN DEFAULT 0")

    conn.commit()
    print("Schema updated successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
