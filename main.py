from langchain.chat_models import chat_models
import streamlit as st
import os
import json
import re

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
st.header("Math Exercise")
st.subheader("Generate Math Exercise for practice 🤖")

# Math topic selection
Math_topic = st.selectbox(
    "Choose a Math topic for today's Exercise:",
    ["LCM", "HCF", "Percentage", "Fractions", "Decimals", "Division", 
     "Multiples", "Long addition", "Long subtraction", "Long multiplication", "Long division"],
    key="math_topic_select"
)

def generate_question(topic):
    """Generate a new question when the topic changes"""
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
         
         Example: {json.dumps(example, indent=2)}"""}
    ]
    
    try:
        with st.spinner(f"Generating {topic} question..."):
            st.session_state.llm_response = llm.invoke(messages)
            st.session_state.response_dict = clean_json_response(st.session_state.llm_response.content)
            st.session_state.current_topic = topic
            st.rerun()  # Refresh to show the new question
    except Exception as e:
        st.error(f"Error generating question: {str(e)}")

def clean_json_response(raw_json):
    """Clean and fix common JSON formatting issues in LLM responses"""
    try:
        # Remove code blocks and LaTeX markers
        cleaned = re.sub(r'```(json)?|```', '', raw_json)
        cleaned = re.sub(r'\\[a-zA-Z]+\{', '', cleaned)  # Remove LaTeX commands
        cleaned = cleaned.replace('\\', '\\\\')  # Escape backslashes
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON from malformed response
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        raise

# Initialize the LLM model
try:
    os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
except Exception as e:
    st.error(f"Failed to initialize LLM: {str(e)}")
    st.stop()

# Generate question automatically when topic changes
if st.session_state.current_topic != Math_topic:
    generate_question(Math_topic)

# Show question and options if available
if st.session_state.response_dict and st.session_state.current_topic == Math_topic:
    try:
        # Display the Question
        st.subheader("Question:")
        st.write(st.session_state.response_dict["Question"])
        
        options = [
            ("A", st.session_state.response_dict["Choices"]["A"]),
            ("B", st.session_state.response_dict["Choices"]["B"]),
            ("C", st.session_state.response_dict["Choices"]["C"]),
            ("D", st.session_state.response_dict["Choices"]["D"])
        ]
        
        # Create radio buttons with labels
        choice_key = st.radio(
            "Select an option:",
            options=[opt[0] for opt in options],
            format_func=lambda x: f"{x}: {options[['A','B','C','D'].index(x)][1]}"
        )
        
        if st.button("Submit Answer"):
            selected_answer = st.session_state.response_dict["Choices"][choice_key]
            st.write(f"✅ You selected: **{selected_answer}**")
            
            # Check if answer is correct
            correct_answer_key = st.session_state.response_dict["Correct Answer"]
            if choice_key == correct_answer_key:
                st.success("Correct! 🎉")
            else:
                st.error(f"Sorry, the correct answer is {correct_answer_key}: {st.session_state.response_dict['Choices'][correct_answer_key]}")
            
            # Show explanation
            st.subheader("Explanation:")
            st.write(st.session_state.response_dict["Explanation"])
            
    except KeyError as e:
        st.error(f"Invalid response format from LLM. Missing key: {str(e)}")
        st.write("Full response:", st.session_state.response_dict)
    except Exception as e:
        st.error(f"Error displaying question: {str(e)}")
