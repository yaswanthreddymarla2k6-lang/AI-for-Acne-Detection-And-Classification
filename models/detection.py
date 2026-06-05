from datetime import datetime

from . import db

class DetectionSession(db.Model):
    """Detection session for tracking user detection batches"""
    __tablename__ = 'detection_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(255))
    total_detections = db.Column(db.Integer, default=0)
    severity_level = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    detections = db.relationship('Detection', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id, image_path=None, total_detections=0, severity_level=None):
        self.user_id = user_id
        self.image_path = image_path
        self.total_detections = total_detections
        self.severity_level = severity_level
    
    def calculate_severity(self):
        """Calculate severity level based on detection count"""
        if self.total_detections == 0:
            self.severity_level = 'Clear Skin'
        elif self.total_detections < 5:
            self.severity_level = 'Mild'
        elif self.total_detections < 15:
            self.severity_level = 'Moderate'
        else:
            self.severity_level = 'Severe'
    
    def to_dict(self):
        """Convert session object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_path': self.image_path,
            'total_detections': self.total_detections,
            'severity_level': self.severity_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'detections': [detection.to_dict() for detection in self.detections]
        }
    
    def __repr__(self):
        return f'<DetectionSession {self.id} - User {self.user_id}>'

class Detection(db.Model):
    """Individual detection result"""
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('detection_sessions.id'), nullable=False)
    acne_type = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    bbox_x = db.Column(db.Integer, nullable=False)
    bbox_y = db.Column(db.Integer, nullable=False)
    bbox_width = db.Column(db.Integer, nullable=False)
    bbox_height = db.Column(db.Integer, nullable=False)
    crop_image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, session_id, acne_type, confidence, bbox_x, bbox_y, bbox_width, bbox_height, crop_image_path=None):
        self.session_id = session_id
        self.acne_type = acne_type
        self.confidence = confidence
        self.bbox_x = bbox_x
        self.bbox_y = bbox_y
        self.bbox_width = bbox_width
        self.bbox_height = bbox_height
        self.crop_image_path = crop_image_path
    
    def to_dict(self):
        """Convert detection object to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'acne_type': self.acne_type,
            'confidence': float(self.confidence),
            'bbox_x': self.bbox_x,
            'bbox_y': self.bbox_y,
            'bbox_width': self.bbox_width,
            'bbox_height': self.bbox_height,
            'crop_image_path': self.crop_image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Detection {self.acne_type} - Confidence {self.confidence}>'
