from datetime import datetime
from flask import jsonify
import math

def format_response(success=True, message=None, data=None, error=None, status_code=200):
    """Format standardized API response"""
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    if error:
        response['error'] = error
    
    return jsonify(response), status_code

def paginate_query(query, page=1, per_page=20, max_per_page=100):
    """Paginate database query"""
    # Ensure valid page and per_page values
    try:
        page = max(1, int(page))
        per_page = min(max(1, int(per_page)), max_per_page)
    except (ValueError, TypeError):
        page = 1
        per_page = 20
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count and paginated results
    total = query.count()
    items = query.offset(offset).limit(per_page).all()
    
    # Calculate pagination info
    total_pages = math.ceil(total / per_page)
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': has_next,
            'has_prev': has_prev,
            'next_page': page + 1 if has_next else None,
            'prev_page': page - 1 if has_prev else None
        }
    }

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def format_duration(seconds):
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def calculate_severity_score(detection_count, confidence_sum=None):
    """Calculate severity score based on detection count and confidence"""
    # Base score from detection count
    if detection_count == 0:
        base_score = 0
    elif detection_count < 5:
        base_score = 25
    elif detection_count < 15:
        base_score = 50
    else:
        base_score = 75
    
    # Adjust score based on average confidence if provided
    if confidence_sum and detection_count > 0:
        avg_confidence = confidence_sum / detection_count
        confidence_bonus = avg_confidence * 25  # Max 25 points for confidence
        final_score = min(100, base_score + confidence_bonus)
    else:
        final_score = base_score
    
    return round(final_score, 2)

def extract_filename_from_path(file_path):
    """Extract filename from full path"""
    import os
    return os.path.basename(file_path)

def generate_unique_filename(original_filename, prefix=''):
    """Generate unique filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = original_filename.rsplit('.', 1) if '.' in original_filename else (original_filename, '')
    
    if prefix:
        name = f"{prefix}_{name}_{timestamp}"
    else:
        name = f"{name}_{timestamp}"
    
    return f"{name}.{ext}" if ext else name

def safe_serialize(obj):
    """Safely serialize object to JSON-compatible format"""
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, (list, tuple)):
        return [safe_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: safe_serialize(value) for key, value in obj.items()}
    else:
        return str(obj)

def calculate_detection_statistics(detections):
    """Calculate statistics from detection results"""
    if not detections:
        return {
            'total_count': 0,
            'type_counts': {},
            'avg_confidence': 0,
            'max_confidence': 0,
            'severity_score': 0
        }
    
    total_count = len(detections)
    type_counts = {}
    confidence_sum = 0
    max_confidence = 0
    
    for detection in detections:
        # Count by type
        acne_type = detection.get('acne_type', 'unknown')
        type_counts[acne_type] = type_counts.get(acne_type, 0) + 1
        
        # Confidence statistics
        confidence = detection.get('confidence', 0)
        confidence_sum += confidence
        max_confidence = max(max_confidence, confidence)
    
    avg_confidence = confidence_sum / total_count if total_count > 0 else 0
    severity_score = calculate_severity_score(total_count, confidence_sum)
    
    return {
        'total_count': total_count,
        'type_counts': type_counts,
        'avg_confidence': round(avg_confidence, 3),
        'max_confidence': round(max_confidence, 3),
        'severity_score': round(severity_score, 2)
    }

def validate_pagination_params(page, per_page, max_per_page=100):
    """Validate and normalize pagination parameters"""
    try:
        page = max(1, int(page) if page else 1)
        per_page = min(max(1, int(per_page) if per_page else 20), max_per_page)
        return page, per_page
    except (ValueError, TypeError):
        return 1, 20

def create_error_response(error_type, message, status_code=400):
    """Create standardized error response"""
    return format_response(
        success=False,
        error={
            'type': error_type,
            'message': message
        },
        status_code=status_code
    )

def merge_dicts(*dicts):
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

def is_valid_image_format(filename):
    """Check if file has valid image format"""
    valid_formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
    if not filename or '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in valid_formats
