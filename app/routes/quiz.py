from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Quiz, Question, Subject, Chapter
from app.extensions import db
from app.utils.helpers import is_user_admin

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/subjects", methods=["GET"])
@jwt_required()
def get_all_subjects():
    subjects = Subject.query.all()
    subjects_list = [
        {
            'id': subject.id,
            'name': subject.name,
            'description': subject.description
        } for subject in subjects
    ]
    return jsonify({'subjects': subjects_list})


@quiz_bp.route("/subjects/<int:subject_id>/chapters", methods=["GET"])
@jwt_required()
def get_all_chapters(subject_id):
    subject = Subject.query.get(subject_id)

    if not subject:
        return jsonify({"error": "Subject not found"}), 404
    
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    chapters_list = [
        {
            'id': chapter.id,
            'name': chapter.name,
            'description': chapter.description,
            'quiz_id': chapter.quiz[0].id,
            'date_of_quiz': chapter.quiz[0].date_of_quiz,
            'time_duration': chapter.quiz[0].time_duration
        } for chapter in chapters
    ]
    return jsonify({'chapters': chapters_list})


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
    user_id = int(get_jwt_identity())
    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not questions:
        return jsonify({"error": "No questions found for this quiz"}), 404

    question_list = []
    for q in questions:
        question = {
            "id": q.id,
            "question_statement": q.question_statement,
            "options": [q.option1, q.option2, q.option3, q.option4]
        }
        if is_user_admin(user_id):
            question["correct_option"] = q.correct_option 
        else:
            question["option"] = 0
        question_list.append(question)

    return jsonify({"questions": question_list, "time_duration": quiz.time_duration}), 200

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

    correct_answers = {str(q.id): q.correct_option for q in questions}
    user_answers = data["answers"]
    score = sum(1 for q_id, ans in user_answers.items() if correct_answers.get(q_id) == int(ans))

    return jsonify({"message": "Quiz submitted", "total_score": score}), 200