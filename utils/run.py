#!/usr/bin/env python3
"""
Development server runner for Acne Detection System
"""

import os
import sys
from app import create_app

def main():
    """Main entry point"""
    # Set environment variables
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('PORT', '5000')
    
    # Create app
    app = create_app()
    
    print("🚀 Starting Acne Detection System")
    print("=" * 50)
    print(f"📍 Environment: {app.config['ENV']}")
    print(f"🌐 Server: http://0.0.0.0:{os.environ.get('PORT', '5000')}")
    print(f"🗄️  Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"📁 Uploads: {app.config['UPLOAD_FOLDER']}")
    print("=" * 50)
    
    # Check if models exist
    yolo_path = app.config.get('YOLO_MODEL_PATH', 'best1.pt')
    efficientnet_path = app.config.get('EFFICIENTNET_MODEL_PATH', 'acne_weights.pth')
    
    if not os.path.exists(yolo_path):
        print(f"⚠️  Warning: YOLO model not found at {yolo_path}")
    
    if not os.path.exists(efficientnet_path):
        print(f"⚠️  Warning: EfficientNet model not found at {efficientnet_path}")
    
    # Check database
    if not os.path.exists('acne_detection.db'):
        print("⚠️  Warning: Database not found. Run 'python migrations/init_db.py' first")
        return
    
    try:
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', '5000')),
            debug=app.config.get('DEBUG', False),
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
