"""
nlp_pipeline.py
---------------
spaCy-based NLP pipeline for resume analysis.

Responsibilities:
  - Lazy-load the spaCy model once per process (thread-safe singleton)
  - Detect resume sections by scanning for common header keywords
  - Extract skills, tools, programming languages, and soft skills
    using a curated vocabulary matched against the document tokens
  - Extract named entities: ORG, GPE, PERSON, DATE for context signals
"""

import re
from functools import lru_cache
from typing import Dict, List

# ---------------------------------------------------------------------------
# Curated skill vocabulary
# ---------------------------------------------------------------------------

TECHNICAL_SKILLS = {
    # Programming languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go",
    "rust", "swift", "kotlin", "ruby", "php", "r", "scala", "matlab",
    "perl", "bash", "shell", "powershell", "dart", "lua", "haskell",
    # Web / Frontend
    "html", "css", "react", "vue", "angular", "nextjs", "nuxtjs",
    "tailwindcss", "bootstrap", "jquery", "webpack", "vite", "sass", "less",
    "redux", "graphql", "rest", "restful", "soap",
    # Backend / Frameworks
    "flask", "django", "fastapi", "express", "spring", "laravel", "rails",
    "node", "nodejs", "asp.net", ".net", "gin", "fiber",
    # Databases
    "mysql", "postgresql", "sqlite", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "oracle", "mssql", "firebase", "supabase",
    "neo4j", "influxdb",
    # Cloud / DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github actions", "ci/cd", "linux", "nginx", "apache",
    "heroku", "vercel", "netlify", "cloudflare",
    # Data / ML / AI
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "matplotlib", "seaborn", "spark", "hadoop", "airflow", "mlflow",
    "langchain", "huggingface", "openai", "data analysis", "data science",
    "statistics", "regression", "classification", "clustering",
    # Tools / Platforms
    "git", "github", "gitlab", "bitbucket", "jira", "confluence",
    "postman", "figma", "photoshop", "illustrator", "xd", "slack",
    "notion", "trello", "linux", "macos", "windows",
    # Mobile
    "android", "ios", "react native", "flutter", "xamarin",
    # Security
    "cybersecurity", "penetration testing", "oauth", "jwt", "ssl", "tls",
    "encryption", "firewalls", "siem",
}

SOFT_SKILLS = {
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "project management", "presentation", "negotiation",
    "mentoring", "analytical", "detail oriented", "self motivated",
    "customer service", "conflict resolution", "decision making",
}

# Resume section header keywords mapped to canonical section names
SECTION_HEADERS = {
    "experience": "experience",
    "work experience": "experience",
    "employment": "experience",
    "professional experience": "experience",
    "work history": "experience",
    "career history": "experience",
    "education": "education",
    "academic background": "education",
    "qualifications": "education",
    "skills": "skills",
    "technical skills": "skills",
    "core competencies": "skills",
    "competencies": "skills",
    "expertise": "skills",
    "summary": "summary",
    "profile": "summary",
    "objective": "summary",
    "professional summary": "summary",
    "about me": "summary",
    "career objective": "summary",
    "projects": "projects",
    "personal projects": "projects",
    "academic projects": "projects",
    "certifications": "certifications",
    "certificates": "certifications",
    "awards": "certifications",
    "achievements": "certifications",
    "languages": "languages",
    "interests": "interests",
    "hobbies": "interests",
    "publications": "publications",
    "volunteer": "volunteer",
    "contact": "contact",
    "references": "references",
}


@lru_cache(maxsize=1)
def _load_model():
    """Load spaCy model once and cache it for the process lifetime."""
    try:
        import spacy
        return spacy.load("en_core_web_sm")
    except OSError:
        # Model not downloaded; fall back to blank model
        import spacy
        return spacy.blank("en")


