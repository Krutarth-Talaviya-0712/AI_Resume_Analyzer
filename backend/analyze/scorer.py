"""
scorer.py
---------
Computes two scores for an analyzed resume:

  1. ATS Score (0-100)
     Simulates how well an Applicant Tracking System would parse and rank
     the resume based on structural signals and keyword presence.

  2. Overall Score (0-100)
     A holistic quality rating combining ATS fitness, skill breadth,
     experience completeness, language quality, and section coverage.

Both scores are derived from the NLP feature dictionary returned by
nlp_pipeline.analyze_resume_text(), with no external API calls.
"""

from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Scoring weights
# ---------------------------------------------------------------------------

# ATS sub-score weights (must sum to 100)
ATS_WEIGHTS = {
    "contact_info":      10,
    "sections":          25,
    "keyword_density":   30,
    "formatting":        15,
    "quantification":    20,
}

# Overall sub-score weights (must sum to 100)
OVERALL_WEIGHTS = {
    "ats_score":            40,
    "skill_breadth":        20,
    "experience_quality":   20,
    "language_quality":     10,
    "section_coverage":     10,
}

# Sections that carry the most weight in ATS parsing
HIGH_VALUE_SECTIONS = {"experience", "education", "skills"}
BONUS_SECTIONS = {"summary", "projects", "certifications"}

# Role-specific keyword sets used for keyword density scoring
ROLE_KEYWORD_SETS = {
    "software": {
        "python", "java", "javascript", "git", "api", "backend", "frontend",
        "database", "sql", "agile", "testing", "deploy", "code review",
    },
    "data": {
        "python", "pandas", "numpy", "machine learning", "data analysis",
        "sql", "visualization", "statistics", "model", "pipeline",
    },
    "devops": {
        "docker", "kubernetes", "ci/cd", "aws", "azure", "terraform",
        "ansible", "monitoring", "linux", "scripting", "automation",
    },
    "design": {
        "figma", "photoshop", "illustrator", "ux", "ui", "wireframe",
        "prototype", "user research", "typography", "branding",
    },
    "management": {
        "leadership", "project management", "agile", "scrum", "stakeholder",
        "roadmap", "strategy", "team", "budget", "kpi",
    },
}


def compute_scores(nlp_features: Dict) -> Dict:
    """
    Compute ATS and Overall scores from NLP feature dict.

    Parameters
    ----------
    nlp_features : dict
        Output of nlp_pipeline.analyze_resume_text()

    Returns
    -------
    dict with keys:
        ats_score, overall_score, ats_breakdown, overall_breakdown,
        strengths, improvements
    """
    ats_breakdown = _compute_ats_breakdown(nlp_features)
    ats_score = sum(ats_breakdown.values())

    overall_breakdown = _compute_overall_breakdown(nlp_features, ats_score)
    overall_score = sum(overall_breakdown.values())

    strengths, improvements = _generate_feedback(nlp_features, ats_breakdown, overall_breakdown)

    return {
        "ats_score": min(round(ats_score), 100),
        "overall_score": min(round(overall_score), 100),
        "ats_breakdown": {k: round(v, 1) for k, v in ats_breakdown.items()},
        "overall_breakdown": {k: round(v, 1) for k, v in overall_breakdown.items()},
        "strengths": strengths,
        "improvements": improvements,
    }


# ---------------------------------------------------------------------------
# ATS sub-score computations
# ---------------------------------------------------------------------------

def _compute_ats_breakdown(f: Dict) -> Dict[str, float]:
    """Compute each weighted ATS sub-score."""
    return {
        "contact_info":    _score_contact(f),
        "sections":        _score_sections(f),
        "keyword_density": _score_keywords(f),
        "formatting":      _score_formatting(f),
        "quantification":  _score_quantification(f),
    }


def _score_contact(f: Dict) -> float:
    """Up to 10 points: email + phone + URL."""
    score = 0.0
    if f.get("has_email"):
        score += 4.0
    if f.get("has_phone"):
        score += 3.5
    if f.get("has_url"):
        score += 2.5
    return score


