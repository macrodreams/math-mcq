from langchain.chat_models import ChatOpenAI  # Updated import
import streamlit as st
import os
import json
import re

# Initialize session state variables
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
     "Multiples", "Long addition", "Long subtraction", "Long multiplication", "Long division"]
)

# Initialize the LLM model
try:
    os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
    # Using standard OpenAI model instead of custom model
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
except Exception as e:
    st.error(f"Failed to initialize LLM: {str(e)}")
    st.stop()

def format_explanation(explanation):
    """Format the explanation text with proper line breaks and markdown"""
    if not explanation:
        return ""
    # Replace numbered steps with markdown headers
    explanation = re.sub(r'\nStep (\d+):', r'\n### Step \1:', explanation)
    # Replace bullet points with markdown bullets
    explanation = explanation.replace('\n- ', '\n- ')
    # Ensure proper line breaks
    explanation = explanation.replace('\n', '  \n')  # Markdown line breaks
    return explanation

def clean_json_response(raw_json):
    """Clean and fix common JSON formatting issues in LLM responses"""
    if not raw_json:
        return {}
    try:
        # Remove code blocks and LaTeX markers
        cleaned = re.sub(r'```(json)?|```', '', raw_json)
        cleaned = re.sub(r'\\[a-zA-Z]+\{', '', cleaned)  # Remove LaTeX commands
        cleaned = cleaned.replace('\\', '\\\\')  # Escape backslashes
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {str(e)}")
        # Try to extract JSON from malformed response
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return {}

# Generate question when button is clicked
if st.button(f"Generate {Math_topic} Math Problem"):
    example = {
        "Question": "What is 144 ÷ 12?",
        "Choices": {"A": "10", "B": "11", "C": "12", "D": "13"},
        "Correct Answer": "C",
        "Explanation": """### Step 1: Identify the given numbers
- Dividend: 144
- Divisor: 12

### Step 2: Set up the long division
 12 | 144

### Step 3: Divide the first digit
- 12 goes into 14 one time
- Write 1 above the 4 in the quotient
- Multiply 1 × 12 = 12
- Subtract: 14 - 12 = 2

### Step 4: Bring down the next digit (4)
- Now we have 24
- 12 goes into 24 two times
- Write 2 above the 4 in the quotient
- Multiply 2 × 12 = 24
- Subtract: 24 - 24 = 0

Final Answer: 12"""
    }
    
    messages = [
        {"role": "system", "content": "You are an AI tutor generating multiple-choice math questions."},
        {"role": "user", "content": f"""Generate a math question about {Math_topic} for 6th grade. 
         Requirements:
         1. Return valid JSON format (no code blocks, no LaTeX)
         2. Use ONLY plain text
         3. Explanation should use clear markdown formatting
         
         Example: {json.dumps(example, indent=2)}"""}
    ]
    
    try:
        with st.spinner("Generating question..."):
            st.session_state.llm_response = llm.invoke(messages)
            
            if hasattr(st.session_state.llm_response, 'content'):
                # Clean and parse the response
                st.session_state.response_dict = clean_json_response(st.session_state.llm_response.content)
                
                if st.session_state.response_dict:
                    # Display the Question
                    st.subheader("Question:")
                    st.write(st.session_state.response_dict.get("Question", ""))
                else:
                    st.error("Failed to parse response. Showing raw response:")
                    st.text_area("Raw Response", st.session_state.llm_response.content, height=200)
            else:
                st.error("Invalid response format from LLM")
                
    except Exception as e:
        st.error(f"Error generating question: {str(e)}")
        if 'llm_response' in st.session_state and hasattr(st.session_state.llm_response, 'content'):
            st.text_area("Error Details - Raw Response", st.session_state.llm_response.content, height=200)

# Show options if we have a question
if st.session_state.get('response_dict'):
    try:
        choices = st.session_state.response_dict.get("Choices", {})
        if len(choices) >= 4:  # Ensure we have all 4 choices
            options = [
                ("A", choices.get("A", "")),
                ("B", choices.get("B", "")),
                ("C", choices.get("C", "")),
                ("D", choices.get("D", ""))
            ]
            
            # Create radio buttons with labels
            choice_key = st.radio(
                "Select an option:",
                options=[opt[0] for opt in options],
                format_func=lambda x: f"{x}: {options[['A','B','C','D'].index(x)][1]}"
            )
            
            if st.button("Submit Answer"):
                selected_answer = choices.get(choice_key, "")
                st.write(f"✅ You selected: **{selected_answer}**")
                
                # Check if answer is correct
                correct_answer_key = st.session_state.response_dict.get("Correct Answer", "")
                if choice_key == correct_answer_key:
                    st.success("Correct! 🎉")
                else:
                    st.error(f"Sorry, the correct answer is {correct_answer_key}: {choices.get(correct_answer_key, '')}")
                
                # Show explanation with proper formatting
                st.subheader("Explanation:")
                formatted_explanation = format_explanation(st.session_state.response_dict.get("Explanation", ""))
                st.markdown(formatted_explanation)
        else:
            st.error("Incomplete choices in response")
            
    except Exception as e:
        st.error(f"Error displaying question: {str(e)}")
