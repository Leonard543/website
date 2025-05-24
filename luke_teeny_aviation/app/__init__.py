import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db, Airline, Aircraft, Registration

def create_app():
    app = Flask(__name__)
    
    # Configure SQLAlchemy
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    instance_path = os.path.join(base_dir, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "teeny_aviation.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads/' # Relative to the project root where run.py is

    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Register Blueprints
    from .routes import main_bp, admin_bp, archive_bp # Import archive_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(archive_bp) # Register archive_bp

    return app
