import sqlite3
import os
import bcrypt
from src.config import USE_SUPABASE, SUPABASE_HOST, SUPABASE_PORT, SUPABASE_DB, SUPABASE_USER, SUPABASE_PASSWORD, SQLITE_DB_PATH

# PostgreSQL support (conditional)
if USE_SUPABASE:
    import psycopg2
    from psycopg2.extras import RealDictCursor

def get_connection():
    """Returns a connection to the database (SQLite or PostgreSQL based on config)."""
    if USE_SUPABASE:
        # Try PostgreSQL connection; if it fails, fall back to local SQLite so the UI can still run.
        try:
            return psycopg2.connect(
                host=SUPABASE_HOST,
                port=SUPABASE_PORT,
                database=SUPABASE_DB,
                user=SUPABASE_USER,
                password=SUPABASE_PASSWORD
            )
        except Exception as e:
            print("Warning: could not connect to Supabase/Postgres (falling back to SQLite):", e)
            # Fall back to SQLite to keep the app usable in local development
            if not os.path.exists("data"):
                os.makedirs("data")
            return sqlite3.connect(SQLITE_DB_PATH)
    else:
        # SQLite connection
        if not os.path.exists("data"):
            os.makedirs("data")
        return sqlite3.connect(SQLITE_DB_PATH)

def init_db():
    """Initializes the database with necessary tables."""
    conn = get_connection()
    cursor = conn.cursor()

    if USE_SUPABASE:
        # PostgreSQL Table Definitions
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                cnpj TEXT UNIQUE,
                email TEXT,
                phone TEXT,
                address TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                client_id INTEGER REFERENCES clients (id) ON DELETE SET NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debtors (
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                cpf_cnpj TEXT,
                rg TEXT,
                email TEXT,
                phone TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_history (
                id SERIAL PRIMARY KEY,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                contact_type TEXT NOT NULL,
                contact_value TEXT NOT NULL,
                status TEXT DEFAULT 'ativo',
                notes TEXT,
                attempt_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guarantors (
                id SERIAL PRIMARY KEY,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                cpf TEXT,
                rg TEXT,
                email TEXT,
                phone TEXT,
                notes TEXT,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS addresses (
                id SERIAL PRIMARY KEY,
                debtor_id INTEGER,
                guarantor_id INTEGER,
                client_id INTEGER NOT NULL,
                cep TEXT,
                street TEXT,
                number TEXT,
                neighborhood TEXT,
                city TEXT,
                state TEXT,
                is_primary BOOLEAN DEFAULT false,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id) ON DELETE CASCADE,
                FOREIGN KEY (guarantor_id) REFERENCES guarantors (id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debts (
                id SERIAL PRIMARY KEY,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                contract_type TEXT NOT NULL,
                description TEXT,
                original_value NUMERIC NOT NULL,
                due_date DATE NOT NULL,
                fine_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS legal_expenses (
                id SERIAL PRIMARY KEY,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                value NUMERIC NOT NULL,
                date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agreements (
                id SERIAL PRIMARY KEY,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                debt_id INTEGER,
                status TEXT DEFAULT 'active',
                agreement_date DATE NOT NULL,
                agreed_value NUMERIC NOT NULL,
                total_installments INTEGER DEFAULT 1,
                installment_value NUMERIC,
                interest_rate NUMERIC DEFAULT 0,
                first_installment_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE,
                FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE SET NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                agreement_id INTEGER,
                debt_id INTEGER,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                payment_date DATE NOT NULL,
                amount NUMERIC NOT NULL,
                installment_number INTEGER,
                payment_method TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agreement_id) REFERENCES agreements (id) ON DELETE SET NULL,
                FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE SET NULL,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
            )
        ''')
        
    else:
        # SQLite Table Definitions (original)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cnpj TEXT UNIQUE,
                email TEXT,
                phone TEXT,
                address TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                client_id INTEGER REFERENCES clients (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debtors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                cpf_cnpj TEXT,
                rg TEXT,
                email TEXT,
                phone TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                contact_type TEXT NOT NULL,
                contact_value TEXT NOT NULL,
                status TEXT DEFAULT 'ativo',
                notes TEXT,
                attempt_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id),
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        # Check if RG column exists (for migration)
        cursor.execute("PRAGMA table_info(debtors)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'rg' not in columns:
            cursor.execute("ALTER TABLE debtors ADD COLUMN rg TEXT")
            print("Migrated: Added 'rg' column to debtors.")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guarantors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                cpf TEXT,
                rg TEXT,
                email TEXT,
                phone TEXT,
                notes TEXT,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id),
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debtor_id INTEGER,
                guarantor_id INTEGER,
                client_id INTEGER NOT NULL,
                cep TEXT,
                street TEXT,
                number TEXT,
                neighborhood TEXT,
                city TEXT,
                state TEXT,
                is_primary BOOLEAN DEFAULT 0,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id),
                FOREIGN KEY (guarantor_id) REFERENCES guarantors (id),
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                contract_type TEXT NOT NULL,
                description TEXT,
                original_value REAL NOT NULL,
                due_date TEXT NOT NULL,
                fine_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id),
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS legal_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                value REAL NOT NULL,
                date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id),
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agreements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                debt_id INTEGER,
                status TEXT DEFAULT 'active',
                agreement_date TEXT NOT NULL,
                agreed_value REAL NOT NULL,
                total_installments INTEGER DEFAULT 1,
                installment_value REAL,
                interest_rate REAL DEFAULT 0,
                first_installment_date TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id),
                FOREIGN KEY (client_id) REFERENCES clients (id),
                FOREIGN KEY (debt_id) REFERENCES debts (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agreement_id INTEGER,
                debt_id INTEGER,
                debtor_id INTEGER NOT NULL,
                payment_date TEXT NOT NULL,
                amount REAL NOT NULL,
                installment_number INTEGER,
                payment_method TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agreement_id) REFERENCES agreements (id),
                FOREIGN KEY (debt_id) REFERENCES debts (id),
                FOREIGN KEY (debtor_id) REFERENCES debtors (id)
            )
        ''')
    
    conn.commit()
    conn.close()
    create_default_admin()

def create_default_admin():
    """Creates a default admin user if no users exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT count(*) FROM users')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Create default admin: admin / admin
        password = "admin".encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)' if USE_SUPABASE else 'INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                       (('admin', hashed.decode('utf-8'))))
        conn.commit()
        print("Default admin user created.")
    
    conn.close()
