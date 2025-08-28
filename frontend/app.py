import streamlit as st
import base64
from pages import contact ,  features , upload , demo
# --- PAGE CONFIG ---
st.set_page_config(page_title="NarrativeNexus", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- FUNCTION TO LOAD IMAGE AS BASE64 (so background always works) ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Encode your background image
bin_str = get_base64_of_bin_file("waves.png")

# --- CUSTOM CSS ---
st.markdown(f"""
    <style>
    /* Remove Streamlit padding */
    .block-container {{
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        background: transparent !important;
    }}

    /* Background Image */
    [data-testid="stAppViewContainer"] {{
        background: url("data:image/png;base64,{bin_str}") no-repeat center center fixed;
        background-size: cover;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}
    
    /* Dark overlay */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.6);  /* 0.6 = 60% darkness, adjust as needed */
        z-index: 0;
        }}

    [data-testid="stAppViewContainer"] > .main {{
        position: relative;
        z-index: 1;
        padding-left: 5%;   /* 5% space from left */
        padding-right: 5%;  /* 5% space from right */
        box-sizing: border-box; /* ensures padding doesn’t break layout */
        max-width: 90%;      /* optional: restrict content width */
        margin: 0 auto;      /* center content */
    }}
    [data-testid="stVerticalBlock"] {{
    padding-left: 30px !important;
    padding-right: 30px !important;
}}



    /* Navbar */
    .navbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 10px;
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
    .nav-links button {{
        background: transparent;
        border: none;
        padding: 0;
        cursor: pointer;
        margin-left: 35px;
        text-decoration: none;
        color: #d1d5db;
        font-size: 16px;
        font-weight: 500;
        transition: 0.3s;
    }}
    .nav-links button:hover {{
        color: #ef4444;
    }}
    .active {{
            background-color: #e63946 !important; /* active tab color */
            color: white !important;
            font-weight: 600;
        }}

    /* Hero section */
    .hero {{
        text-align: center;
        padding: 20px 20px 20px 20px;
    }}
    .hero h1 {{
        font-size: 56px;
        font-weight: 800;
        color: #ef4444;
        margin-bottom: 10px;
    }}
    .hero h3 {{
        font-size: 26px;
        font-weight: 600;
        color: #e5e7eb;
        margin-bottom: 2px;
    }}
    .hero p {{
        font-size: 18px;
        max-width: 750px;
        margin: 0 auto 40px auto;
        line-height: 1.6;
        color: #d1d5db;
    }}
    .button-container {{
        margin-top: 35px;
    }}
    .btn {{
        padding: 14px 32px;
        border-radius: 8px;
        border: none;
        font-size: 17px;
        cursor: pointer;
        font-weight: 600;
        margin: 0 12px;
    }}
    .btn-primary {{
        background: linear-gradient(90deg,#ef4444,#dc2626);
        color: white;
    }}
    .btn-primary:hover {{
        background: linear-gradient(90deg,#dc2626,#b91c1c);
    }}
    .btn-secondary {{
        background: #1f2937;
        color: white;
    }}
    .btn-secondary:hover {{
        background: #374151;
    }}

    /* Features section */
    .features {{
        display: flex;
        justify-content: center;
        gap: 40px;
        margin-top: 10px;
        padding-bottom: 20px;
    }}
    .card {{
        background: rgba(255,255,255,0.09);
        padding: 40px 30px;
        border-radius: 16px;
        text-align: center;
        width: 300px;
        transition: transform 0.3s ease;
    }}
    .card:hover {{
        transform: translateY(-10px);
    }}
    .card h4 {{
        margin-top: 15px;
        font-size: 22px;
        font-weight: 600;
        color: white;
    }}
    .card p {{
        margin-top: 10px;
        font-size: 16px;
        color: #d1d5db;
    }}
    </style>
""", unsafe_allow_html=True)


params = st.query_params

if "page" in params:
    st.session_state.page = params["page"]

current_page = st.session_state.page

# --- NAVBAR ---
st.markdown("""
<div class="navbar">
    <h1>NarrativeNexus</h1>
    <div class="nav-links">
        <form action="" method="get">
            <button name="page" value="Home" class="{'active' if current_page == 'Home' else ''}">Home</button>
            <button name="page" value="Upload" class="{'active' if current_page == 'Upload' else ''}">Upload</button>
            <button name="page" value="Features" class="{'active' if current_page == 'Features' else ''}">Features</button>
            <button name="page" value="Demo" class="{'active' if current_page == 'Demo' else ''}">Demo</button>
            <button name="page" value="Contact" class="{'active' if current_page == 'Contact' else ''}">Contact</button>
        </form>
    </div>
</div>
<div class="page-content">
""", unsafe_allow_html=True)


if st.session_state.page =="Home":
# --- HERO SECTION ---
    st.markdown("""
    <div class="hero">
        <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80" fill="none">
        <circle cx="40" cy="40" r="36" fill="url(#grad)" opacity="0.15"/>
        <rect x="22" y="42" width="8" height="18" rx="2" fill="url(#barGrad)"/>
        <rect x="36" y="32" width="8" height="28" rx="2" fill="url(#barGrad)"/>
        <rect x="50" y="22" width="8" height="38" rx="2" fill="url(#barGrad)"/>
        <path d="M64 12 L68 20 L76 24 L68 28 L64 36 L60 28 L52 24 L60 20 Z" fill="url(#sparkGrad)"/>
        <defs>
            <linearGradient id="grad" x1="0" y1="0" x2="80" y2="80" gradientUnits="userSpaceOnUse">
            <stop stop-color="#ef4444"/>
            <stop offset="1" stop-color="#b91c1c"/>
            </linearGradient>
            <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="40" gradientUnits="userSpaceOnUse">
            <stop stop-color="#ef4444"/>
            <stop offset="1" stop-color="#991b1b"/>
            </linearGradient>
            <linearGradient id="sparkGrad" x1="52" y1="12" x2="76" y2="36" gradientUnits="userSpaceOnUse">
            <stop stop-color="#f87171"/>
            <stop offset="1" stop-color="#dc2626"/>
            </linearGradient>
        </defs>
        </svg>
        <h1>NarrativeNexus</h1>
        <h3>The Dynamic Text Analysis Platform</h3>
        <p>Transform any text into actionable insights. Our AI-powered platform extracts key themes, generates summaries, and provides strategic recommendations to drive informed decisions.</p>
        <div class="button-container">
            <form action="" method="get" style="display:inline;">
                <button class="btn btn-primary" name="page" value="Upload">Start Analyzing →</button>
            </form>
            <form action="" method="get" style="display:inline;">
                <button class="btn btn-secondary" name="page" value="Demo">Watch Demo</button>
            </form>
        </div>

    </div>
    """, unsafe_allow_html=True)

    # --- FEATURES SECTION ---
    st.markdown("""
    <div class="features">
        <div class="card">
            <h4>🎯 Theme Extraction</h4>
            <p>Identify key themes and topics automatically</p>
        </div>
        <div class="card">
            <h4>📊 Smart Insights</h4>
            <p>Get actionable recommendations from your text</p>
        </div>
        <div class="card">
            <h4>⚡ Real-time Analysis</h4>
            <p>Process and analyze text in seconds</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
elif st.session_state.page == "Demo":
    demo.show()
elif st.session_state.page == "Features":
    features.show()
elif st.session_state.page == "Upload":
    upload.show()
elif st.session_state.page == "Contact":
    contact.show()
st.markdown("</div>", unsafe_allow_html=True)