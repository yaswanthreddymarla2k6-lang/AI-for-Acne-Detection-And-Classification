# 🗂️ Project Structure Documentation

## 📁 Organized Directory Structure

```
acne-backend-prod/
├── 📄 Core Application Files
│   ├── app.py                    # Main Flask application
│   ├── config.py                 # Configuration settings
│   ├── run.py                    # Development server runner
│   └── requirements.txt           # Python dependencies
│
├── 📊 Database & Models
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User authentication model
│   │   ├── detection.py         # Detection and session models
│   │   └── setting.py          # System settings model
│   └── migrations/              # Database scripts
│       └── init_db.py          # Database initialization
│
├── 🔧 Business Logic (Services)
│   └── services/                # Core business logic
│       ├── __init__.py
│       ├── auth_service.py      # Authentication & user management
│       ├── ml_service.py        # ML model integration
│       └── file_service.py      # File handling & storage
│
├── 🌐 API Endpoints (Routes)
│   └── routes/                  # API route definitions
│       ├── __init__.py
│       ├── auth.py             # Authentication endpoints
│       ├── api.py              # Main detection API
│       └── admin.py            # Admin management endpoints
│
├── 🛠️ Utilities & Helpers
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── security.py         # Security utilities
│       ├── validators.py       # Input validation
│       └── helpers.py          # Helper functions
│
├── 🎨 Frontend Assets
│   ├── static/                   # Static files (CSS, JS, images)
│   │   ├── css/               # Stylesheets
│   │   │   ├── style.css
│   │   │   └── style-modern.css
│   │   ├── js/                # JavaScript files
│   │   │   └── auth.js
│   │   └── images/            # Image assets
│   └── templates/               # HTML templates
│       ├── auth/               # Authentication pages
│       │   ├── login.html
│       │   └── signup.html
│       ├── dashboard/          # Dashboard pages
│       │   ├── dashboard.html
│       │   └── dashboard-modern.html
│       ├── upload/            # Upload pages
│       │   ├── upload.html
│       │   └── upload-modern.html
│       ├── index.html          # Main landing page
│       ├── index-modern.html  # Modern landing page
│       └── about.html          # About page
│
├── 📁 User Data Storage
│   ├── uploads/                  # User uploaded files
│   └── acne_detection.db        # SQLite database
│
├── 🤖 ML Models
│   ├── best1.pt                 # YOLO detection model
│   └── acne_weights.pth         # EfficientNet classification model
│
├── 📚 Documentation
│   ├── README.md                # Main documentation
│   ├── PROJECT_STRUCTURE.md     # This file
│   └── .env.example            # Environment variables template
│
└── 🗑️ Legacy Files (Cleaned Up)
    └── [Old unorganized files removed]
```

## 🎯 Key Improvements Made

### ✅ **Proper Separation of Concerns**
- **Models** separated from business logic
- **Services** handle core functionality
- **Routes** only handle HTTP requests
- **Utilities** reusable across the application

### ✅ **Clean Frontend Organization**
- **Static files** organized by type (CSS, JS, images)
- **Templates** organized by functionality (auth, dashboard, upload)
- **Removed duplicate and legacy files**

### ✅ **Professional Backend Structure**
- **Configuration** centralized in config.py
- **Database models** properly organized
- **API endpoints** logically grouped
- **Security utilities** separated and reusable

## 🚀 How to Navigate

### **For Development:**
```bash
# Main application
app.py                 # Edit main Flask app
config.py              # Modify configuration
run.py                 # Start development server

# Add new features
services/               # Add business logic
routes/                 # Add API endpoints
models/                 # Add database models
utils/                  # Add utilities
```

### **For Frontend:**
```bash
# Static assets
static/css/             # Edit styles
static/js/              # Edit JavaScript
static/images/          # Add images

# HTML templates
templates/auth/         # Authentication pages
templates/dashboard/    # Dashboard pages
templates/upload/      # Upload pages
```

### **For Database:**
```bash
# Models and migrations
models/                 # Database models
migrations/            # Database scripts
```

## 📋 File Responsibilities

| Directory | Purpose | Key Files |
|-----------|---------|------------|
| `models/` | Database definitions | `user.py`, `detection.py`, `setting.py` |
| `services/` | Business logic | `auth_service.py`, `ml_service.py`, `file_service.py` |
| `routes/` | API endpoints | `auth.py`, `api.py`, `admin.py` |
| `utils/` | Helper functions | `security.py`, `validators.py`, `helpers.py` |
| `static/css/` | Stylesheets | `style.css`, `style-modern.css` |
| `static/js/` | JavaScript | `auth.js` |
| `templates/auth/` | Authentication UI | `login.html`, `signup.html` |
| `templates/dashboard/` | Dashboard UI | `dashboard.html`, `dashboard-modern.html` |
| `templates/upload/` | Upload UI | `upload.html`, `upload-modern.html` |

## 🔧 Configuration Management

### **Environment Variables** (`.env`)
```bash
# Copy template and configure
cp .env.example .env

# Key settings
FLASK_ENV=development
DATABASE_URL=sqlite:///acne_detection.db
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### **Application Config** (`config.py`)
```python
# Different environments
- Development (SQLite, debug=True)
- Production (PostgreSQL, debug=False)
- Testing (In-memory database)
```

## 🎨 Frontend Asset Organization

### **CSS Structure**
```
static/css/
├── style.css           # Original styles
└── style-modern.css   # Modern responsive styles
```

### **JavaScript Structure**
```
static/js/
└── auth.js            # Authentication functionality
```

### **Template Structure**
```
templates/
├── auth/              # User authentication
│   ├── login.html
│   └── signup.html
├── dashboard/         # User dashboard
│   ├── dashboard.html
│   └── dashboard-modern.html
├── upload/            # File upload interface
│   ├── upload.html
│   └── upload-modern.html
├── index.html         # Landing page
├── index-modern.html  # Modern landing
└── about.html         # About page
```

## 🛠️ Development Workflow

### **Adding New Features:**
1. **Models**: Add to `models/` directory
2. **Services**: Implement business logic in `services/`
3. **Routes**: Create API endpoints in `routes/`
4. **Utils**: Add helpers in `utils/`
5. **Templates**: Add HTML in `templates/`
6. **Static**: Add CSS/JS in `static/`

### **Database Changes:**
1. **Modify models** in `models/` directory
2. **Create migration** in `migrations/` directory
3. **Update database** with migration script

### **Frontend Changes:**
1. **Templates**: Edit HTML in appropriate `templates/` subdirectory
2. **Styles**: Add CSS in `static/css/`
3. **Scripts**: Add JavaScript in `static/js/`

## 📊 This Structure Provides:

### ✅ **Maintainability**
- Clear separation of concerns
- Logical file organization
- Easy navigation and understanding

### ✅ **Scalability**
- Modular architecture
- Reusable components
- Easy feature addition

### ✅ **Professional Standards**
- Industry best practices
- Clean code organization
- Proper separation of layers

### ✅ **Development Efficiency**
- Quick file location
- Clear responsibilities
- Reduced cognitive load

---

**🎉 This organized structure follows Flask and Python best practices, making the application maintainable, scalable, and professional!**
