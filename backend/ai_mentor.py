# ai_mentor.py
import requests
import json

# Ollama server config (default Ollama port)
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "phi3:mini"



def call_ollama(prompt: str) -> str:
    """Send a prompt to Ollama and return the response."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.6,
                    "top_p": 0.9
                }
            },
            timeout=180
        )

        if response.status_code != 200:
            print("Ollama error:", response.text)
            return ""

        data = response.json()
        return data.get("response", "").strip()

    except Exception as e:
        print("Ollama connection error:", e)
        return ""


# ---------------------------
# Mentiza-Style AI Mentor
# ---------------------------

def get_next_question(context: dict, previous_answer: str = None) -> str:
    """
    Ask next interview question like Mentiza.
    If previous answer is weak, politely ask to repeat in correct format.
    """
    prompt = f"""
You are a friendly AI Interviewer like Mentiza.

Skill: {context['topic']}
Difficulty: {context['difficulty']}
Question Number: {context['question_number']}
Previous Answer: {previous_answer if previous_answer else "None"}

Rules:
- Talk friendly like a mentor.
- If previous answer is wrong or incomplete:
  - Say politely that improvement is needed.
  - Tell what is missing.
  - Ask the user to repeat in proper format.
- If answer is good:
  - Praise shortly.
  - Ask next technical question.
- Ask only ONE question.
- Keep tone supportive and motivating.

Now respond:
"""
    return call_ollama(prompt)


def evaluate_answer(question: str, answer: str) -> str:
    """
    Evaluate answer like Mentiza:
    - Score
    - Feedback
    - Encourage retry if needed
    """
    prompt = f"""
You are an AI Mentor like Mentiza.

Question:
{question}

Student Answer:
{answer}

Give output strictly like:

Score: <number out of 100>
Feedback:
<Encouraging + what is missing + how to improve>

Tone must be friendly and motivating.
"""
    return call_ollama(prompt)


def generate_interview_summary(data: dict) -> str:
    """
    Final Mentiza-style summary
    """
    prompt = f"""
You are an AI Mentor like Mentiza.

Interview Data:
{json.dumps(data, indent=2)}

Create:
1. Motivation message (2 lines)
2. Strengths
3. Weaknesses
4. Learning roadmap (step-by-step)

Tone: Friendly, hopeful, encouraging.
"""
    return call_ollama(prompt)


def chat_with_mentor(message: str, history: list = None) -> str:
    """
    General mentor chat mode.
    """
    history_text = ""
    if history:
        for h in history:
            history_text += f"User: {h['user']}\nMentor: {h['mentor']}\n"

    prompt = f"""
You are Skillin AI Mentor.
You are friendly, patient, and technical like Mentiza.

Conversation:
{history_text}

User: {message}
Mentor:
"""
    return call_ollama(prompt)
