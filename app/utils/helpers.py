from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import User

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.username != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return func(*args, **kwargs)
    
    return decorated_function
