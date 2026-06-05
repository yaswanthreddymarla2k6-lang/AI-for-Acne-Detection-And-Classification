from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/public-detect', methods=['POST'])
def public_detect_acne():
    """Public acne detection endpoint (no authentication required)"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'VALIDATION_ERROR',
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'VALIDATION_ERROR',
                'message': 'No file selected'
            }), 400
        
        # Validate file is an image
        if not file.content_type.startswith('image/'):
            return jsonify({
                'success': False,
                'error': 'VALIDATION_ERROR',
                'message': 'File must be an image'
            }), 400
        
        # For demo purposes, return mock detection results
        # In production, this would call the actual ML models
        mock_detections = [
            {
                'type': 'Blackheads',
                'confidence': 0.85,
                'bbox': {'x': 100, 'y': 150, 'width': 30, 'height': 30}
            },
            {
                'type': 'Whiteheads',
                'confidence': 0.92,
                'bbox': {'x': 200, 'y': 180, 'width': 25, 'height': 25}
            },
            {
                'type': 'Papules',
                'confidence': 0.78,
                'bbox': {'x': 300, 'y': 220, 'width': 35, 'height': 35}
            }
        ]
        
        return jsonify({
            'success': True,
            'message': 'Detection completed successfully',
            'data': {
                'total_detections': len(mock_detections),
                'severity_level': 'Moderate',
                'detections': mock_detections,
                'annotated_image': None,  # Would contain base64 image in production
                'statistics': {
                    'blackheads': 1,
                    'whiteheads': 1,
                    'papules': 1,
                    'pustules': 0,
                    'cysts': 0
                },
                'processed_at': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Public detection error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'SERVER_ERROR',
            'message': 'Detection failed'
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is running',
        'timestamp': datetime.utcnow().isoformat()
    })
