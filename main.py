from langchain.chat_models import init_chat_model
import streamlit as st
import os
import json
import re

# OpenAI-inspired CSS styling
def load_ai_styles():
    st.markdown("""
    <style>
        :root {
            --ai-primary: #10a37f;
            --ai-primary-dark: #0d8b6b;
            --ai-secondary: #f5f5f5;
            --ai-card-bg: #ffffff;
            --ai-text: #333333;
            --ai-border: #e0e0e0;
        }
        
        .ai-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .ai-card {
            background-color: var(--ai-card-bg);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid var(--ai-border);
        }
        
        .ai-button {
            background-color: var(--ai-primary);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .ai-button:hover {
            background-color: var(--ai-primary-dark);
        }
        
        .ai-radio {
            margin: 8px 0;
        }
        
        .ai-correct {
            color: var(--ai-primary);
            font-weight: 500;
        }
        
        .ai-incorrect {
            color: #ef4444;
        }
        
        .ai-header {
            color: var(--ai-primary);
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

load_ai_styles()

# Initialize session state
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "llm_response" not in st.session_state:
    st.session_state.llm_response = None
if "response_dict" not in st.session_state:
    st.session_state.response_dict = None
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None

# App Header
st.markdown("""
<div class="ai-container">
    <div class="ai-card">
        <h1 style="color: var(--ai-primary);">Math Practice</h1>
        <p style="color: var(--ai-text);">AI-powered math problem generator</p>
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

# Main content
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="ai-card">
            <h3 class="ai-header">Select Topic</h3>
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
        if st.button("🔄 New Question", use_container_width=True, key="ai_new_question"):
            st.session_state.current_topic = None

# Generate question when topic changes
if st.session_state.current_topic != Math_topic:
    generate_question(Math_topic)

# Display question if available
if st.session_state.get('response_dict') and st.session_state.current_topic == Math_topic:
    try:
        with st.container():
            st.markdown(f"""
            <div class="ai-card">
                <h3 class="ai-header">Question</h3>
                <p>{st.session_state.response_dict.get("Question", "No question available")}</p>
            </div>
            """, unsafe_allow_html=True)
            
            choices = st.session_state.response_dict.get("Choices", {})
            if len(choices) >= 4:
                # Create properly formatted options list
                options = [
                    ("A", ' '.join(str(choices.get("A", "")).strip().split())),
                    ("B", ' '.join(str(choices.get("B", "")).strip().split())),
                    ("C", ' '.join(str(choices.get("C", "")).strip().split())),
                    ("D", ' '.join(str(choices.get("D", "")).strip().split()))
                ]
                
                # Display radio buttons
                choice_key = st.radio(
                    "Select your answer:",
                    options=[opt[0] for opt in options],
                    format_func=lambda x: f"{x}: {options[['A','B','C','D'].index(x)][1]}",
                    key="ai_answer_choices"
                )
                
                if st.button("Submit Answer", type="primary", key="ai_submit"):
                    selected_answer = options[['A','B','C','D'].index(choice_key)][1]
                    correct_answer_key = st.session_state.response_dict.get("Correct Answer", "")
                    correct_answer_text = options[['A','B','C','D'].index(correct_answer_key)][1] if correct_answer_key in ['A','B','C','D'] else ""
                    
                    if choice_key == correct_answer_key:
                        st.balloons()
                        st.success(f"✅ Correct! The answer is {correct_answer_key}: {correct_answer_text}")
                    else:
                        st.error(f"❌ Incorrect. The correct answer is {correct_answer_key}: {correct_answer_text}")
                    
                    with st.expander("Explanation", expanded=True):
                        st.markdown(f"""
                        <div class="ai-card">
                            <h4 class="ai-header">Solution</h4>
                            <p><b>Your answer:</b> <span class="{'ai-correct' if choice_key == correct_answer_key else 'ai-incorrect'}">{choice_key}: {selected_answer}</span></p>
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
<div class="ai-container">
    <div class="ai-card" style="text-align: center; padding: 16px;">
        <p style="color: var(--ai-text);">Math Practice • Powered by AI</p>
    </div>
</div>
""", unsafe_allow_html=True)
