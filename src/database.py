import sqlite3
import os
import bcrypt
from src.config import USE_SUPABASE, SUPABASE_HOST, SUPABASE_PORT, SUPABASE_DB, SUPABASE_USER, SUPABASE_PASSWORD, SQLITE_DB_PATH
import pandas as pd

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
                main_forum TEXT,
                jurisdiction_state TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_forums (
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL,
                forum_name TEXT NOT NULL,
                forum_code TEXT,
                state TEXT,
                city TEXT,
                is_main BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE,
                UNIQUE(client_id, forum_code)
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS judicial_processes (
                id SERIAL PRIMARY KEY,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                debt_id INTEGER,
                process_type TEXT NOT NULL,
                process_number TEXT UNIQUE,
                forum_id INTEGER,
                vara TEXT,
                distribution_date DATE,
                status TEXT DEFAULT 'ativo',
                description TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE,
                FOREIGN KEY (debt_id) REFERENCES debts (id) ON DELETE SET NULL,
                FOREIGN KEY (forum_id) REFERENCES client_forums (id) ON DELETE SET NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS petition_templates (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                process_type TEXT NOT NULL,
                description TEXT,
                template_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS judicial_petitions (
                id SERIAL PRIMARY KEY,
                process_id INTEGER NOT NULL,
                petition_type TEXT NOT NULL,
                template_id INTEGER,
                petition_date DATE,
                status TEXT DEFAULT 'rascunho',
                content TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (process_id) REFERENCES judicial_processes (id) ON DELETE CASCADE,
                FOREIGN KEY (template_id) REFERENCES petition_templates (id) ON DELETE SET NULL
            )
        ''')

        # Kanban / Board for simple task tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kanban_cards (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'todo',
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                main_forum TEXT,
                jurisdiction_state TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_forums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                forum_name TEXT NOT NULL,
                forum_code TEXT,
                state TEXT,
                city TEXT,
                is_main INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id),
                UNIQUE(client_id, forum_code)
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
                client_id INTEGER NOT NULL,
                payment_date TEXT NOT NULL,
                amount REAL NOT NULL,
                installment_number INTEGER,
                payment_method TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agreement_id) REFERENCES agreements (id),
                FOREIGN KEY (debt_id) REFERENCES debts (id),
                FOREIGN KEY (debtor_id) REFERENCES debtors (id),
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS judicial_processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debtor_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                debt_id INTEGER,
                process_type TEXT NOT NULL,
                process_number TEXT UNIQUE,
                forum_id INTEGER,
                vara TEXT,
                distribution_date TEXT,
                status TEXT DEFAULT 'ativo',
                description TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debtor_id) REFERENCES debtors (id),
                FOREIGN KEY (client_id) REFERENCES clients (id),
                FOREIGN KEY (debt_id) REFERENCES debts (id),
                FOREIGN KEY (forum_id) REFERENCES client_forums (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS petition_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                process_type TEXT NOT NULL,
                description TEXT,
                template_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS judicial_petitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_id INTEGER NOT NULL,
                petition_type TEXT NOT NULL,
                template_id INTEGER,
                petition_date TEXT,
                status TEXT DEFAULT 'rascunho',
                content TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (process_id) REFERENCES judicial_processes (id),
                FOREIGN KEY (template_id) REFERENCES petition_templates (id)
            )
        ''')

        # Kanban / Board for simple task tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kanban_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'todo',
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    conn.commit()
    conn.close()
    # Seed in-memory petition templates into the DB if table is empty
    try:
        seed_default_petition_templates()
    except Exception:
        pass
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
        
        # Determine placeholder style based on actual connection type
        use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
        if use_postgres_style:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', ('admin', hashed.decode('utf-8')))
        else:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('admin', hashed.decode('utf-8')))
        conn.commit()
        print("Default admin user created.")
    
    conn.close()


def get_petition_templates(process_type=None):
    """Return petition templates from DB filtered by process_type if provided."""
    conn = get_connection()
    cursor = conn.cursor()
    # Choose parameter placeholder style based on actual connection type
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    if process_type:
        query = 'SELECT id, name, process_type, description, template_content FROM petition_templates WHERE process_type = %s' if use_postgres_style else 'SELECT id, name, process_type, description, template_content FROM petition_templates WHERE process_type = ?'
        cursor.execute(query, (process_type,))
    else:
        query = 'SELECT id, name, process_type, description, template_content FROM petition_templates'
        cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    templates = []
    for row in rows:
        templates.append({
            'id': row[0],
            'name': row[1],
            'process_type': row[2],
            'description': row[3],
            'template_content': row[4],
        })
    return templates


def seed_default_petition_templates():
    """Seed default petition templates from package file into DB if none exist."""
    try:
        from src.petition_templates import get_all_petition_types as _get_defaults
        defaults = _get_defaults()
    except Exception:
        return

    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    # Check if any templates exist
    cursor.execute('SELECT count(*) FROM petition_templates')
    count = cursor.fetchone()[0]
    if count == 0:
        # Insert defaults
        for key, data in defaults.items():
            # key is like 'inicial_juntada_custas'
            process_type = key.split('_')[0]
            name = data.get('name')
            description = data.get('description')
            template_content = data.get('content')
            if use_postgres_style:
                cursor.execute('INSERT INTO petition_templates (name, process_type, description, template_content) VALUES (%s, %s, %s, %s)', (name, process_type, description, template_content))
            else:
                cursor.execute('INSERT INTO petition_templates (name, process_type, description, template_content) VALUES (?, ?, ?, ?)', (name, process_type, description, template_content))
        conn.commit()
    conn.close()


def list_judicial_processes(filters=None):
    """List judicial processes with optional filters.

    Filters: dict keys may include client_id, process_type, status, forum_id, vara, distribution_date_from, distribution_date_to
    """
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    base_query = 'SELECT id, debtor_id, client_id, debt_id, process_type, process_number, forum_id, vara, distribution_date, status, description, notes FROM judicial_processes'
    params = []
    if filters:
        clauses = []
        if 'client_id' in filters and filters['client_id']:
            clauses.append('client_id = %s' if use_postgres_style else 'client_id = ?')
            params.append(filters['client_id'])
        if 'process_type' in filters and filters['process_type']:
            clauses.append('process_type = %s' if use_postgres_style else 'process_type = ?')
            params.append(filters['process_type'])
        if 'status' in filters and filters['status']:
            clauses.append('status = %s' if use_postgres_style else 'status = ?')
            params.append(filters['status'])
        if 'forum_id' in filters and filters['forum_id']:
            clauses.append('forum_id = %s' if use_postgres_style else 'forum_id = ?')
            params.append(filters['forum_id'])
        if 'vara' in filters and filters['vara']:
            clauses.append('vara = %s' if use_postgres_style else 'vara = ?')
            params.append(filters['vara'])
        if 'distribution_date_from' in filters and filters['distribution_date_from']:
            clauses.append('distribution_date >= %s' if use_postgres_style else 'distribution_date >= ?')
            params.append(filters['distribution_date_from'])
        if 'distribution_date_to' in filters and filters['distribution_date_to']:
            clauses.append('distribution_date <= %s' if use_postgres_style else 'distribution_date <= ?')
            params.append(filters['distribution_date_to'])
        if clauses:
            base_query += ' WHERE ' + ' AND '.join(clauses)
    cursor.execute(base_query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    processes = []
    for row in rows:
        processes.append({
            'id': row[0],
            'debtor_id': row[1],
            'client_id': row[2],
            'debt_id': row[3],
            'process_type': row[4],
            'process_number': row[5],
            'forum_id': row[6],
            'vara': row[7],
            'distribution_date': row[8],
            'status': row[9],
            'description': row[10],
            'notes': row[11],
        })
    return processes


def create_judicial_petition(process_id, petition_type, template_id=None, content=None, petition_date=None, status='rascunho'):
    """Create a judicial petition entry in DB.
    Returns created petition id.
    """
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    if petition_date is None:
        import datetime
        petition_date = datetime.date.today()
    if use_postgres_style:
        cursor.execute('INSERT INTO judicial_petitions (process_id, petition_type, template_id, petition_date, status, content) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id', (process_id, petition_type, template_id, petition_date, status, content))
        result = cursor.fetchone()
        petition_id = result[0]
    else:
        cursor.execute('INSERT INTO judicial_petitions (process_id, petition_type, template_id, petition_date, status, content) VALUES (?, ?, ?, ?, ?, ?)', (process_id, petition_type, template_id, petition_date, status, content))
        petition_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return petition_id


def create_judicial_process(debtor_id, client_id, debt_id=None, process_type='inicial', process_number=None, forum_id=None, vara=None, distribution_date=None, status='ativo', description=None, notes=None):
    """Create a judicial process record and return its id."""
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    if use_postgres_style:
        cursor.execute('INSERT INTO judicial_processes (debtor_id, client_id, debt_id, process_type, process_number, forum_id, vara, distribution_date, status, description, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
                       (debtor_id, client_id, debt_id, process_type, process_number, forum_id, vara, distribution_date, status, description, notes))
        new_id = cursor.fetchone()[0]
    else:
        cursor.execute('INSERT INTO judicial_processes (debtor_id, client_id, debt_id, process_type, process_number, forum_id, vara, distribution_date, status, description, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (debtor_id, client_id, debt_id, process_type, process_number, forum_id, vara, distribution_date, status, description, notes))
        new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def list_judicial_petitions(process_id):
    """List petitions linked to a judicial process."""
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    if use_postgres_style:
        cursor.execute('SELECT id, petition_type, template_id, petition_date, status, content FROM judicial_petitions WHERE process_id = %s ORDER BY petition_date DESC', (process_id,))
    else:
        cursor.execute('SELECT id, petition_type, template_id, petition_date, status, content FROM judicial_petitions WHERE process_id = ? ORDER BY petition_date DESC', (process_id,))
    rows = cursor.fetchall()
    conn.close()
    petitions = []
    for r in rows:
        petitions.append({
            'id': r[0],
            'petition_type': r[1],
            'template_id': r[2],
            'petition_date': r[3],
            'status': r[4],
            'content': r[5]
        })
    return petitions


def update_judicial_petition_status(petition_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    if use_postgres_style:
        cursor.execute('UPDATE judicial_petitions SET status = %s WHERE id = %s', (status, petition_id))
    else:
        cursor.execute('UPDATE judicial_petitions SET status = ? WHERE id = ?', (status, petition_id))
    conn.commit()
    conn.close()
    return True


def get_template_by_id(template_id):
    """Return a petition template by id."""
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    if use_postgres_style:
        cursor.execute('SELECT id, name, process_type, description, template_content FROM petition_templates WHERE id = %s', (template_id,))
    else:
        cursor.execute('SELECT id, name, process_type, description, template_content FROM petition_templates WHERE id = ?', (template_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        'id': row[0],
        'name': row[1],
        'process_type': row[2],
        'description': row[3],
        'template_content': row[4],
    }


def create_petition_template(name, process_type, description, template_content):
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    if use_postgres_style:
        cursor.execute('INSERT INTO petition_templates (name, process_type, description, template_content) VALUES (%s, %s, %s, %s) RETURNING id', (name, process_type, description, template_content))
        new_id = cursor.fetchone()[0]
    else:
        cursor.execute('INSERT INTO petition_templates (name, process_type, description, template_content) VALUES (?, ?, ?, ?)', (name, process_type, description, template_content))
        new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_petition_template(template_id, name=None, process_type=None, description=None, template_content=None):
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    # Build update parts
    sets = []
    params = []
    if name is not None:
        sets.append('name = %s' if use_postgres_style else 'name = ?')
        params.append(name)
    if process_type is not None:
        sets.append('process_type = %s' if use_postgres_style else 'process_type = ?')
        params.append(process_type)
    if description is not None:
        sets.append('description = %s' if use_postgres_style else 'description = ?')
        params.append(description)
    if template_content is not None:
        sets.append('template_content = %s' if use_postgres_style else 'template_content = ?')
        params.append(template_content)
    if not sets:
        conn.close()
        return False
    query = 'UPDATE petition_templates SET ' + ', '.join(sets) + (' WHERE id = %s' if use_postgres_style else ' WHERE id = ?')
    params.append(template_id)
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return True


def delete_petition_template(template_id):
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    if use_postgres_style:
        cursor.execute('DELETE FROM petition_templates WHERE id = %s', (template_id,))
    else:
        cursor.execute('DELETE FROM petition_templates WHERE id = ?', (template_id,))
    conn.commit()
    conn.close()
    return True


def delete_debtor_by_cpf(cpf_cnpj: str):
    """Delete a debtor and related records by CPF/CNPJ (digits-only match).

    Returns deleted debtor id if deleted, else None.
    """
    if not cpf_cnpj:
        return None
    digits = ''.join(filter(str.isdigit, str(cpf_cnpj)))
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Fetch all debtors and match by digits-only
        cursor.execute('SELECT id, cpf_cnpj FROM debtors')
        rows = cursor.fetchall()
        target_id = None
        for row in rows:
            # row format differs by db driver
            row_id = row[0]
            row_cpf = row[1]
            row_digits = ''.join(filter(str.isdigit, str(row_cpf or '')))
            if row_digits == digits:
                target_id = row_id
                break
        if target_id is None:
            return None
        # Delete using FK cascade
        # If we attempted Supabase but fell back to SQLite (connection is sqlite3.Connection),
        # use SQLite parameter style. Otherwise use the Supabase/Postgres style.
        use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
        if use_postgres_style:
            cursor.execute('DELETE FROM debtors WHERE id = %s', (target_id,))
        else:
            cursor.execute('DELETE FROM debtors WHERE id = ?', (target_id,))
        conn.commit()
        return target_id
    finally:
        conn.close()


def get_kanban_cards(status=None):
    """Return all kanban cards, optionally filtered by status, ordered by order_index."""
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    if status:
        if use_postgres_style:
            cursor.execute('SELECT id, title, description, status, order_index FROM kanban_cards WHERE status = %s ORDER BY order_index ASC', (status,))
        else:
            cursor.execute('SELECT id, title, description, status, order_index FROM kanban_cards WHERE status = ? ORDER BY order_index ASC', (status,))
    else:
        if use_postgres_style:
            cursor.execute('SELECT id, title, description, status, order_index FROM kanban_cards ORDER BY status, order_index ASC')
        else:
            cursor.execute('SELECT id, title, description, status, order_index FROM kanban_cards ORDER BY status, order_index ASC')
    rows = cursor.fetchall()
    conn.close()
    cards = []
    for r in rows:
        cards.append({'id': r[0], 'title': r[1], 'description': r[2], 'status': r[3], 'order_index': r[4]})
    return cards


def create_kanban_card(title, description=None, status='todo'):
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    if use_postgres_style:
        cursor.execute('INSERT INTO kanban_cards (title, description, status) VALUES (%s, %s, %s) RETURNING id', (title, description, status))
        new_id = cursor.fetchone()[0]
    else:
        cursor.execute('INSERT INTO kanban_cards (title, description, status) VALUES (?, ?, ?)', (title, description, status))
        new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_kanban_card(card_id, title=None, description=None, status=None, order_index=None):
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    sets = []
    params = []
    if title is not None:
        sets.append('title = %s' if use_postgres_style else 'title = ?')
        params.append(title)
    if description is not None:
        sets.append('description = %s' if use_postgres_style else 'description = ?')
        params.append(description)
    if status is not None:
        sets.append('status = %s' if use_postgres_style else 'status = ?')
        params.append(status)
    if order_index is not None:
        sets.append('order_index = %s' if use_postgres_style else 'order_index = ?')
        params.append(order_index)
    if not sets:
        conn.close()
        return False
    query = 'UPDATE kanban_cards SET ' + ', '.join(sets) + (' WHERE id = %s' if use_postgres_style else ' WHERE id = ?')
    params.append(card_id)
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return True


def delete_kanban_card(card_id):
    conn = get_connection()
    cursor = conn.cursor()
    use_postgres_style = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
    if use_postgres_style:
        cursor.execute('DELETE FROM kanban_cards WHERE id = %s', (card_id,))
    else:
        cursor.execute('DELETE FROM kanban_cards WHERE id = ?', (card_id,))
    conn.commit()
    conn.close()
    return True


def get_dashboard_kpis():
    """Retrieve all KPI metrics for the dashboard in a single call."""
    conn = get_connection()
    try:
        # Total Debtors
        total_debtors = pd.read_sql_query("SELECT count(*) as cnt FROM debtors", conn).iloc[0, 0]
        
        # Total Original Value & Total Debts
        debts_stats = pd.read_sql_query("SELECT COALESCE(sum(original_value), 0) as total_val, count(*) as cnt FROM debts", conn)
        total_original_value = debts_stats.iloc[0]['total_val']
        total_debts = debts_stats.iloc[0]['cnt']
        
        # Active Agreements
        agreements_df = pd.read_sql_query("SELECT * FROM agreements", conn)
        active_agreements = len(agreements_df[agreements_df['status'] == 'active']) if not agreements_df.empty else 0
        
        # Payments & Recovery
        payments_df = pd.read_sql_query("SELECT * FROM payments", conn)
        total_recovered = payments_df['amount'].sum() if not payments_df.empty else 0
        total_payments = len(payments_df)
        
        # Recovery Rate
        recovery_rate = (total_recovered / total_original_value * 100) if total_original_value > 0 else 0
        
        return {
            "total_debtors": total_debtors,
            "total_debts": total_debts,
            "total_original_value": total_original_value,
            "active_agreements": active_agreements,
            "total_recovered": total_recovered,
            "total_payments": total_payments,
            "recovery_rate": recovery_rate
        }
    except Exception as e:
        print(f"Error fetching KPIs: {e}")
        return {
            "total_debtors": 0, "total_debts": 0, "total_original_value": 0,
            "active_agreements": 0, "total_recovered": 0, "total_payments": 0, "recovery_rate": 0
        }
    finally:
        conn.close()

def get_clients():
    """Retrieve all clients as a DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM clients ORDER BY name", conn)
    finally:
        conn.close()

def get_debtors():
    """Retrieve all debtors as a DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM debtors ORDER BY name", conn)
    finally:
        conn.close()

def get_debts(debtor_id=None):
    """Retrieve debts as a DataFrame, optionally filtered by debtor_id."""
    conn = get_connection()
    try:
        if debtor_id:
            # Check connection type for parameter style
            import sqlite3
            use_postgres = USE_SUPABASE and not isinstance(conn, sqlite3.Connection)
            if use_postgres:
                 return pd.read_sql_query("SELECT * FROM debts WHERE debtor_id = %s", conn, params=(debtor_id,))
            else:
                 return pd.read_sql_query("SELECT * FROM debts WHERE debtor_id = ?", conn, params=(debtor_id,))
        else:
            return pd.read_sql_query("SELECT * FROM debts", conn)
    except Exception as e:
        print(f"Error fetching debts: {e}")
        return pd.DataFrame()
    finally:
         conn.close()
