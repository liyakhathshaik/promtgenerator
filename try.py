#done using stremamlit...............................................


import streamlit as st
import google.generativeai as genai
import logging
import json
import os
from dotenv import load_dotenv,dotenv_values
load_dotenv()
# Initialize logging
logging.basicConfig(level=logging.INFO)

# Gemini API Key (replace "YOUR_API_KEY" with your actual key or load from environment variable)
 # Use os.environ.get("GEMINI_API_KEY") for secure storage

# Configure the Gemini client
try:
    genai.configure(api_key="AIzaSyDI_nBkIwy7OsZfuyKh6tUJZYHYwRa25tQ")
except Exception as e:
    logging.error(f"Failed to configure Gemini API: {e}")
    st.error("Failed to configure Gemini API. Please check your API key.")
    st.stop()

# Streamlit UI
st.title("Prompt Generator and Evaluator")

# Step 1: User enters a rough prompt for refinement
st.header("Refine Your Prompt")
user_input = st.text_area("Enter your rough prompt:", placeholder="E.g., I want to ask GPT about AI in education.")
mode = st.selectbox("How should the refined prompt be?", ["Creativity", "Technical", "Mix of Both"])

# Function to refine the prompt
def refine_prompt(user_input, mode):
    task_instructions = {
        "Creativity": (
            "You will act as an expert prompt creator to refine the following prompt into a creative, imaginative, and engaging version. "
            "Ensure the refined prompt captures the essence of the original input while inspiring engaging and imaginative responses.\n\n"
            "Input Prompt:\n{user_input}\n\nOutput:"
        ),
        "Technical": (
            "You will act as an expert prompt creator to refine the following prompt into a technical, precise, and factually accurate version. "
            "Ensure the refined prompt maintains logical structure, clarity, and correctness, tailored for technical queries.\n\n"
            "Input Prompt:\n{user_input}\n\nOutput:"
        ),
        "Mix of Both": (
            "You will act as an expert prompt creator to refine the following prompt, balancing creativity with technical precision. "
            "Ensure the refined prompt is both engaging and technically accurate, offering a perfect blend of imaginative and precise details.\n\n"
            "Input Prompt:\n{user_input}\n\nOutput:"
        )
    }

    if mode not in task_instructions:
        return "Invalid mode selected."

    instruction = task_instructions[mode].replace("{user_input}", user_input)
    try:
        # Use Gemini API to refine the prompt
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(instruction)
        return response.text
    except Exception as e:
        logging.error(f"API call failed: {e}")
        return f"Error refining prompt: {e}"

if st.button("Refine Prompt"):
    if user_input.strip():
        refined_prompt = refine_prompt(user_input, mode)
        st.text_area("Refined Prompt:", value=refined_prompt, height=150)
    else:
        st.warning("Please enter a rough prompt to refine.")

# Step 2: Evaluate the prompt with critique
st.header("Evaluate a Prompt")
prompt_to_evaluate = st.text_area("Enter the prompt for evaluation:")

# Function to evaluate prompts with critique
def evaluate_prompt(prompt_to_evaluate):
    instruction = (
        "You will act as an expert prompt evaluator. Evaluate the following prompt based on these criteria: "
        "1. Structure: Is the prompt logically organized? "
        "2. Clarity: Is the prompt precise and unambiguous? "
        "3. Words and Tone: Is the language appropriate for the audience and purpose? "
        "4. Effectiveness: Does the prompt achieve its intended goal?\n\n"
        "Prompt to Evaluate:\n{prompt_to_evaluate}\n\n*Critique:*\n{Provide detailed feedback with actionable suggestions for improvement.}"
    )

    instruction = instruction.replace("{prompt_to_evaluate}", prompt_to_evaluate)

    try:
        # Use Gemini API for evaluation
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(instruction)
        return response.text
    except Exception as e:
        logging.error(f"API call failed: {e}")
        return f"Error evaluating prompt: {e}"

if st.button("Evaluate Prompt"):
    if prompt_to_evaluate.strip():
        evaluation_result = evaluate_prompt(prompt_to_evaluate)
        st.text_area("Evaluation Result:", value=evaluation_result, height=250)
    else:
        st.warning("Please enter a prompt for evaluation.")

# Feedback Section
st.header("Feedback and Report")
issue_description = st.text_area("Describe the issue or provide feedback:")
user_email = st.text_input("Your email (optional):")

if st.button("Submit Feedback"):
    if issue_description.strip():
        feedback = {"description": issue_description, "email": user_email}
        with open("feedback_log.json", "a") as log_file:
            json.dump(feedback, log_file)
            log_file.write("\n")
        st.success("Feedback submitted successfully.")
    else:
        st.warning("Please provide a description for your feedback.")
