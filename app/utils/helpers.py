from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import User

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            if not is_user_admin(user_id):
                return jsonify({"error": "Admin access required"}), 403
            
            return fn(*args, **kwargs)
        except ValueError:
            return jsonify({"error": "Invalid user identity in token"}), 401
        except Exception as e:
            return jsonify({"error": f"Authentication error: {str(e)}"}), 401
    return wrapper

def is_user_admin(user_id):
    user = User.query.get(user_id)
    return user.role == "admin"
