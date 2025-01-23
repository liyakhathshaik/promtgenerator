from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import logging

app = Flask(__name__)

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Configure Google Gemini API Key
API_KEY = "AIzaSyDI_nBkIwy7OsZfuyKh6tUJZYHYwRa25tQ"  # Replace with your actual API key
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    logging.error(f"Failed to configure Gemini API: {e}")
    raise e


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/feedback")
def feedback_page():
    return render_template("feedback.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/technique")
def technique_page():
    return render_template("technique.html")

@app.route("/learn")
def learn_page():
    return render_template("learn.html")


@app.route("/refine", methods=["POST"])
def refine():
    try:
        # Parse request data
        data = request.json
        user_prompt = data.get("prompt", "").strip()
        max_words = data.get("max_words", "medium")  # Default to "medium"
        tags = data.get("tags", [])
        target_model = data.get("model", "ChatGPT")  # Default target is "ChatGPT"

        # Validate input
        if not user_prompt:
            return jsonify({"error": "Prompt cannot be empty"}), 400

        # Adjust word count range based on "max_words"
        word_count_map = {
            "short": "300-500 words",
            "medium": "800-1000 words",
            "long": "1500-2000 words"
        }
        word_limit_context = word_count_map.get(max_words, "800-1000 words")

        # Build a dynamic instruction for Gemini to refine the prompt
        instruction = (
            f"You are a professional prompt generator. Your task is to take the following user input and transform it into a "
            f"high-quality, optimized prompt for the target AI model '{target_model}'. The prompt should help the user learn about "
            f"the topic in a structured and comprehensive way. Follow these guidelines:\n\n"
            f"1. **Objective**: Clearly define the purpose of the prompt (e.g., learning about Agentic AI from basics).\n"
            f"2. **Structure**: Break the prompt into logical sections (e.g., foundational concepts, advanced topics, applications).\n"
            f"3. **Specificity**: Include specific details or examples to guide the model.\n"
            f"4. **Tone**: Use a professional and engaging tone.\n"
            f"5. **Word Count**: Ensure the prompt adheres to the word limit: {word_limit_context}.\n\n"
            f"**Tags**: Incorporate the following tags into the prompt: {', '.join(tags) if tags else 'None'}.\n\n"
            f"**User Input**:\n{user_prompt}\n\n"
            f"**Optimized Prompt**:"
        )

        # Call Gemini AI to refine the prompt
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(instruction)

        # Clean up the output (remove unwanted symbols like stars)
        cleaned_output = response.text.replace("*", "").strip()

        # Return the refined prompt
        return jsonify({
            "target_model": target_model,
            "refined_output": cleaned_output
        })
    except Exception as e:
        logging.error(f"Error in refine: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/evaluate", methods=["POST"])
def evaluate():
    try:
        # Parse request data
        data = request.json
        user_prompt = data.get("prompt", "").strip()

        # Validate input
        if not user_prompt:
            return jsonify({"error": "Prompt cannot be empty"}), 400

        # Build an instruction for Gemini to evaluate the prompt
        instruction = (
            f"You are a professional prompt evaluator. Your task is to analyze the following user input and provide feedback on how to improve it. "
            f"Focus on the following aspects:\n\n"
            f"1. **Clarity**: Is the prompt clear and easy to understand?\n"
            f"2. **Specificity**: Does the prompt provide enough details for the AI model to generate a meaningful response?\n"
            f"3. **Structure**: Is the prompt logically structured?\n"
            f"4. **Tone**: Is the tone appropriate for the intended audience?\n"
            f"5. **Suggestions**: Provide specific suggestions for improvement.\n\n"
            f"**User Input**:\n{user_prompt}\n\n"
            f"**Evaluation**:"
        )

        # Call Gemini AI to evaluate the prompt
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(instruction)

        # Clean up the output (remove unwanted symbols like stars)
        cleaned_output = response.text.replace("*", "").strip()

        # Return the evaluation feedback
        return jsonify({
            "evaluation": cleaned_output
        })
    except Exception as e:
        logging.error(f"Error in evaluate: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)