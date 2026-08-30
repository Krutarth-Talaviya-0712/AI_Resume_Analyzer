"""
job_suggester.py
----------------
Suggests relevant job roles based on detected resume skills using
TF-IDF vectorization and cosine similarity.

The job role catalog is embedded in this module — no external API
or database query is required. Each role maps to a set of expected
skills and keywords. The candidate's detected skills are compared
against each role's skill profile to produce a ranked list with
match percentages.
"""

from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# Job Role Catalog
# Each entry: role title -> list of representative skills/keywords
# ---------------------------------------------------------------------------

JOB_CATALOG: Dict[str, List[str]] = {
    "Software Engineer": [
        "python", "java", "javascript", "c++", "algorithms", "data structures",
        "git", "api", "rest", "backend", "frontend", "testing", "agile",
        "sql", "database", "code review", "system design",
    ],
    "Frontend Developer": [
        "javascript", "typescript", "react", "vue", "angular", "html", "css",
        "tailwindcss", "bootstrap", "responsive design", "webpack", "vite",
        "redux", "graphql", "ui", "ux", "accessibility",
    ],
    "Backend Developer": [
        "python", "java", "nodejs", "flask", "django", "fastapi", "express",
        "spring", "rest api", "graphql", "sql", "postgresql", "mysql",
        "mongodb", "redis", "docker", "microservices",
    ],
    "Full Stack Developer": [
        "javascript", "typescript", "react", "nodejs", "python", "flask",
        "django", "sql", "mongodb", "rest api", "docker", "git",
        "html", "css", "agile",
    ],
    "Data Scientist": [
        "python", "pandas", "numpy", "scikit-learn", "machine learning",
        "deep learning", "statistics", "data analysis", "visualization",
        "matplotlib", "seaborn", "tensorflow", "pytorch", "sql",
        "feature engineering", "model evaluation",
    ],
    "Machine Learning Engineer": [
        "python", "tensorflow", "pytorch", "scikit-learn", "deep learning",
        "nlp", "computer vision", "mlflow", "model deployment",
        "kubernetes", "docker", "data pipelines", "feature engineering",
        "huggingface", "langchain",
    ],
    "Data Engineer": [
        "python", "spark", "hadoop", "airflow", "sql", "etl", "data pipelines",
        "kafka", "aws", "gcp", "azure", "postgresql", "mongodb",
        "data warehousing", "dbt", "snowflake",
    ],
    "Data Analyst": [
        "python", "sql", "excel", "tableau", "power bi", "data analysis",
        "statistics", "visualization", "pandas", "reporting",
        "business intelligence", "data cleaning",
    ],
    "DevOps Engineer": [
        "docker", "kubernetes", "jenkins", "ci/cd", "aws", "azure", "gcp",
        "terraform", "ansible", "linux", "bash", "monitoring", "nginx",
        "git", "infrastructure as code", "helm",
    ],
    "Cloud Solutions Architect": [
        "aws", "azure", "gcp", "cloud architecture", "terraform", "docker",
        "kubernetes", "microservices", "security", "networking", "cost optimization",
        "serverless", "lambda", "s3", "vpc",
    ],
    "Cybersecurity Analyst": [
        "cybersecurity", "penetration testing", "network security", "siem",
        "firewalls", "intrusion detection", "vulnerability assessment",
        "encryption", "compliance", "forensics", "python", "linux",
    ],
    "Mobile Developer (Android)": [
        "android", "kotlin", "java", "android studio", "rest api",
        "sqlite", "firebase", "jetpack compose", "mvvm", "git",
    ],
    "Mobile Developer (iOS)": [
        "ios", "swift", "objective-c", "xcode", "swiftui", "rest api",
        "core data", "firebase", "mvvm", "git",
    ],
    "React Native Developer": [
        "react native", "javascript", "typescript", "expo", "rest api",
        "redux", "firebase", "mobile development", "android", "ios",
    ],
    "UI/UX Designer": [
        "figma", "sketch", "adobe xd", "photoshop", "illustrator",
        "user research", "wireframing", "prototyping", "usability testing",
        "design systems", "typography", "branding", "accessibility",
    ],
    "Product Manager": [
        "product management", "roadmap", "agile", "scrum", "stakeholder",
        "user stories", "jira", "analytics", "strategy", "kpi",
        "market research", "prioritization", "leadership",
    ],
    "Project Manager": [
        "project management", "agile", "scrum", "jira", "budget",
        "risk management", "team leadership", "stakeholder management",
        "microsoft project", "communication", "pmp",
    ],
    "QA Engineer": [
        "testing", "selenium", "cypress", "jest", "pytest", "api testing",
        "postman", "test automation", "bug tracking", "jira", "agile",
        "performance testing", "load testing",
    ],
    "Embedded Systems Engineer": [
        "c", "c++", "embedded", "rtos", "microcontrollers", "arduino",
        "raspberry pi", "assembly", "hardware", "firmware", "uart", "spi",
    ],
    "Blockchain Developer": [
        "solidity", "ethereum", "web3", "smart contracts", "blockchain",
        "javascript", "python", "defi", "nft", "cryptography",
    ],
    "Site Reliability Engineer": [
        "linux", "python", "go", "docker", "kubernetes", "prometheus",
        "grafana", "ci/cd", "incident management", "automation",
        "observability", "aws", "scalability",
    ],
    "AI Research Engineer": [
        "python", "pytorch", "tensorflow", "nlp", "computer vision",
        "transformers", "huggingface", "research", "mathematics",
        "statistics", "arxiv", "deep learning",
    ],
    "Database Administrator": [
        "sql", "postgresql", "mysql", "oracle", "mssql", "backup",
        "performance tuning", "indexing", "replication", "stored procedures",
        "query optimization", "nosql",
    ],
    "Business Analyst": [
        "business analysis", "requirements gathering", "sql", "excel",
        "tableau", "stakeholder", "jira", "agile", "process improvement",
        "documentation", "communication",
    ],
    "Technical Writer": [
        "technical writing", "documentation", "markdown", "api documentation",
        "confluence", "notion", "editing", "communication", "research",
        "user manuals", "swagger",
    ],
    "Network Engineer": [
        "cisco", "networking", "tcp/ip", "routing", "switching", "firewalls",
        "vpn", "dns", "dhcp", "linux", "bgp", "ospf", "network security",
    ],
    "Game Developer": [
        "unity", "unreal engine", "c#", "c++", "game design", "3d modeling",
        "physics", "animation", "opengl", "directx", "blender",
    ],
    "Scrum Master": [
        "scrum", "agile", "sprint planning", "retrospectives", "jira",
        "team facilitation", "conflict resolution", "stakeholder",
        "kanban", "csm", "coaching",
    ],
    "Data Architect": [
        "data modeling", "sql", "nosql", "etl", "data warehousing",
        "snowflake", "redshift", "big data", "data governance",
        "spark", "kafka", "schema design",
    ],
    "Platform Engineer": [
        "kubernetes", "docker", "terraform", "aws", "azure", "python",
        "go", "linux", "ci/cd", "observability", "internal tools",
        "microservices", "service mesh",
    ],
}


