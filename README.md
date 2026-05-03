# Production-Grade RAG Python App

A complete, production-ready Retrieval-Augmented Generation (RAG) application built with Python. This app allows users to upload PDF documents and ask questions about them. It uses an asynchronous background queue for smooth PDF ingestion and leverages the power of Google's Gemini AI models for accurate search and generation.

## 🚀 Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/) for a clean, interactive user interface.
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) for lightning-fast API endpoints.
- **Background Jobs / Orchestration**: [Inngest](https://www.inngest.com/) for reliable, queue-based background processing of PDF ingestion.
- **Vector Database**: [Qdrant](https://qdrant.tech/) (Local) for highly efficient storage and cosine-similarity search of document embeddings.
- **AI / LLM**: [Google GenAI SDK](https://ai.google.dev/) using `gemini-2.5-flash` for high-speed generation and `gemini-embedding-2` (3072-dimensional) for superior text embedding.

## ✨ Features
- **PDF Uploads**: Upload documents which are instantly processed in the background.
- **Intelligent Chunking**: Employs a sliding-window text chunker (4000 char chunks with 500 char overlaps) ensuring context is perfectly preserved.
- **Accurate Search**: Retrieves the top 10 most relevant chunks from the Qdrant database to feed into the Gemini LLM.
- **Expert Analysis**: Prompt-engineered to provide clear, concise, and highly accurate answers formatted with bullet points and bold text—strictly relying on the uploaded document.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Node.js (for running the Inngest local dev server)
- A Google Gemini API Key

### 2. Environment Configuration
Create a `.env` file in the root directory and add your Gemini API key:
```ini
GEMINI_API_KEY="your_google_gemini_api_key_here"
```

### 3. Install Dependencies
Set up your virtual environment and install the required Python packages:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
*(Note: If a requirements.txt is missing, ensure you install `fastapi`, `uvicorn`, `streamlit`, `qdrant-client`, `google-genai`, `inngest`, `pypdf`, and `python-dotenv`.)*

---

## 💻 How to Run the Application

This application requires three separate terminals running concurrently to operate correctly.

### Terminal 1: Start the Inngest Dev Server
This runs the local queue that manages background workflows like PDF chunking and database ingestion.
```bash
npx inngest-cli@latest dev
```
*(This usually runs on port 8288)*

### Terminal 2: Start the FastAPI Backend
This runs the core API server that handles logic and communicates with the Inngest server.
```bash
source .venv/bin/activate
uvicorn main:app --port 8000
```

### Terminal 3: Start the Streamlit Frontend
This launches the web interface for uploading PDFs and asking questions.
```bash
source .venv/bin/activate
streamlit run streamlit_app.py
```
*(The UI will be accessible at `http://localhost:8501`)*

---

## 📄 Usage
1. Open the Streamlit UI in your browser.
2. In the **"Upload a PDF to Ingest"** section, browse for your PDF. 
3. Wait for the green success message indicating the Inngest job has finished processing the text.
4. Scroll down to **"Ask a question about your PDFs"** and type your query! The model will use the local vector database to find your answer.