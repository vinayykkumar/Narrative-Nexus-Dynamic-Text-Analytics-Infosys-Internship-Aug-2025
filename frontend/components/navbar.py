import streamlit as st

def navbar():
    st.markdown("""
    <div class="navbar">
        <h1>NarrativeNexus</h1>
        <div class="nav-links">
            <a href="/Home">Home</a>
            <a href="/Features">Features</a>
            <a href="/Demo">Demo</a>
            <a href="/Contact">Contact</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
