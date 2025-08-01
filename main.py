import streamlit as st
import google.generativeai as genai
import logging
import json
import requests

# Configure Google Gemini API Key
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    logging.error(f"Failed to configure Gemini API: {e}")
    raise e

# Initialize session state
def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    if 'tags' not in st.session_state:
        st.session_state.tags = []
    if 'output' not in st.session_state:
        st.session_state.output = ""
    if 'evaluation' not in st.session_state:
        st.session_state.evaluation = ""

init_session_state()

# Navigation
def navigation():
    pages = {
        "Home": "🏠",
        "Learn": "📚",
        "About": "ℹ️",
        "Feedback": "📝",
        "Techniques": "🧠"
    }
    
    st.sidebar.title("Prompt Generator")
    st.session_state.page = st.sidebar.radio("Navigate to:", list(pages.keys()), 
                                            format_func=lambda x: f"{pages[x]} {x}")

# Custom CSS for styling
st.markdown("""
<style>
    /* General Styles */
    body {
        font-family: 'Poppins', Arial, sans-serif;
        background: #1a1a1a;
        color: #e0e0e0;
    }
    
    .stApp {
        background: #1a1a1a;
        color: #e0e0e0;
    }
    
    /* Container Styles */
    .custom-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    /* Button Styles */
    .stButton>button {
        background: #3498db !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        transition: background 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background: #2980b9 !important;
    }
    
    /* Input Styles */
    .stTextArea>div>div>textarea, 
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #e0e0e0 !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
    }
    
    /* Tag Styles */
    .tag {
        display: inline-block;
        background: #3498db;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 5px;
        font-size: 14px;
    }
    
    /* Output Styles */
    .output-box {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        white-space: pre-wrap;
        color: #e0e0e0;
        position: relative;
    }
    
    h1, h2, h3 {
        color: #3498db !important;
    }
</style>
""", unsafe_allow_html=True)

# Home Page
def home_page():
    st.title("Generate Your Prompt")
    
    with st.container():
        st.subheader("Input Prompt")
        prompt = st.text_area("Enter your prompt here...", height=150, key="input_prompt")
        
        col1, col2 = st.columns(2)
        with col1:
            word_limit = st.selectbox("Word Limit", 
                                     ["Short (300-500 words)", "Medium (800-1000 words)", "Long (1500-2000 words)"],
                                     index=1)
        
        with col2:
            model = st.selectbox("Target Model", ["ChatGPT", "Gemini", "Custom"])
            if model == "Custom":
                custom_model = st.text_input("Custom Model Name")
            else:
                custom_model = ""
        
        tag_input = st.text_input("Add a tag (e.g., technical)")
        if st.button("Add Tag") and tag_input:
            if tag_input not in st.session_state.tags:
                st.session_state.tags.append(tag_input)
        
        if st.session_state.tags:
            st.write("Tags:")
            for tag in st.session_state.tags:
                st.markdown(f'<span class="tag">{tag}</span>', unsafe_allow_html=True)
            if st.button("Clear Tags"):
                st.session_state.tags = []
        
        if st.button("Generate Optimized Prompt"):
            if not prompt.strip():
                st.error("Prompt cannot be empty")
            else:
                with st.spinner("Generating prompt..."):
                    try:
                        # Map word limit selection
                        word_map = {
                            "Short (300-500 words)": "300-500 words",
                            "Medium (800-1000 words)": "800-1000 words",
                            "Long (1500-2000 words)": "1500-2000 words"
                        }
                        word_limit_context = word_map.get(word_limit, "800-1000 words")
                        
                        # Build instruction
                        instruction = (
                            f"You are a professional prompt generator. Your task is to take the following user input and transform it into a "
                            f"high-quality, optimized prompt for the target AI model '{model if model != 'Custom' else custom_model}'. "
                            f"Follow these guidelines:\n\n"
                            f"1. **Objective**: Clearly define the purpose of the prompt\n"
                            f"2. **Structure**: Break the prompt into logical sections\n"
                            f"3. **Specificity**: Include specific details or examples\n"
                            f"4. **Tone**: Use a professional and engaging tone\n"
                            f"5. **Word Count**: Ensure the prompt adheres to: {word_limit_context}\n\n"
                            f"**Tags**: {', '.join(st.session_state.tags) if st.session_state.tags else 'None'}\n\n"
                            f"**User Input**:\n{prompt}\n\n"
                            f"**Optimized Prompt**:"
                        )
                        
                        # Call Gemini AI
                        model_api = genai.GenerativeModel("gemini-1.5-flash")
                        response = model_api.generate_content(instruction)
                        
                        # Clean up output
                        cleaned_output = response.text.replace("*", "").strip()
                        st.session_state.output = cleaned_output
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.session_state.output:
            st.subheader("Generated Prompt")
            st.markdown(f'<div class="output-box">{st.session_state.output}</div>', unsafe_allow_html=True)
            
            if st.button("Copy to Clipboard"):
                st.session_state.copied = True
                st.experimental_set_query_params(copy=st.session_state.output)
                st.success("Copied to clipboard!")
        
        st.divider()
        st.subheader("Evaluate Your Prompt")
        
        if st.button("Evaluate Prompt"):
            if not prompt.strip():
                st.error("Prompt cannot be empty")
            else:
                with st.spinner("Evaluating prompt..."):
                    try:
                        # Build instruction
                        instruction = (
                            f"You are a professional prompt evaluator. Analyze this prompt:\n\n"
                            f"**User Input**:\n{prompt}\n\n"
                            f"Focus on:\n"
                            f"1. **Clarity**: Is the prompt clear?\n"
                            f"2. **Specificity**: Enough details?\n"
                            f"3. **Structure**: Logical organization?\n"
                            f"4. **Tone**: Appropriate for audience?\n"
                            f"5. **Suggestions**: Specific improvements\n\n"
                            f"**Evaluation**:"
                        )
                        
                        # Call Gemini AI
                        model_api = genai.GenerativeModel("gemini-1.5-flash")
                        response = model_api.generate_content(instruction)
                        
                        # Clean up output
                        cleaned_output = response.text.replace("*", "").strip()
                        st.session_state.evaluation = cleaned_output
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.session_state.evaluation:
            st.subheader("Evaluation Result")
            st.markdown(f'<div class="output-box">{st.session_state.evaluation}</div>', unsafe_allow_html=True)
            
            if st.button("Learn More About Prompt Engineering"):
                st.session_state.page = "Learn"