def suggest_jobs(detected_skills: List[str], top_n: int = 6) -> List[Dict]:
    """
    Suggest the most relevant job roles for a resume based on detected skills.

    Uses TF-IDF vectorization and cosine similarity to compare the candidate's
    skill set against each job role's expected skill profile.

    Parameters
    ----------
    detected_skills : list of str
        Combined list of technical and soft skills extracted from the resume.
    top_n : int
        Number of top job suggestions to return (default 6).

    Returns
    -------
    list of dict, each containing:
        - title: str — job role title
        - match_score: int — percentage match (0-100)
        - matched_skills: list[str] — skills present in both resume and role
        - missing_skills: list[str] — top skills the resume is missing for this role
    """
    if not detected_skills:
        return _fallback_suggestions(top_n)

    candidate_text = " ".join(detected_skills).lower()

    role_titles = list(JOB_CATALOG.keys())
    role_texts = [" ".join(skills) for skills in JOB_CATALOG.values()]

    # Build corpus: candidate text + all role profiles
    corpus = [candidate_text] + role_texts

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, analyzer="word")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Cosine similarity between candidate (index 0) and each role
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Rank roles by similarity
    ranked_indices = similarities.argsort()[::-1][:top_n]

    results = []
    candidate_set = set(s.lower() for s in detected_skills)

    for idx in ranked_indices:
        role_title = role_titles[idx]
        role_skills = [s.lower() for s in JOB_CATALOG[role_title]]
        match_score = round(float(similarities[idx]) * 100)

        # Clamp: a perfect match should not exceed 98 to stay realistic
        match_score = min(match_score, 98)

        matched = [s for s in role_skills if any(s in cs or cs in s for cs in candidate_set)]
        missing = [s for s in role_skills if s not in matched][:5]

        results.append({
            "title": role_title,
            "match_score": match_score,
            "matched_skills": matched[:8],
            "missing_skills": missing,
        })

    return results


def _fallback_suggestions(top_n: int) -> List[Dict]:
    """Return generic suggestions when no skills are detected."""
    generic = [
        "Software Engineer", "Data Analyst", "Business Analyst",
        "Project Manager", "Technical Writer",
    ]
    return [
        {
            "title": role,
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": JOB_CATALOG.get(role, [])[:5],
        }
        for role in generic[:top_n]
    ]
