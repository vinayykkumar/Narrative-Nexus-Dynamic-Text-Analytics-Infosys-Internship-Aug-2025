import streamlit as st
import base64

def load_css():
    # Load background
    def get_base64(bin_file):
        with open(bin_file, "rb") as f:
            return base64.b64encode(f.read()).decode()

    bin_str = get_base64("assets/waves.png")

    st.markdown(f"""
    <style>
    .block-container {{
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        background: transparent !important;
    }}

    [data-testid="stAppViewContainer"] {{
        background: url("data:image/png;base64,{bin_str}") no-repeat center center fixed;
        background-size: cover;
    }}

    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.6);  
        z-index: 0;
    }}

    [data-testid="stAppViewContainer"] > .main {{
        position: relative;
        z-index: 1;
    }}

    .navbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 40px;
        background: rgba(0,0,0,0.4);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        position: sticky;
        top: 0;
        z-index: 100;
    }}
    .navbar h1 {{
        color: #ef4444;
        font-size: 28px;
        font-weight: 700;
    }}
    .nav-links a {{
        margin-left: 35px;
        text-decoration: none;
        color: #d1d5db;
        font-size: 16px;
        font-weight: 500;
        transition: 0.3s;
    }}
    .nav-links a:hover {{
        color: #ef4444;
    }}
    </style>
    """, unsafe_allow_html=True)
