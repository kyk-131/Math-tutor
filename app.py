import os
import openai
import pytesseract
import sympy as sp
import speech_recognition as sr
import pyttsx3
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)
openai.api_key = "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"
engine = pyttsx3.init()
recognizer = sr.Recognizer()

# Solve math expressions
def solve_math(expression):
    try:
        solution = sp.simplify(expression)
        steps = sp.pretty(solution, use_unicode=True)
        return str(solution), steps
    except Exception as e:
        return str(e), "Error solving the problem."

# Process image input
def extract_text_from_image(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception as e:
        return "Error extracting text."

# AI chatbot response
def chat_with_ai(question):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": question}]
    )
    return response["choices"][0]["message"]["content"].strip()

# Voice output
def speak_response(text):
    engine.say(text)
    engine.runAndWait()

# Voice input
def recognize_speech():
    with sr.Microphone() as source:
        print("Listening for a math problem...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError:
        return "Speech recognition service error."

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    problem = data.get("problem", "")
    solution, steps = solve_math(problem)
    speak_response(f"The solution is {solution}")
    return jsonify({"solution": solution, "steps": steps})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get("question", "")
    response = chat_with_ai(question)
    speak_response(response)
    return jsonify({"response": response})

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    file = request.files['file']
    image_path = os.path.join("uploads", file.filename)
    file.save(image_path)
    text = extract_text_from_image(image_path)
    solution, steps = solve_math(text)
    speak_response(f"The extracted text is {text} and the solution is {solution}")
    return jsonify({"extracted_text": text, "solution": solution, "steps": steps})

@app.route('/voice', methods=['GET'])
def voice_input():
    text = recognize_speech()
    solution, steps = solve_math(text)
    speak_response(f"You said {text}. The solution is {solution}")
    return jsonify({"recognized_text": text, "solution": solution, "steps": steps})

if __name__ == '__main__':
    app.run(debug=True)
