from langchain.chat_models import init_chat_model
import streamlit as st
import os
import json
import re

# Load external CSS
def load_css():
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found. Using default styles.")

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
<div style="padding: 20px;">
    <p style="color: #5F6368; font-size: 1.1rem;">
        Practice math concepts with AI-generated problems
    </p>
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
        with st.spinner(f"🧠 Generating {topic} question..."):
            st.session_state.llm_response = llm.invoke(messages)
            if hasattr(st.session_state.llm_response, 'content'):
                st.session_state.response_dict = clean_json_response(st.session_state.llm_response.content)
                st.session_state.current_topic = topic
            else:
                st.error("Invalid response format from LLM")
    except Exception as e:
        st.error(f"Error generating question: {str(e)}")

# Sidebar
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

# Main content
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

# Generate question when topic changes
if st.session_state.current_topic != Math_topic:
    generate_question(Math_topic)

# Display question if available
if st.session_state.get('response_dict') and st.session_state.current_topic == Math_topic:
    try:
        # Question display with error handling
        question_text = st.session_state.response_dict.get("Question", "No question available")
        st.markdown(f"""
        <div class="google-card">
            <h3 style="margin-top: 0; color: #202124;">Question</h3>
            <p style="font-size: 1.1rem; color: #202124;">{question_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Answer choices with error handling
        choices = st.session_state.response_dict.get("Choices", {})
        if len(choices) >= 4:
            options = [
                ("A", ' '.join(str(choices.get("A", "")).strip().split()),
                ("B", ' '.join(str(choices.get("B", "")).strip().split()),
                ("C", ' '.join(str(choices.get("C", "")).strip().split()),
                ("D", ' '.join(str(choices.get("D", "")).strip().split())
            ]
            
            choice_key = st.radio(
                "Select your answer:",
                options=[opt[0] for opt in options],
                format_func=lambda x: f"<span class='choice-label'>{x}:</span> {options[['A','B','C','D'].index(x)][1]}",
                horizontal=True,
                key="answer_radio"
            )
            
            if st.button("Submit Answer", type="primary", use_container_width=True):
                selected_answer = options[['A','B','C','D'].index(choice_key)][1]
                correct_answer_key = st.session_state.response_dict.get("Correct Answer", "")
                correct_answer_text = options[['A','B','C','D'].index(correct_answer_key)][1] if correct_answer_key in ['A','B','C','D'] else ""
                
                if choice_key == correct_answer_key:
                    st.balloons()
                    st.success("""
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 24px; margin-right: 10px;">✅</span>
                        <span style="font-weight: 600;">Correct! Excellent work!</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"""
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 24px; margin-right: 10px;">❌</span>
                        <span>Not quite right. The correct answer is <b>{correct_answer_key}: {correct_answer_text}</b></span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Explanation with error handling
                explanation = st.session_state.response_dict.get("Explanation", "No explanation available")
                with st.expander("📖 Detailed Explanation", expanded=True):
                    st.markdown(f"""
                    <div class="explanation-box">
                        <div style="display: flex; align-items: center; margin-bottom: 12px;">
                            <span class="header-icon">📚</span>
                            <h4 style="margin: 0;">Step-by-Step Solution</h4>
                        </div>
                        <p><b>Your answer:</b> <span class="{'correct-answer' if choice_key == correct_answer_key else 'incorrect-answer'}">{choice_key}: {selected_answer}</span></p>
                        <p><b>Correct answer:</b> {correct_answer_key}: {correct_answer_text}</p>
                        <div style="margin-top: 16px;">
                            {explanation.replace('\n', '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("Incomplete answer choices in response")
            
    except Exception as e:
        st.error(f"Error displaying question: {str(e)}")
        if 'llm_response' in st.session_state:
            st.write("Raw response:", st.session_state.llm_response.content)

# Footer
st.markdown("""
<div style="text-align: center; color: #5F6368; margin-top: 40px;">
    <p>Math Practice • AI-Powered Learning</p>
</div>
""", unsafe_allow_html=True)
