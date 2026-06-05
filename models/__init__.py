from flask_sqlalchemy import SQLAlchemy

# Shared database instance
db = SQLAlchemy()

from .user import User
from .detection import DetectionSession, Detection
from .setting import Setting

__all__ = ['User', 'DetectionSession', 'Detection', 'Setting', 'db']
