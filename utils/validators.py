import re
from email_validator import validate_email as email_validate

def validate_email(email):
    """Validate email format"""
    try:
        # Use email-validator library for comprehensive validation
        valid = email_validate(email)
        return valid is True
    except:
        return False

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False
    
    if len(password) < 6:
        return False
    
    # Additional password requirements can be added:
    # - At least one uppercase letter
    # - At least one lowercase letter
    # - At least one number
    # - At least one special character
    
    return True

def validate_username(username):
    """Validate username format"""
    if not username:
        return False
    
    # Username should be 3-30 characters
    if len(username) < 3 or len(username) > 30:
        return False
    
    # Only allow alphanumeric characters, underscores, and hyphens
    pattern = r'^[a-zA-Z0-9_-]+$'
    return re.match(pattern, username) is not None

def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid phone number (10-15 digits)
    return len(digits_only) >= 10 and len(digits_only) <= 15

def validate_date(date_string, format='%Y-%m-%d'):
    """Validate date format"""
    try:
        from datetime import datetime
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False

def validate_url(url):
    """Validate URL format"""
    if not url:
        return True  # URL is optional
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def validate_file_extension(filename, allowed_extensions):
    """Validate file extension"""
    if not filename or '.' not in filename:
        return False
    
    file_ext = filename.rsplit('.', 1)[1].lower()
    return file_ext in allowed_extensions

def validate_file_size(file_size, max_size_mb=16):
    """Validate file size in MB"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes

def validate_age(age):
    """Validate age (must be between 0 and 150)"""
    try:
        age_int = int(age)
        return 0 <= age_int <= 150
    except (ValueError, TypeError):
        return False

def validate_numeric(value, min_val=None, max_val=None):
    """Validate numeric value with optional min/max constraints"""
    try:
        num_value = float(value)
        
        if min_val is not None and num_value < min_val:
            return False
        
        if max_val is not None and num_value > max_val:
            return False
        
        return True
    except (ValueError, TypeError):
        return False

def sanitize_string(input_string, max_length=None):
    """Sanitize and validate string input"""
    if not input_string:
        return ""
    
    # Remove leading/trailing whitespace
    sanitized = input_string.strip()
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\n', '\r', '\t']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Apply length limit if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

def validate_json_structure(data, required_fields=None):
    """Validate JSON structure and required fields"""
    if not isinstance(data, dict):
        return False, "Invalid JSON structure"
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, "Valid JSON structure"

def validate_confidence_score(confidence):
    """Validate confidence score (0.0 to 1.0)"""
    try:
        conf_value = float(confidence)
        return 0.0 <= conf_value <= 1.0
    except (ValueError, TypeError):
        return False

def validate_bbox(bbox):
    """Validate bounding box coordinates"""
    if not isinstance(bbox, dict):
        return False
    
    required_keys = ['x', 'y', 'width', 'height']
    if not all(key in bbox for key in required_keys):
        return False
    
    try:
        x = int(bbox['x'])
        y = int(bbox['y'])
        width = int(bbox['width'])
        height = int(bbox['height'])
        
        # Check if coordinates are valid
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            return False
        
        return True
    except (ValueError, TypeError):
        return False

def validate_acne_type(acne_type):
    """Validate acne type against known categories"""
    valid_types = ['blackheads', 'cysts', 'papules', 'pustules', 'whiteheads']
    return acne_type.lower() in valid_types

def validate_severity_level(severity):
    """Validate severity level"""
    valid_levels = ['Clear Skin', 'Mild', 'Moderate', 'Severe']
    return severity in valid_levels
