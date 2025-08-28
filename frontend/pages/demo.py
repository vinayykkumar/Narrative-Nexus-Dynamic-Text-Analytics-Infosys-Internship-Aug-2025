import streamlit as st

def show():
    # Hero Section
    st.markdown("""
    <div style="text-align: center;">
        <h1 style="font-size: 3rem; font-weight: bold; color: #ff4b4b;">
            Experience NarrativeNexus
        </h1>
        <p style="font-size: 1.2rem; color: #d9d9d9; max-width: 700px; margin: 0 auto;margin-bottom: 2rem;">
            Watch our demo to explore how NarrativeNexus transforms raw text into insightful narratives, 
            making analysis easier, faster, and visually engaging.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Demo Video Section (Embed YouTube or Local)
    video_url = "https://www.youtube.com/embed/BHACKCNDMW8"  # Replace with your video link
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <iframe width="800" height="450" 
            src="{video_url}" 
            title="NarrativeNexus Demo" frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen></iframe>
        </div>
        """, unsafe_allow_html=True)

    # Call to Action
    st.markdown("""
    <div style="text-align: center">
        <h2 style="color: #ff4b4b;">Ready to Explore?</h2>
        <p style="color: #cccccc; font-size: 1.1rem;">
            Try uploading your own text now and see NarrativeNexus in action.
        </p>
        <a href="?page=upload">
            <button style="margin-bottom: 20px;background-color: #ff4b4b; color: white; padding: 0.8rem 2rem; 
            border: none; border-radius: 8px; font-size: 1rem; cursor: pointer;">
                Get Started 🚀
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
