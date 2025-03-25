from flask import Flask
from app.extensions import db, jwt, bcrypt, cors

def create_app():
    app = Flask(__name__)
    
    from app.config import Config
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    

    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    from app.routes.quiz import quiz_bp
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(quiz_bp, url_prefix="/quiz")

    with app.app_context():
        db.create_all()
        create_admin_if_not_exists()
    
    return app

def create_admin_if_not_exists():
    from app.models import User
    
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            email='admin@quizmaster.com',
            full_name='Quiz Master Admin',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

app = create_app()