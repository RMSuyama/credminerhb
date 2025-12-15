
def create_kanban_columns_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS kanban_columns") # Reset for this refactor to ensure clean state or handle migration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kanban_columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                order_index INTEGER DEFAULT 0
            )
        """)
        
        # Seed default columns if empty
        cursor.execute("SELECT COUNT(*) FROM kanban_columns")
        if cursor.fetchone()[0] == 0:
            default_cols = [("A Fazer", 0), ("Em Progresso", 1), ("Feito", 2)]
            cursor.executemany("INSERT INTO kanban_columns (name, order_index) VALUES (?, ?)", default_cols)
            
        conn.commit()
    except Exception as e:
        print(f"Error creating kanban_columns table: {e}")

# ... (Add this to init_db)
