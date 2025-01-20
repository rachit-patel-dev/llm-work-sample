# Interview Assistant Bot

## Overview

The **Interview Bot** is a Streamlit application that simulates a job interview by generating custom questions based on the candidate's profile. It leverages OpenAI's API to create an interactive chat experience, asking interview questions and providing an analysis based on the candidate's responses and job description.

## Features

- **Resume Parsing**: Extracts text from an uploaded PDF resume.
- **Customizable Interview**: Generates a set number of interview questions tailored to the candidate's experience and the job description.
- **Real-Time Chat**: Displays interview questions and responses in a conversational style, simulating a real-time interview.
- **Overall Analysis**: After the interview, the bot generates an overall analysis of the candidate’s suitability for the job, including ratings and a conclusion.

## Requirements

- Python 3.11
- Streamlit
- OpenAI Python Client
- python-dotenv
- PyPDF2

## Installation

1. Clone the repository or download the code.

2. Create a `.env` file in the project root directory and add your OpenAI API key.

3. Run the app locally:

    - Create and activate a virtual environment:

    ```bash
    python -m venv venv
    venv\Scripts\activate # On Windows
    source venv/bin/activate  # On macOS/Linux
    ```

    - Install the requirements

    ```bash
    pip install -r requirements.txt
    ```
    - Run the app:

    ```bash
    streamlit run app.py
    ```

4. Run the app using docker:

    ```bash
    docker build -t interview-bot-app .
    docker run -p 8501:8501 interview-bot-app
    ```
