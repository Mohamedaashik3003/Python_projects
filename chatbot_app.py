from flask import Flask, request, jsonify
from transformers import pipeline
import sqlite3

app = Flask(__name__)
chatbot = pipeline("text-generation", model="gpt2")

def init_db():
    conn = sqlite3.connect("chat_logs.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS logs (user TEXT, bot TEXT)")
    conn.commit()
    conn.close()

def log_interaction(user_msg, bot_reply):
    conn = sqlite3.connect("chat_logs.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (user, bot) VALUES (?, ?)", (user_msg, bot_reply))
    conn.commit()
    conn.close()

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    response = chatbot(user_input, max_length=100, num_return_sequences=1)[0]["generated_text"]
    bot_reply = response[len(user_input):].strip()
    log_interaction(user_input, bot_reply)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
