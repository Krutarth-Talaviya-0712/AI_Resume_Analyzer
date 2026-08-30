"""
chatbot_routes.py
-----------------
Flask blueprint for the ResumeCraft site assistant chatbot.

Routes
------
POST /api/chatbot/message
    Accepts a JSON body with field 'message' (string).
    Returns a JSON response with field 'reply' (string).
    No authentication required — the chatbot is publicly accessible.
"""

from flask import Blueprint, jsonify, request

from .intent_handler import get_response

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/message", methods=["POST"])
def handle_message():
    """
    Process an incoming chat message and return a response.

    Request body (JSON):
        { "message": "How does the resume analyzer work?" }

    Response (JSON):
        { "reply": "The Resume Analyzer lets you upload..." }
    """
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()

    if not user_message:
        return jsonify({"reply": "Please type a message and I will do my best to help."}), 200

    if len(user_message) > 500:
        return jsonify({"reply": "Your message is too long. Please keep questions under 500 characters."}), 400

    reply = get_response(user_message)
    return jsonify({"reply": reply}), 200
