from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from models.user import User
from models.detection import DetectionSession
from utils.helpers import format_response, create_error_response, paginate_query
from utils.security import is_admin_user, log_security_event
from utils.validators import validate_email, validate_username
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Admin authentication decorator
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = AuthService.get_current_user()
        if not current_user or not is_admin_user(current_user):
            return create_error_response('AUTHORIZATION_ERROR', 'Admin access required', 403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """Get all users (admin only)"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        
        # Build query
        query = User.query
        
        if search:
            query = query.filter(
                (User.username.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%'))
            )
        
        # Order by creation date
        query = query.order_by(User.created_at.desc())
        
        # Paginate results
        paginated_result = paginate_query(query, page, per_page)
        
        # Format user data
        users_data = []
        for user in paginated_result['items']:
            user_dict = user.to_dict()
            # Add statistics
            user_stats = AuthService.get_user_stats(user.id)
            user_dict['stats'] = user_stats
            users_data.append(user_dict)
        
        return format_response(
            success=True,
            data={
                'users': users_data,
                'pagination': paginated_result['pagination']
            }
        )
        
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Failed to get users')

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """Get specific user details (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return create_error_response('NOT_FOUND', 'User not found')
        
        # Get detailed user statistics
        user_stats = AuthService.get_user_stats(user_id)
        
        user_data = user.to_dict()
        user_data['detailed_stats'] = user_stats
        
        return format_response(
            success=True,
            data=user_data
        )
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Failed to get user')

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """Update user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return create_error_response('NOT_FOUND', 'User not found')
        
        data = request.get_json()
        if not data:
            return create_error_response('VALIDATION_ERROR', 'No data provided')
        
        # Update allowed fields
        if 'email' in data:
            email = data['email'].strip()
            if not validate_email(email):
                return create_error_response('VALIDATION_ERROR', 'Invalid email format')
            user.email = email
        
        if 'username' in data:
            username = data['username'].strip()
            if not validate_username(username):
                return create_error_response('VALIDATION_ERROR', 'Invalid username format')
            
            # Check if username is already taken by another user
            existing_user = User.query.filter(
                (User.username == username) & (User.id != user_id)
            ).first()
            if existing_user:
                return create_error_response('VALIDATION_ERROR', 'Username already exists')
            
            user.username = username
        
        if 'role' in data:
            role = data['role']
            if role not in ['user', 'admin']:
                return create_error_response('VALIDATION_ERROR', 'Invalid role')
            user.role = role
        
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        from flask import current_app
        db = current_app.extensions['sqlalchemy'].db
        db.session.commit()
        
        current_admin_id = get_jwt_identity()
        log_security_event('USER_UPDATED', f'Admin {current_admin_id} updated user {user_id}', current_admin_id)
        
        return format_response(
            success=True,
            message='User updated successfully',
            data=user.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Failed to update user')

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return create_error_response('NOT_FOUND', 'User not found')
        
        # Prevent admin from deleting themselves
        current_admin_id = get_jwt_identity()
        if user_id == current_admin_id:
            return create_error_response('VALIDATION_ERROR', 'Cannot delete your own account')
        
        from flask import current_app
        db = current_app.extensions['sqlalchemy'].db
        
        # Delete user (cascade will handle related records)
        db.session.delete(user)
        db.session.commit()
        
        log_security_event('USER_DELETED', f'Admin {current_admin_id} deleted user {user_id}', current_admin_id)
        
        return format_response(
            success=True,
            message='User deleted successfully'
        )
        
    except Exception as e:
        logger.error(f"Delete user error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Failed to delete user')

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        from flask import current_app
        db = current_app.extensions['sqlalchemy'].db
        
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(role='admin').count()
        
        # Detection statistics
        total_sessions = DetectionSession.query.count()
        recent_sessions = DetectionSession.query.filter(
            DetectionSession.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        # User growth (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_users = User.query.filter(User.created_at >= thirty_days_ago).count()
        
        # Detection trends
        severity_stats = db.session.query(
            DetectionSession.severity_level,
            db.func.count(DetectionSession.id).label('count')
        ).group_by(DetectionSession.severity_level).all()
        
        severity_distribution = {stat.severity_level: stat.count for stat in severity_stats}
        
        stats_data = {
            'users': {
                'total': total_users,
                'active': active_users,
                'admin': admin_users,
                'new_last_30_days': new_users
            },
            'detections': {
                'total_sessions': total_sessions,
                'today': recent_sessions,
                'severity_distribution': severity_distribution
            },
            'system': {
                'uptime': 'N/A',  # Would need actual uptime tracking
                'version': '1.0.0'
            }
        }
        
        return format_response(
            success=True,
            data=stats_data
        )
        
    except Exception as e:
        logger.error(f"Get admin stats error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Failed to get statistics')

@admin_bp.route('/detections', methods=['GET'])
@jwt_required()
@admin_required
def get_all_detections():
    """Get all detection sessions (admin only)"""
    try:
        # Get pagination and filter parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_id = request.args.get('user_id', type=int)
        severity = request.args.get('severity', '').strip()
        date_from = request.args.get('date_from', '').strip()
        date_to = request.args.get('date_to', '').strip()
        
        # Build query
        query = DetectionSession.query
        
        # Apply filters
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if severity:
            query = query.filter_by(severity_level=severity)
        
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.fromisoformat(date_from)
                query = query.filter(DetectionSession.created_at >= date_from_obj)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.fromisoformat(date_to)
                query = query.filter(DetectionSession.created_at <= date_to_obj)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        # Order by creation date
        query = query.order_by(DetectionSession.created_at.desc())
        
        # Paginate results
        paginated_result = paginate_query(query, page, per_page)
        
        # Format sessions with user information
        sessions_data = []
        for session in paginated_result['items']:
            session_dict = session.to_dict()
            # Add user information
            user = User.query.get(session.user_id)
            if user:
                session_dict['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            sessions_data.append(session_dict)
        
        return format_response(
            success=True,
            data={
                'sessions': sessions_data,
                'pagination': paginated_result['pagination']
            }
        )
        
    except Exception as e:
        logger.error(f"Get all detections error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Failed to get detections')

@admin_bp.route('/system/logs', methods=['GET'])
@jwt_required()
@admin_required
def get_system_logs():
    """Get system logs (admin only)"""
    try:
        # In a real implementation, you would read from log files
        # For now, return recent security events
        
        # This is a placeholder implementation
        logs_data = {
            'security_events': [
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'event_type': 'SYSTEM_STATUS',
                    'message': 'System is running normally',
                    'level': 'INFO'
                }
            ],
            'note': 'This is a placeholder. Implement proper log reading in production.'
        }
        
        return format_response(
            success=True,
            data=logs_data
        )
        
    except Exception as e:
        logger.error(f"Get system logs error: {str(e)}")
        return create_error_response('SERVER_ERROR', 'Failed to get system logs')
