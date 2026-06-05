from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from services.auth_service import AuthService
from utils.validators import validate_email, validate_password, validate_username
from utils.security import log_security_event
from utils.helpers import format_response, create_error_response
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('INVALID_REQUEST', 'No data provided')
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validate inputs
        if not username:
            return create_error_response('VALIDATION_ERROR', 'Username is required')
        
        if not validate_username(username):
            return create_error_response('VALIDATION_ERROR', 'Invalid username format. Use 3-30 characters (letters, numbers, underscore, hyphen)')
        
        if not email:
            return create_error_response('VALIDATION_ERROR', 'Email is required')
        
        if not validate_email(email):
            return create_error_response('VALIDATION_ERROR', 'Invalid email format')
        
        if not password:
            return create_error_response('VALIDATION_ERROR', 'Password is required')
        
        if not validate_password(password):
            return create_error_response('VALIDATION_ERROR', 'Password must be at least 6 characters long')
        
        if password != confirm_password:
            return create_error_response('VALIDATION_ERROR', 'Passwords do not match')
        
        # Register user
        result = AuthService.register_user(username, email, password)
        
        if result['success']:
            return format_response(
                success=True,
                message='Registration successful',
                data=result['user'],
                status_code=201
            )
        else:
            return create_error_response('REGISTRATION_ERROR', result['message'])
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Registration failed')

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('INVALID_REQUEST', 'No data provided')
        
        username_or_email = data.get('username', '').strip()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)
        
        if not username_or_email or not password:
            return create_error_response('VALIDATION_ERROR', 'Username and password are required')
        
        # Authenticate user
        result = AuthService.authenticate_user(username_or_email, password)
        
        if result['success']:
            # Set token expiration based on remember me
            if remember_me:
                current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Never expires
                expires_delta = False
            else:
                expires_delta = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
            
            return format_response(
                success=True,
                message='Login successful',
                data={
                    'user': result['user'],
                    'tokens': result['tokens'],
                    'expires_in': str(expires_delta) if expires_delta else 'never'
                }
            )
        else:
            return create_error_response('AUTHENTICATION_ERROR', result['message'])
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Login failed')

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    try:
        current_user_id = get_jwt_identity()
        
        # In a real implementation, you might want to:
        # - Add the token to a blacklist
        # - Revoke the token
        # - Clear session data
        
        log_security_event('USER_LOGOUT', f'User logged out: {current_user_id}', current_user_id)
        
        return format_response(
            success=True,
            message='Logout successful'
        )
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Logout failed')

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user information"""
    try:
        user = AuthService.get_current_user()
        
        if not user:
            return create_error_response('AUTHENTICATION_ERROR', 'User not found')
        
        return format_response(
            success=True,
            data=user.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Failed to get user information')

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('INVALID_REQUEST', 'No data provided')
        
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not old_password or not new_password:
            return create_error_response('VALIDATION_ERROR', 'Old and new passwords are required')
        
        if not validate_password(new_password):
            return create_error_response('VALIDATION_ERROR', 'New password must be at least 6 characters long')
        
        if new_password != confirm_password:
            return create_error_response('VALIDATION_ERROR', 'New passwords do not match')
        
        current_user_id = get_jwt_identity()
        result = AuthService.update_user_password(current_user_id, old_password, new_password)
        
        if result['success']:
            return format_response(
                success=True,
                message='Password changed successfully'
            )
        else:
            return create_error_response('PASSWORD_CHANGE_ERROR', result['message'])
            
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Password change failed')

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = AuthService.get_current_user()
        
        if not user:
            return create_error_response('AUTHENTICATION_ERROR', 'User not found')
        
        # Generate new tokens
        tokens = user.generate_tokens()
        
        return format_response(
            success=True,
            message='Token refreshed successfully',
            data={'tokens': tokens}
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Token refresh failed')

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify JWT token validity"""
    try:
        data = request.get_json()
        token = data.get('token', '') if data else ''
        
        if not token:
            return create_error_response('VALIDATION_ERROR', 'Token is required')
        
        # In a real implementation, you would decode and verify the token
        # For now, this is a placeholder
        
        return format_response(
            success=True,
            message='Token verification endpoint',
            data={'valid': True, 'message': 'Token verification not implemented'}
        )
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Token verification failed')
