from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Subject, Chapter, Quiz, Question, User
from app.utils.helpers import admin_required
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/subjects", methods=["POST"])
@jwt_required()
@admin_required
def create_subject():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        if "name" not in data:
            return jsonify({"error": "Name is required"}), 400
        
        existing_subject = Subject.query.filter_by(name=data["name"]).first()
        if existing_subject:
            return jsonify({"error": "Subject with this name already exists"}), 400
        
        subject = Subject(
            name=data["name"], 
            description=data.get("description", "")
        )
        
        db.session.add(subject)
        db.session.commit()
        
        return jsonify({
            "message": "Subject created",
            "subject": subject.id,
            "name": subject.name
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    

@admin_bp.route("/subjects/edit/<int:subject_id>", methods=["POST"])
@jwt_required()
@admin_required
def edit_subject(subject_id):
    try:
        data = request.get_json()
        if not subject_id:
            return jsonify({"error": "Invalid subject"}), 400
        
        existing_subject = Subject.query.filter_by(name=data["name"]).first()
        if existing_subject.id != subject_id:
            return jsonify({"error": "Subject with this name already exists"}), 400
        
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({"error": "Subject not found"}), 404
        subject.name = data["name"]
        subject.description = data.get("description", "")
        db.session.commit()
        
        return jsonify({
            "message": "Subject created",
            "subject": subject.id,
            "name": subject.name
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@admin_bp.route("/subjects/<int:subject_id>/chapters", methods=["POST"])
@jwt_required()
@admin_required
def create_chapter(subject_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        if "name" not in data:
            return jsonify({"error": "Name is required"}), 400
        
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({"error": "Subject not found"}), 404

        existing_chapter = Chapter.query.filter_by(name=data["name"], subject_id=subject_id).first()
        if existing_chapter:
            return jsonify({"error": "Chapter with this name already exists in the subject"}), 400
        
        chapter = Chapter(
            name=data["name"], 
            description=data.get("description", ""),
            subject_id=subject_id
        )
        db.session.add(chapter)
        db.session.commit()
        
        return jsonify({
            "message": "Chapter created",
            "chapter": chapter.id,
            "name": chapter.name
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    
@admin_bp.route("/quizzes", methods=["POST"])
@jwt_required()
@admin_required
def create_quiz():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        required_fields = ["chapter_id", "date_of_quiz", "time_duration"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        chapter = Chapter.query.get(data["chapter_id"])
        if not chapter:
            return jsonify({"error": "Chapter not found"}), 404
        
        existing_quiz = Quiz.query.filter_by(chapter_id=data["chapter_id"]).first()
        if existing_quiz:
            return jsonify({"error": "A quiz already exists for this chapter"}), 400

        try:
            if isinstance(data["date_of_quiz"], str):
                quiz_date = datetime.strptime(data["date_of_quiz"], "%Y-%m-%d %H:%M:%S")
            else:
                quiz_date = data["date_of_quiz"]
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"}), 400

        quiz = Quiz(
            chapter_id=data["chapter_id"],
            date_of_quiz=quiz_date,
            time_duration=data["time_duration"],
            remarks=data.get("remarks", "")
        )
        db.session.add(quiz)
        db.session.commit()
        
        return jsonify({
            "message": "Quiz created",
            "quiz": quiz.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@admin_bp.route("/quizzes/<int:quiz_id>/questions", methods=["POST"])
@jwt_required()
@admin_required
def create_question(quiz_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        required_fields = ["question_statement", "option1", "option2", "option3", "option4", "correct_option"]

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({"error": "Quiz not found"}), 404
            
        if not (1 <= data["correct_option"] <= 4):
            return jsonify({"error": "Correct option must be between 1 and 4"}), 400
        
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
        
        return jsonify({
            "message": "Question added",
            "question": question.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    try:
        users = User.query.all()
        user_list = [{
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        } for user in users]
        return jsonify({"users": user_list}), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching users: {str(e)}"}), 500
    

@admin_bp.route("/generate-test-data", methods=["POST"])
@jwt_required()
@admin_required
def generate_test_data():
    try:
        from seed_data import seed_data

        data = request.get_json() or {}
        num_users = data.get("num_users", 10)
        num_subjects = data.get("num_subjects", 5)
        
        seed_data(num_users, num_subjects)
        
        return jsonify({
            "message": "Test data generated successfully",
            "users_created": num_users,
            "subjects_created": num_subjects
        }), 201
    except Exception as e:
        return jsonify({"error": f"Error generating test data: {str(e)}"}), 500
    
@admin_bp.route("/subjects/<int:subject_id>/complete-chapter", methods=["POST"])
@jwt_required()
@admin_required
def create_complete_chapter(subject_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        if not all(key in data for key in ["chapter", "quiz", "questions"]):
            return jsonify({"error": "Missing required sections: chapter, quiz, and questions"}), 400

        chapter_data = data["chapter"]
        if "name" not in chapter_data:
            return jsonify({"error": "Chapter name is required"}), 400
            
        quiz_data = data["quiz"]
        if not all(key in quiz_data for key in ["date_of_quiz", "time_duration"]):
            return jsonify({"error": "Quiz must include date_of_quiz and time_duration"}), 400
            
        questions_data = data["questions"]
        if not isinstance(questions_data, list) or len(questions_data) == 0:
            return jsonify({"error": "Questions must be a non-empty array"}), 400
            
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({"error": f"Subject with ID {subject_id} not found"}), 404
            
        existing_chapter = Chapter.query.filter_by(
            subject_id=subject_id, name=chapter_data["name"]
        ).first()
        
        if existing_chapter:
            return jsonify({"error": f"Chapter with name '{chapter_data['name']}' already exists for this subject"}), 400
            
        try:
            chapter = Chapter(
                name=chapter_data["name"],
                description=chapter_data.get("description", ""),
                subject_id=subject_id
            )
            db.session.add(chapter)
            db.session.flush()
            
            try:
                if isinstance(quiz_data["date_of_quiz"], str):
                    quiz_date = datetime.strptime(quiz_data["date_of_quiz"], "%Y-%m-%d %H:%M:%S")
                else:
                    quiz_date = quiz_data["date_of_quiz"]
            except ValueError:
                db.session.rollback()
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"}), 400
                
            quiz = Quiz(
                chapter_id=chapter.id,
                date_of_quiz=quiz_date,
                time_duration=quiz_data["time_duration"],
                remarks=quiz_data.get("remarks", "")
            )
            db.session.add(quiz)
            db.session.flush()
            
            created_questions = []
            for idx, q_data in enumerate(questions_data, 1):
                required_question_fields = ["question_statement", "option1", "option2", 
                                          "option3", "option4", "correct_option"]
                if not all(field in q_data for field in required_question_fields):
                    db.session.rollback()
                    return jsonify({
                        "error": f"Question #{idx} is missing required fields",
                        "required_fields": required_question_fields
                    }), 400
                
                if not (1 <= q_data["correct_option"] <= 4):
                    db.session.rollback()
                    return jsonify({
                        "error": f"Question #{idx}: Correct option must be between 1 and 4"
                    }), 400
                
                question = Question(
                    quiz_id=quiz.id,
                    question_statement=q_data["question_statement"],
                    option1=q_data["option1"],
                    option2=q_data["option2"],
                    option3=q_data["option3"],
                    option4=q_data["option4"],
                    correct_option=q_data["correct_option"]
                )
                db.session.add(question)
                created_questions.append(question)
            
            db.session.commit()
            
            response = {
                "message": "Chapter with quiz and questions created successfully",
                "chapter": {
                    "id": chapter.id,
                    "name": chapter.name,
                    "subject_id": chapter.subject_id
                },
                "quiz": {
                    "id": quiz.id,
                    "date_of_quiz": quiz.date_of_quiz.strftime("%Y-%m-%d %H:%M:%S"),
                    "time_duration": quiz.time_duration
                },
                "questions_count": len(created_questions)
            }
            
            return jsonify(response), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500