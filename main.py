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
        <h3 style="color: var(--macrodreams-primary);">Topics</h3>
    """, unsafe_allow_html=True)
    
    Math_topic = st.selectbox(
        "Choose a topic:",
        ["LCM", "HCF", "Percentage", "Fractions", "Decimals", "Division", 
         "Multiples", "Long addition", "Long subtraction", "Long multiplication", "Long division"],
        key="math_topic_select",
        label_visibility="collapsed"
    )
    
    st.markdown("""
    <hr style="border: none; border-top: 1px solid var(--macrodreams-border); margin: 16px 0;">
    <h3 style="color: var(--macrodreams-primary);">Difficulty</h3>
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

# Main content
st.markdown("""
<div class="macrodreams-container">
    <div class="macrodreams-card" style="border-radius: 0 0 12px 12px;">
        <h1 style="color: var(--macrodreams-primary); margin-bottom: 8px;">Math Practice</h1>
        <p style="color: var(--macrodreams-text);">Master math concepts with AI-generated problems</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize the LLM model
try:
    os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
    llm = init_chat_model(
        "ft:gpt-4o-mini-2024-07-18:personal:my-math-llm-26th-1st:BFD9gRWW", 
        model_provider="openai"
    )
except Exception as e:
    st.error(f"Failed to initialize LLM: {str(e)}")
    st.stop()

def clean_json_response(raw_json):
    """Clean and fix common JSON formatting issues in LLM responses"""
    try:
        cleaned = re.sub(r'```(json)?|```', '', raw_json)
        cleaned = re.sub(r'\\[a-zA-Z]+\{', '', cleaned)
        cleaned = cleaned.replace('\\', '\\\\')
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        st.error(f"Error parsing response: {str(e)}")
        return None

def generate_question(topic):
    """Generate a new question for the selected topic"""
    example = {
        "Question": "What is 10 + 5?",
        "Choices": {"A": "12", "B": "15", "C": "18", "D": "20"},
        "Correct Answer": "B",
        "Explanation": "Step 1: Add the numbers\n10 + 5 = 15\n\nFinal Answer: 15"
    }
    
    messages = [
        {"role": "system", "content": "You are an AI tutor generating multiple-choice math questions."},
        {"role": "user", "content": f"""Generate a math question about {topic} for 6th grade. 
         Requirements:
         1. Return valid JSON format (no code blocks, no LaTeX)
         2. Use ONLY plain text
         3. Explanation should use simple numbered steps
         4. Ensure choices are cleanly formatted without extra spaces
         
         Example: {json.dumps(example, indent=2)}"""}
    ]
    
    try:
        with st.spinner(f"Generating {topic} question..."):
            st.session_state.llm_response = llm.invoke(messages)
            if hasattr(st.session_state.llm_response, 'content'):
                st.session_state.response_dict = clean_json_response(st.session_state.llm_response.content)
                st.session_state.current_topic = topic
            else:
                st.error("Invalid response format from LLM")
    except Exception as e:
        st.error(f"Error generating question: {str(e)}")

# Generate question when topic changes
if st.session_state.current_topic != Math_topic:
    generate_question(Math_topic)

# Display question if available
if st.session_state.get('response_dict') and st.session_state.current_topic == Math_topic:
    try:
        with st.container():
            st.markdown(f"""
            <div class="macrodreams-card">
                <h3 class="macrodreams-header">Question</h3>
                <p style="font-size: 1.1rem;">{st.session_state.response_dict.get("Question", "No question available")}</p>
            </div>
            """, unsafe_allow_html=True)
            
            choices = st.session_state.response_dict.get("Choices", {})
            if len(choices) >= 4:
                options = [
                    ("A", ' '.join(str(choices.get("A", "")).strip().split())),
                    ("B", ' '.join(str(choices.get("B", "")).strip().split())),
                    ("C", ' '.join(str(choices.get("C", "")).strip().split())),
                    ("D", ' '.join(str(choices.get("D", "")).strip().split()))
                ]
                
                choice_key = st.radio(
                    "Select your answer:",
                    options=[opt[0] for opt in options],
                    format_func=lambda x: f"{x}: {' '.join(options[['A','B','C','D'].index(x)][1])}",
                    key="answer_choices"
                )
                
                if st.button("Submit Answer", type="primary", key="submit_answer"):
                    selected_answer = ' '.join(options[['A','B','C','D'].index(choice_key)][1])
                    correct_answer_key = st.session_state.response_dict.get("Correct Answer", "")
                    correct_answer_text = ' '.join(options[['A','B','C','D'].index(correct_answer_key)][1]) if correct_answer_key in ['A','B','C','D'] else ""
                    
                    if choice_key == correct_answer_key:
                        st.balloons()
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 8px; color: #10b981;">
                            <span style="font-size: 1.2rem;">✅</span>
                            <span>Correct! The answer is <b>{correct_answer_key}: {correct_answer_text}</b></span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 8px; color: #ef4444;">
                            <span style="font-size: 1.2rem;">❌</span>
                            <span>Incorrect. The correct answer is <b>{correct_answer_key}: {correct_answer_text}</b></span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with st.expander("Explanation", expanded=True):
                        st.markdown(f"""
                        <div class="macrodreams-explanation">
                            <h4 class="macrodreams-header">Solution</h4>
                            <p><b>Your answer:</b> <span class="{'macrodreams-correct' if choice_key == correct_answer_key else 'macrodreams-incorrect'}">{choice_key}: {selected_answer}</span></p>
                            <p><b>Correct answer:</b> {correct_answer_key}: {correct_answer_text}</p>
                            <div style="margin-top: 16px;">
                                {st.session_state.response_dict.get("Explanation", "").replace('\n', '<br>')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("Incomplete answer choices in response")
                
    except Exception as e:
        st.error(f"Error displaying question: {str(e)}")

# Footer
st.markdown("""
<div class="macrodreams-container">
    <div class="macrodreams-card" style="text-align: center; padding: 16px; border-radius: 12px 12px 0 0;">
        <p style="color: var(--macrodreams-text);">Math Practice • Powered by AI</p>
    </div>
</div>
""", unsafe_allow_html=True)
