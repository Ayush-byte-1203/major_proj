# EcoScrap - Sustainable Scrap Marketplace
## ♻️ Building a Sustainable Future Through Technology

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 **Quick Start**

```bash
# Clone the repository
git clone <repository-url>
cd ecoscrap

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd ecoscrap
pip install -r requirements.txt

# Initialize database
python3 init_db.py

# Run the application
python3 app_modular.py  # Recommended: Modular version
# OR
python3 app.py          # Original monolithic version
# OR
python3 run.py          # Using startup script
```

**Access the application at:** `http://localhost:5001`

## 📁 **Project Structure**

The EcoScrap project is organized into a clean, logical structure:

```
ecoscrap/                          # Root project directory
├── README.md                      # This file - Project overview
├── ecoscrap/                      # Backend application
│   ├── app.py                     # Original monolithic application
│   ├── app_modular.py            # 🆕 Modular application (recommended)
│   ├── models.py                  # Database models & ORM
│   ├── decorators.py              # Access control decorators
│   ├── config.py                  # Configuration management
│   ├── requirements.txt            # Python dependencies
│   ├── init_db.py                 # Database initialization
│   ├── run.py                     # Application startup script
│   ├── ecoscrap.db               # SQLite database
│   └── routes/                    # Route modules
│       ├── __init__.py            # Package initialization
│       ├── auth.py                # Authentication routes
│       ├── products.py            # Product management routes
│       ├── pickups.py             # Pickup scheduling routes
│       ├── transactions.py        # Order processing routes
│       ├── admin.py               # Administrative functions
│       ├── dashboard.py           # Dashboard & analytics
│       └── content.py             # Content management
├── frontend/                      # Frontend application
│   ├── index.html                 # Main HTML entry point
│   ├── css/                       # Stylesheets
│   │   ├── main.css              # Main CSS imports
│   │   ├── base.css              # Base styles & variables
│   │   ├── layout.css            # Layout systems
│   │   ├── components.css        # UI components
│   │   └── utilities.css         # Utility classes
│   └── js/                        # JavaScript modules
│       ├── main.js                # Main entry point
│       ├── api-client.js          # API communication
│       ├── core/                  # Core application logic
│       │   └── app.js            # Core app functionality
│       └── modules/               # Feature modules
│           ├── auth.js            # Authentication
│           ├── marketplace.js     # Product management
│           ├── pickups.js         # Pickup scheduling
│           ├── dashboard.js       # Analytics
│           ├── content.js         # Content management
│           ├── database.js        # Data persistence
│           └── ui.js              # UI utilities
├── docs/                          # Documentation
│   ├── ECOSCRAP_CHEATSHEET.md    # Complete developer cheat sheet
│   ├── ECOSCRAP_CHEATSHEET.html  # Interactive HTML cheat sheet
│   └── MODULAR_STRUCTURE.md      # Detailed architecture guide
├── tools/                         # Development tools
│   └── convert_to_pdf.py         # HTML to PDF converter
└── venv/                          # Python virtual environment
```

## 🏗️ **New Modular Architecture**

The EcoScrap application has been completely refactored into a modular, maintainable structure:

### **🔄 Migration Status**
- ✅ **Completed**: Models, decorators, auth routes, product routes
- 🔄 **In Progress**: Pickup, transaction, admin, dashboard routes
- 📋 **To Implement**: Content management routes

### **Benefits of Modular Structure**
- **Maintainability:** Smaller, focused files
- **Scalability:** Easy to add new features
- **Team Development:** Multiple developers can work simultaneously
- **Testing:** Independent module testing
- **Code Reuse:** Modules can be shared across applications

## 🌟 **Key Features**

### **🛡️ Authentication & Security**
- **Multi-role System**: Customer, Dealer, Admin roles
- **Secure Authentication**: Flask-Login with password hashing
- **Role-based Access Control**: Decorators for endpoint protection
- **Session Management**: Secure user sessions

### **🏪 Marketplace Operations**
- **Product Management**: Create, update, delete products
- **Approval Workflow**: Admin approval for marketplace visibility
- **Category System**: Organized product categorization
- **Stock Management**: Real-time inventory tracking

