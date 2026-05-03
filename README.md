<div align="center">

<br/>

# 🧠 RAG Pipeline

### *Upload a PDF. Ask a question. Get a grounded, intelligent answer.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC244C?style=for-the-badge)](https://qdrant.tech)
[![Inngest](https://img.shields.io/badge/Inngest-Job_Queue-6366F1?style=for-the-badge)](https://inngest.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br/>

> A **production-grade Retrieval-Augmented Generation** system that transforms static PDFs into an interactive, queryable knowledge base — with zero hallucinations and full source grounding.

<br/>

[**Quick Start**](#%EF%B8%8F-setup--installation) · [**Architecture**](#-system-architecture) · [**Features**](#-features) · [**Usage**](#-usage)

</div>

---

## 🗺️ System Architecture

The application is built around three independently running services that communicate to form a complete RAG pipeline.

### High-Level Overview

```mermaid
graph TD
    User(["👤 User"]):::actor

    subgraph Frontend["🖥️ Streamlit UI  ·  localhost:8501"]
        UI_UP["📂 PDF Upload"]
        UI_QA["💬 Q&A Interface"]
    end

    subgraph Backend["⚙️ FastAPI Backend  ·  localhost:8000"]
        API_ING["/ingest endpoint"]
        API_QRY["/query endpoint"]
        EMBED["gemini-embedding-2\n3072-dim encoder"]
    end

    subgraph Queue["🔁 Inngest Dev Server  ·  localhost:8288"]
        JOB["Background Job\nPDF Ingestion"]
        CHUNK["Sliding-Window Chunker\n4000 chars / 500 overlap"]
    end

    subgraph VectorDB["🔍 Qdrant  ·  Local"]
        UPSERT["Upsert Vectors"]
        SEARCH["Cosine Similarity Search\nTop K = 10"]
    end

    LLM["✨ gemini-2.5-flash\nAnswer Generation"]

    User -->|"upload PDF"| UI_UP
    UI_UP -->|"POST /ingest"| API_ING
    API_ING -->|"enqueue job"| JOB
    JOB --> CHUNK
    CHUNK -->|"text chunks"| EMBED
    EMBED -->|"vectors"| UPSERT

    User -->|"ask question"| UI_QA
    UI_QA -->|"POST /query"| API_QRY
    API_QRY --> EMBED
    EMBED -->|"query vector"| SEARCH
    SEARCH -->|"top 10 chunks"| LLM
    LLM -->|"grounded answer"| UI_QA

    classDef actor fill:#6366f1,stroke:#4f46e5,color:#fff,font-weight:bold
```

---

### PDF Ingestion Pipeline

```mermaid
flowchart LR
    A(["📄 PDF Uploaded"]):::input
    B["pypdf\nText Extraction"]:::step
    C["Sliding Window Chunker\n4000 chars · 500 overlap"]:::step
    D["gemini-embedding-2\n→ 3072-dim vector per chunk"]:::step
    E[("🗃️ Qdrant\nVector DB")]:::store

    A --> B --> C --> D --> E

    classDef input  fill:#6366f1,stroke:#4f46e5,color:#fff,font-weight:bold
    classDef step   fill:#f1f5f9,stroke:#cbd5e1,color:#1e293b
    classDef store  fill:#dc2626,stroke:#b91c1c,color:#fff
```

---

### Query & Answer Pipeline

```mermaid
flowchart LR
    Q(["❓ User Question"]):::input
    A["gemini-embedding-2\n→ 3072-dim query vector"]:::step
    B[("🗃️ Qdrant\nVector DB")]:::store
    C["Cosine Similarity\nTop 10 Chunks Retrieved"]:::step
    D["Context Assembly\n+ System Prompt"]:::step
    E["gemini-2.5-flash\nGrounded Generation"]:::llm
    R(["✅ Answer"]):::output

    Q --> A --> B --> C --> D --> E --> R

    classDef input  fill:#6366f1,stroke:#4f46e5,color:#fff,font-weight:bold
    classDef step   fill:#f1f5f9,stroke:#cbd5e1,color:#1e293b
    classDef store  fill:#dc2626,stroke:#b91c1c,color:#fff
    classDef llm    fill:#1d4ed8,stroke:#1e40af,color:#fff
    classDef output fill:#059669,stroke:#047857,color:#fff,font-weight:bold
```

---

### Module Dependency Map

```mermaid
graph LR
    subgraph App["Python Application"]
        SL["streamlit_app.py\nFrontend UI"]
        MA["main.py\nFastAPI + Inngest"]
        DL["data_loader.py\nPDF Parser & Chunker"]
        VD["vector_db.py\nQdrant Client"]
        CT["custom_types.py\nPydantic Models"]
    end

    subgraph Services["External Services"]
        QD[("Qdrant\nLocal Vector DB")]
        GEM["Google GenAI SDK\nEmbeddings + LLM"]
        INN["Inngest\nJob Queue"]
    end

    SL -->|"HTTP requests"| MA
    MA --> DL
    MA --> VD
    MA --> CT
    DL --> CT
    VD --> QD
    MA -->|"embed + generate"| GEM
    MA -->|"enqueue / receive"| INN
```

---

## ✨ Features

| Feature | Detail |
|---|---|
| 📄 **Async PDF Ingestion** | Upload PDFs via Streamlit; Inngest handles chunking in a background job — no timeouts, no blocking |
| 🔪 **Sliding-Window Chunking** | 4,000-character chunks with 500-character overlaps preserve cross-boundary context perfectly |
| 🧠 **High-Dimensional Embeddings** | `gemini-embedding-2` produces 3,072-dimensional vectors for nuanced semantic representation |
| 🎯 **Top-K Retrieval** | Qdrant cosine-similarity search returns the 10 most relevant chunks per query |
| 🛡️ **Hallucination-Free Answers** | Prompt-engineered to answer strictly from document content — if it's not in the PDF, the model says so |
| ⚡ **Fast Generation** | `gemini-2.5-flash` delivers sub-second response times on most queries |
| 🧩 **Modular Codebase** | Clean separation: parser, vector DB, API, and UI are each independently replaceable |

---

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | [Streamlit](https://streamlit.io) | PDF upload UI and Q&A chat interface |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com) + Uvicorn | REST API, request routing, orchestration |
| **Job Queue** | [Inngest](https://inngest.com) | Reliable async background job execution |
| **PDF Parsing** | [pypdf](https://pypdf.readthedocs.io) | Extracts raw text from uploaded PDFs |
| **Embeddings** | `gemini-embedding-2` (Google) | Converts text to 3,072-dim semantic vectors |
| **Vector Store** | [Qdrant](https://qdrant.tech) (local) | Cosine-similarity nearest-neighbour search |
| **LLM** | `gemini-2.5-flash` (Google) | Grounded natural language answer generation |
| **Config** | `python-dotenv` | Secure API key management via `.env` |

---

## 📁 Project Structure

```
RAG-app/
│
├── main.py              # ⚙️  FastAPI app — API routes & Inngest function registration
├── streamlit_app.py     # 🖥️  Streamlit frontend — upload & Q&A interface
├── data_loader.py       # 📄  PDF parser & sliding-window text chunker
├── vector_db.py         # 🔍  Qdrant client — upsert embeddings & similarity search
├── custom_types.py      # 🧩  Pydantic models & shared type definitions
│
├── pyproject.toml       # 📦  Project metadata & dependency spec
├── uv.lock              # 🔒  Locked dependency versions
├── .python-version      # 🐍  Pinned Python version
└── .gitignore
```

---

## 🛠️ Setup & Installation

### Prerequisites

| Requirement | Version | Link |
|---|---|---|
| Python | 3.10+ | [python.org](https://python.org/downloads) |
| Node.js | Any LTS | [nodejs.org](https://nodejs.org) |
| Google Gemini API Key | — | [Get key →](https://aistudio.google.com/app/apikey) |

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/tanusingh04/RAG-app.git
cd RAG-app
```

---

### Step 2 — Configure Environment Variables

Create a `.env` file in the project root:

```ini
# .env
GEMINI_API_KEY="your_google_gemini_api_key_here"
```

> ⚠️ Never commit this file. It is already covered by `.gitignore`.

---

### Step 3 — Create a Virtual Environment & Install Dependencies

```bash
# Create the virtual environment
python -m venv .venv

# Activate — macOS / Linux
source .venv/bin/activate

# Activate — Windows
.venv\Scripts\activate

# Install all packages
pip install fastapi uvicorn streamlit qdrant-client google-genai inngest pypdf python-dotenv
```

> 💡 Or if a `requirements.txt` is present: `pip install -r requirements.txt`

---

## 💻 Running the Application

This app requires **three terminals running in parallel**. Start them in this order.

```
┌─────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│   Terminal 1            │  │   Terminal 2             │  │   Terminal 3             │
│   Inngest Queue         │  │   FastAPI Backend        │  │   Streamlit UI           │
│   port :8288            │  │   port :8000             │  │   port :8501             │
├─────────────────────────┤  ├──────────────────────────┤  ├──────────────────────────┤
│                         │  │  source .venv/bin/activ  │  │  source .venv/bin/activ  │
│  npx inngest-cli@latest │  │  uvicorn main:app        │  │  streamlit run           │
│  dev                    │  │    --port 8000           │  │    streamlit_app.py      │
└─────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘
        Start first                  Start second                  Start third
```

> ✅ Once all three are running, open **http://localhost:8501** in your browser.

---

## 📖 Usage

```
  1. 🌐  Open http://localhost:8501

  2. 📂  Find the "Upload a PDF to Ingest" section
          └── Browse and select your PDF file

  3. ⏳  Wait for the green ✅ success banner
          └── Inngest has chunked, embedded, and indexed your document

  4. 💬  Scroll to "Ask a question about your PDFs"
          └── Type your question and press Enter

  5. 🎯  Receive a grounded, structured answer
          └── Bullet points, bold text — strictly from your document
```

---

## ⚙️ Configuration Reference

| Parameter | Value | Location |
|---|---|---|
| `CHUNK_SIZE` | `4000` characters | `data_loader.py` |
| `CHUNK_OVERLAP` | `500` characters | `data_loader.py` |
| `TOP_K_RESULTS` | `10` chunks | `vector_db.py` |
| `EMBEDDING_DIMENSIONS` | `3072` | `gemini-embedding-2` default |
| `SIMILARITY_METRIC` | Cosine | Qdrant collection config |
| `GENERATION_MODEL` | `gemini-2.5-flash` | `main.py` |

---

## 🤝 Contributing

Contributions are welcome! Here's the workflow:

```bash
# 1. Fork and clone your fork
git clone https://github.com/YOUR_USERNAME/RAG-app.git

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes and commit
git commit -m "feat: describe your change clearly"

# 4. Push and open a Pull Request
git push origin feature/your-feature-name
```

Please keep PRs focused with a clear description of what changed and why.

---

## 📜 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

<div align="center">

<br/>

**Built with 🧠 intelligence, ☕ caffeine, and a love for clean architecture.**

*Found this useful? Drop a ⭐ — it keeps the momentum going.*

[![GitHub stars](https://img.shields.io/github/stars/tanusingh04/RAG-app?style=social)](https://github.com/tanusingh04/RAG-app/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/tanusingh04/RAG-app?style=social)](https://github.com/tanusingh04/RAG-app/network/members)

<br/>

</div>
