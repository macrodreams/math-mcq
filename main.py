import streamlit as st
from langchain.chat_models import init_chat_model
import os
import json
import re

# Corrected FontAwesome CSS link
fa_css = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
"""
st.markdown(fa_css, unsafe_allow_html=True)

# Define icons for each topic using FontAwesome
topic_icons = {
    "LCM": "<i class='fas fa-link'></i>",
    "HCF": "<i class='fas fa-link'></i>",
    "Percentage": "<i class='fas fa-percentage'></i>",
    "Fractions": "<i class='fas fa-fraction'></i>",
    "Decimals": "<i class='fas fa-hashtag'></i>",
    "Division": "<i class='fas fa-divide'></i>",
    "Multiples": "<i class='fas fa-times'></i>",
    "Long addition": "<i class='fas fa-plus'></i>",
    "Long subtraction": "<i class='fas fa-minus'></i>",
    "Long multiplication": "<i class='fas fa-times'></i>",
    "Long division": "<i class='fas fa-divide'></i>"
}

# DeepSeek-inspired CSS styling
st.markdown("""
<style>
    :root {
        --deepseek-blue: #2563eb;
        --deepseek-light-blue: #3b82f6;
        --deepseek-dark-blue: #1d4ed8;
        --deepseek-bg: #f8fafc;
        --deepseek-card: #ffffff;
    }
    .main {
        background-color: var(--deepseek-bg);
    }
    .stSelectbox, .stRadio > div {
        background-color: var(--deepseek-card);
        border-radius: 12px;
        padding: 12px;
        border: 1px solid #e2e8f0;
    }
    .stButton button {
        background-color: var(--deepseek-blue);
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton button:hover {
        background-color: var(--deepseek-dark-blue);
        transform: translateY(-1px);
    }
    .question-card {
        background-color: var(--deepseek-card);
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .correct-answer {
        color: #10b981;
        font-weight: 600;
    }
    .incorrect-answer {
        color: #ef4444;
    }
    .explanation-box {
        background-color: #f0f9ff;
        border-left: 4px solid var(--deepseek-blue);
        padding: 20px;
        margin: 20px 0;
        border-radius: 0 12px 12px 0;
    }
    .header-icon {
        font-size: 24px;
        margin-right: 10px;
        vertical-align: middle;
    }
    .topic-select {
        background-color: var(--deepseek-card);
        border-radius: 12px;
        padding: 16px;
    }
    .choice-label {
        font-weight: 500;
        margin-right: 8px;
    }
    .stSelectbox {
        width: 100%;
    }
    .answer-button {
        background-color: var(--deepseek-light-blue);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        margin: 5px;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .answer-button:hover {
        background-color: var(--deepseek-blue);
    }
    .correct-answer-button {
        background-color: #10b981;
    }
    .incorrect-answer-button {
        background-color: #ef4444;
    }
</style>
""", unsafe_allow_html=True)

# App Header with custom logo
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 20px;">
    <h1 style="margin: 0;"><span class="header-icon"><i class="fas fa-calculator"></i></span> Math Genius</h1>
</div>
<p style="color: #64748b; font-size: 1.1rem;">
    Master math concepts with AI-powered practice problems
</p>
""", unsafe_allow_html=True)

# Initialize session state
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "llm_response" not in st.session_state:
    st.session_state.llm_response = None
if "response_dict" not in st.session_state:
    st.session_state.response_dict = None
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None

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
        data = json.loads(cleaned)
        
        # Validate the JSON structure
        required_keys = ["Question", "Choices", "Correct Answer", "Explanation"]
        if not all(key in data for key in required_keys):
            raise ValueError("Invalid JSON structure")
        
        return data
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {str(e)}")
        return None
    except ValueError as e:
        st.error(f"Error validating JSON: {str(e)}")
        return None

def generate_question(topic, difficulty):
    """Generate a new question for the selected topic and difficulty"""
    example = {
        "Question": "What is the LCM of 8 and 12?",
        "Choices": {"A": "12", "B": "24", "C": "36", "D": "48"},
        "Correct Answer": "B",
        "Explanation": "Step 1: Identify the given numbers (8 and 12)\nStep 2: Find the multiples of each number\nMultiples of 8: 8, 16, 24, 32, ...\nMultiples of 12: 12, 24, 36, ...\nStep 3: Identify the smallest common multiple\nThe smallest common multiple is 24\n\n\nFinal Answer: 24"
    }
    
    messages = [
        {"role": "system", "content": "You are an AI tutor generating multiple-choice math questions."},
        {"role": "user", "content": f"""Generate a {difficulty.lower()} math question about {topic} for 6th grade. 
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
            response = clean_json_response(st.session_state.llm_response.content)
            
            if response:
                st.session_state.response_dict = response
                st.session_state.current_topic = topic
            else:
                st.error("Failed to generate a valid question. Please try again.")
    except Exception as e:
        st.error(f"Error generating question: {str(e)}")

# Sidebar with DeepSeek styling
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <h2 style="margin: 0;"><span class="header-icon"><i class="fas fa-cog"></i></span> Settings</h2>
    </div>
    """", unsafe_allow_html=True)
    
    difficulty = st.select_slider(
        "Difficulty Level",
        options=["Easy", "Medium", "Hard"],
        value="Medium",
        help="Adjust the difficulty of generated questions"
    )
    
    st.markdown("---")
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <h3 style="margin: 0;"><span class="header-icon"><i class="fas fa-info-circle"></i></span> About</h3>
    </div>
    <p style="color: #64748b;">
        This AI tutor generates math problems for 6th grade students. 
        Select a topic to begin your practice session.
    </p>
    """", unsafe_allow_html=True)

# Main content area
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="topic-select">
            <h3 style="margin-top: 0;"><span class="header-icon"><i class="fas fa-book"></i></span> Select Topic</h3>
        </div>
        """", unsafe_allow_html=True)
        Math_topic = st.selectbox(
            "",
            ["LCM", "HCF", "Percentage", "Fractions", "Decimals", "Division", 
             "Multiples", "Long addition", "Long subtraction", "Long multiplication", "Long division"],
            key="math_topic_select",
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

# Generate question when topic changes
if st.session_state.current_topic != Math_topic:
    generate_question(Math_topic, difficulty)

# Display question if available
if st.session_state.response_dict and st.session_state.current_topic == Math_topic:
    with st.container():
        st.markdown("---")
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <h2 style="margin: 0;"><span class="header-icon">{topic_icons[Math_topic]}</span> {Math_topic} Practice</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Question card
        st.markdown(f"""
        <div class="question-card">
            <div style="display: flex; align-items: center; margin-bottom: 16px;">
                <span class="header-icon"><i class="fas fa-question"></i></span>
                <h3 style="margin: 0;">Question</h3>
            </div>
            <p style="font-size: 1.5rem; line-height: 1.6; font-weight: bold;">{st.session_state.response_dict["Question"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Clean and format answer choices
        raw_choices = st.session_state.response_dict["Choices"]
        options = [
            ("A", ' '.join(str(raw_choices["A"]).strip().split())),
            ("B", ' '.join(str(raw_choices["B"]).strip().split())),
            ("C", ' '.join(str(raw_choices["C"]).strip().split())),
            ("D", ' '.join(str(raw_choices["D"]).strip().split()))
        ]
        
        # Display clean answer buttons
        selected_answer = None
        for option in options:
            button = st.button(option[1], key=option[0], on_click=lambda: setattr(st.session_state, 'selected_answer', option[0]))
            button.add_style("answer-button")
        
        if selected_answer:
            correct_answer_key = st.session_state.response_dict["Correct Answer"]
            correct_answer_text = options[['A','B','C','D'].index(correct_answer_key)][1]
            
            if selected_answer == correct_answer_key:
                st.balloons()
                st.success("Correct! Excellent work!")
            else:
                st.error(f"Not quite right. The correct answer is {correct_answer_key}: {correct_answer_text}")
            
            # Explanation
            with st.expander("📖 Detailed Explanation", expanded=True):
                st.markdown(f"""
                <div class="explanation-box">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <span class="header-icon"><i class="fas fa-book-open"></i></span>
                        <h4 style="margin: 0;">Step-by-Step Solution</h4>
                    </div>
                    <p><b>Your answer:</b> <span class="{'correct-answer' if selected_answer == correct_answer_key else 'incorrect-answer'}">{selected_answer}: {options[['A','B','C','D'].index(selected_answer)][1]}</span></p>
                    <p><b>Correct answer:</b> {correct_answer_key}: {correct_answer_text}</p>
                    <div style="margin-top: 16px;">
                        {st.session_state.response_dict["Explanation"].replace('\n', '<br>')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; margin-top: 40px;">
    <p>Math Genius • AI-Powered Learning</p>
</div>
"""", unsafe_allow_html=True)