### **📦 Pickup & Collection**
- **Smart Scheduling**: Automated pickup scheduling
- **Rate Calculation**: Real-time scrap value estimation
- **Material Classification**: Support for various scrap types
- **Status Tracking**: Complete pickup lifecycle management

### **💳 Transaction Processing**
- **Order Management**: Complete order lifecycle
- **Payment Methods**: COD, UPI, Card, Net Banking
- **Status Tracking**: Pending, completed, cancelled states
- **Financial Records**: Comprehensive transaction history

### **📊 Analytics & Dashboard**
- **Role-specific Metrics**: Different views for each user type
- **Business Intelligence**: Revenue, orders, user statistics
- **Performance Tracking**: System-wide analytics
- **Real-time Updates**: Live data refresh

## 🛠️ **Technology Stack**

### **Backend**
- **Framework**: Flask 2.3+
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Security**: Werkzeug password hashing
- **Architecture**: Modular blueprint-based structure

### **Frontend**
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with custom properties
- **JavaScript**: ES6+ modular architecture
- **Responsive Design**: Mobile-first approach

### **Development Tools**
- **Code Quality**: Black (formatting), Flake8 (linting)
- **Virtual Environment**: Python venv
- **Package Management**: pip with requirements.txt

## 🔐 **Security Features**

### **Authentication & Authorization**
- **Password Security**: Bcrypt hashing with salt
- **Session Management**: Secure Flask-Login sessions
- **Role-based Access**: Granular permission control
- **Input Validation**: Comprehensive request validation

### **Data Protection**
- **SQL Injection Prevention**: SQLAlchemy ORM
- **XSS Protection**: Input sanitization
- **CSRF Protection**: Built-in Flask security
- **Secure Headers**: Production-ready security headers

## 📊 **Database Schema**

### **Core Models**
- **User**: Authentication, profiles, roles
- **Product**: Marketplace items, approval workflow
- **Transaction**: Order and payment records
- **Pickup**: Scrap collection scheduling
- **Rate**: Current scrap material pricing
- **Tip**: Educational content for users

### **Relationships**
- Users can have multiple products (dealers)
- Users can have multiple transactions (customers/dealers)
- Users can have multiple pickups (customers)
- Products belong to dealers
- Transactions connect customers and dealers

## 🚀 **API Endpoints**

### **Authentication (`/api/auth`)**
- `POST /register` - User registration
- `POST /login` - User authentication
- `POST /logout` - User logout
- `GET/PUT /profile` - Profile management
- `POST /change-password` - Password updates

### **Products (`/api/products`)**
- `GET /` - List products with filtering
- `POST /` - Create new products (dealers)
- `PUT/DELETE /<id>` - Manage products
- `POST /<id>/approve` - Approve products (admins)
- `POST /<id>/reject` - Reject products (admins)

### **Pickups (`/api/pickups`)**
- `GET /` - List pickups by user role
- `POST /` - Schedule new pickups (customers)

### **Transactions (`/api/transactions`)**
- `GET /` - List transactions by user role
- `POST /` - Create new orders (customers)

### **Admin (`/api/admin`)**
- `GET /users` - List all users (admins)

### **Dashboard (`/api/dashboard`)**
- `GET /stats` - Role-specific statistics

### **Content (`/api`)**
- `GET /rates` - Current scrap material rates
- `GET /tips` - Educational content and tips
- `POST /calculate-estimate` - Scrap value estimation

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Security
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///ecoscrap.db

# Server
FLASK_ENV=development
FLASK_DEBUG=True
```

### **Configuration Classes**
- **Config**: Base configuration
- **DevelopmentConfig**: Development environment settings
- **TestingConfig**: Testing environment settings
- **ProductionConfig**: Production environment settings

## 📱 **Responsive Design**

### **Breakpoints**
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### **Design System**
- **Color Palette**: Consistent color scheme
- **Typography**: Scalable font system
- **Spacing**: Systematic spacing scale
- **Components**: Reusable UI components

## 🧪 **Testing & Development**

### **Running Tests**
```bash
# Navigate to backend directory
cd ecoscrap

