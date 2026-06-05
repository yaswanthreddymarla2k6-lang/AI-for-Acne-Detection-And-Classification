from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from models.user import User
from models.setting import Setting
from utils.validators import validate_email, validate_password
from utils.security import log_security_event
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    def register_user(username, email, password, role='user'):
        """Register a new user"""
        try:
            # Validate inputs
            if not username or not email or not password:
                return {'success': False, 'message': 'Username, email, and password are required'}
            
            if not validate_email(email):
                return {'success': False, 'message': 'Invalid email format'}
            
            if not validate_password(password):
                return {'success': False, 'message': 'Password must be at least 6 characters long'}
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                return {'success': False, 'message': 'Username already exists'}
            
            if User.query.filter_by(email=email).first():
                return {'success': False, 'message': 'Email already exists'}
            
            # Create new user
            user = User(username=username, email=email, password=password, role=role)
            
            from flask import current_app
            db = current_app.extensions['sqlalchemy'].db
            db.session.add(user)
            db.session.commit()
            
            log_security_event('USER_REGISTERED', f'New user registered: {username}')
            
            return {
                'success': True, 
                'message': 'User registered successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return {'success': False, 'message': 'Registration failed'}
    
    @staticmethod
    def authenticate_user(username_or_email, password):
        """Authenticate user and return tokens"""
        try:
            # Find user by username or email
            user = User.query.filter(
                (User.username == username_or_email) | 
                (User.email == username_or_email)
            ).first()
            
            if not user or not user.is_active:
                log_security_event('LOGIN_FAILED', f'Failed login attempt for: {username_or_email}')
                return {'success': False, 'message': 'Invalid credentials'}
            
            if not user.check_password(password):
                log_security_event('LOGIN_FAILED', f'Failed login attempt for: {username_or_email}')
                return {'success': False, 'message': 'Invalid credentials'}
            
            # Update last login
            user.update_last_login()
            
            # Generate tokens
            tokens = user.generate_tokens()
            
            log_security_event('LOGIN_SUCCESS', f'Successful login for: {user.username}')
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'tokens': tokens
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {'success': False, 'message': 'Authentication failed'}
    
    @staticmethod
    def get_current_user():
        """Get current authenticated user"""
        try:
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return None
            
            user = User.query.get(current_user_id)
            return user if user and user.is_active else None
            
        except Exception as e:
            logger.error(f"Get current user error: {str(e)}")
            return None
    
    @staticmethod
    def update_user_password(user_id, old_password, new_password):
        """Update user password"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            if not user.check_password(old_password):
                return {'success': False, 'message': 'Current password is incorrect'}
            
            if not validate_password(new_password):
                return {'success': False, 'message': 'New password must be at least 6 characters long'}
            
            user.set_password(new_password)
            
            from flask import current_app
            db = current_app.extensions['sqlalchemy'].db
            db.session.commit()
            
            log_security_event('PASSWORD_CHANGED', f'Password changed for user: {user.username}')
            
            return {'success': True, 'message': 'Password updated successfully'}
            
        except Exception as e:
            logger.error(f"Password update error: {str(e)}")
            return {'success': False, 'message': 'Password update failed'}
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate user account"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            user.is_active = False
            
            from flask import current_app
            db = current_app.extensions['sqlalchemy'].db
            db.session.commit()
            
            log_security_event('USER_DEACTIVATED', f'User deactivated: {user.username}')
            
            return {'success': True, 'message': 'User deactivated successfully'}
            
        except Exception as e:
            logger.error(f"User deactivation error: {str(e)}")
            return {'success': False, 'message': 'User deactivation failed'}
    
    @staticmethod
    def get_user_stats(user_id):
        """Get user statistics"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            from models.detection import DetectionSession
            total_sessions = DetectionSession.query.filter_by(user_id=user_id).count()
            
            # Get recent activity
            recent_sessions = DetectionSession.query.filter_by(user_id=user_id)\
                .order_by(DetectionSession.created_at.desc())\
                .limit(10).all()
            
            return {
                'user': user.to_dict(),
                'total_sessions': total_sessions,
                'recent_sessions': [session.to_dict() for session in recent_sessions]
            }
            
        except Exception as e:
            logger.error(f"Get user stats error: {str(e)}")
            return None
