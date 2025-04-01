from langchain.chat_models import init_chat_model
import streamlit as st
import os
import json
import re

# DeepSeek-inspired CSS styling
def load_deepseek_styles():
    st.markdown("""
    <style>
        :root {
            --macrodreams-primary: #2563eb;
            --macrodreams-primary-light: #3b82f6;
            --macrodreams-primary-dark: #1d4ed8;
            --macrodreams-secondary: #f8fafc;
            --macrodreams-card: #ffffff;
            --macrodreams-text: #1e293b;
            --macrodreams-border: #e2e8f0;
            --macrodreams-sidebar: #f1f5f9;
        }
        
        .macrodreams-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 0;
        }
        
        .macrodreams-card {
            background-color: var(--macrodreams-card);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid var(--macrodreams-border);
        }
        
        .macrodreams-button {
            background-color: var(--macrodreams-primary);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .macrodreams-button:hover {
            background-color: var(--macrodreams-primary-dark);
        }
        
        .macrodreams-newchat {
            width: 100%;
            margin-bottom: 16px;
            background-color: var(--macrodreams-primary);
        }
        
        .macrodreams-radio {
            margin: 12px 0;
        }
        
        .macrodreams-correct {
            color: #10b981;
            font-weight: 500;
        }
        
        .macrodreams-incorrect {
            color: #ef4444;
        }
        
        .macrodreams-header {
            color: var(--macrodreams-primary);
            margin-bottom: 12px;
        }
        
        .macrodreams-sidebar {
            background-color: var(--macrodreams-sidebar);
            padding: 16px;
            height: 100vh;
        }
        
        .macrodreams-explanation {
            background-color: #f0f9ff;
            border-left: 4px solid var(--macrodreams-primary);
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 12px 12px 0;
        }
        
        [data-testid="stSidebar"] {
            background-color: var(--macrodreams-sidebar) !important;
        }
        
        .macrodreams-selectbox {
            margin-top: 8px;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)

load_deepseek_styles()

# Initialize session state
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "llm_response" not in st.session_state:
    st.session_state.llm_response = None
if "response_dict" not in st.session_state:
    st.session_state.response_dict = None
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None

# Sidebar with DeepSeek styling
with st.sidebar:
    st.markdown("""
    <div class="macrodreams-sidebar">
        <div style="margin-bottom: 24px;">
            <button class="macrodreams-button macrodreams-newchat" onclick="window.location.reload()">
                <span>+</span> New Question
            </button>
        </div>
        <h3 style="color: var(--macrodreams-primary); margin-bottom: 8px;">Topics</h3>
    """, unsafe_allow_html=True)
    
    # Topic selectbox under Topics heading
    Math_topic = st.selectbox(
        "Choose a topic:",
        ["LCM", "HCF", "Percentage", "Fractions", "Decimals", "Division", 
         "Multiples", "Long addition", "Long subtraction", "Long multiplication", "Long division"],
        key="math_topic_select",
        label_visibility="collapsed"
    )
    
    st.markdown("""
    <hr style="border: none; border-top: 1px solid var(--macrodreams-border); margin: 16px 0;">
    <h3 style="color: var(--macrodreams-primary); margin-bottom: 8px;">Difficulty</h3>
    """, unsafe_allow_html=True)
    
    difficulty = st.select_slider(
        "",
        options=["Easy", "Medium", "Hard"],
        value="Medium",
        label_visibility="collapsed"
    )
    
    st.markdown("""
    <hr style="border: none; border-top: 1px solid var(--macrodreams-border); margin: 16px 0;">
    <p style="color: var(--macrodreams-text);">
        AI math tutor for 6th grade students. Select a topic to begin.
    </p>
    </div>
    """, unsafe_allow_html=True)

# Rest of your code remains the same...
# [Keep all the remaining code exactly as it was, including the main content area]
