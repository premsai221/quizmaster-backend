from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, Quiz, Question
from datetime import datetime

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/<int:quiz_id>", methods=["GET"])
@jwt_required()
def get_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    question_list = [
        {
            "id": q.id,
            "question_statement": q.question_statement,
            "options": [q.option1, q.option2, q.option3, q.option4]
        }
        for q in questions
    ]

    quiz_data = {
        "id": quiz.id,
        "chapter_id": quiz.chapter_id,
        "date_of_quiz": str(quiz.date_of_quiz),
        "time_duration": quiz.time_duration,
        "questions": question_list
    }

    return jsonify({"quiz": quiz_data}), 200

@quiz_bp.route("/<int:quiz_id>/questions", methods=["GET"])
@jwt_required()
def get_quiz_questions(quiz_id):
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not questions:
        return jsonify({"error": "No questions found for this quiz"}), 404

    question_list = [
        {
            "id": q.id,
            "question_statement": q.question_statement,
            "options": [q.option1, q.option2, q.option3, q.option4]
        }
        for q in questions
    ]

    return jsonify({"questions": question_list}), 200

@quiz_bp.route("/<int:quiz_id>/submit", methods=["POST"])
@jwt_required()
def submit_quiz(quiz_id):
    data = request.get_json()
    if not data or "answers" not in data:
        return jsonify({"error": "Missing answers"}), 400

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if not questions:
        return jsonify({"error": "No questions found"}), 404

    correct_answers = {q.id: q.correct_option for q in questions}
    user_answers = data["answers"]
    score = sum(1 for q_id, ans in user_answers.items() if correct_answers.get(q_id) == ans)

    return jsonify({"message": "Quiz submitted", "total_score": score}), 200
