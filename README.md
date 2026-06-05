# Acne Detection System - Production Backend

🚀 **Advanced AI-powered acne detection and classification system with unified Python Flask backend**

## 📋 Overview

This is a complete rewrite of the original acne detection system, featuring:
- **Unified Python Flask Backend** - Single technology stack
- **Professional Architecture** - Industry-standard patterns
- **Secure Authentication** - JWT tokens, password hashing
- **Scalable Database** - PostgreSQL/SQLite with proper models
- **ML Integration** - Direct access to PyTorch models
- **Production Ready** - Docker support, logging, monitoring

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Python Flask App               │
├─────────────────────────────────────────┤
│  Authentication Layer                   │
│  ├── JWT Session Management             │
│  ├── User Registration/Login           │
│  └── Role-based Access Control          │
├─────────────────────────────────────────┤
│  API Layer                              │
│  ├── RESTful Endpoints                  │
│  ├── File Upload Handling               │
│  └── Response Formatting                │
├─────────────────────────────────────────┤
│  ML Service Layer                       │
│  ├── YOLO Detection                     │
│  ├── EfficientNet Classification         │
│  └── Result Processing                  │
├─────────────────────────────────────────┤
│  Data Layer                             │
│  ├── PostgreSQL/SQLite Database         │
│  ├── User Management                    │
│  ├── Detection History                  │
│  └── System Settings                    │
└─────────────────────────────────────────┘
```

## 🛠️ Technology Stack

### Backend Framework
- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Authentication
- **Flask-CORS** - Cross-origin requests
- **Flask-Migrate** - Database migrations
- **Flask-Limiter** - Rate limiting

### Database
- **SQLite** (Development)
- **PostgreSQL** (Production)
- **SQLAlchemy** ORM

### Security
- **bcrypt** - Password hashing
- **JWT** - Token authentication
- **Werkzeug** - Security utilities

### Machine Learning
- **PyTorch** - Deep learning framework
- **OpenCV** - Image processing
- **Ultralytics** - YOLO detection
- **EfficientNet** - Classification model

## 📁 Project Structure

```
acne-backend-prod/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt           # Python dependencies
├── run.py                   # Development server runner
├── .env.example             # Environment variables template
├── models/                  # Database models
│   ├── __init__.py
│   ├── user.py              # User model
│   ├── detection.py         # Detection models
│   └── setting.py          # Settings model
├── services/                # Business logic
│   ├── __init__.py
│   ├── auth_service.py      # Authentication logic
│   ├── ml_service.py        # ML inference logic
│   └── file_service.py      # File handling logic
├── routes/                  # API endpoints
│   ├── __init__.py
│   ├── auth.py             # Authentication routes
│   ├── api.py              # Main API routes
│   └── admin.py            # Admin routes
├── utils/                   # Utilities
│   ├── __init__.py
│   ├── security.py         # Security utilities
│   ├── validators.py       # Input validation
│   └── helpers.py          # Helper functions
├── migrations/              # Database scripts
│   └── init_db.py          # Database initialization
├── uploads/                 # User uploaded files
├── static/                  # Static assets
├── templates/               # HTML templates
├── logs/                    # Application logs
└── best1.pt               # YOLO detection model
└── acne_weights.pth         # EfficientNet classification model
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- pip (Python package manager)

### 2. Installation

```bash
# Clone the project
cd acne-backend-prod

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Initialize database
python migrations/init_db.py

# Start development server
python run.py
```

### 3. Access the Application
- **API Base URL**: `http://localhost:5000/api`
- **Health Check**: `http://localhost:5000/health`
- **Default Admin**: `admin` / `admin123` ⚠️

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "confirm_password": "password123"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "testuser",
    "password": "password123",
    "remember_me": false
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

### Detection Endpoints

#### Analyze Image
```http
POST /api/detect
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <image_file>
```

#### Get Detection History
```http
GET /api/detection-history?page=1&per_page=20
Authorization: Bearer <access_token>
```

### Admin Endpoints

#### Get All Users
```http
GET /api/admin/users
Authorization: Bearer <admin_token>
```

