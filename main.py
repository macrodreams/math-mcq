from langchain.chat_models import init_chat_model
import streamlit as st
import os
import json

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
    [
        "LCM", "HCF", "Percentage", "Fractions", "Decimals", "Division",
        "Multiples", "Long addition", "Long subtraction", "Long multiplication", "Long division"
    ]
)

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

# Generate question when button is clicked
if st.button(f"Generate {Math_topic} Math Problem"):
    messages = [
        {
            "role": "system",
            "content": "You are an AI tutor generating multiple-choice math questions with step-by-step explanations."
        },
        {
            "role": "user",
            "content": f"Generate a math question involving {Math_topic} for 6th grade with Challenge level moderate. "
                       f"Return the response in JSON format with these keys: Question, Choices (with A, B, C, D), "
                       f"Correct Answer, and Explanation."
        }
    ]

    try:
        response = llm.invoke(messages)
        response_content = response.get("content", "")

        if response_content:
            # Ensure proper JSON formatting
            response_content = response_content.replace("\\", "\\\\")  # Escape backslashes if any
            st.session_state.response_dict = json.loads(response_content)

            # Display the Question
            st.subheader("Question:")
            st.write(st.session_state.response_dict["Question"])

    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON format from LLM: {str(e)}")
    except Exception as e:
        st.error(f"Error generating question: {str(e)}")

# Show options if we have a question
if st.session_state.response_dict:
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
        format_func=lambda x: f"{x}: {options[['A', 'B', 'C', 'D'].index(x)][1]}"
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
