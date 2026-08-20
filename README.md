# AI Resume Analyzer & Builder

<div align="center">

![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

A full-stack, ATS-friendly resume creation and analysis platform. Build professional, highly tailored resumes in minutes with 50+ modern layouts, real-time live preview, section reordering, and direct PDF downloads.

[Features](#-key-features) • [Tech Stack](#-tech-stack) • [Project Structure](#-project-structure) • [Getting Started](#-getting-started) • [API Documentation](#-api-endpoints) • [Author](#-author)

</div>

---

## 🚀 Key Features

- **50+ Professional Templates**: Choose from a wide collection of modern, classic, creative, and technical resume designs optimized for ATS parsing.
- **Split-Screen Live Editor**: Edit resume details (experience, education, projects, skills, certifications, custom sections) on the left panel with instant visual feedback on the right.
- **Dynamic Section Management**: Add, remove, and reorder sections (Summary, Experience, Education, Projects, Skills, Languages, Certifications, Interests) on the fly.
- **1-Click PDF Generation**: High-fidelity, print-safe vector/A4 PDF export powered by `html2pdf.js`.
- **JWT Authentication & Cloud Storage**: Secure user authentication (Bcrypt + JWT) allowing users to save, manage, reload, and update multiple resume versions.
- **Modern Responsive Design**: Glassmorphism UI elements, dark/light accents, and smooth micro-interactions built with Tailwind CSS.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS, PostCSS, Autoprefixer
- **Routing**: React Router v6
- **Icons**: React Icons
- **PDF Export**: `html2pdf.js` / HTML5 Canvas / jsPDF
- **HTTP Client**: Axios (with centralized JWT interceptors)

### Backend
- **Framework**: Flask (Python)
- **Database ORM**: Flask-SQLAlchemy (SQLite / PostgreSQL ready)
- **Authentication**: Flask-JWT-Extended, Flask-Bcrypt
- **CORS**: Flask-CORS
- **Configuration**: `python-dotenv`
- **NLP / Parsing Libraries**: `pdfplumber`, `python-docx`, `spacy`, `scikit-learn`

---

## 📁 Project Structure

```text
AI_Resume_Analyer/
├── backend/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth_routes.py         # Signup, login, profile routes
│   ├── create_resume/
│   │   ├── __init__.py
│   │   └── resume_routes.py       # CRUD operations for resumes
│   ├── app.py                     # Flask application factory & config
│   ├── extensions.py              # DB, JWT, and Bcrypt instances
│   ├── models.py                  # SQLAlchemy models (User, Resume, Analysis)
│   ├── requirements.txt           # Python dependencies
│   └── .env.example               # Backend environment template
│
├── frontend/
│   ├── public/                    # Static assets
│   ├── src/
│   │   ├── context/
│   │   │   └── AuthContext.jsx    # Global authentication & user state
│   │   ├── features/
│   │   │   ├── create-resume/     # Resume builder, editor & 50+ templates
│   │   │   ├── login/             # Login view & authentication flow
│   │   │   ├── signup/            # Registration view & validation
│   │   │   └── resume/            # "My Resumes" dashboard view
│   │   ├── shared/
│   │   │   ├── components/        # Navbar, ProtectedRoute, EditableField
│   │   │   ├── pages/             # Landing / Home page
│   │   │   └── utils/             # Axios instance & sample starter data
│   │   ├── App.jsx                # Router configuration
│   │   ├── main.jsx               # React DOM root
│   │   └── index.css              # Global styles & print utilities
│   ├── package.json               # Frontend dependencies & scripts
│   ├── tailwind.config.js         # Tailwind theme configuration
│   ├── vite.config.js             # Vite bundler configuration
│   └── .env.example               # Frontend environment template
│
├── .gitignore                     # Git exclusion rules
├── LICENSE                        # MIT License
└── README.md                      # Documentation
```

---

## ⚡ Getting Started

### Prerequisites
- **Node.js** (v18.x or higher) & **npm**
- **Python** (v3.10 or higher) & **pip**
- **Git**

---

### 1. Backend Setup

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate

   # On Windows (PowerShell):
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   *(Optionally customize `JWT_SECRET_KEY` and `DATABASE_URL` in `.env`)*

5. Run the Flask backend server:
   ```bash
   python app.py
   ```
   The backend API will start at `http://localhost:5000`.

---

### 2. Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. (Optional) Set up client environment variables:
   ```bash
   cp .env.example .env
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   Open your browser at `http://localhost:5173`.

---

## 📡 API Endpoints

### Authentication (`/api/auth`)
| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/signup` | No | Register a new user account |
| `POST` | `/login` | No | Authenticate user & return JWT token |
| `GET` | `/me` | Yes (Bearer) | Fetch logged-in user profile |

### Resume Management (`/api/resume`)
| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/` | Yes (Bearer) | Save a new resume |
| `GET` | `/` | Yes (Bearer) | List all resumes belonging to user |
| `GET` | `/:id` | Yes (Bearer) | Fetch full resume details & content |
| `PUT` | `/:id` | Yes (Bearer) | Update an existing resume |
| `DELETE` | `/:id` | Yes (Bearer) | Delete a resume |

---

## 🔮 Roadmap

- [x] 50+ responsive resume layout templates
- [x] Live interactive preview & quick section reordering
- [x] Client-side A4 PDF generation
- [x] JWT authentication and resume cloud persistence
- [ ] AI ATS Resume Parser & Score analyzer
- [ ] Job Description Keyword Matcher & Gap Analysis
- [ ] AI Cover Letter Generator

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more details.

---

## 👤 Author

**Krutarth Talaviya**
- GitHub: [@Krutarth-Talaviya-0712](https://github.com/Krutarth-Talaviya-0712)
- Email: [krutarthtalaviya11@gmail.com](mailto:krutarthtalaviya11@gmail.com)

---

<div align="center">
  <sub>Built with ❤️ by Krutarth Talaviya</sub>
</div>
