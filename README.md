# AIVOA — AI-Powered Customer Complaint Management System

> **Pharma QMS Customer Complaint Module** with AI Copilot powered by LangGraph + Groq

An AI-powered complaint management system for the pharmaceutical manufacturing industry (API & FDF). The system features a two-panel interface: a structured complaint form on the left and an AI Copilot chat on the right that extracts, classifies, and assesses complaint data from unstructured text.

## 🏗️ Architecture

```
┌─────────────────────┐     ┌─────────────────────────────────┐
│     React + Redux    │────▶│   FastAPI Backend (Python)       │
│     (Vite)           │◀────│                                 │
│                      │     │   ┌─────────────────────────┐   │
│  ┌──────┐ ┌────────┐│     │   │   LangGraph Agent        │   │
│  │ Form │ │Copilot ││     │   │   ┌─────────────────┐   │   │
│  │      │ │ Panel  ││     │   │   │ Groq gemma2-9b  │   │   │
│  └──────┘ └────────┘│     │   │   └─────────────────┘   │   │
└─────────────────────┘     │   └─────────────────────────┘   │
                             │   ┌─────────────────────────┐   │
                             │   │   PostgreSQL Database    │   │
                             │   └─────────────────────────┘   │
                             └─────────────────────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Redux Toolkit + Vite |
| Backend | Python + FastAPI |
| AI Agent | LangGraph (multi-step workflow) |
| LLM | Groq API — `gemma2-9b-it` (primary), `llama-3.3-70b-versatile` (fallback) |
| Database | PostgreSQL |
| Font | Google Inter |

## ✨ Features

### Core Workflow
- **AI Complaint Extraction**: Paste raw complaint email/text → AI extracts all form fields
- **File Upload**: Upload PDF/text complaint files for automatic parsing
- **Conversational Corrections**: Chat with Copilot to correct specific fields naturally
- **Risk Assessment**: AI generates severity, next action, and risk narrative
- **Commit to QMS Ledger**: Save complaint to PostgreSQL database

### Bonus AI Features
- ✅ **Complaint Completeness Checker** — Validates mandatory fields before commit
- ✅ **Root Cause Recommendation** — AI suggests probable root causes
- ✅ **Duplicate Complaint Detection** — Checks DB for matching batch/product
- ✅ **CAPA Recommendation** — Corrective and Preventive Actions
- ✅ **Complaint Summary** — Synthesizes formal QMS description
- ✅ **AI Risk Classification** — Severity + Next Action + Risk narrative

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.10+
- **PostgreSQL** running locally
- **Groq API Key** (free at https://console.groq.com/keys)

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd aivoa-complaint-system
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and DATABASE_URL
```

### 3. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE complaint_mgmt;"

# Tables are auto-created on first run
```

### 4. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

## 📋 Usage Demo

### 1. Paste a Complaint
In the Copilot panel, paste text like:
```
Apollo Pharmacy reported discolored capsules in Amoxicillin Capsules 500 mg.
Batch number AMX240602. Manufacturing date March 2026. Expiry date February 2028.
Please log this complaint.
```

### 2. AI Extracts & Fills the Form
The Copilot extracts all fields and populates the form automatically. The status changes from "Pending Triage" to "Ready to Commit".

### 3. Make Corrections
Type corrections naturally:
```
Sorry, the batch number is BMX240602 and affected quantity is 48 capsules
```

### 4. Commit to QMS Ledger
Click "Commit to QMS Ledger" to save to the database.

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment config
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # ORM models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── complaints.py    # CRUD endpoints
│   │   │   └── copilot.py       # AI chat endpoint
│   │   ├── services/
│   │   │   ├── ai_agent.py      # LangGraph workflow
│   │   │   ├── groq_client.py   # Groq API wrapper
│   │   │   ├── complaint_parser.py
│   │   │   └── risk_assessor.py
│   │   └── utils/
│   │       └── file_parser.py   # PDF/text extraction
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── store/               # Redux slices
│       ├── components/          # React components
│       └── services/api.js      # Axios client
├── sample_data/                 # Sample complaint files
└── README.md
```

## 🤖 LangGraph Agent Workflow

```
receive_input → classify_intent → [extract | correct | question] → assess_risk → format_response
```

The agent classifies user intent and routes to the appropriate processing path:
- **New Complaint**: Extracts all fields from unstructured text
- **Correction**: Updates only the specified fields
- **Question**: Answers QMS-related queries
- **Completeness Check**: Validates mandatory fields

## 📝 License

Built for AIVOA Round 1 AI Product Engineer (Interns) Assessment.