def analyze_resume_text(text: str) -> Dict:
    """
    Run the full NLP pipeline on extracted resume text.

    Returns a dictionary containing:
      - detected_sections: list of canonical section names found
      - technical_skills: list of detected technical skills
      - soft_skills: list of detected soft skills
      - entities: dict with lists of ORG, GPE, DATE, PERSON entities
      - word_count: total word count
      - sentence_count: total sentence count
      - has_email: bool
      - has_phone: bool
      - has_url: bool
      - bullet_count: approximate number of bullet/list items
      - quantification_count: number of quantified achievements (numbers/%)
    """
    nlp = _load_model()

    # spaCy has a default max_length of 1,000,000 — trim if needed
    truncated_text = text[:500_000]
    doc = nlp(truncated_text)

    return {
        "detected_sections": _detect_sections(text),
        "technical_skills": _extract_technical_skills(text),
        "soft_skills": _extract_soft_skills(text),
        "entities": _extract_entities(doc),
        "word_count": len([t for t in doc if not t.is_space]),
        "sentence_count": len(list(doc.sents)),
        "has_email": bool(re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)),
        "has_phone": bool(
            re.search(
                r"(\+?\d[\d\s\-().]{7,}\d)", text
            )
        ),
        "has_url": bool(
            re.search(
                r"(https?://|www\.|linkedin\.com|github\.com)", text, re.IGNORECASE
            )
        ),
        "bullet_count": _count_bullets(text),
        "quantification_count": _count_quantifications(text),
    }


def _detect_sections(text: str) -> List[str]:
    """
    Scan text line-by-line for section headers.
    A line is considered a section header if it is short (<= 60 chars)
    and matches a known section keyword (case-insensitive).
    """
    found = set()
    for line in text.splitlines():
        stripped = line.strip().rstrip(":").lower()
        if stripped and len(stripped) <= 60:
            if stripped in SECTION_HEADERS:
                found.add(SECTION_HEADERS[stripped])
            else:
                # Partial match: check if the line contains a header keyword
                for header, canonical in SECTION_HEADERS.items():
                    if header in stripped and len(stripped) < len(header) + 10:
                        found.add(canonical)
                        break
    return sorted(found)


def _extract_technical_skills(text: str) -> List[str]:
    """Match curated technical skill keywords against the resume text."""
    text_lower = text.lower()
    found = []
    for skill in TECHNICAL_SKILLS:
        # Use word-boundary-aware match for single-word skills
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def _extract_soft_skills(text: str) -> List[str]:
    """Match curated soft skill keywords against the resume text."""
    text_lower = text.lower()
    found = []
    for skill in SOFT_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def _extract_entities(doc) -> Dict[str, List[str]]:
    """Extract named entities grouped by type."""
    entities: Dict[str, List[str]] = {
        "organizations": [],
        "locations": [],
        "dates": [],
        "persons": [],
    }
    label_map = {
        "ORG": "organizations",
        "GPE": "locations",
        "DATE": "dates",
        "PERSON": "persons",
    }
    seen = set()
    for ent in doc.ents:
        key = label_map.get(ent.label_)
        if key:
            text_val = ent.text.strip()
            dedup_key = (key, text_val.lower())
            if dedup_key not in seen and text_val:
                entities[key].append(text_val)
                seen.add(dedup_key)
    return entities


def _count_bullets(text: str) -> int:
    """Count lines that look like bullet points."""
    bullet_pattern = re.compile(r"^\s*[-*•·▪▸►→>]\s+\S")
    return sum(1 for line in text.splitlines() if bullet_pattern.match(line))


def _count_quantifications(text: str) -> int:
    """
    Count achievement statements that include numeric quantification.
    Examples: 'improved by 30%', 'managed 15 engineers', '$1.2M revenue'.
    """
    quant_pattern = re.compile(
        r"(\b\d[\d,]*\.?\d*\s*(%|percent|million|billion|k\b|m\b|\+))"
        r"|(\$[\d,]+)"
        r"|\b(\d+)\s+(engineers?|developers?|teams?|projects?|clients?|users?|members?|years?|months?)",
        re.IGNORECASE,
    )
    return len(quant_pattern.findall(text))
