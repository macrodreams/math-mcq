from langchain.chat_models import init_chat_model
import streamlit as st
import os
import json
import re

# Load external CSS
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "llm_response" not in st.session_state:
    st.session_state.llm_response = None
if "response_dict" not in st.session_state:
    st.session_state.response_dict = None
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None

# Google-style App Header
st.markdown("""
<div class="google-header">
    <h1><span class="header-icon">🔢</span> Math Practice</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding: 20px;">
    <p style="color: #5F6368; font-size: 1.1rem;">
        Practice math concepts with AI-generated problems
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize the LLM model (keep your existing code)
# ...

# Google-style Sidebar
with st.sidebar:
    st.markdown("""
    <div class="google-card" style="padding: 16px;">
        <h3 style="margin-top: 0; color: #202124;">Settings</h3>
    """, unsafe_allow_html=True)
    
    difficulty = st.select_slider(
        "Difficulty Level",
        options=["Easy", "Medium", "Hard"],
        value="Medium"
    )
    
    st.markdown("""
    <hr style="border: none; border-top: 1px solid #DADCE0; margin: 16px 0;">
    <h3 style="color: #202124;">About</h3>
    <p style="color: #5F6368;">
        AI-generated math problems for 6th grade students.
    </p>
    </div>
    """, unsafe_allow_html=True)

# Main content area with Google styling
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="google-card">
            <h3 style="margin-top: 0; color: #202124;">Select Topic</h3>
        """, unsafe_allow_html=True)
        Math_topic = st.selectbox(
            "",
            ["LCM", "HCF", "Percentage", "Fractions", "Decimals", "Division", 
             "Multiples", "Long addition", "Long subtraction", "Long multiplication", "Long division"],
            key="math_topic_select",
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        if st.button("🔄 New Question", use_container_width=True):
            st.session_state.current_topic = None

# [Keep all your existing question generation and display logic]
# Just update the containers to use google-card class where appropriate

# For example, where you display the question:
st.markdown(f"""
<div class="google-card">
    <h3 style="margin-top: 0; color: #202124;">Question</h3>
    <p style="font-size: 1.1rem; color: #202124;">{st.session_state.response_dict["Question"]}</p>
</div>
""", unsafe_allow_html=True)

# [Rest of your existing code...]
