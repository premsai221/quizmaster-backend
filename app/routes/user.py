from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Quiz, Score
from datetime import datetime

user_bp = Blueprint("user", __name__)

@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "qualification": user.qualification,
        "dob": str(user.dob)
    }

    return jsonify({"user": user_data}), 200

@user_bp.route("/quizzes", methods=["GET"])
@jwt_required()
def get_quizzes():
    quizzes = Quiz.query.all()
    quiz_list = [
        {"id": quiz.id, "chapter_id": quiz.chapter_id, "date_of_quiz": str(quiz.date_of_quiz), "time_duration": quiz.time_duration}
        for quiz in quizzes
    ]
    return jsonify({"quizzes": quiz_list}), 200

@user_bp.route("/quizzes/<int:quiz_id>/attempt", methods=["POST"])
@jwt_required()
def attempt_quiz(quiz_id):
    user_id = get_jwt_identity()
    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    data = request.get_json()
    total_scored = data.get("total_scored", 0)

    score_entry = Score(
        quiz_id=quiz_id,
        user_id=user_id,
        time_stamp_of_attempt=datetime.utcnow(),
        total_scored=total_scored
    )

    db.session.add(score_entry)
    db.session.commit()

    return jsonify({"message": "Quiz attempt recorded", "score_id": score_entry.id}), 201

@user_bp.route("/scores", methods=["GET"])
@jwt_required()
def get_scores():
    user_id = get_jwt_identity()
    scores = Score.query.filter_by(user_id=user_id).all()

    score_list = [
        {"quiz_id": score.quiz_id, "total_scored": score.total_scored, "attempted_on": str(score.time_stamp_of_attempt)}
        for score in scores
    ]

    return jsonify({"scores": score_list}), 200
