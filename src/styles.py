
import streamlit as st

def load_custom_css():
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* === PREMIUM DARK & ORANGE THEME === */
        :root {
            /* Palette: Deep Slate, Charcoal, Burnt Orange, Off-White */
            --bg-dark: #121212;         /* Deep background (not pitch black) */
            --bg-elevated: #1E1E1E;     /* Slightly lighter for cards/sidebar */
            --bg-input: #2C2C2C;        /* Input backgrounds */
            
            --primary-orange: #E67E22;  /* Burnt Orange (More elegant than neon) */
            --accent-orange: #D35400;   /* Darker orange for gradients/hover */
            --highlight-orange: #F39C12; /* Lighter gold-orange for emphasis */
            
            --text-main: #ECEFF1;       /* Cool off-white */
            --text-muted: #B0BEC5;      /* Blue-grey for secondary text */
            
            --border-subtle: #333333;
            --border-focus: #E67E22;
            
            --shadow-card: 0 4px 6px rgba(0, 0, 0, 0.3);
            --shadow-hover: 0 8px 12px rgba(0, 0, 0, 0.4);
            
            --sidebar-width: 280px;
        }

        /* --- GLOBAL & TYPOGRAPHY --- */
        .stApp {
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3 {
            color: var(--text-main) !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }
        
        h1 span, h2 span, h3 span {
            color: var(--primary-orange);
        }
        
        p, li, label {
            color: var(--text-muted);
            font-weight: 400;
        }

        /* --- SIDEBAR --- */
        section[data-testid="stSidebar"] {
            background-color: var(--bg-elevated);
            border-right: 1px solid var(--border-subtle);
        }
        
        /* Sidebar Navigation "Buttons" -> Menu Items */
        section[data-testid="stSidebar"] div.stButton button {
            background: transparent !important;
            border: none !important;
            border-radius: 6px !important;
            color: var(--text-muted) !important;
            text-align: left !important;
            width: 100%;
            padding: 0.6rem 0.6rem !important; /* Reduced left padding to align left */
            margin-bottom: 4px;
            font-weight: 500 !important;
            transition: all 0.2s ease;
            box-shadow: none !important;
        }
        
        section[data-testid="stSidebar"] div.stButton button:hover {
            background: rgba(230, 126, 34, 0.1) !important;
            color: var(--primary-orange) !important;
            padding-left: 0.8rem !important; /* Subtle slide effect */
        }
        
        section[data-testid="stSidebar"] div.stButton button:focus {
             background: rgba(230, 126, 34, 0.15) !important;
             color: var(--highlight-orange) !important;
             border-left: 3px solid var(--primary-orange) !important;
        }
        
        /* Divider in Sidebar */
        section[data-testid="stSidebar"] hr {
            margin: 1.5rem 0;
            border-color: var(--border-subtle) !important;
        }

        /* --- MAIN BUTTONS --- */
        /* Primary/Action Buttons in main area */
        div.stButton > button {
            background-color: var(--primary-orange) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 6px rgba(230, 126, 34, 0.2);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        div.stButton > button:hover {
            background-color: var(--accent-orange) !important;
            box-shadow: 0 6px 12px rgba(230, 126, 34, 0.3);
            transform: translateY(-1px);
        }

        div.stButton > button:active {
            transform: translateY(1px);
            box-shadow: none;
        }
        
        /* Secondary buttons (use a class or specific selector if possible, standard streamlit buttons rely on type) */
        button[kind="secondary"] {
            background-color: transparent !important;
            border: 1px solid var(--border-subtle) !important;
            color: var(--text-muted) !important;
            box-shadow: none !important;
        }
        
        button[kind="secondary"]:hover {
             border-color: var(--primary-orange) !important;
             color: var(--primary-orange) !important;
        }

        /* --- INPUTS & FORMS --- */
        div[data-baseweb="input"] {
            background-color: var(--bg-input) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: 8px !important;
        }
        
        div[data-baseweb="select"] > div {
             background-color: var(--bg-input) !important;
             border-color: var(--border-subtle) !important;
        }
        
        div[data-baseweb="base-input"] input {
            color: var(--text-main) !important;
        }
        
        /* Focus states manually overridden via border color on container if possible, 
           or globally addressing the focus-within pseudo class */
        div[data-baseweb="input"]:focus-within {
             border-color: var(--primary-orange) !important;
             box-shadow: 0 0 0 1px var(--primary-orange);
        }

        label[data-testid="stLabel"] {
            color: var(--text-muted) !important;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.4rem;
        }

        /* --- CARDS / CONTAINERS --- */
        div[data-testid="stMetric"], div.stDataFrame, .stExpander {
            background-color: var(--bg-elevated) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: 4px !important; /* Sharper corners */
            box-shadow: none !important; /* Flat design */
        }
        
        /* Metric Specifics */
        div[data-testid="stMetric"] {
            padding: 1rem;
        }
        div[data-testid="stMetricValue"] {
            color: var(--primary-orange) !important;
        }
        
        /* --- KANBAN CARD --- */
        .kanban-card {
            background-color: var(--bg-input);
            border-left: 4px solid var(--primary-orange);
            padding: 12px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: transform 0.2s;
        }
        
        .kanban-card:hover {
            background-color: #333;
            transform: translateX(4px);
        }
        
        .kanban-card strong {
            color: var(--text-main);
            font-size: 1rem;
            display: block;
            margin-bottom: 6px;
        }
        
        .card-desc {
            color: var(--text-muted);
            font-size: 0.85rem;
            line-height: 1.4;
        }

        /* --- ALERTS --- */
        div[data-testid="stAlert"] {
            background-color: rgba(230, 126, 34, 0.05) !important;
            border: 1px solid rgba(230, 126, 34, 0.2) !important;
        }

        /* --- TABLES --- */
        thead tr th {
            background-color: var(--bg-input) !important;
            color: var(--text-main) !important;
            font-weight: 600 !important;
        }
        tbody tr td {
            background-color: var(--bg-elevated) !important;
            color: var(--text-muted) !important;
            border-bottom: 1px solid var(--border-subtle) !important;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-dark);
        }
        ::-webkit-scrollbar-thumb {
            background: #444;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-orange);
        }




        
    </style>
    """, unsafe_allow_html=True)
