from flask import Flask
from app.extensions import db, jwt, bcrypt, cors, cache

def create_app():
    app = Flask(__name__)
    
    # Load config
    from app.config import Config
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    cache.init_app(app)
    
    # Configure JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"error": "Invalid token provided"}, 401
        
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"error": "Token has expired"}, 401
        
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        print(error)
        return {"error": "Missing authorization token"}, 401
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    from app.routes.quiz import quiz_bp
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(quiz_bp, url_prefix="/quiz")
    
    # Configure Celery
    from app.tasks import celery
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    # Create database tables and initialize admin
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

# Create app instance
app = create_app()