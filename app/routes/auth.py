from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from app.extensions import db
from app.models import User
from datetime import timedelta, datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    resp = jsonify({"message": "logged out successfully"})
    unset_jwt_cookies(resp)
    return resp, 200

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        required_fields = ["email", "password", "full_name", "qualification", "dob", "phone_number"]

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already exists"}), 400
        try:
            dob = datetime.fromisoformat(data["dob"]).date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        user = User(
            email=data["email"],
            full_name=data["full_name"],
            qualification=data["qualification"],
            phone_number=data["phone_number"],
            dob=dob
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password required"}), 400

        for user in User.query.all():
            print(user.email)
        user = User.query.filter_by(email=data["email"]).first()

        if not user or not user.check_password(data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401
        access_token = create_access_token(
            identity=str(user.id),  
            expires_delta=timedelta(hours=2)
        )
        resp = jsonify({
            "message": "Login successful", 
            "access_token": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        })
        set_access_cookies(resp, access_token)
        return resp, 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    try:
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