from datetime import datetime
from . import db

class Setting(db.Model):
    """System settings model"""
    __tablename__ = 'settings'
    
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, key, value, description=None):
        self.key = key
        self.value = value
        self.description = description
    
    def to_dict(self):
        """Convert setting object to dictionary"""
        return {
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_setting(key, default=None):
        """Get setting value by key"""
        from flask import current_app
        with current_app.app_context():
            setting = Setting.query.filter_by(key=key).first()
            return setting.value if setting else default
    
    @staticmethod
    def set_setting(key, value, description=None):
        """Set setting value"""
        from flask import current_app
        with current_app.app_context():
            setting = Setting.query.filter_by(key=key).first()
            if setting:
                setting.value = value
                if description:
                    setting.description = description
            else:
                setting = Setting(key, value, description)
                db.session.add(setting)
            db.session.commit()
    
    def __repr__(self):
        return f'<Setting {self.key}: {self.value}>'