# Run all tests
python3 -m pytest

# Run specific test file
python3 -m pytest tests/test_auth.py

# Run with coverage
python3 -m pytest --cov=app tests/
```

### **Code Quality**
```bash
# Navigate to backend directory
cd ecoscrap

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### **Development Server**
```bash
# Navigate to backend directory
cd ecoscrap

# Development mode (auto-reload)
python3 app_modular.py

# Production mode
gunicorn app_modular:app
```

## 📚 **Documentation**

### **Available Documentation**
- **README.md**: This file - Project overview and setup
- **docs/ECOSCRAP_CHEATSHEET.md**: Complete developer cheat sheet
- **docs/ECOSCRAP_CHEATSHEET.html**: Interactive HTML cheat sheet
- **docs/MODULAR_STRUCTURE.md**: Detailed modular architecture guide
- **Inline Code Comments**: Comprehensive function documentation

### **Code Documentation Standards**
- **Function Documentation**: Purpose, parameters, returns, examples
- **Class Documentation**: Purpose, fields, methods, relationships
- **Module Documentation**: Overview, contents, usage examples
- **Security Documentation**: Authentication, authorization, validation

## 🚀 **Deployment**

### **Development**
```bash
# Navigate to backend directory
cd ecoscrap

# Local development
python3 app_modular.py

# With environment variables
FLASK_ENV=development python3 app_modular.py
```

### **Production**
```bash
# Navigate to backend directory
cd ecoscrap

# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app_modular:app

# Using uWSGI
uwsgi --http :8000 --module app_modular:app
```

### **Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY ecoscrap/requirements.txt .
RUN pip install -r requirements.txt
COPY ecoscrap/ .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app_modular:app"]
```

## 🤝 **Contributing**

### **Development Workflow**
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### **Code Standards**
- **Python**: PEP 8 compliance
- **JavaScript**: ES6+ standards
- **CSS**: BEM methodology
- **Documentation**: Comprehensive inline comments

### **Testing Requirements**
- **Unit Tests**: All new features
- **Integration Tests**: API endpoints
- **Coverage**: Minimum 80% code coverage
- **Documentation**: All public functions documented

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Flask Community**: For the excellent web framework
- **SQLAlchemy Team**: For the powerful ORM
- **Open Source Contributors**: For inspiration and tools
- **EcoScrap Team**: For building sustainable solutions

## 📞 **Support & Contact**

- **Documentation**: [docs/](docs/) directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@ecoscrap.com

---

**EcoScrap Development Team**  
*Building a sustainable future through technology*  
*Version 2.0.0 | 2024 - Modular Architecture Release*

---

## 🆕 **What's New in v2.0.0**

### **Major Refactoring**
- **Modular Architecture**: Complete code reorganization
- **Blueprint-based Routing**: Flask blueprints for better organization
- **Separated Concerns**: Models, routes, and business logic separated
- **Enhanced Documentation**: Comprehensive inline documentation

### **Improved Maintainability**
- **Smaller Files**: Focused, single-responsibility modules
- **Better Organization**: Clear file structure and naming
- **Easier Testing**: Independent module testing
- **Team Development**: Multiple developers can work simultaneously

### **Enhanced Security**
- **Centralized Decorators**: Consistent access control
- **Better Validation**: Comprehensive input validation
- **Security Documentation**: Clear security feature documentation
- **Role-based Access**: Granular permission system

### **Developer Experience**
- **Clear Structure**: Easy to understand and navigate
- **Comprehensive Comments**: Every function documented
- **Usage Examples**: Code examples and patterns
- **Best Practices**: Industry-standard Flask patterns

## 🎯 **Quick Navigation**

- **🚀 Get Started**: Follow the Quick Start section above
- **📁 Backend**: Navigate to `ecoscrap/` directory for Python code
- **🎨 Frontend**: Navigate to `frontend/` directory for HTML/CSS/JS
- **📚 Documentation**: Check `docs/` directory for detailed guides
- **🛠️ Tools**: Use `tools/` directory for development utilities
