#!/usr/bin/env python3
"""
Database initialization script for Acne Detection System
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.user import User
from models.detection import DetectionSession, Detection
from models.setting import Setting
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_database():
    """Create database tables and initial data"""
    
    # Import the app configuration
    from config import config
    from flask import Flask
    
    # Create Flask app for database operations
    app = Flask(__name__)
    app.config.from_object(config['development'])
    
    # Initialize database
    from models import db
    db.init_app(app)
    
    print("🚀 Initializing Acne Detection Database...")
    
    # Create all tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Create default admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@acnedetection.com',
                password='admin123',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created:")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  Please change this password immediately!")
        
        # Create default settings
        default_settings = [
            ('max_file_size', '10485760', 'Maximum file size in bytes (10MB)'),
            ('allowed_file_types', 'jpg,jpeg,png', 'Allowed image file types'),
            ('detection_confidence', '0.5', 'Default detection confidence threshold'),
            ('max_detections_per_image', '50', 'Maximum detections allowed per image'),
            ('maintenance_mode', 'false', 'System maintenance mode'),
            ('api_version', '1.0.0', 'Current API version'),
            ('session_timeout_hours', '24', 'Session timeout in hours'),
            ('enable_registration', 'true', 'Allow new user registration'),
            ('max_login_attempts', '5', 'Maximum login attempts before lockout'),
            ('email_verification_required', 'false', 'Require email verification for new accounts')
        ]
        
        for key, value, description in default_settings:
            existing = Setting.query.filter_by(key=key).first()
            if not existing:
                setting = Setting(key, value, description)
                db.session.add(setting)
        
        db.session.commit()
        print("✅ Default settings created")
        
        # Display database information
        display_database_info(db)
        
        print("\n🎉 Database initialization completed!")
        print("\n📋 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start the application: python app.py")
        print("3. Open browser: http://localhost:5000")

def display_database_info(db):
    """Display database information"""
    with db.app_context():
        print("\n📊 Database Information:")
        
        # User count
        user_count = User.query.count()
        print(f"👥 Users: {user_count}")
        
        # Settings count
        settings_count = Setting.query.count()
        print(f"⚙️  Settings: {settings_count}")
        
        # Display settings
        settings = Setting.query.all()
        print("⚙️  Current Settings:")
        for setting in settings:
            print(f"   - {setting.key}: {setting.value}")
        
        # Check admin user
        admin_user = User.query.filter_by(role='admin').first()
        if admin_user:
            print("\n🔑 Admin User:")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Created: {admin_user.created_at}")
            print("   ⚠️  Please change the default admin password!")

def reset_database():
    """Reset database (drop and recreate)"""
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///acne_detection.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    print("🔄 Resetting database...")
    
    with app.app_context():
        db.drop_all()
        print("✅ Database tables dropped")
        
        db.create_all()
        print("✅ Database tables recreated")
        
        # Recreate initial data
        create_database()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        reset_database()
    else:
        create_database()
