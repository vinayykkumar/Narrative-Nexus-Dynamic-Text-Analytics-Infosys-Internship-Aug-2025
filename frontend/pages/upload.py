import streamlit as st

def show():
    # --- CSS for content styling ---
    st.markdown("""
    <style>
      .app-title{
        text-align:center;
        font-weight:800;
        letter-spacing:.4px;
        font-size:46px;
        line-height:1.1;
        background:linear-gradient(90deg, #ef4444, #b91c1c);
        -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
        margin-top: 40px;
        margin-bottom:.35rem;
      }
      .app-sub{
        text-align:center; color:#e5e5e5; font-size:18px;
        margin-bottom:32px;
      }
      .pane{
        background:rgba(17,18,20,0.85);
        border:1px solid #1c1d21;
        border-radius:14px;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.02), 0 10px 30px rgba(0,0,0,0.45);
        padding:22px 22px 20px;
        height: 520px;
        display:flex; flex-direction:column;
      }
      .pane h3{
        display:flex; gap:10px; align-items:center;
        font-size:22px; font-weight:700; margin:2px 0 14px 0;
      }
      .doc-icon { width:22px; height:22px; }
      textarea, .stTextArea textarea{
        background:#0c0d10 !important; color:#ffffff !important;
        border:1px solid rgba(255,255,255,0.2) !important;
        border-radius:8px !important; min-height:260px !important;
        resize:vertical;
        font-size:14px;
      }
      div.stButton > button:first-child {
        border:none; border-radius:10px;
        padding:12px 16px; font-weight:700; letter-spacing:.2px;
        background:linear-gradient(90deg, #ef4444, #dc2626);
        color:white; transition:all .15s ease;
      }
      div.stButton > button:first-child:hover {
        filter:brightness(1.06); transform:translateY(-1px);
      }
      .brain-wrap{ flex:1; display:flex; align-items:center; justify-content:center; flex-direction:column; }
      .brain-svg{ width:120px; height:120px; opacity:.95; }
      .hint{ color:#e5e5e5; text-align:center; margin-top:14px; max-width: 440px; }
      /* Column padding */
      .col-padding {
        padding-left: 30px;
        padding-right: 30px;
      }
    </style>
    """, unsafe_allow_html=True)

    # --- TITLE ---
    st.markdown('<div class="app-title">Analyze Your Text</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-sub">Paste your content below or upload a file to get started with intelligent analysis</div>', unsafe_allow_html=True)

    # --- LAYOUT ---
    left, right = st.columns(2, gap="large")

    with left:
        st.markdown('<div class="col-padding">', unsafe_allow_html=True)  # Add padding wrapper
        st.markdown("""
        <h3>
          <svg class="doc-icon" viewBox="0 0 24 24" fill="none">
            <path d="M7.5 3.5h6.1L18 7.9V20.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 6 20.5V5a1.5 1.5 0 0 1 1.5-1.5Z" stroke="#ef4444" stroke-width="1.6"/>
            <path d="M13.5 3.5V8a1 1 0 0 0 1 1h4.5" stroke="#ef4444" stroke-width="1.6"/>
          </svg>
          Input Text
        </h3>
        """, unsafe_allow_html=True)

        text = st.text_area("Paste your text content here...", height=200, label_visibility="collapsed")
        file = st.file_uploader("Upload File", type=["txt", "pdf", "docx"], label_visibility="collapsed")
        analyze = st.button("Analyze Text", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)  # Close padding wrapper

    with right:
        st.markdown('<div class="col-padding">', unsafe_allow_html=True)  # Add padding wrapper
        st.markdown("""
        <div class="pane">
          <h3>Ready to Analyze</h3>
          <div class="brain-wrap">
            <svg class="brain-svg" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg" fill="none">
              <g stroke="#ffffff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round">
                <path d="M96 56c-22-6-44 8-52 29-5 14-5 30 3 43-10 7-15 19-13 31 3 16 17 27 33 27h29" />
                <path d="M96 56v28c0 12-8 22-20 25" />
                <path d="M96 116c-12 4-20 14-20 26v60" />
                <path d="M160 56c22-6 44 8 52 29 5 14 5 30-3 43 10 7 15 19 13 31-3 16-17 27-33 27h-29" />
                <path d="M160 56v28c0 12 8 22 20 25" />
                <path d="M160 116c12 4 20 14 20 26v60" />
                <path d="M128 88v112" />
                <path d="M96 152h64" />
                <path d="M80 88h32" />
                <path d="M144 88h32" />
              </g>
            </svg>
            <div class="hint">
              Enter your text content and click <b>Analyze Text</b> to get started with intelligent insights.
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # Close padding wrapper
