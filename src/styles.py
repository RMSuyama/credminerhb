
import streamlit as st

def load_custom_css():
    st.markdown("""
    <style>
        /* === BLACK & ORANGE THEME === */
        :root {
            --bg-dark: #0e0e0e; /* Muito escuro, quase preto */
            --bg-card: #141414; /* Cinza muito escuro para cards */
            --bg-hover: #1f1f1f;
            --primary-orange: #ff5e00; /* Laranja vibrante */
            --accent-orange: #ff8c00; /* Laranja um pouco mais claro */
            --text-main: #e0e0e0;
            --text-muted: #a0a0a0;
            --border-color: #333333;
            --sidebar-bg: #050505;
        }

        /* Global Reset & Background */
        .stApp {
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-orange) !important;
            font-weight: 700 !important;
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
        }
        
        section[data-testid="stSidebar"] .stMarkdown {
            color: var(--text-muted);
        }

        /* Buttons */
        div.stButton > button {
            background-color: transparent !important;
            color: var(--primary-orange) !important;
            border: 1px solid var(--primary-orange) !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.3s ease !important;
            font-weight: 600 !important;
        }

        div.stButton > button:hover {
            background-color: var(--primary-orange) !important;
            color: black !important;
            box-shadow: 0 0 15px rgba(255, 94, 0, 0.4);
            transform: translateY(-2px);
        }

        div.stButton > button:active {
            transform: translateY(0);
        }

        /* Input Fields */
        input, select, textarea {
            background-color: var(--bg-card) !important;
            color: var(--text-main) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 6px !important;
        }

        input:focus, select:focus, textarea:focus {
            border-color: var(--primary-orange) !important;
            box-shadow: 0 0 0 1px var(--primary-orange) !important;
        }
        
        /* Dataframes & Tables */
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background-color: var(--bg-card);
        }
        
        div[data-testid="stDataFrame"] th {
            background-color: #1a1a1a !important;
            color: var(--primary-orange) !important;
        }
        
        div[data-testid="stDataFrame"] td {
            background-color: var(--bg-card) !important;
            color: var(--text-main) !important;
            border-bottom: 1px solid #222 !important;
        }

        /* Metrics / Cards */
        div[data-testid="stMetric"] {
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px;
            padding: 15px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }
        
        div[data-testid="stMetric"]:hover {
            border-color: var(--primary-orange) !important;
            box-shadow: 0 4px 12px rgba(255, 94, 0, 0.15);
        }

        div[data-testid="stMetric"] label {
            color: var(--text-muted) !important;
            font-size: 0.9rem !important;
        }
        
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: var(--primary-orange) !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            text-shadow: 0 0 10px rgba(255, 94, 0, 0.2);
        }

        /* Custom Cards (e.g. Kanban) */
        .kanban-card {
            background: var(--bg-card);
            padding: 12px;
            border-radius: 8px;
            border-left: 3px solid var(--primary-orange);
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            color: var(--text-main);
        }
        
        .kanban-card strong {
            color: white;
            display: block;
            margin-bottom: 4px;
        }
        
        .card-desc {
            color: var(--text-muted);
            font-size: 0.85rem;
        }

        /* Dividers */
        hr {
            border-color: var(--border-color) !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: var(--bg-card) !important;
            color: var(--text-main) !important;
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }

        /* Toast / Alerts */
        div[data-testid="stToast"] {
            background-color: var(--bg-card) !important;
            border-left: 4px solid var(--primary-orange) !important;
        }
        
        div[data-testid="stAlert"] {
            background-color: rgba(255, 94, 0, 0.1) !important;
            border: 1px solid rgba(255, 94, 0, 0.3) !important;
            color: var(--text-main) !important;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-dark); 
        }
        ::-webkit-scrollbar-thumb {
            background: #333; 
            border-radius: 5px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-orange); 
        }

    </style>
    """, unsafe_allow_html=True)