def _score_sections(f: Dict) -> float:
    """
    Up to 25 points: presence of high-value sections.
    High-value (experience, education, skills): 7 pts each
    Bonus (summary, projects, certifications): 2 pts each
    """
    detected = set(f.get("detected_sections", []))
    score = 0.0

    for section in HIGH_VALUE_SECTIONS:
        if section in detected:
            score += 7.0

    for section in BONUS_SECTIONS:
        if section in detected:
            score += 2.0

    return min(score, ATS_WEIGHTS["sections"])


def _score_keywords(f: Dict) -> float:
    """
    Up to 30 points: technical + soft skill keyword density.
    Formula: min(detected_count / target_count, 1.0) * max_points
    Targets: 12 technical skills + 4 soft skills for a full score.
    """
    tech_count = len(f.get("technical_skills", []))
    soft_count = len(f.get("soft_skills", []))

    tech_score = min(tech_count / 12.0, 1.0) * 20.0
    soft_score = min(soft_count / 4.0, 1.0) * 10.0

    return tech_score + soft_score


def _score_formatting(f: Dict) -> float:
    """
    Up to 15 points: word count, bullet usage, professional length.
    Ideal resume: 300-700 words, at least 5 bullet points.
    """
    score = 0.0
    word_count = f.get("word_count", 0)
    bullet_count = f.get("bullet_count", 0)

    # Word count (optimal 300-700)
    if 300 <= word_count <= 700:
        score += 8.0
    elif 200 <= word_count < 300 or 700 < word_count <= 900:
        score += 5.0
    elif word_count > 150:
        score += 2.0

    # Bullet points
    if bullet_count >= 10:
        score += 7.0
    elif bullet_count >= 5:
        score += 5.0
    elif bullet_count >= 2:
        score += 2.5

    return min(score, ATS_WEIGHTS["formatting"])


def _score_quantification(f: Dict) -> float:
    """
    Up to 20 points: quantified achievements in experience.
    Target: at least 5 quantified statements for full score.
    """
    count = f.get("quantification_count", 0)
    return min(count / 5.0, 1.0) * ATS_WEIGHTS["quantification"]


# ---------------------------------------------------------------------------
# Overall score computations
# ---------------------------------------------------------------------------

def _compute_overall_breakdown(f: Dict, ats_score: float) -> Dict[str, float]:
    """Compute each weighted overall sub-score."""
    return {
        "ats_score":          (ats_score / 100.0) * OVERALL_WEIGHTS["ats_score"],
        "skill_breadth":      _score_skill_breadth(f),
        "experience_quality": _score_experience_quality(f),
        "language_quality":   _score_language_quality(f),
        "section_coverage":   _score_section_coverage(f),
    }


def _score_skill_breadth(f: Dict) -> float:
    """Up to 20 points: variety and depth of technical + soft skills."""
    tech = len(f.get("technical_skills", []))
    soft = len(f.get("soft_skills", []))
    total = tech + soft
    return min(total / 20.0, 1.0) * OVERALL_WEIGHTS["skill_breadth"]


def _score_experience_quality(f: Dict) -> float:
    """
    Up to 20 points: inferred from entity signals.
    - Number of ORG entities (companies) indicates experience breadth
    - DATE entities indicate timeline completeness
    """
    orgs = len(f.get("entities", {}).get("organizations", []))
    dates = len(f.get("entities", {}).get("dates", []))

    org_score = min(orgs / 4.0, 1.0) * 12.0
    date_score = min(dates / 6.0, 1.0) * 8.0

    return org_score + date_score


def _score_language_quality(f: Dict) -> float:
    """
    Up to 10 points: vocabulary diversity and sentence structure.
    Vocabulary diversity = unique_words / total_words (type-token ratio)
    """
    word_count = f.get("word_count", 0)
    sentence_count = f.get("sentence_count", 1)

    if word_count == 0:
        return 0.0

    # Good resumes have avg 10-20 words per sentence
    avg_words = word_count / max(sentence_count, 1)
    structure_score = 5.0 if 8 <= avg_words <= 22 else 2.0

    # Word count diversity proxy: more words = better vocabulary coverage
    density_score = min(word_count / 400.0, 1.0) * 5.0

    return structure_score + density_score


def _score_section_coverage(f: Dict) -> float:
    """Up to 10 points: bonus for having well-rounded section coverage."""
    detected = set(f.get("detected_sections", []))
    all_desired = HIGH_VALUE_SECTIONS | BONUS_SECTIONS

    coverage_ratio = len(detected & all_desired) / len(all_desired)
    return coverage_ratio * OVERALL_WEIGHTS["section_coverage"]


