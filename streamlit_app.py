# enhanced_ui.py
"""
Enhanced Streamlit UI for Biomedical Engineering Chatbot
Features modern design, animations, and improved user experience
"""

import streamlit as st
import json
from datetime import datetime
import time
import random
from api_client import process_query, process_query_with_context, USE_MOCK_MODE
from rag import retrieve_from_rag, load_rag_index, save_rag_index
import config
import os
import plotly.graph_objects as go
import plotly.express as px

# Page configuration with custom theme
st.set_page_config(
    page_title="BioMed AI Assistant",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/biomed-chat',
        'Report a bug': "https://github.com/yourusername/biomed-chat/issues",
        'About': "# BioMed AI Assistant\nPowered by Grok-4 with RAG Technology"
    }
)

# Enhanced CSS for modern, beautiful UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    
    /* Header Styles */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        animation: slideDown 0.5s ease-out;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .header-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        font-weight: 400;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    
    .status-live {
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(58, 123, 213, 0.4);
    }
    
    .status-demo {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    /* Chat Message Styles */
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 18px 18px 5px 18px;
        padding: 1rem 1.5rem;
        margin-left: 20%;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        animation: slideInRight 0.3s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #2c3e50;
        border-radius: 18px 18px 18px 5px;
        padding: 1rem 1.5rem;
        margin-right: 20%;
        border: 1px solid #e9ecef;
        animation: slideInLeft 0.3s ease-out;
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Tool Card Styles */
    .tool-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .tool-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* RAG Context Box */
    .rag-context {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        color: #2d3436;
        font-size: 0.9rem;
        box-shadow: 0 3px 10px rgba(253, 203, 110, 0.3);
    }
    
    /* Sidebar Styles */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    .sidebar-section {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Input Field Styles */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Metrics Card */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.12);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 0.5rem;
    }
    
    /* Loading Animation */
    .loading-dots {
        display: inline-block;
        animation: loading 1.4s infinite;
    }
    
    @keyframes loading {
        0%, 80%, 100% {
            opacity: 0;
        }
        40% {
            opacity: 1;
        }
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #2d3436;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'rag_initialized' not in st.session_state:
    try:
        if os.path.exists(config.RAG_INDEX_PATH):
            load_rag_index(config.RAG_INDEX_PATH)
            st.session_state.rag_initialized = True
    except:
        st.session_state.rag_initialized = False
if 'theme' not in st.session_state:
    st.session_state.theme = 'gradient'
if 'show_metrics' not in st.session_state:
    st.session_state.show_metrics = True

# Header with animated gradient
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🧬 BioMed AI Assistant</h1>
        <p class="header-subtitle">Advanced Biomedical Engineering Intelligence with RAG Technology</p>
    </div>
""", unsafe_allow_html=True)

# Status indicator
status_class = "status-demo" if USE_MOCK_MODE else "status-live"
status_text = "🎭 Demo Mode" if USE_MOCK_MODE else "🚀 Live AI"
st.markdown(f'<div class="status-badge {status_class}">{status_text}</div>', unsafe_allow_html=True)

# Create columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    # Metrics Dashboard
    if st.session_state.show_metrics:
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            st.markdown("""
                <div class="metric-card">
                    <div class="metric-value">""" + str(len(st.session_state.messages)) + """</div>
                    <div class="metric-label">Messages</div>
                </div>
            """, unsafe_allow_html=True)
        
        with metrics_col2:
            rag_status = "Active" if st.session_state.rag_initialized else "Empty"
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{rag_status}</div>
                    <div class="metric-label">RAG Status</div>
                </div>
            """, unsafe_allow_html=True)
        
        with metrics_col3:
            tool_count = len(config.TOOL_DEFINITIONS) if hasattr(config, 'TOOL_DEFINITIONS') else 0
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{tool_count}</div>
                    <div class="metric-label">Tools Available</div>
                </div>
            """, unsafe_allow_html=True)
        
        with metrics_col4:
            mode = "Demo" if USE_MOCK_MODE else "Live"
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{mode}</div>
                    <div class="metric-label">API Mode</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Chat Interface
    st.markdown("### 💬 Conversation")
    
    # Display chat messages with enhanced styling
    for idx, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
                <div class="chat-container">
                    <div class="user-message">
                        <strong>You:</strong><br>
                        {message["content"]}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-container">
                    <div class="assistant-message">
                        <strong>🤖 Assistant:</strong><br>
                        {message["content"]}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Show RAG context if available
            if "rag_context" in message and message["rag_context"]:
                with st.expander("📚 Retrieved Context", expanded=False):
                    st.markdown(f"""
                        <div class="rag-context">
                            {message["rag_context"]}
                        </div>
                    """, unsafe_allow_html=True)

with col2:
    # Enhanced Sidebar Content
    st.markdown("### ⚙️ Control Panel")
    
    # API Key Configuration
    with st.expander("🔑 API Configuration", expanded=not USE_MOCK_MODE):
        api_key = st.text_input(
            "Grok API Key",
            type="password",
            value=os.getenv("GROK_API_KEY", ""),
            help="Enter your Grok/xAI API key for full functionality"
        )
        if api_key and api_key != "your-api-key-here":
            config.GROK_API_KEY = api_key
            if st.button("🔄 Reload with API"):
                st.rerun()
    
    # RAG Settings
    with st.expander("📊 RAG Settings", expanded=True):
        show_rag = st.checkbox("Show Retrieved Context", value=True)
        rag_top_k = st.slider(
            "Documents to Retrieve",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of similar documents to retrieve from memory"
        )
        
        col_save, col_clear = st.columns(2)
        with col_save:
            if st.button("💾 Save Memory"):
                save_rag_index()
                st.success("Memory saved!")
        with col_clear:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.session_state.conversation_history = []
                st.rerun()
    
    # Available Tools Display
    with st.expander("🛠️ Available Tools", expanded=True):
        tools_info = [
            ("🔬", "PubMed Search", "Search biomedical literature"),
            ("🧬", "Sequence Analysis", "Analyze DNA/RNA/Protein"),
            ("💊", "Drug Properties", "Calculate molecular properties"),
            ("📈", "Pharmacokinetics", "Simulate drug behavior"),
            ("🏥", "Medical Imaging", "Analyze medical images")
        ]
        
        for icon, name, desc in tools_info:
            st.markdown(f"""
                <div class="tool-card">
                    <strong>{icon} {name}</strong><br>
                    <small style="color: #6c757d;">{desc}</small>
                </div>
            """, unsafe_allow_html=True)
    
    # Quick Examples
    with st.expander("💡 Example Queries", expanded=False):
        examples = [
            "What are the latest CRISPR advances?",
            "Analyze the DNA sequence ATGCGATCGTAGC",
            "Search PubMed for CAR-T therapy",
            "Explain ECG signal processing",
            "What are FDA 510(k) requirements?"
        ]
        
        for example in examples:
            if st.button(f"→ {example}", key=f"ex_{example[:20]}"):
                st.session_state.prompt_input = example

# Advanced Features Section
with st.expander("🎨 Advanced Features", expanded=False):
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    
    with col_feat1:
        st.session_state.show_metrics = st.checkbox("Show Metrics Dashboard", value=st.session_state.show_metrics)
    
    with col_feat2:
        animation_speed = st.select_slider(
            "Animation Speed",
            options=["Slow", "Normal", "Fast"],
            value="Normal"
        )
    
    with col_feat3:
        if st.button("📊 Generate Report"):
            st.info("Report generation coming soon!")

# Chat Input Area
st.markdown("---")
user_input = st.text_input(
    "💭 Ask your biomedical engineering question...",
    key="user_input",
    placeholder="E.g., 'Explain the mechanism of CRISPR-Cas9' or 'Analyze sequence ATGCGATCG'",
    value=st.session_state.get('prompt_input', '')
)

# Clear prompt_input after use
if 'prompt_input' in st.session_state:
    del st.session_state.prompt_input

col_send, col_voice, col_clear = st.columns([3, 1, 1])

with col_send:
    send_button = st.button("🚀 Send Message", use_container_width=True)

with col_voice:
    voice_button = st.button("🎤 Voice", use_container_width=True, disabled=True)

with col_clear:
    clear_button = st.button("🔄 Reset", use_container_width=True)
    if clear_button:
        st.session_state.messages = []
        st.rerun()

# Process user input
if (send_button or user_input) and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show typing indicator
    with st.spinner("🧠 Thinking..."):
        # Simulate processing time for better UX
        if USE_MOCK_MODE:
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            progress_bar.empty()
        
        try:
            # Get RAG context
            rag_context = retrieve_from_rag(user_input, top_k=rag_top_k) if show_rag else ""
            
            # Process query
            if st.session_state.conversation_history:
                response, new_history = process_query_with_context(
                    user_input,
                    st.session_state.conversation_history[-10:]
                )
                st.session_state.conversation_history = new_history
            else:
                response = process_query(user_input)
                st.session_state.conversation_history = [
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": response}
                ]
            
            # Add assistant message
            message_data = {"role": "assistant", "content": response}
            if show_rag and rag_context:
                message_data["rag_context"] = rag_context[:500] + "..." if len(rag_context) > 500 else rag_context
            
            st.session_state.messages.append(message_data)
            
            # Show success notification
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            if USE_MOCK_MODE:
                st.info("💡 Running in demo mode. Some features may be limited.")
    
    # Rerun to show new messages
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem 0;">
        <p>Built with ❤️ for the Biomedical Engineering Community</p>
        <p style="font-size: 0.9rem;">Powered by Grok-4 AI • RAG Technology • Advanced Biomedical Tools</p>
    </div>
""", unsafe_allow_html=True)