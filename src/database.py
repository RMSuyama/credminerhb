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
        
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)' if USE_SUPABASE else 'INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                       (('admin', hashed.decode('utf-8'))))
        conn.commit()
        print("Default admin user created.")
    
    conn.close()


def get_petition_templates(process_type=None):
    """Return petition templates from DB filtered by process_type if provided."""
    conn = get_connection()
    cursor = conn.cursor()
    if process_type:
        query = 'SELECT id, name, process_type, description, template_content FROM petition_templates WHERE process_type = %s' if USE_SUPABASE else 'SELECT id, name, process_type, description, template_content FROM petition_templates WHERE process_type = ?'
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
            if USE_SUPABASE:
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
    base_query = 'SELECT id, debtor_id, client_id, debt_id, process_type, process_number, forum_id, vara, distribution_date, status, description, notes FROM judicial_processes'
    params = []
    if filters:
        clauses = []
        if 'client_id' in filters and filters['client_id']:
            clauses.append('client_id = %s' if USE_SUPABASE else 'client_id = ?')
            params.append(filters['client_id'])
        if 'process_type' in filters and filters['process_type']:
            clauses.append('process_type = %s' if USE_SUPABASE else 'process_type = ?')
            params.append(filters['process_type'])
        if 'status' in filters and filters['status']:
            clauses.append('status = %s' if USE_SUPABASE else 'status = ?')
            params.append(filters['status'])
        if 'forum_id' in filters and filters['forum_id']:
            clauses.append('forum_id = %s' if USE_SUPABASE else 'forum_id = ?')
            params.append(filters['forum_id'])
        if 'vara' in filters and filters['vara']:
            clauses.append('vara = %s' if USE_SUPABASE else 'vara = ?')
            params.append(filters['vara'])
        if 'distribution_date_from' in filters and filters['distribution_date_from']:
            clauses.append('distribution_date >= %s' if USE_SUPABASE else 'distribution_date >= ?')
            params.append(filters['distribution_date_from'])
        if 'distribution_date_to' in filters and filters['distribution_date_to']:
            clauses.append('distribution_date <= %s' if USE_SUPABASE else 'distribution_date <= ?')
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
    if petition_date is None:
        import datetime
        petition_date = datetime.date.today()
    if USE_SUPABASE:
        cursor.execute('INSERT INTO judicial_petitions (process_id, petition_type, template_id, petition_date, status, content) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id', (process_id, petition_type, template_id, petition_date, status, content))
        result = cursor.fetchone()
        petition_id = result[0]
    else:
        cursor.execute('INSERT INTO judicial_petitions (process_id, petition_type, template_id, petition_date, status, content) VALUES (?, ?, ?, ?, ?, ?)', (process_id, petition_type, template_id, petition_date, status, content))
        petition_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return petition_id


def get_template_by_id(template_id):
    """Return a petition template by id."""
    conn = get_connection()
    cursor = conn.cursor()
    if USE_SUPABASE:
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
    if USE_SUPABASE:
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
    # Build update parts
    sets = []
    params = []
    if name is not None:
        sets.append('name = %s' if USE_SUPABASE else 'name = ?')
        params.append(name)
    if process_type is not None:
        sets.append('process_type = %s' if USE_SUPABASE else 'process_type = ?')
        params.append(process_type)
    if description is not None:
        sets.append('description = %s' if USE_SUPABASE else 'description = ?')
        params.append(description)
    if template_content is not None:
        sets.append('template_content = %s' if USE_SUPABASE else 'template_content = ?')
        params.append(template_content)
    if not sets:
        conn.close()
        return False
    query = 'UPDATE petition_templates SET ' + ', '.join(sets) + (' WHERE id = %s' if USE_SUPABASE else ' WHERE id = ?')
    params.append(template_id)
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return True


def delete_petition_template(template_id):
    conn = get_connection()
    cursor = conn.cursor()
    if USE_SUPABASE:
        cursor.execute('DELETE FROM petition_templates WHERE id = %s', (template_id,))
    else:
        cursor.execute('DELETE FROM petition_templates WHERE id = ?', (template_id,))
    conn.commit()
    conn.close()
    return True