#### Get System Statistics
```http
GET /api/admin/stats
Authorization: Bearer <admin_token>
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Database
DATABASE_URL=sqlite:///acne_detection.db

# File Upload
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=uploads

# ML Models
YOLO_MODEL_PATH=best1.pt
EFFICIENTNET_MODEL_PATH=acne_weights.pth
```

## 🔐 Security Features

- **Password Hashing** - bcrypt with salt
- **JWT Authentication** - Secure token-based auth
- **Input Validation** - Comprehensive input sanitization
- **Rate Limiting** - Configurable request limits
- **CORS Protection** - Cross-origin request handling
- **SQL Injection Prevention** - Parameterized queries
- **File Security** - File type and size validation
- **Security Logging** - Comprehensive audit trail

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Detection Sessions Table
```sql
CREATE TABLE detection_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    image_path VARCHAR(255),
    total_detections INTEGER DEFAULT 0,
    severity_level VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Detections Table
```sql
CREATE TABLE detections (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES detection_sessions(id),
    acne_type VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    bbox_x INTEGER NOT NULL,
    bbox_y INTEGER NOT NULL,
    bbox_width INTEGER NOT NULL,
    bbox_height INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker build -t acne-detection-api .

# Run container
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads acne-detection-api
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test registration
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123","confirm_password":"test123"}'
```

## 📈 Performance Features

- **Model Caching** - ML models loaded once at startup
- **Database Connection Pooling** - Efficient database connections
- **File Upload Optimization** - Streaming uploads
- **Response Caching** - Configurable response caching
- **Background Tasks** - Async processing support

## 🔍 Monitoring and Logging

### Application Logs
- **Location**: `logs/acne_detection.log`
- **Rotation**: 10MB files, 10 backups
- **Format**: Timestamp, level, message, location

### Security Events
- **User Registration/Login**
- **Failed Authentication Attempts**
- **File Uploads**
- **Admin Actions**
- **System Changes**

### Health Monitoring
- **Database Connectivity**
- **Model Loading Status**
- **Storage Statistics**
- **API Response Times**

## 🚀 Production Deployment

### Pre-deployment Checklist
- [ ] Set strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Configure production database (PostgreSQL)
- [ ] Set up SSL certificates
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Change default admin password
- [ ] Review and update CORS settings
- [ ] Test all API endpoints
- [ ] Load test with production models

### Deployment Steps
```bash
# 1. Set up production server
sudo apt update && sudo apt install python3-pip postgresql nginx

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with production values

# 4. Initialize database
python migrations/init_db.py

# 5. Start with Gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app

# 6. Configure Nginx reverse proxy
# Edit /etc/nginx/sites-available/acne-detection
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API examples

## 🔄 Version History

### v2.0.0 - Production Backend
- ✅ Complete rewrite with unified Flask backend
- ✅ Professional architecture with proper separation of concerns
- ✅ JWT-based authentication system
- ✅ PostgreSQL database support
- ✅ Comprehensive API documentation
- ✅ Security best practices
- ✅ Docker deployment support
- ✅ Production-ready configuration

### v1.0.0 - Original System
- ✅ Basic Flask + Node.js dual backend
- ✅ JSON file database
- ✅ Simple authentication
- ✅ YOLO + EfficientNet ML models

---

## 🎯 Key Improvements in v2.0.0

1. **Unified Backend**: Single Python Flask application
2. **Professional Architecture**: Industry-standard patterns and practices
3. **Enhanced Security**: JWT tokens, proper password hashing, security logging
4. **Scalable Database**: PostgreSQL support with proper migrations
5. **Comprehensive API**: RESTful endpoints with proper documentation
6. **Production Ready**: Docker support, monitoring, logging
7. **Better Error Handling**: Standardized error responses
8. **Input Validation**: Comprehensive validation and sanitization
9. **Rate Limiting**: Configurable request rate limits
10. **Admin Panel**: Complete user and system management

**This backend is production-ready and follows industry best practices for security, scalability, and maintainability.**
