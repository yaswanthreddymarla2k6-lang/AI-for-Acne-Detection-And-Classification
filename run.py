#!/usr/bin/env python3
"""
Development server runner for Acne Detection System
"""

import os
import sys
from app import app

def main():
    """Main entry point"""
    print("🚀 Starting Acne Detection System")
    print("=" * 50)
    print(f"📍 Environment: development")
    print(f"🌐 Server: http://0.0.0.0:5000")
    print(f"🗄️  Database: sqlite:///acne_detection.db")
    print(f"📁 Uploads: uploads")
    print("=" * 50)
    
    # Check if models exist
    yolo_path = 'c:/Users/SHIV SHAKTI TEA CO/Downloads/project_changed_yolo_fn/review 1 copy/best1.pt'
    efficientnet_path = 'c:/Users/SHIV SHAKTI TEA CO/Downloads/project_changed_yolo_fn/review 1 copy/acne_weights.pth'
    
    if not os.path.exists(yolo_path):
        print(f"⚠️  Warning: YOLO model not found at {yolo_path}")
    
    if not os.path.exists(efficientnet_path):
        print(f"⚠️  Warning: EfficientNet model not found at {efficientnet_path}")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
