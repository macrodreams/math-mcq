from langchain.chat_models import init_chat_model
import streamlit as st
import os
import json
import re

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stSelectbox, .stRadio > div {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
        border: none;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .question-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .correct-answer {
        color: #4CAF50;
        font-weight: bold;
    }
    .incorrect-answer {
        color: #f44336;
    }
    .explanation-box {
        background-color: #f1f8e9;
        border-left: 4px solid #4CAF50;
        padding: 15px;
        margin: 15px 0;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "llm_response" not in st.session_state:
    st.session_state.llm_response = None
if "response_dict" not in st.session_state:
    st.session_state.response_dict = None
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None

### Streamlit App ###
st.title("🧮 Math Mastery Practice")
st.markdown("Practice your math skills with AI-generated exercises!")

# Sidebar for settings and info
with st.sidebar:
    st.header("Settings")
    difficulty = st.select_slider(
        "Difficulty Level",
        options=["Easy", "Medium", "Hard"],
        value="Medium"
    )
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app generates math problems for 6th grade students.")
    st.markdown("Select a topic to get started!")

# Math topic selection in main area
col1, col2 = st.columns([3, 1])
with col1:
    Math_topic = st.selectbox(
        "Choose a Math topic:",
        ["LCM", "HCF", "Percentage", "Fractions", "Decimals", "Division", 
         "Multiples", "Long addition", "Long subtraction", "Long multiplication", "Long division"],
        key="math_topic_select"
    )

with col2:
    st.markdown("")  # Spacer
    if st.button("🔄 Regenerate"):
        st.session_state.current_topic = None  # Force regeneration

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

# (Keep all your existing functions: clean_json_response, generate_question)

# Generate question automatically when topic changes
if st.session_state.current_topic != Math_topic:
    generate_question(Math_topic)

# Show question and options if available
if st.session_state.response_dict and st.session_state.current_topic == Math_topic:
    with st.container():
        st.markdown("---")
        st.markdown(f"### 📝 {Math_topic} Question")
        
        # Question card
        with st.expander("View Question", expanded=True):
            st.markdown(f"""
            <div class="question-card">
                <h4>{st.session_state.response_dict["Question"]}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            options = [
                ("A", st.session_state.response_dict["Choices"]["A"]),
                ("B", st.session_state.response_dict["Choices"]["B"]),
                ("C", st.session_state.response_dict["Choices"]["C"]),
                ("D", st.session_state.response_dict["Choices"]["D"])
            ]
            
            # Create radio buttons with labels
            choice_key = st.radio(
                "Select your answer:",
                options=[opt[0] for opt in options],
                format_func=lambda x: f"{x}: {options[['A','B','C','D'].index(x)][1]}",
                horizontal=True
            )
            
            if st.button("Submit Answer", type="primary"):
                selected_answer = st.session_state.response_dict["Choices"][choice_key]
                correct_answer_key = st.session_state.response_dict["Correct Answer"]
                
                if choice_key == correct_answer_key:
                    st.balloons()
                    st.success("🎉 Correct! Well done!")
                else:
                    st.error(f"❌ Not quite right. Let's review the solution.")
                
                # Show explanation in a nicely formatted box
                with st.expander("See Explanation", expanded=True):
                    st.markdown(f"""
                    <div class="explanation-box">
                        <h4>📚 Explanation</h4>
                        <p><strong>Your answer:</strong> <span class="{'correct-answer' if choice_key == correct_answer_key else 'incorrect-answer'}">{selected_answer}</span></p>
                        <p><strong>Correct answer:</strong> {st.session_state.response_dict['Choices'][correct_answer_key]}</p>
                        <hr>
                        {st.session_state.response_dict["Explanation"].replace('\n', '<br>')}
                    </div>
                    """, unsafe_allow_html=True)

# Add a progress tracker at the bottom
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    st.markdown("""
    **Progress:**  
    🔵 Not started  
    🟡 In progress  
    🟢 Completed
    """)