# Learn Page
def learn_page():
    st.title("Prompt Engineering Guide")
    
    with st.container():
        st.subheader("Prompt Introduction")
        st.write("""
        Prompt Engineering helps to effectively design and improve prompts to get better results 
        on different tasks with LLMs. While the previous basic examples were fun, in this section 
        we cover more advanced prompting engineering techniques that allow us to achieve more complex 
        tasks and improve reliability and performance of LLMs.
        """)
    
    st.divider()
    
    with st.container():
        st.subheader("Prompt Techniques")
        techniques = [
            "Zero-shot Prompting",
            "Few-shot Prompting",
            "Chain-of-Thought Prompting",
            "Meta Prompting",
            "Self-Consistency",
            "Generate Knowledge Prompting",
            "Prompt Chaining",
            "Tree of Thoughts",
            "Retrieval Augmented Generation",
            "Automatic Prompt Engineer",
            "Automatic Reasoning and Tool-use",
            "Active-Prompt",
            "Directional Stimulus Prompting",
            "Program-Aided Language Models",
            "ReAct",
            "Reflexion",
            "Multimodal CoT",
            "Graph Prompting"
        ]
        
        for i, technique in enumerate(techniques):
            with st.expander(f"{i+1}. {technique}"):
                st.write(f"**Use Case:** General purpose technique for {technique.split(' ')[0].lower()} prompts")
                st.write(f"**Developed By:** Research Community")
                st.write(f"**Example Implementation:** Commonly used in state-of-the-art LLMs")

# About Page
def about_page():
    st.title("About Prompt Generator")
    
    with st.container():
        st.write("""
        Prompting is a powerful tool that helps users craft queries or inputs for AI systems effectively.
        This app helps refine and evaluate prompts to ensure clarity, creativity, and technical precision.
        Use this tool to enhance your AI interactions!
        """)
    
    with st.container():
        st.subheader("About the Developer")
        st.write("""
        This project is developed by **Liyakhath Shaik**, a passionate developer who loves building tools 
        that make AI more accessible and effective.
        """)
        
        st.write("Connect with me:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("[GitHub](https://github.com/your-github)")
        with col2:
            st.markdown("[Portfolio](https://your-portfolio.com)")
        with col3:
            st.markdown("[Email](mailto:liyakhath0409@gmail.com)")
    
    with st.container():
        st.subheader("Future Plans for This Project")
        st.markdown("""
        - Add multi-language support for prompt generation and evaluation
        - Integrate more AI models for diverse prompt refinement
        - Enable users to save and manage their prompts
        - Add a community feature to share and discuss prompts
        """)

# Feedback Page
def feedback_page():
    st.title("Feedback")
    
    with st.form("feedback_form"):
        feedback = st.text_area("Enter your feedback here...", height=150)
        email = st.text_input("Your email (optional)")
        language = st.selectbox("Language", ["English", "Spanish", "French", "Hindi"])
        
        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            if not feedback.strip():
                st.error("Please enter your feedback")
            else:
                try:
                    # Google Apps Script endpoint
                    script_url = "https://script.google.com/macros/s/AKfycbyNptReTdjxtgfVb_Bho_l4-tBpzxvMM0W6_5IhzRRBd9QMsB9sn5yyoPp19RLGcrfV/exec"
                    
                    # Send feedback data
                    data = {
                        'feedback': feedback,
                        'email': email,
                        'language': language
                    }
                    
                    response = requests.post(script_url, json=data)
                    
                    if response.status_code == 200:
                        st.success("Feedback submitted successfully!")
                    else:
                        st.error("Failed to submit feedback. Please try again.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Techniques Page
def techniques_page():
    st.title("Prompt Engineering Techniques")
    
    techniques = [
        {
            "name": "Zero-shot Prompting",
            "use_case": "Tasks where no examples are provided",
            "example": "Translate this to French: 'Hello' -> 'Bonjour'",
            "developed": "OpenAI"
        },
        {
            "name": "Few-shot Prompting",
            "use_case": "Tasks with limited examples",
            "example": "Translate: 'Hello' -> 'Bonjour', 'Goodbye' -> 'Au revoir', 'Thank you' -> ?",
            "developed": "OpenAI"
        },
        {
            "name": "Chain-of-Thought",
            "use_case": "Complex reasoning tasks",
            "example": "Solve step-by-step: If John has 5 apples...",
            "developed": "Google Research"
        }
        # Add more techniques as needed
    ]
    
    for tech in techniques:
        with st.expander(tech["name"]):
            st.write(f"**Use Case:** {tech['use_case']}")
            st.write(f"**Example:** {tech['example']}")
            st.write(f"**Developed By:** {tech['developed']}")

# Main App
def main():
    st.set_page_config(
        page_title="Prompt Generator",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    navigation()
    
    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Learn":
        learn_page()
    elif st.session_state.page == "About":
        about_page()
    elif st.session_state.page == "Feedback":
        feedback_page()
    elif st.session_state.page == "Techniques":
        techniques_page()

if __name__ == "__main__":
    main()
