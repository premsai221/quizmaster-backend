from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, cache
from app.models import User, Quiz, Score
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

@user_bp.route("/quizzes", methods=["GET"])
@jwt_required()
@cache.cached(timeout=60)  # Cache for 1 minute
def get_quizzes():
    try:
        quizzes = Quiz.query.all()
        quiz_list = [
            {
                "id": quiz.id, 
                "chapter_id": quiz.chapter_id, 
                "date_of_quiz": str(quiz.date_of_quiz), 
                "time_duration": quiz.time_duration
            }
            for quiz in quizzes
        ]
        return jsonify({"quizzes": quiz_list}), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching quizzes: {str(e)}"}), 500

@user_bp.route("/quizzes/<int:quiz_id>/attempt", methods=["POST"])
@jwt_required()
def attempt_quiz(quiz_id):
    try:
        user_id = int(get_jwt_identity())
        quiz = Quiz.query.get(quiz_id)

        if not quiz:
            return jsonify({"error": "Quiz not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        total_scored = data.get("total_scored", 0)
        total_possible = data.get("total_possible", 0)

        score_entry = Score(
            quiz_id=quiz_id,
            user_id=user_id,
            time_stamp_of_attempt=datetime.utcnow(),
            total_scored=total_scored,
            total_possible=total_possible,
            completed=True
        )

        db.session.add(score_entry)
        db.session.commit()
        
        # Clear user scores cache if using memoization
        if hasattr(get_scores, 'uncached'):
            cache.delete_memoized(get_scores, user_id)

        return jsonify({"message": "Quiz attempt recorded", "score_id": score_entry.id}), 201
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