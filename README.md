# AI Resume Analyzer & Builder

<div align="center">

![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-3.7-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

A full-stack, ATS-friendly resume creation and analysis platform. Build professional resumes in minutes using 50+ modern layouts, then upload any existing resume to receive an ATS score, a detailed NLP-powered quality report, and job role suggestions — all without any external API subscriptions.

[Features](#key-features) &bull; [Tech Stack](#tech-stack) &bull; [Architecture](#ml-architecture) &bull; [Project Structure](#project-structure) &bull; [Getting Started](#getting-started) &bull; [API Reference](#api-reference) &bull; [Author](#author)

</div>

---

## Key Features

- **50+ Professional Templates** — Modern, classic, creative, and technical resume layouts optimized for ATS parsing and PDF export.
- **Split-Screen Live Editor** — Edit experience, education, projects, skills, certifications, and custom sections with instant live preview.
- **Dynamic Section Management** — Add, remove, and reorder any section on the fly without reloading.
- **One-Click PDF Generation** — High-fidelity A4 PDF export powered by `html2pdf.js`.
- **AI Resume Analyzer** — Upload a PDF or DOCX resume and receive:
  - ATS Score (0-100) broken down across five weighted factors
  - Overall quality score covering skill breadth, experience completeness, and language quality
  - Specific strengths and prioritized improvement recommendations
  - Detected skills, named entities, and document statistics
- **Job Role Suggestions** — TF-IDF cosine similarity matching against a 30-role curated catalog, with matched and missing skill breakdowns.
- **Site Assistant Chatbot** — Floating chat widget that answers questions about the platform features, analyzer, pricing, and usage.
- **JWT Authentication** — Secure signup/login with bcrypt password hashing and 7-day access tokens.
- **Cloud Resume Storage** — Save, reload, and manage multiple resume versions from your account dashboard.

---

## Tech Stack

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | React 18 with Vite |
| Styling | Tailwind CSS 3, PostCSS |
| Routing | React Router v6 |
| HTTP Client | Axios with centralized JWT interceptors |
| PDF Export | html2pdf.js / html2canvas / jsPDF |

### Backend
| Layer | Technology |
|-------|-----------|
| Framework | Flask 3.0 (Python) |
| ORM | Flask-SQLAlchemy (SQLite / PostgreSQL) |
| Authentication | Flask-JWT-Extended, Flask-Bcrypt |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| NLP Engine | spaCy 3.7 (en_core_web_sm) |
| ML Scoring | scikit-learn (TF-IDF, cosine similarity) |
| CORS | Flask-CORS |

---

## ML Architecture

### Resume Analysis Pipeline

```
Upload (PDF/DOCX)
       |
       v
Text Extraction (pdfplumber / python-docx)
       |
       v
NLP Pipeline (spaCy en_core_web_sm)
  - Section header detection
  - Technical & soft skill extraction (curated vocabulary)
  - Named entity recognition (ORG, GPE, DATE)
  - Structural signals (bullets, quantification, word count)
       |
       v
Scoring Engine (heuristic + TF-IDF)
  +------ ATS Score (0-100) ------+
  | Contact info         (10 pts) |
  | Section structure    (25 pts) |
  | Keyword density      (30 pts) |
  | Formatting signals   (15 pts) |
  | Quantified wins      (20 pts) |
  +--------------------------------+
  +--- Overall Score (0-100) -----+
  | ATS score (40%)               |
  | Skill breadth (20%)           |
  | Experience quality (20%)      |
  | Language quality (10%)        |
  | Section coverage (10%)        |
  +--------------------------------+
       |
       v
Job Role Suggester (TF-IDF cosine similarity)
  - Candidate skill vector vs. 30-role catalog
  - Returns top 6 matches with matched/missing skills
       |
       v
Persist to Analysis table + Return JSON report
```

### Chatbot Architecture

The chatbot uses a lightweight keyword-intent matching system with 15 defined intents covering all platform features. No external API is required; all responses are pre-written and matched via regex pattern scoring.

---

## Project Structure

```text
AI_Resume_Analyer/
├── backend/
│   ├── analyze/
│   │   ├── __init__.py
│   │   ├── analyze_routes.py      # Upload endpoint, history endpoints
│   │   ├── extractor.py           # PDF/DOCX text extraction
│   │   ├── nlp_pipeline.py        # spaCy NLP: sections, skills, entities
│   │   ├── scorer.py              # ATS + overall score computation
│   │   └── job_suggester.py       # TF-IDF job role matching (30 roles)
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth_routes.py         # Signup, login, profile
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── chatbot_routes.py      # POST /api/chatbot/message
│   │   └── intent_handler.py      # Keyword-based intent matching (15 intents)
│   ├── create_resume/
│   │   ├── __init__.py
│   │   └── resume_routes.py       # Resume CRUD
│   ├── app.py                     # Flask application factory
│   ├── extensions.py              # DB, JWT, Bcrypt singletons
│   ├── models.py                  # User, Resume, Analysis models
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── features/
│   │   │   ├── analyze/
│   │   │   │   ├── AnalyzePage.jsx              # Drag-and-drop upload + results
│   │   │   │   └── components/
│   │   │   │       ├── ScoreRing.jsx            # Animated SVG circular progress ring
│   │   │   │       ├── AnalysisReport.jsx       # Section/skill/feedback breakdown
│   │   │   │       └── JobSuggestions.jsx       # Job role match cards
│   │   │   ├── create-resume/
│   │   │   ├── login/
│   │   │   ├── resume/
│   │   │   └── signup/
│   │   ├── shared/
│   │   │   ├── components/
│   │   │   │   ├── ChatbotWidget.jsx            # Floating site assistant chatbot
│   │   │   │   ├── EditableField.jsx
│   │   │   │   ├── Navbar.jsx
│   │   │   │   └── ProtectedRoute.jsx
│   │   │   ├── pages/
│   │   │   │   └── Home.jsx
│   │   │   └── utils/
│   │   │       ├── api.js
│   │   │       └── dummyData.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## Getting Started

### Prerequisites
- Node.js v18+ and npm
- Python 3.10+ and pip
- Git

---

### 1. Clone the Repository

```bash
git clone https://github.com/Krutarth-Talaviya-0712/AI_Resume_Analyer.git
cd AI_Resume_Analyer
```

---

### 2. Backend Setup

```bash
cd backend
```

Create and activate a virtual environment:

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Download the spaCy language model (required for the NLP pipeline):

```bash
python -m spacy download en_core_web_sm
```

Configure environment variables:

```bash
cp .env.example .env
```

Start the backend server:

```bash
python app.py
```

The API will be available at `http://localhost:5000`. Database tables are created automatically on first run.

---

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend
npm install
```

Optionally copy the environment file:

```bash
cp .env.example .env
```

Start the development server:

```bash
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## API Reference

### Authentication — `/api/auth`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/signup` | No | Register a new user account |
| POST | `/login` | No | Authenticate and receive a JWT |
| GET | `/me` | Bearer | Fetch authenticated user profile |

### Resume Management — `/api/resume`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/` | Bearer | Save a new resume |
| GET | `/` | Bearer | List all resumes for the user |
| GET | `/<id>` | Bearer | Fetch resume with full content |
| PUT | `/<id>` | Bearer | Update an existing resume |
| DELETE | `/<id>` | Bearer | Delete a resume |

### Resume Analysis — `/api/analyze`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/upload` | Bearer | Upload PDF/DOCX, run ML pipeline, return full report |
| GET | `/history` | Bearer | List past analysis records (last 20) |
| GET | `/history/<id>` | Bearer | Fetch full report for a specific past analysis |

**Upload request**: `multipart/form-data` with field name `resume` (PDF or DOCX, max 5 MB).

**Response fields**: `ats_score`, `overall_score`, `ats_breakdown`, `overall_breakdown`, `strengths`, `improvements`, `technical_skills`, `soft_skills`, `detected_sections`, `entities`, `stats`, `job_suggestions`.

### Chatbot — `/api/chatbot`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/message` | No | Send a message, receive a platform-related response |

**Request**: `{ "message": "How does the ATS score work?" }`
**Response**: `{ "reply": "ATS stands for..." }`

---

## Roadmap

- [x] 50+ responsive resume layout templates
- [x] Live interactive preview and section reordering
- [x] Client-side A4 PDF generation
- [x] JWT authentication and resume cloud persistence
- [x] AI ATS Resume Analyzer with ML scoring pipeline
- [x] Job role suggestions via TF-IDF cosine similarity
- [x] Site assistant chatbot

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built by Krutarth Talaviya</sub>
</div>
