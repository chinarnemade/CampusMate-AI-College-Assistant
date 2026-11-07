import json
import sqlite3
from datetime import datetime
from pathlib import Path
from functools import wraps

from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import ollama

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "campusmate.db"
DATA_PATH = BASE_DIR / "data" / "college_data.json"

app = Flask(__name__)
app.secret_key = "campusmate-local-dev-secret-change-this"

MODEL = "qwen2.5:1.5b"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    college_data = json.load(f)

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()

init_db()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Please log in first."}), 401
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def user_chat(chat_id):
    conn = db()
    row = conn.execute(
        "SELECT * FROM chats WHERE id=? AND user_id=?",
        (chat_id, session["user_id"])
    ).fetchone()
    conn.close()
    return row

def create_chat(title="New Chat"):
    now = datetime.now().isoformat(timespec="seconds")
    conn = db()
    cur = conn.execute(
        "INSERT INTO chats(user_id,title,created_at,updated_at) VALUES(?,?,?,?)",
        (session["user_id"], title[:80], now, now)
    )
    chat_id = cur.lastrowid
    conn.commit()
    conn.close()
    return chat_id

BASE_SYSTEM = f"""
You are CampusMate, an AI College Assistant for Ramrao Adik Institute of Technology (RAIT).

Use the college knowledge base below for college-specific information.
Never invent current HOD names, faculty details, exam dates, notices, event dates,
library timings, placement statistics, or other time-sensitive facts.
If a fact is unavailable or marked for verification, say so.

Be friendly, concise, and useful. You are a student assistant, not an official
college authority.

COLLEGE KNOWLEDGE BASE:
{json.dumps(college_data, indent=2, ensure_ascii=False)}
"""

ASSIGNMENT_SYSTEM = f"""
You are CampusMate's Assignment Coach for RAIT students.

Help students understand and complete academic assignments ethically.
When a student provides a subject, topic, question, or assignment prompt:
- Identify the subject/topic.
- Explain the underlying concept in simple language.
- Break the task into manageable steps.
- Provide formulas, examples, pseudocode, outlines, or worked examples where useful.
- For programming questions, explain the logic and provide illustrative code when appropriate.
- For theory assignments, help structure an answer and identify key points.
- For numerical problems, show the method and reasoning.
- If the user asks for a full submission, provide a useful study-oriented draft/structure
  and encourage them to adapt it to their own work.
- Do not pretend that an answer is an official faculty solution.
- Ask for the subject or assignment question if it is missing.

Relevant college context:
{json.dumps(college_data, indent=2, ensure_ascii=False)}
"""

@app.get("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("app.html", college=college_data["college_name"])

@app.get("/login")
def login():
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("login.html")

@app.post("/api/signup")
def signup():
    body = request.get_json() or {}
    name = str(body.get("name", "")).strip()
    email = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", ""))

    if not name or not email or len(password) < 6:
        return jsonify({"error": "Enter your name, a valid email, and a password of at least 6 characters."}), 400

    conn = db()
    try:
        cur = conn.execute(
            "INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)",
            (name, email, generate_password_hash(password), datetime.now().isoformat(timespec="seconds"))
        )
        user_id = cur.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "An account with that email already exists."}), 409
    conn.close()

    session["user_id"] = user_id
    session["name"] = name
    session["email"] = email
    return jsonify({"ok": True})

@app.post("/api/login")
def api_login():
    body = request.get_json() or {}
    email = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", ""))

    conn = db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Incorrect email or password."}), 401

    session["user_id"] = user["id"]
    session["name"] = user["name"]
    session["email"] = user["email"]
    return jsonify({"ok": True})

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.get("/api/me")
@login_required
def me():
    return jsonify({
        "name": session["name"],
        "email": session["email"]
    })

@app.get("/api/chats")
@login_required
def chats():
    conn = db()
    rows = conn.execute(
        "SELECT id,title,created_at,updated_at FROM chats WHERE user_id=? ORDER BY updated_at DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return jsonify({"chats": [dict(r) for r in rows]})

@app.post("/api/chats")
@login_required
def new_chat():
    body = request.get_json() or {}
    title = str(body.get("title", "New Chat")).strip() or "New Chat"
    chat_id = create_chat(title)
    return jsonify({"id": chat_id, "title": title[:80]})

@app.delete("/api/chats/<int:chat_id>")
@login_required
def delete_chat(chat_id):
    if not user_chat(chat_id):
        return jsonify({"error": "Chat not found."}), 404
    conn = db()
    conn.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
    conn.execute("DELETE FROM chats WHERE id=? AND user_id=?", (chat_id, session["user_id"]))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.get("/api/chats/<int:chat_id>")
@login_required
def get_chat(chat_id):
    if not user_chat(chat_id):
        return jsonify({"error": "Chat not found."}), 404
    conn = db()
    rows = conn.execute(
        "SELECT role,content,created_at FROM messages WHERE chat_id=? ORDER BY id ASC",
        (chat_id,)
    ).fetchall()
    conn.close()
    return jsonify({"messages": [dict(r) for r in rows]})

@app.post("/api/chat")
@login_required
def chat():
    body = request.get_json() or {}
    chat_id = body.get("chat_id")
    user_text = str(body.get("message", "")).strip()
    mode = body.get("mode", "chat")
    subject = str(body.get("subject", "")).strip()

    if not user_text:
        return jsonify({"error": "Please enter a message."}), 400

    if chat_id and not user_chat(int(chat_id)):
        return jsonify({"error": "Chat not found."}), 404

    if not chat_id:
        chat_id = create_chat(user_text[:60])

    conn = db()
    history_rows = conn.execute(
        "SELECT role,content FROM messages WHERE chat_id=? ORDER BY id ASC LIMIT 12",
        (chat_id,)
    ).fetchall()
    conn.close()

    system_prompt = ASSIGNMENT_SYSTEM if mode == "assignment" else BASE_SYSTEM
    if mode == "assignment" and subject:
        system_prompt += f"\n\nThe student has selected subject: {subject}. Tailor the explanation to this subject."

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend({"role": r["role"], "content": r["content"]} for r in history_rows)
    messages.append({"role": "user", "content": user_text})

    try:
        response = ollama.chat(model=MODEL, messages=messages)
        answer = response["message"]["content"].strip()
    except Exception as e:
        app.logger.exception("Ollama request failed")
        return jsonify({"error": "Local AI error: " + str(e)}), 500

    now = datetime.now().isoformat(timespec="seconds")
    conn = db()
    conn.execute(
        "INSERT INTO messages(chat_id,role,content,created_at) VALUES(?,?,?,?)",
        (chat_id, "user", user_text, now)
    )
    conn.execute(
        "INSERT INTO messages(chat_id,role,content,created_at) VALUES(?,?,?,?)",
        (chat_id, "assistant", answer, now)
    )
    conn.execute(
        "UPDATE chats SET updated_at=? WHERE id=? AND user_id=?",
        (now, chat_id, session["user_id"])
    )
    conn.commit()
    conn.close()

    return jsonify({"chat_id": chat_id, "answer": answer})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
