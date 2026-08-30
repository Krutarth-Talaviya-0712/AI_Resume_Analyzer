"""
analyze_routes.py
-----------------
Flask blueprint exposing the resume analysis API.

Routes
------
POST /api/analyze/upload
    Accepts a multipart/form-data file upload (PDF or DOCX).
    Runs the NLP pipeline, scoring engine, and job suggester.
    Persists the result in the Analysis table.
    Returns a detailed JSON report.

GET /api/analyze/history
    Returns all past analysis records for the authenticated user.

GET /api/analyze/history/<int:analysis_id>
    Returns the full report for a specific past analysis.
"""

import json
import os

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models import Analysis

from .extractor import extract_text
from .job_suggester import suggest_jobs
from .nlp_pipeline import analyze_resume_text
from .scorer import compute_scores

analyze_bp = Blueprint("analyze", __name__)

# Maximum upload size: 5 MB
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "docx"}


def _allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@analyze_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_and_analyze():
    """
    Accept a resume file, run the full ML analysis pipeline, persist the
    result, and return a structured JSON report.

    Expects: multipart/form-data with field name 'resume'
    Returns: JSON analysis report
    """
    current_user_id = int(get_jwt_identity())

    if "resume" not in request.files:
        return jsonify({"message": "No file provided. Send the file in the 'resume' field."}), 400

    file = request.files["resume"]

    if not file.filename:
        return jsonify({"message": "No file selected."}), 400

    if not _allowed_file(file.filename):
        return jsonify({
            "message": "Unsupported file type. Please upload a PDF or DOCX file."
        }), 422

    # Guard against oversized uploads
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_FILE_SIZE_BYTES:
        return jsonify({
            "message": f"File too large. Maximum allowed size is {MAX_FILE_SIZE_BYTES // (1024*1024)} MB."
        }), 413

    # ── Text extraction ────────────────────────────────────────────────────
    try:
        extracted_text = extract_text(file)
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 422
    except Exception:
        return jsonify({
            "message": "Could not parse the uploaded file. Ensure it is a valid, non-corrupted PDF or DOCX."
        }), 500

    if len(extracted_text.strip()) < 50:
        return jsonify({
            "message": "The uploaded file appears to be empty or contains no readable text. "
                       "Scanned image PDFs are not supported at this time."
        }), 422

    # ── NLP pipeline ──────────────────────────────────────────────────────
    try:
        nlp_features = analyze_resume_text(extracted_text)
    except Exception:
        return jsonify({
            "message": "An error occurred during text analysis. Please try again."
        }), 500

    # ── Scoring ───────────────────────────────────────────────────────────
    score_result = compute_scores(nlp_features)

    # ── Job suggestions ───────────────────────────────────────────────────
    all_detected_skills = (
        nlp_features.get("technical_skills", [])
        + nlp_features.get("soft_skills", [])
    )
    job_suggestions = suggest_jobs(all_detected_skills, top_n=6)

    # ── Assemble full report ──────────────────────────────────────────────
    report = {
        "filename": file.filename,
        "ats_score": score_result["ats_score"],
        "overall_score": score_result["overall_score"],
        "ats_breakdown": score_result["ats_breakdown"],
        "overall_breakdown": score_result["overall_breakdown"],
        "strengths": score_result["strengths"],
        "improvements": score_result["improvements"],
        "technical_skills": nlp_features["technical_skills"],
        "soft_skills": nlp_features["soft_skills"],
        "detected_sections": nlp_features["detected_sections"],
        "entities": nlp_features["entities"],
        "stats": {
            "word_count": nlp_features["word_count"],
            "sentence_count": nlp_features["sentence_count"],
            "bullet_count": nlp_features["bullet_count"],
            "quantification_count": nlp_features["quantification_count"],
            "has_email": nlp_features["has_email"],
            "has_phone": nlp_features["has_phone"],
            "has_url": nlp_features["has_url"],
        },
        "job_suggestions": job_suggestions,
    }

    # ── Persist to database ───────────────────────────────────────────────
    try:
        analysis_record = Analysis(
            user_id=current_user_id,
            filename=file.filename,
            overall_score=report["overall_score"],
            ats_score=report["ats_score"],
            report_data=json.dumps(report),
        )
        db.session.add(analysis_record)
        db.session.commit()
        report["analysis_id"] = analysis_record.id
    except Exception:
        # Non-fatal: return the report even if persistence fails
        report["analysis_id"] = None

    return jsonify(report), 200


@analyze_bp.route("/history", methods=["GET"])
@jwt_required()
def get_analysis_history():
    """Return a paginated list of all past analyses for the current user."""
    current_user_id = int(get_jwt_identity())
    records = (
        Analysis.query
        .filter_by(user_id=current_user_id)
        .order_by(Analysis.created_at.desc())
        .limit(20)
        .all()
    )
    return jsonify([r.to_dict() for r in records]), 200


@analyze_bp.route("/history/<int:analysis_id>", methods=["GET"])
@jwt_required()
def get_analysis_detail(analysis_id: int):
    """Return the full report for a specific past analysis."""
    current_user_id = int(get_jwt_identity())
    record = Analysis.query.filter_by(
        id=analysis_id, user_id=current_user_id
    ).first()

    if not record:
        return jsonify({"message": "Analysis record not found."}), 404

    return jsonify(record.to_dict()), 200
