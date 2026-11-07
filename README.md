# 🎓 CampusMate – AI-Powered College Assistant

**CampusMate** is an AI-powered college assistant designed to help students of **Ramrao Adik Institute of Technology (RAIT)** access college-related information and receive personalized academic guidance through an intelligent chatbot.

Built using Python, Flask, SQLite, and Ollama, CampusMate combines a college-specific knowledge base with a locally running Large Language Model (LLM) to provide conversational assistance and assignment support.

---

## 🚀 Key Features

### 1. AI-Powered College Assistant
- Provides conversational assistance for college-related queries.
- Uses a structured college knowledge base to answer institution-specific questions.
- Designed to avoid generating unverified information about faculty, examination dates, notices, and other time-sensitive details.

### 2. Assignment Coach
- Helps students understand academic concepts and assignment questions.
- Breaks complex problems into manageable steps.
- Provides explanations, formulas, examples, pseudocode, and programming guidance.
- Supports theory-based and numerical assignments.

### 3. User Authentication
- User registration and login functionality.
- Secure password hashing using Werkzeug.
- Session-based authentication.
- Individual user access to chat conversations.

### 4. Chat History Management
- Automatically saves conversations.
- Maintains individual chat histories for users.
- Allows users to retrieve previous conversations.
- Supports creating and deleting chats.

### 5. Local AI Integration
- Integrates Ollama to run the Qwen 2.5 (1.5B) language model locally.
- Processes user queries through the locally hosted LLM.
- Maintains conversational context using previous messages.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Flask | Backend web framework and API development |
| SQLite | User accounts and chat history storage |
| Ollama | Local LLM execution |
| Qwen 2.5 (1.5B) | AI language model |
| HTML | Frontend structure |
| CSS | User interface styling |
| Werkzeug | Password hashing and authentication utilities |

---

## 🏗️ Project Architecture

CampusMate follows a modular web application architecture.

**Application Workflow:**

1. The student interacts with the web interface.
2. Flask receives and processes the request.
3. Authentication and session management ensure user access.
4. The application retrieves relevant conversation history from SQLite.
5. The appropriate system prompt and college knowledge base are provided to the AI model.
6. Ollama processes the request using Qwen 2.5.
7. The generated response is returned to the frontend.
8. User queries and AI responses are stored in the database.

---

## 📂 Project Structure

```text
CampusMate-V2/
│
├── app.py
│   └── Main Flask application and API endpoints
│
├── data/
│   └── college_data.json
│       └── College-specific knowledge base
│
├── static/
│   └── style.css
│       └── Frontend styling
│
├── templates/
│   ├── app.html
│   └── login.html
│
├── requirements.txt
│   └── Python dependencies
│
├── .gitignore
│
└── README.md
```

---

## ⚙️ Installation and Setup

### Prerequisites

Make sure you have the following installed:

- Python 3.9 or later
- pip
- Ollama

### Step 1: Clone the Repository

```bash
git clone https://github.com/chinarnemade/CampusMate-AI-College-Assistant.git
```

Navigate to the project directory:

```bash
cd CampusMate-AI-College-Assistant
```

### Step 2: Create a Virtual Environment

```bash
python3 -m venv venv
```

Activate it:

**macOS / Linux**
```bash
source venv/bin/activate
```

**Windows**
```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Ollama

Install Ollama from:

https://ollama.com/

Download the required model:

```bash
ollama pull qwen2.5:1.5b
```

Make sure the Ollama service is running before starting the application.

### Step 5: Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

Register an account and start interacting with CampusMate!

---

## 🔐 Data and Security

- Passwords are stored as secure hashes rather than plain text.
- User conversations are associated with individual accounts.
- Chat access is restricted to the authenticated owner.
- SQLite is used for local data persistence.
- The AI model runs locally through Ollama.

**Note:** Configure a secure Flask secret key using an environment variable before deploying the application. Do not commit local databases or sensitive credentials.

---

## 🎯 Project Objectives

- Make college-related information more accessible to students.
- Provide personalized AI-based academic assistance.
- Simplify the process of understanding assignments and technical concepts.
- Explore practical applications of Large Language Models in educational environments.
- Build an intelligent, locally hosted student assistance system.

---

## 🔮 Future Enhancements

- Integration of college notices and announcements.
- Document and PDF-based question answering.
- Faculty and department information retrieval.
- Integration of academic schedules and examination updates.
- Improved semantic search and Retrieval-Augmented Generation (RAG).
- Deployment with production-ready authentication and database infrastructure.

---

## 👩‍💻 Developer

**Chinar Nemade**

GitHub: [@chinarnemade](https://github.com/chinarnemade)

---

⭐ If you find this project interesting, consider giving the repository a star!

**CampusMate – Making College Assistance Smarter with AI.**
