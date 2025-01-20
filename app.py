import streamlit as st
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
QUESTIONS_COUNT = int(os.getenv("QUESTIONS_COUNT"))

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return "No text found in resume"

def main():
    try:
        st.title("Interview Bot")

        # Initialize session state for error message and chat input disabled
        if 'show_error' not in st.session_state:
            st.session_state.show_error = False
        if 'input_submitted' not in st.session_state:
            st.session_state.input_submitted = False

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        error_placeholder = st.empty()
        # Display error message if show_error is True
        if st.session_state.show_error:
            error_placeholder.error("Please fill in all fields.")
            time.sleep(3)
            error_placeholder.empty()

        name = st.text_input("Name")
        description = st.text_input("Job Description")
        resume = st.file_uploader("Upload Your Resume", type=["pdf"])

        # Experience input
        col1, col2 = st.columns(2)
        with col1:
            experience_value = st.number_input("Experience", min_value=0, step=1)
        with col2:
            experience_unit = st.selectbox("Unit", ["Years", "Months"])

        if st.button("Submit"):
            if name and description and resume and experience_value:
                # Extract text from PDF
                pdf_text = extract_text_from_pdf(resume)

                # Enable chat input
                st.session_state.input_submitted = True
                # Reset error state
                st.session_state.show_error = False
                
                # Initial backend message
                initial_message = {
                    "role": "user",
                    "content": f"""
You are conducting an interview for the following candidate. Here is the candidate's information:
- **Name**: {name}
- **Job Description**: {description}
- **Experience**: {experience_value} {experience_unit}
- **Resume Text**: {pdf_text}

Please create {QUESTIONS_COUNT} interview questions tailored to the candidate's experience and the provided job description.
Make sure to send the questions one after the other following a conversational style.
Focus on assessing the candidate's skills, qualifications, and fit for the role.
"""
                }
                st.session_state.messages.append(initial_message)

                # Get response from OpenAI for the initial message
                stream_response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[initial_message],
                    stream=True
                )
                with st.chat_message("assistant"):
                    response = st.write_stream(stream_response)  # Display the analysis
                    st.session_state.messages.append({"role": "assistant", "content": response})

            else:
                # Set error state to True
                error_placeholder.error("Please fill in all fields.")
                time.sleep(3)
                error_placeholder.empty()

        else:
            # Display chat history excluding the initial prompt
            if st.session_state.messages:
                for msg in st.session_state.messages:
                    if msg["role"] == "user" and "You are conducting an interview" in msg["content"]:
                        continue  # Skip displaying the initial prompt
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

        # React to user input only if the form is submitted
        if st.session_state.input_submitted:
            if prompt := st.chat_input("Start typing..."):
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})
                assistant_question_count = sum(
                    1 for msg in st.session_state.messages 
                    if msg["role"] == "assistant"
                )

                if assistant_question_count >= QUESTIONS_COUNT:
                    # Generate overall analysis after the 10th question
                    analysis_prompt = {
                        "role": "user",
                        "content": f"""
Please review the interview questions below, the candidate's experience, and the job description provided. 
Give an overall analysis of the candidate's suitability for the role, including:
1. A rating for the candidate's expertise in the technology stack.
2. A conclusion on whether the candidate is a suitable fit for the job based on their responses.

The analysis should be concise, clear, and easy to understand. Also include a thank you note at the end.

**Job Description**: {description}
**Candidate's Experience**: {experience_value} {experience_unit}

Interview Questions:
""" + "".join(f"- {msg['content']}\n" for msg in st.session_state.messages if msg["role"] == "assistant")
                    }
                    st.session_state.messages.append(analysis_prompt)

                    # Display assistant response in chat message container
                    with st.chat_message("assistant"):
                        analysis_response = client.chat.completions.create(
                            model=OPENAI_MODEL,
                            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                            stream=True,
                        )
                        response = st.write_stream(analysis_response)
                        st.session_state.messages.append({"role": "assistant", "content": response})

                else:
                    with st.chat_message("assistant"):
                        stream = client.chat.completions.create(
                            model=OPENAI_MODEL,
                            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                            stream=True,
                        )
                        response = st.write_stream(stream)
                        st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        print(f"Error: {e}")
        st.error("An error occurred. Please try again later.")

if __name__ == "__main__":
    main()