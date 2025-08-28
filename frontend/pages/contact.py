import streamlit as st

def show():
    st.set_page_config(page_title="Contact | NarrativeNexus", layout="wide")

    # --- STYLES ---
    st.markdown("""
    <style>
    /* Page background */
    .stApp {
        background-color: #0b0b0d;
        color: #ffffff;
    }

    /* Contact Boxes */
    .contact-box {
        background: rgba(17,18,20,0.85);
        border: 1px solid #1c1d21;
        border-radius: 14px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(255,75,75,0.2);
    }

    .contact-title {
        font-size: 28px;
        font-weight: 800;
        color: #ff4b4b;
        margin-bottom: 15px;
        text-align: center;
    }

    .contact-item {
        margin: 12px 0;
        font-size: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Form Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea {
        background: #111214 !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        padding: 8px;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > textarea:focus {
        border: 1px solid #ff4b4b !important;
        outline: none !important;
    }

    /* Submit Button */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ff4b4b, #dc2626);
        color: white;
        font-weight: 700;
        border-radius: 10px;
        padding: 10px 24px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        filter: brightness(1.1);
        transform: translateY(-1px);
    }

    /* Responsive Columns */
    @media (max-width: 768px) {
        .stColumns {flex-direction: column;}
    }
                
    </style>
    """, unsafe_allow_html=True)


    col1, col2 = st.columns([1, 1.5])

    # LEFT COLUMN
    with col1:
        st.markdown('<div class="contact-title">Contact Information</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="contact-item" style="margin-left: 150px;">📍 Hyderabad, India</div>
        <div class="contact-item" style="margin-left: 150px;">📞 +91 98765 43210</div>
        <div class="contact-item" style="margin-left: 150px;">✉️ support@narrativenexus.ai</div>
        <div class="contact-item" style="margin-left: 150px;">🌐 www.narrativenexus.ai</div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # RIGHT COLUMN - FORM
    with col2:
        st.markdown('<div class="contact-title">Send us a Message</div>', unsafe_allow_html=True)

        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Your Message")

        if st.button("Submit"):
            if name and email and message:
                st.success("✅ Thank you! Your message has been sent.")
            else:
                st.error("⚠️ Please fill out all fields before submitting.")

        st.markdown('</div>', unsafe_allow_html=True)
