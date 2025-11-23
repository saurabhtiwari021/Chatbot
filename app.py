from flask import Flask, request, jsonify, render_template
from rapidfuzz import fuzz
import openai
import json
import os

app = Flask(__name__)

openai.api_key = "k-proj-q2Q0syQRudVXva_VmJthK_KKZQype9CD2KtWc-vUD97tWmJd3Mzg8ZvzHngTB8fboHZRQlhGsHT3BlbkFJDKje_b2hcGvhmg5Nol3vhHK30cT89sQB7kACNPWal75gwnYKoRMeQiY_KUdT9Nkhp_5xs7QqcA"


FAQ_FILE = "faq_data.json"
CHAT_HISTORY_FILE = "chat_history.json"

if os.path.exists(FAQ_FILE):
    with open(FAQ_FILE, "r") as f:
        faq_data = json.load(f)
else:
    faq_data = {}
    with open(FAQ_FILE, "w") as f:
        json.dump(faq_data, f, indent=4)

if os.path.exists(CHAT_HISTORY_FILE):
    with open(CHAT_HISTORY_FILE, "r") as f:
        chat_history = json.load(f)
else:
    chat_history = []
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(chat_history, f, indent=4)


def save_chat(user_message, bot_response):
    chat_history.append({"user": user_message, "bot": bot_response})
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(chat_history, f, indent=4)


def save_new_faq(question, answer):
    faq_data[question] = answer
    with open(FAQ_FILE, "w") as f:
        json.dump(faq_data, f, indent=4)  


def find_faq_match(user_message):
    best_match = None
    best_score = 0
    for question, answer in faq_data.items():
        score = fuzz.ratio(user_message.lower(), question.lower())
        if score > best_score:
            best_score = score
            best_match = (question, answer)
    return best_match if best_score > 85 else None

def get_ai_response(user_message, faq_answer=None):
    try:
        messages = [
            {
                "role": "system",
                "content": "You are MIA, a friendly travel assistant for Jharkhand tourism. "
                           "Always give clear, warm, and useful answers about Jharkhand tourism, "
                           "culture, food, and travel. If the user just greets you (hi, hello, etc.), "
                           "respond politely and introduce yourself."
            }
        ]

        if faq_answer:
            messages.append({"role": "system", "content": f"FAQ info: {faq_answer}"})

        recent_history = chat_history[-5:]
        for chat in recent_history:
            messages.append({"role": "user", "content": chat["user"]})
            messages.append({"role": "assistant", "content": chat["bot"]})

        messages.append({"role": "user", "content": user_message})

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("⚠️ AI Error:", e)
        return None


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    print("👉 User asked:", user_message)

    greetings = ["hi", "hii", "hello", "hey", "hola"]
    if user_message.lower() in greetings:
        bot_response = "Hello 👋 I’m MIA, your travel assistant for Jharkhand! How can I help you today?"
        save_chat(user_message, bot_response)
        return jsonify({"response": bot_response})

    match = find_faq_match(user_message)
    if match:
        question, faq_answer = match
        print(f"✅ FAQ Match Found: {question}")

        ai_extra = get_ai_response(user_message, faq_answer)
        response_text = faq_answer
        if ai_extra and ai_extra.lower() not in faq_answer.lower():
            response_text += f"\n\n🤖 Extra Info: {ai_extra}"

        save_chat(user_message, response_text)
        return jsonify({"response": response_text})

    ai_answer = get_ai_response(user_message)

    if ai_answer:
        if len(user_message.split()) <= 8:
            save_new_faq(user_message, ai_answer)

        save_chat(user_message, ai_answer)
        return jsonify({"response": ai_answer})

    return jsonify({"response": "⚠️ Sorry, I couldn’t fetch an answer. Try rephrasing your question."})


if __name__ == "__main__":
    app.run(debug=True)
