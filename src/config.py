import os

# Try Streamlit secrets first (for cloud deployment)
try:
    import streamlit as st
    USE_SUPABASE = st.secrets["database"]["USE_SUPABASE"].lower() == "true"
    SUPABASE_HOST = st.secrets["database"]["SUPABASE_HOST"]
    SUPABASE_PORT = st.secrets["database"]["SUPABASE_PORT"]
    SUPABASE_DB = st.secrets["database"]["SUPABASE_DB"]
    SUPABASE_USER = st.secrets["database"]["SUPABASE_USER"]
    SUPABASE_PASSWORD = st.secrets["database"]["SUPABASE_PASSWORD"]
except (KeyError, FileNotFoundError, AttributeError):
    # Fallback to environment variables (local dev)
    from dotenv import load_dotenv
    load_dotenv()
    USE_SUPABASE = os.getenv("USE_SUPABASE", "False").lower() == "true"
    SUPABASE_HOST = os.getenv("SUPABASE_HOST", "")
    SUPABASE_PORT = os.getenv("SUPABASE_PORT", "5432")
    SUPABASE_DB = os.getenv("SUPABASE_DB", "postgres")
    SUPABASE_USER = os.getenv("SUPABASE_USER", "")
    SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "")

# Local SQLite Configuration
SQLITE_DB_PATH = os.path.join("data", "debtors.db")
