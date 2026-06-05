import logging
from datetime import datetime
from flask import current_app, request
import hashlib
import secrets

logger = logging.getLogger(__name__)

def log_security_event(event_type, message, user_id=None):
    """Log security events for monitoring and auditing"""
    try:
        security_log = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'message': message,
            'user_id': user_id,
            'ip_address': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr) if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None
        }
        
        # Log to file (in production, this should go to a proper security logging system)
        logger.warning(f"SECURITY_EVENT: {security_log}")
        
        # In production, you might want to:
        # - Send to SIEM system
        # - Store in security database
        # - Send alerts for suspicious activity
        
    except Exception as e:
        logger.error(f"Security logging error: {str(e)}")

def generate_csrf_token():
    """Generate CSRF token for form protection"""
    return secrets.token_urlsafe(32)

def validate_csrf_token(token):
    """Validate CSRF token"""
    # In a real implementation, you'd store tokens in session
    # For now, this is a placeholder
    return True

def hash_password(password, salt=None):
    """Hash password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Use SHA-256 with salt (in production, use bcrypt or Argon2)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return {
        'hash': password_hash,
        'salt': salt
    }

def verify_password(password, hashed_password, salt):
    """Verify password against hash"""
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash == hashed_password

def rate_limit_check(user_id, action, limit=100, window_minutes=60):
    """Check if user has exceeded rate limit"""
    # This is a simplified implementation
    # In production, use Redis or database for rate limiting
    from flask import current_app
    
    # For now, always return True (no rate limiting)
    # Implement proper rate limiting based on your needs
    return True

def sanitize_input(input_string):
    """Sanitize user input to prevent XSS"""
    if not input_string:
        return ""
    
    # Basic XSS prevention
    dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'onerror=', 'onload=']
    sanitized = input_string
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()

def is_admin_user(user):
    """Check if user has admin privileges"""
    return user and user.role == 'admin'

def get_client_ip():
    """Get client IP address, considering proxies"""
    if request:
        # Check for forwarded IP
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Return direct IP
        return request.remote_addr
    
    return None

def check_file_security(file_path):
    """Check if file upload is secure"""
    try:
        import os
        
        # Check file size
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if os.path.getsize(file_path) > max_size:
            return False, "File too large"
        
        # Check file extension
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
        file_ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
        
        if file_ext not in allowed_extensions:
            return False, f"File type '{file_ext}' not allowed"
        
        # Additional security checks can be added here:
        # - Magic number verification
        # - Virus scanning
        # - Content analysis
        
        return True, "File is secure"
        
    except Exception as e:
        logger.error(f"File security check error: {str(e)}")
        return False, "Security check failed"

def generate_api_key():
    """Generate secure API key"""
    return secrets.token_urlsafe(32)

def validate_api_key(api_key):
    """Validate API key"""
    # In production, validate against database
    # For now, this is a placeholder
    return len(api_key) == 43  # Length of token_urlsafe(32)

def encrypt_sensitive_data(data, key=None):
    """Encrypt sensitive data"""
    # In production, use proper encryption like AES
    # This is a placeholder
    import base64
    encoded = base64.b64encode(data.encode()).decode()
    return encoded

def decrypt_sensitive_data(encoded_data, key=None):
    """Decrypt sensitive data"""
    # In production, use proper decryption
    # This is a placeholder
    import base64
    decoded = base64.b64decode(encoded_data.encode()).decode()
    return decoded
