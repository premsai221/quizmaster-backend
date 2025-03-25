from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from flask_cors import CORS

from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.user import user_bp
from app.routes.quiz import quiz_bp

from app.config import Config

jwt = JWTManager()

app = Flask(__name__)
cors = CORS(app)

db = SQLAlchemy(app)
app.config.from_object(Config)

jwt.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(quiz_bp, url_prefix="/quiz")