# ---------------------------------------------------------------------------
# Feedback generation
# ---------------------------------------------------------------------------

def _generate_feedback(
    f: Dict,
    ats_breakdown: Dict[str, float],
    overall_breakdown: Dict[str, float],
) -> Tuple[List[str], List[str]]:
    """Generate human-readable strengths and areas for improvement."""
    strengths: List[str] = []
    improvements: List[str] = []
    detected = set(f.get("detected_sections", []))

    # Contact information
    if f.get("has_email") and f.get("has_phone"):
        strengths.append("Contact information is complete with email and phone number.")
    else:
        if not f.get("has_email"):
            improvements.append("Add a professional email address to the contact section.")
        if not f.get("has_phone"):
            improvements.append("Include a phone number for recruiters to reach you.")

    # LinkedIn/portfolio URL
    if f.get("has_url"):
        strengths.append("LinkedIn or portfolio URL is present, which increases recruiter engagement.")
    else:
        improvements.append("Add a LinkedIn profile or portfolio URL to stand out.")

    # Section coverage
    if HIGH_VALUE_SECTIONS.issubset(detected):
        strengths.append("All core sections (Experience, Education, Skills) are present.")
    else:
        missing = HIGH_VALUE_SECTIONS - detected
        for section in missing:
            improvements.append(f"Add a clearly labeled '{section.title()}' section for better ATS parsing.")

    if "summary" in detected:
        strengths.append("A professional summary section helps recruiters quickly understand your profile.")
    else:
        improvements.append("Add a 2-3 sentence professional summary at the top to capture attention.")

    if "projects" in detected:
        strengths.append("Projects section demonstrates practical experience beyond job titles.")

    if "certifications" in detected:
        strengths.append("Certifications section strengthens your technical credibility.")

    # Technical skills
    tech_count = len(f.get("technical_skills", []))
    if tech_count >= 10:
        strengths.append(f"{tech_count} technical skills detected, showing strong domain coverage.")
    elif tech_count >= 5:
        strengths.append(f"{tech_count} technical skills detected.")
        improvements.append("Consider adding more specific technical tools or frameworks you have used.")
    else:
        improvements.append(
            "Add a dedicated Skills section listing programming languages, frameworks, and tools."
        )

    # Soft skills
    soft_count = len(f.get("soft_skills", []))
    if soft_count >= 3:
        strengths.append("Soft skills are mentioned, which adds interpersonal depth to the profile.")
    else:
        improvements.append(
            "Weave in a few soft skills (leadership, communication, teamwork) naturally in your descriptions."
        )

    # Quantification
    quant_count = f.get("quantification_count", 0)
    if quant_count >= 5:
        strengths.append(
            f"Strong use of numbers and metrics ({quant_count} quantified achievements found). "
            "This significantly improves credibility."
        )
    elif quant_count >= 2:
        strengths.append(f"{quant_count} quantified achievement(s) found.")
        improvements.append(
            "Add more metrics to experience bullets: percentages, team sizes, revenue figures, timelines."
        )
    else:
        improvements.append(
            "Quantify your achievements: instead of 'improved performance', write 'improved load time by 40%'."
        )

    # Formatting
    bullet_count = f.get("bullet_count", 0)
    if bullet_count >= 8:
        strengths.append("Good use of bullet points makes the resume easy to scan.")
    elif bullet_count >= 3:
        improvements.append(
            "Use more bullet points in experience and project descriptions to improve scannability."
        )
    else:
        improvements.append(
            "Format experience entries with bullet points rather than paragraphs — ATS systems parse these better."
        )

    # Word count
    word_count = f.get("word_count", 0)
    if 300 <= word_count <= 700:
        strengths.append(
            f"Resume length ({word_count} words) is within the ideal ATS-friendly range of 300-700 words."
        )
    elif word_count < 300:
        improvements.append(
            f"Resume is too brief ({word_count} words). Expand experience and project descriptions."
        )
    elif word_count > 800:
        improvements.append(
            f"Resume may be too long ({word_count} words). Consider trimming to 1-2 pages."
        )

    return strengths, improvements
