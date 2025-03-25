from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, Subject, Chapter, Quiz, Question, User
from app.utils.helpers import admin_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/subjects", methods=["POST"])
@jwt_required()
@admin_required
def create_subject():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400
    
    subject = Subject(name=data["name"], description=data.get("description", ""))
    db.session.add(subject)
    db.session.commit()
    
    return jsonify({"message": "Subject created", "subject": subject.id}), 201

@admin_bp.route("/subjects/<int:subject_id>/chapters", methods=["POST"])
@jwt_required()
@admin_required
def create_chapter(subject_id):
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400
    
    chapter = Chapter(name=data["name"], description=data.get("description", ""), subject_id=subject_id)
    db.session.add(chapter)
    db.session.commit()
    
    return jsonify({"message": "Chapter created", "chapter": chapter.id}), 201

@admin_bp.route("/quizzes", methods=["POST"])
@jwt_required()
@admin_required
def create_quiz():
    data = request.get_json()
    required_fields = ["chapter_id", "date_of_quiz", "time_duration"]
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    quiz = Quiz(
        chapter_id=data["chapter_id"],
        date_of_quiz=data["date_of_quiz"],
        time_duration=data["time_duration"],
        remarks=data.get("remarks", "")
    )
    db.session.add(quiz)
    db.session.commit()
    
    return jsonify({"message": "Quiz created", "quiz": quiz.id}), 201

@admin_bp.route("/quizzes/<int:quiz_id>/questions", methods=["POST"])
@jwt_required()
@admin_required
def create_question(quiz_id):
    data = request.get_json()
    required_fields = ["question_statement", "option1", "option2", "option3", "option4", "correct_option"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    question = Question(
        quiz_id=quiz_id,
        question_statement=data["question_statement"],
        option1=data["option1"],
        option2=data["option2"],
        option3=data["option3"],
        option4=data["option4"],
        correct_option=data["correct_option"]
    )
    db.session.add(question)
    db.session.commit()
    
    return jsonify({"message": "Question added", "question": question.id}), 201

@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "full_name": user.full_name} for user in users]
    return jsonify({"users": user_list}), 200
