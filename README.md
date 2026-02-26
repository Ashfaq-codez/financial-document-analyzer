# Financial Document Analyzer 📊🤖

An enterprise-ready, multi-agent AI API built with FastAPI, CrewAI, and Celery. This system ingests financial documents (PDFs), extracts critical data, and utilizes specialized AI agents to generate structured, strictly factual investment insights. 

It features a non-blocking asynchronous architecture using a Redis message queue and persistent SQLite storage.

## 🐛 Bugs Found & Fixed

During development, several critical issues were identified and resolved to ensure logically perfect and deterministic execution:

1. **Dependency Hell (Pydantic Validation Clashes)**
   * **Issue:** The original setup suffered from severe version conflicts between `langchain-core` (using Pydantic V2) and `crewai==0.130.0` (expecting Pydantic V1), causing immediate crashes when defining tools.
   * **Fix:** Bypassed Langchain decorators and implemented a clean, pure Python class inheriting directly from `crewai.tools.BaseTool`. Locked `openai`, `langchain-core`, and `crewai` to a mathematically stable matrix in `requirements.txt`.
2. **Prompt Hallucinations & Context Window Overflows**
   * **Issue:** The AI was prone to hallucinating numbers, and large PDFs would exceed the OpenAI token limits. Also, dynamic variables like `{query}` were improperly placed in static Agent definitions.
   * **Fix:** Removed dynamic variables from the `agents.py` definitions and moved them strictly to task execution. Implemented a robust `MAX_CHARS` limit and a newline-cleanup loop in `tools.py` to ensure high-fidelity, readable text extraction.
3. **Synchronous Server Blocking (Timeout Risks)**
   * **Issue:** Executing a 2-minute CrewAI process directly inside a FastAPI POST endpoint would freeze the server and cause HTTP timeouts for the user.
   * **Fix:** Completely decoupled the AI execution from the web server by implementing a Celery worker and a Redis message broker.

## ✨ Bonus Features Implemented

* **Queue Worker Model:** Integrated **Celery + Redis** to handle concurrent API requests asynchronously. The server returns a `task_id` instantly while the heavy AI processing happens safely in the background.
* **Database Integration:** Implemented modern SQLAlchemy 2.0 ORM (`Mapped` types) with an SQLite database to permanently store analysis results, track job statuses (`pending`, `completed`, `failed`), and prevent data loss.

## 🚀 Setup and Usage Instructions

### 1. Prerequisites
Ensure you have Python 3.11+ and a running Redis server.
For Arch-based Linux distributions:
```bash
sudo pacman -S redis
sudo systemctl enable --now redis

### 2. Environment Setup
Clone the repository and set up the virtual environment:

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

###Create a .env file in the root directory and add your OpenAI API key:


OPENAI_API_KEY=sk-YourSecretKeyHere

### 3. Running the Application
Because of the asynchronous architecture, you need two terminals.

### Terminal 1: Start the Web API

python main.py

### Terminal 2: Start the Background Worker

celery -A celery_worker.celery_app worker --loglevel=info
📖 API Documentation
Interactive Swagger documentation is available at http://localhost:8000/docs while the server is running.

### Endpoints

GET /

Health check. Returns API status.

POST /analyze

Description: Uploads a PDF and queues it for analysis.

Payload: multipart/form-data (file: PDF, query: string).

Returns: Instantly returns a task_id and status_url.

GET /status/{task_id}

Description: Polls the status of a queued task.

Returns: JSON object containing current status (pending, completed, failed) and the resulting analysis if finished.

GET /analyses

Description: Fetches the full historical log of all processed documents from the SQLite database.