import streamlit as st

def show():
    # --- CUSTOM CSS ---
    st.markdown("""
    <style>
        /* Page background */
        .stApp {
            background-color: #0b0b0d;
            color: white;
        }

        /* Headings */
        .features-header {
            font-size: 2.5rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .features-subheader {
            font-size: 1.1rem;
            text-align: center;
            margin-bottom: 3rem;
            color: #cccccc;
        }

        /* Metrics row */
        .metrics-container {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 4rem;
            flex-wrap: wrap;
        }
        .metric-box {
            background: #111214;
            border: 1px solid #1c1d21;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            flex: 1;
            max-width: 220px;
            min-width: 150px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #ff3333;
        }
        .metric-label {
            margin-top: 0.5rem;
            font-size: 0.95rem;
            color: #cccccc;
        }

        /* Features grid */
        .features-grid {
            margin: 250px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        .feature-card {
            background: #111214;
            border: 1px solid #1c1d21;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        }
        .feature-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.6rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }
        .feature-text {
            font-size: 0.95rem;
            color: #cccccc;
            margin-bottom: 1rem;
        }
        .tag {
            display: inline-block;
            background: #ff3333;
            color: white;
            font-size: 0.7rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 999px;
            margin: 2px 4px 2px 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- CONTENT ---
    st.markdown('<div class="features-header">Powerful Features for <span style="color:#ff3333;">Deep Analysis</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="features-subheader">Our platform combines cutting-edge AI technology with intuitive design to deliver comprehensive text analysis that drives real business value.</div>', unsafe_allow_html=True)

    # --- METRICS ---
    st.markdown("""
    <div class="metrics-container">
        <div class="metric-box">
            <div class="metric-value">&lt; 3 sec</div>
            <div class="metric-label">Analysis Speed</div>
        </div>
        <div class="metric-box">
            <div class="metric-value">94.7%</div>
            <div class="metric-label">Accuracy Rate</div>
        </div>
        <div class="metric-box">
            <div class="metric-value">SOC 2</div>
            <div class="metric-label">Data Security</div>
        </div>
        <div class="metric-box">
            <div class="metric-value">12+</div>
            <div class="metric-label">File Formats</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- FEATURES GRID ---
    st.markdown("""
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-title">🧠 AI-Powered Analysis</div>
            <div class="feature-text">Advanced natural language processing to understand context, sentiment, and meaning behind your text content.</div>
            <span class="tag">NLP</span><span class="tag">Machine Learning</span><span class="tag">Context-Aware</span>
        </div>
        <div class="feature-card">
            <div class="feature-title">🎯 Theme Extraction</div>
            <div class="feature-text">Automatically identify and categorize key themes, topics, and concepts from any text input.</div>
            <span class="tag">Topic Modeling</span><span class="tag">Categorization</span><span class="tag">Auto-tagging</span>
        </div>
        <div class="feature-card">
            <div class="feature-title">📊 Visual Analytics</div>
            <div class="feature-text">Transform your insights into compelling charts, graphs, and visual representations for better understanding.</div>
            <span class="tag">Data Viz</span><span class="tag">Charts</span><span class="tag">Reports</span>
        </div>
        <div class="feature-card">
            <div class="feature-title">💡 Actionable Insights</div>
            <div class="feature-text">Get specific, implementable recommendations based on your text analysis and identified patterns.</div>
            <span class="tag">Recommendations</span><span class="tag">Strategy</span><span class="tag">Action Items</span>
        </div>
        <div class="feature-card">
            <div class="feature-title">⚡ Real-Time Processing</div>
            <div class="feature-text">Lightning-fast analysis that processes thousands of words in seconds, not minutes.</div>
            <span class="tag">Speed</span><span class="tag">Efficiency</span><span class="tag">Real-time</span>
        </div>
        <div class="feature-card">
            <div class="feature-title">🔗 Multi-Source Integration</div>
            <div class="feature-text">Analyze content from various sources - documents, social media, emails, and web content.</div>
            <span class="tag">Integration</span><span class="tag">Multi-format</span><span class="tag">Versatile</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
