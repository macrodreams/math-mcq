from langchain.chat_models import init_chat_model
import streamlit as st
import os
import json
import re

# Initialize session state variables
if "llm_response" not in st.session_state:
    st.session_state.llm_response = None
if "response_dict" not in st.session_state:
    st.session_state.response_dict = None

### Streamlit App ###
st.header("Math Exercise")
st.subheader("Generate Math Exercise for practice 🤖")

# Math topic selection
Math_topic = st.selectbox(
    "Choose a Math topic:",
    ["Addition", "Subtraction", "Multiplication", "Division", "Percentage"]
)

# Initialize LLM
try:
    os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
    llm = init_chat_model("your-model-here", model_provider="openai")
except Exception as e:
    st.error(f"Failed to initialize LLM: {str(e)}")
    st.stop()

def clean_and_parse_response(raw_response):
    """Clean and parse the LLM response to handle special characters"""
    try:
        # Remove code blocks and problematic characters
        cleaned = raw_response.replace('```', '').replace('\n', '\\n')
        # Escape special characters
        cleaned = json.dumps(cleaned)  # First convert to string
        cleaned = json.loads(cleaned)  # Then parse back
        # Now parse the actual JSON content
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: extract JSON portion
        match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group().replace('\n', '\\n'))
            except:
                pass
        raise

if st.button(f"Generate {Math_topic} Problem"):
    example = {
        "Question": "What is 15 + 27?",
        "Choices": {"A": "32", "B": "42", "C": "52", "D": "62"},
        "Correct Answer": "B",
        "Explanation": "Step 1: Add 5 + 7 = 12\\nStep 2: Add 10 + 20 = 30\\nStep 3: 30 + 12 = 42"
    }
    
    messages = [
        {
            "role": "system", 
            "content": "You are a math tutor. Generate questions with:"
                       "\n1. Clean JSON format (no code blocks)"
                       "\n2. Simple text explanations (no complex formatting)"
                       "\n3. Properly escaped special characters"
        },
        {
            "role": "user",
            "content": f"Generate a {Math_topic} question for 6th grade. Use this exact format:\n{json.dumps(example, indent=2)}"
        }
    ]
    
    try:
        response = llm.invoke(messages)
        st.session_state.response_dict = clean_and_parse_response(response.content)
        
        # Display question
        st.subheader("Question:")
        st.write(st.session_state.response_dict["Question"])
        
        # Display choices
        st.write("Options:")
        for key, value in st.session_state.response_dict["Choices"].items():
            st.write(f"{key}: {value}")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.text_area("Raw Response", response.content, height=200)

# Answer checking
if st.session_state.get("response_dict"):
    user_answer = st.radio("Select your answer:", 
                         options=list(st.session_state.response_dict["Choices"].keys()))
    
    if st.button("Check Answer"):
        correct = st.session_state.response_dict["Correct Answer"]
        if user_answer == correct:
            st.success("Correct! 🎉")
        else:
            st.error(f"Incorrect. The right answer is {correct}")
        
        st.subheader("Explanation:")
        st.write(st.session_state.response_dict["Explanation"].replace('\\n', '\n'))
