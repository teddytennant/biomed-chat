# streamlit_app.py
import streamlit as st
import json
from datetime import datetime
from api_client import process_query, process_query_with_context
from rag import retrieve_from_rag, load_rag_index, save_rag_index
import config
import os

# Page configuration
st.set_page_config(
    page_title="Biomedical Engineering Chatbot",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        background-color: #f5f5f5;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #ffffff;
        margin-right: 20%;
        border: 1px solid #e0e0e0;
    }
    .rag-context {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'rag_initialized' not in st.session_state:
    # Try to load existing RAG index
    try:
        if os.path.exists(config.RAG_INDEX_PATH):
            load_rag_index(config.RAG_INDEX_PATH)
            st.session_state.rag_initialized = True
    except:
        st.session_state.rag_initialized = False

# Sidebar
with st.sidebar:
    st.title("🧬 BioMed Chat Settings")
    
    # API Key input
    api_key = st.text_input(
        "Grok API Key",
        type="password",
        value=os.getenv("GROK_API_KEY", ""),
        help="Enter your Grok/xAI API key"
    )
    if api_key:
        config.GROK_API_KEY = api_key
    
    st.divider()
    
    # RAG Settings
    st.subheader("📚 RAG Settings")
    show_rag_context = st.checkbox("Show Retrieved Context", value=True)
    rag_top_k = st.slider("Number of documents to retrieve", 1, 10, config.RAG_TOP_K)
    
    st.divider()
    
    # Tool Status
    st.subheader("🔧 Available Tools")
    tools_list = [
        "🔬 PubMed Search",
        "🧬 Sequence Analysis",
        "💊 Drug Properties",
        "📈 Pharmacokinetics",
        "🏥 Medical Imaging"
    ]
    for tool in tools_list:
        st.write(f"✅ {tool}")
    
    st.divider()
    
    # Session Management
    st.subheader("💾 Session Management")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save RAG Index"):
            save_rag_index()
            st.success("RAG index saved!")
    with col2:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
    
    # Info section
    st.divider()
    st.info("""
    **How to use:**
    1. Enter your question in the chat
    2. The bot will use RAG to retrieve relevant context
    3. Tools will be called automatically when needed
    4. Results are stored for future retrieval
    """)

# Main chat interface
st.title("🧬 Biomedical Engineering Assistant")
st.markdown("Powered by Grok-4 with RAG and specialized biomedical tools")

# Display chat messages
for message in st.session_state.messages:
    with st.container():
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><b>You:</b><br>{message["content"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message"><b>Assistant:</b><br>{message["content"]}</div>', 
                       unsafe_allow_html=True)
            
            # Show RAG context if enabled and available
            if show_rag_context and "rag_context" in message:
                st.markdown(f'<div class="rag-context"><b>📚 Retrieved Context:</b><br>{message["rag_context"]}</div>', 
                           unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Ask a biomedical engineering question...")

if user_input:
    # Check if API key is set
    if not config.GROK_API_KEY or config.GROK_API_KEY == "your-api-key-here":
        st.error("Please enter your Grok API key in the sidebar")
    else:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show user message immediately
        with st.container():
            st.markdown(f'<div class="chat-message user-message"><b>You:</b><br>{user_input}</div>', 
                       unsafe_allow_html=True)
        
        # Show typing indicator
        with st.spinner("🤔 Thinking..."):
            try:
                # Get RAG context for display
                rag_context = retrieve_from_rag(user_input, top_k=rag_top_k)
                
                # Process query with conversation history
                if st.session_state.conversation_history:
                    response, new_history = process_query_with_context(
                        user_input, 
                        st.session_state.conversation_history[-10:]  # Keep last 10 messages
                    )
                    st.session_state.conversation_history = new_history
                else:
                    response = process_query(user_input)
                    st.session_state.conversation_history = [
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": response}
                    ]
                
                # Add assistant message to chat
                message_data = {"role": "assistant", "content": response}
                if show_rag_context and rag_context:
                    message_data["rag_context"] = rag_context[:500] + "..." if len(rag_context) > 500 else rag_context
                
                st.session_state.messages.append(message_data)
                
                # Display assistant response
                with st.container():
                    st.markdown(f'<div class="chat-message assistant-message"><b>Assistant:</b><br>{response}</div>', 
                               unsafe_allow_html=True)
                    
                    if show_rag_context and rag_context:
                        st.markdown(f'<div class="rag-context"><b>📚 Retrieved Context:</b><br>{rag_context[:500]}...</div>', 
                                   unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please check your API key and internet connection")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"Messages in session: {len(st.session_state.messages)}")
with col2:
    st.caption(f"RAG Status: {'✅ Loaded' if st.session_state.rag_initialized else '⏳ Empty'}")
with col3:
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
