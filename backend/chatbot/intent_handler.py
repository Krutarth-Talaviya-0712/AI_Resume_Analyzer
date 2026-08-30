"""
intent_handler.py
-----------------
Rule-based intent recognition and response generation for the site chatbot.

This module handles questions about the ResumeCraft platform itself:
features, how to use the analyzer, pricing, templates, etc.

No external AI API is used. Responses are matched by scanning the user
message for keyword patterns associated with known intents. Multiple
intents can match; the highest-confidence match wins.
"""

import re
from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# Intent definitions
# Each intent has:
#   - keywords: list of regex patterns (case-insensitive) that trigger this intent
#   - response: the reply to send
# ---------------------------------------------------------------------------

INTENTS = [
    {
        "id": "greeting",
        "patterns": [r"\bhello\b", r"\bhi\b", r"\bhey\b", r"\bgreetings\b", r"\bgood\s+(morning|evening|afternoon)\b"],
        "response": (
            "Hello! I am the ResumeCraft assistant. I can help you understand how this platform works, "
            "what features are available, and how to get the most out of your resume analysis. "
            "What would you like to know?"
        ),
    },
    {
        "id": "what_is_resumecraft",
        "patterns": [
            r"what is (this|resumecraft|the (app|platform|tool|website|site))",
            r"(tell me|explain).*(about|what).*(this|resumecraft)",
            r"how does (this|resumecraft|the app) work",
        ],
        "response": (
            "ResumeCraft is an AI-powered resume builder and analyzer. "
            "You can create professional resumes using 50+ templates, export them as PDF, "
            "and upload your existing resume to get an ATS score, a detailed quality analysis, "
            "and personalized job role suggestions — all without any external subscriptions."
        ),
    },
    {
        "id": "resume_analyzer",
        "patterns": [
            r"\banalyze\b", r"\banalysis\b", r"\banalyzer\b",
            r"\bats\s*score\b", r"\bats\b",
            r"(how|can i).*(analyze|check|scan|review|score).*(resume|cv)",
            r"(upload|submit).*(resume|cv)",
        ],
        "response": (
            "The Resume Analyzer lets you upload your resume as a PDF or DOCX file. "
            "It then extracts the text, runs it through an NLP pipeline, and produces:\n\n"
            "- An ATS Score (0-100) showing how well your resume will perform with Applicant Tracking Systems\n"
            "- An Overall Score assessing quality, skill breadth, and experience completeness\n"
            "- A list of strengths and specific improvements\n"
            "- Job role suggestions matched to your skills\n\n"
            "To get started, click the 'Analyze Resume' link in the navigation bar."
        ),
    },
    {
        "id": "ats_score_explain",
        "patterns": [
            r"what is (an? )?ats",
            r"what does ats (mean|stand for|score mean)",
            r"ats (score|meaning|explanation)",
            r"applicant tracking",
        ],
        "response": (
            "ATS stands for Applicant Tracking System. Most companies use ATS software to "
            "automatically filter and rank resumes before a human ever reads them. "
            "An ATS Score of 70 or above generally means your resume is well-structured, "
            "has relevant keywords, and is easy to parse. "
            "Our analyzer evaluates contact info, section presence, keyword density, "
            "formatting signals, and quantified achievements to compute your score."
        ),
    },
    {
        "id": "templates",
        "patterns": [
            r"\btemplate(s)?\b",
            r"(how many|what kind of|which).*(design|layout|format|template)",
            r"(choose|pick|select).*(template|design|layout)",
        ],
        "response": (
            "ResumeCraft offers 50+ professional resume templates spanning categories like:\n\n"
            "- Classic and minimalist designs for corporate roles\n"
            "- Modern and creative layouts for design or startup positions\n"
            "- Technical and developer-focused formats with skills grids\n"
            "- Academic and research-oriented templates\n\n"
            "All templates are ATS-friendly and export cleanly to PDF."
        ),
    },
    {
        "id": "how_to_create_resume",
        "patterns": [
            r"(how|how do i|how to).*(create|make|build|write|start).*(resume|cv)",
            r"(create|build|make).*(resume|cv)",
            r"\bresume builder\b",
        ],
        "response": (
            "Creating a resume on ResumeCraft is straightforward:\n\n"
            "1. Sign up or log in to your account\n"
            "2. Click 'Create Resume' in the navigation bar\n"
            "3. Pick a template from the gallery\n"
            "4. Fill in your details in the live editor on the left\n"
            "5. See the result update in real time on the right\n"
            "6. Add, remove, or reorder sections as needed\n"
            "7. Download as a high-quality PDF when you are done\n\n"
            "Your resumes are saved to your account automatically."
        ),
    },
    {
        "id": "job_suggestions",
        "patterns": [
            r"job (suggestion|recommendation|match)",
            r"(suggest|recommend|find).*(job|role|position|career)",
            r"what jobs (am i|are) (suited|good|right) for",
            r"career (path|advice|guidance)",
        ],
        "response": (
            "After analyzing your resume, ResumeCraft matches your detected skills against "
            "a catalog of 30+ job roles using TF-IDF cosine similarity. "
            "For each suggested role you will see:\n\n"
            "- A percentage match score\n"
            "- Skills from your resume that align with the role\n"
            "- Skills you could add to improve your fit\n\n"
            "This helps you understand which roles you are already competitive for "
            "and where to focus your skill development."
        ),
    },
    {
        "id": "pricing",
        "patterns": [
            r"\bpric(e|ing|es)\b",
            r"\bcost\b",
            r"\bfree\b",
            r"\bpaid\b",
            r"\bsubscri(be|ption)\b",
            r"(is it|is this).*(free|paid|cost money)",
        ],
        "response": (
            "ResumeCraft is completely free to use. There are no subscription fees, "
            "no hidden charges, and no feature gates. "
            "All features — resume builder, PDF export, AI analyzer, and job suggestions — "
            "are available to every registered user at no cost."
        ),
    },
    {
        "id": "signup_login",
        "patterns": [
            r"\b(sign ?up|register|create account|join)\b",
            r"\b(log ?in|login|sign ?in)\b",
            r"(how|how do i).*(sign up|register|create an account|log in)",
        ],
        "response": (
            "Creating an account takes less than a minute. "
            "Click 'Sign Up Free' in the navigation bar, enter your name, username, email, "
            "and password, and you are ready to go. "
            "If you already have an account, click 'Login' and sign in with your email or username."
        ),
    },
    {
        "id": "pdf_export",
        "patterns": [
            r"\bpdf\b",
            r"(download|export|save).*(resume|cv)",
            r"(how|how do i).*(download|export|print).*(resume|cv)",
        ],
        "response": (
            "You can download your resume as a PDF directly from the Resume Builder. "
            "Click the 'Download PDF' button at the top of the builder page. "
            "The export renders a pixel-perfect A4 PDF while preserving all colors, "
            "fonts, and layout from your chosen template."
        ),
    },
    {
        "id": "file_formats",
        "patterns": [
            r"(what|which) file (type|format|extension)",
            r"\bdocx?\b",
            r"(upload|support|accept).*(format|type|file)",
            r"(pdf|docx|word).*(upload|support)",
        ],
        "response": (
            "The Resume Analyzer accepts PDF and DOCX (Microsoft Word) files up to 5 MB. "
            "Note that scanned image PDFs (photos of printed resumes) are not supported "
            "because they contain no machine-readable text. "
            "Always use a digitally created document for best results."
        ),
    },
    {
        "id": "my_resumes",
        "patterns": [
            r"\bmy resumes?\b",
            r"(saved|stored|cloud).*(resume|cv)",
            r"(where|how).*(find|access|view|see).*(my|saved).*(resume|cv)",
        ],
        "response": (
            "All resumes you create and save are stored securely in your account. "
            "Click 'My Resumes' in the navigation bar to view, open, or delete any saved resume. "
            "From there you can also open a resume back into the builder to continue editing."
        ),
    },
    {
        "id": "tech_stack",
        "patterns": [
            r"(tech|technology|stack|built with|made with)",
            r"(what|which).*(language|framework|library|tool).*(used|built|made)",
        ],
        "response": (
            "ResumeCraft is built with the following technologies:\n\n"
            "Frontend: React 18, Vite, TailwindCSS, React Router, Axios\n"
            "Backend: Python, Flask, Flask-JWT-Extended, Flask-SQLAlchemy\n"
            "Database: SQLite (development), PostgreSQL-ready\n"
            "NLP / ML: spaCy, scikit-learn, pdfplumber, python-docx\n\n"
            "The project is open source and available on GitHub."
        ),
    },
    {
        "id": "contact_author",
        "patterns": [
            r"\b(contact|reach|email|author|creator|developer|owner)\b",
            r"who (made|built|created|developed) (this|resumecraft)",
        ],
        "response": (
            "ResumeCraft was built by Krutarth Talaviya. "
            "You can reach out via GitHub at github.com/Krutarth-Talaviya-0712 "
            "or by email at krutarthtalaviya11@gmail.com."
        ),
    },
    {
        "id": "thank_you",
        "patterns": [r"\bthank(s| you)\b", r"\bthanks?\b", r"\bthx\b"],
        "response": (
            "You are welcome! If you have any other questions about ResumeCraft, "
            "feel free to ask. Good luck with your job search."
        ),
    },
    {
        "id": "goodbye",
        "patterns": [r"\b(bye|goodbye|see you|take care|later)\b"],
        "response": "Goodbye! Best of luck with your resume. Come back anytime.",
    },
]

