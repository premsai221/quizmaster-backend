from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, cache
from app.models import User, Quiz, Score, Chapter, Subject
from datetime import datetime
from app.tasks import export_quiz_data

user_bp = Blueprint("user", __name__)

@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    try:
        # Get user ID as string from JWT, convert to int for database query
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "qualification": user.qualification,
            "dob": str(user.dob) if user.dob else None,
            "role": user.role
        }

        return jsonify({"user": user_data}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@user_bp.route("/subject/<int:subject_id>/chapters", methods=["GET"])
@jwt_required()
# @cache.cached(timeout=60)  # Cache for 1 minute
def get_chapters(subject_id):
    user_id = int(get_jwt_identity())
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({"error": "Subject not found"}), 404
        chapters_list = Chapter.query.filter_by(subject_id=subject_id).all()
        chapters = []
        for chapter in chapters_list:
            quiz = chapter.quiz[0]
            score = Score.query.filter_by(quiz_id=quiz.id, user_id=user_id).first()
            chapter_details = {
                'id': chapter.id,
                'name': chapter.name,
                'description': chapter.description,
                'quiz_id': quiz.id,
                'date_of_quiz': quiz.date_of_quiz,
                'time_duration': quiz.time_duration
            }
            if score:
                chapter_details["attempted"] = True
                chapter_details["score"] = {
                    'total_scored': score.total_scored,
                    'total_possible': score.total_possible
                }
            else:
                chapter_details["attempted"] = False
            chapters.append(chapter_details)
        return jsonify({"chapters": chapters, "subject": subject.name}), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching quizzes: {str(e)}"}), 500

@user_bp.route("/quiz/<int:quiz_id>/check", methods=["GET"])
@jwt_required()
def check_quiz_availability(quiz_id):
    try:
        user_id = int(get_jwt_identity())
        quiz = Quiz.query.get(quiz_id)
        print(quiz.date_of_quiz)
        return "ok", 400
    except Exception as e:
        print(e)
        return jsonify({"error": f"Error checking quiz: {str(e)}"}), 500

@user_bp.route("/quiz/<int:quiz_id>/attempt", methods=["POST"])
@jwt_required()
def attempt_quiz(quiz_id):
    try:
        user_id = int(get_jwt_identity())
        quiz = Quiz.query.get(quiz_id)

        correct_options = {}
        total_possible = 0
        for question in quiz.questions:
            correct_options[question.id] = question.correct_option
            total_possible += 1

        if not quiz:
            return jsonify({"error": "Quiz not found"}), 404

        data = request.get_json()
        if not data or "answers" not in data or not isinstance(data["answers"], list):
            return jsonify({"error": "Invalid JSON data"}), 400
        
        marked_options = data["answers"]
        total_scored = 0
        for option in marked_options:
            if correct_options.get(option.question_id) != None:
                if correct_options[option.question_id] == option.marked:
                    total_scored += 1
                del correct_options[option.question_id]

        score_entry = Score(
            quiz_id=quiz_id,
            user_id=user_id,
            time_stamp_of_attempt=datetime.now(),
            total_scored=total_scored,
            total_possible=total_possible,
            completed=True
        )

        db.session.add(score_entry)
        db.session.commit()
        
        # Clear user scores cache if using memoization
        if hasattr(get_scores, 'uncached'):
            cache.delete_memoized(get_scores, user_id)

        return jsonify({"message": "Quiz attempt recorded", "score_id": score_entry.id, "score": total_scored}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error saving quiz attempt: {str(e)}"}), 500

@user_bp.route("/scores", methods=["GET"])
@jwt_required()
@cache.memoize(timeout=300)  # Cache for 5 minutes
def get_scores():
    try:
        user_id = int(get_jwt_identity())
        scores = Score.query.filter_by(user_id=user_id).all()

        score_list = [
            {
                "quiz_id": score.quiz_id, 
                "total_scored": score.total_scored,
                "total_possible": score.total_possible,
                "percentage": (score.total_scored / score.total_possible * 100) if score.total_possible > 0 else 0,
                "attempted_on": str(score.time_stamp_of_attempt)
            }
            for score in scores
        ]

        return jsonify({"scores": score_list}), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching scores: {str(e)}"}), 500

@user_bp.route("/export-scores", methods=["GET"])
@jwt_required()
def export_scores():
    try:
        user_id = int(get_jwt_identity())
        
        # Trigger Celery task
        task = export_quiz_data.delay(user_id)
        
        return jsonify({
            "message": "Export started", 
            "task_id": task.id
        }), 202
    except Exception as e:
        return jsonify({"error": f"Error starting export: {str(e)}"}), 500

@user_bp.route("/export-status/<task_id>", methods=["GET"])
@jwt_required()
def export_status(task_id):
    try:
        task = export_quiz_data.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Export is pending...'
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'data': task.result
            }
        else:
            response = {
                'state': task.state,
                'status': str(task.info)
            }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Error checking export status: {str(e)}"}), 500