FALLBACK_RESPONSE = (
    "I can answer questions about ResumeCraft's features, the resume analyzer, "
    "templates, PDF export, job suggestions, and account management. "
    "Could you rephrase your question or ask something more specific?"
)


def get_response(user_message: str) -> str:
    """
    Match the user message against known intents and return the best response.

    Parameters
    ----------
    user_message : str
        The raw message text from the user.

    Returns
    -------
    str
        A relevant, pre-written response string.
    """
    if not user_message or not user_message.strip():
        return FALLBACK_RESPONSE

    message_lower = user_message.lower().strip()

    best_intent_id, best_match_count = _match_intents(message_lower)

    if best_intent_id and best_match_count > 0:
        for intent in INTENTS:
            if intent["id"] == best_intent_id:
                return intent["response"]

    return FALLBACK_RESPONSE


def _match_intents(message: str) -> Tuple[Optional[str], int]:
    """
    Score all intents against the message and return the best-matching one.

    Returns (intent_id, match_count) for the top match.
    """
    best_id: Optional[str] = None
    best_count = 0

    for intent in INTENTS:
        count = sum(
            1 for pattern in intent["patterns"]
            if re.search(pattern, message, re.IGNORECASE)
        )
        if count > best_count:
            best_count = count
            best_id = intent["id"]

    return best_id, best_count
