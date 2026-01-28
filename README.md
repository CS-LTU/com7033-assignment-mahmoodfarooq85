# Hospital Secure Web App - Healthcare Management System

## 📋 Project Overview

A comprehensive, secure healthcare management system built with Flask (Python).This is professional grade application demonstrates advance level security practices, role-based access control, and comprehensive testing.

**Live Features:**
- 🏥 Professional healthcare data management
- 👥 4 User roles with role-based dashboards (Doctor, Patient, Staff, Admin)
- 🔒 Secure authentication with password hashing
- 📊 Dual database architecture (SQLite + MongoDB)
- 🧪 Comprehensive test suite (50 tests - all passing)
- 📱 Responsive, professional UI/UX
- ✅ Input validation and sanitization

---

## 🏗️ System Architecture

### User Roles & Permissions

| Role | Dashboard | Features | Access |
|------|-----------|----------|--------|
| **Doctor** 👨‍⚕️ | Doctor Dashboard | Patient management, view stats, recent patients | Full patient access |
| **Patient** 🏥 | Patient Dashboard | View health records, appointments, medications | Own records only |
| **Staff** 👨‍💼 | Staff Dashboard | Patient registration, appointments, documentation | Administrative tasks |
| **Admin** 🔐 | Admin Dashboard | System management, user management, backup, logs | Full system access |

### Pages & Routes

```
Public Pages:
  / (Home)
  /about (About)
  /register (Registration - all 4 roles)
  /login (Login)

Protected Pages (Role-based):
  /doctor_dashboard (Doctor only)
  /patient_dashboard (Patient only)
  /staff_dashboard (Staff only)
  /admin_dashboard (Admin only)
  /patients (Doctor only)
  /logout (All authenticated users)
```

---

## 🗄️ Database Architecture

### SQLite (Primary Database)
- **Purpose:** Main authentication and patient records
- **Tables:**
  - `users` - User accounts with hashed passwords
  - `patients` - Patient medical records

### MongoDB (Secondary Database)
- **Purpose:** Data redundancy and NoSQL demonstration
- **Collections:**
  - `users_collection` - User backup with role information
  - `patients_collection` - Patient records backup

**Key Benefit:** Dual storage ensures data integrity and provides redundancy across different database technologies.


## 🔐 Security Features

### Authentication & Authorization
- ✅ **Password Hashing** - Using `werkzeug.security` (bcrypt-based)
- ✅ **Role-Based Access Control (RBAC)** - Four distinct user roles
- ✅ **Session Management** - Secure Flask sessions
- ✅ **Login Required Decorator** - Custom authentication wrapper
- ✅ **Role Enforcement** - Route-level role checking

### Data Protection
- ✅ **Input Validation** - Form validation on all inputs
- ✅ **SQL Injection Prevention** - Parameterized queries
- ✅ **CSRF Protection** - Flask session security
- ✅ **Error Handling** - Graceful error pages (404, 500)

### File Security
- ✅ **Comprehensive .gitignore** - Protects:
  - `.env` - Environment variables (MongoDB credentials)
  - `*.db` - Database files
  - `*.log` - Application and MongoDB logs
  - `__pycache__/` - Python compiled files
  - Log files: `app.log`, `mongo.log`, `error.log`

---

## 📊 Testing

### Test Coverage: **50 Tests - All Passing ✅**

#### Application Tests (test_app.py) - 26 Tests
```
✅ Page Loading Tests (Home, Login, Register, About)
✅ Authentication Tests (Login, Invalid credentials, Logout)
✅ Authorization Tests (Protected pages, Role-based access)
✅ Form Validation Tests (Missing fields, Password mismatch)
✅ Integration Tests (Complete user workflows)
✅ Session Management Tests (Login persistence)
```

#### MongoDB Integration Tests (test_mongo.py) - 24 Tests
```
✅ Connection Tests (MongoDB connectivity)
✅ User Operations (CRUD operations, all 4 roles)
✅ Patient Operations (Insert, update, delete, retrieve)
✅ Data Count Tests (User and patient counts)
✅ Error Handling Tests (Invalid data, non-existent records)
✅ Data Integrity Tests (DateTime validation, role validation)
```

### Running Tests

```bash
# Run all tests
python -m pytest -v

# Run specific test file
python -m pytest test_app.py -v
python -m pytest test_mongo.py -v

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

**Expected Output:**
```
50 passed in ~10 seconds
```

## Frontend Features

### Professional Templates (HTML/CSS)
- base.html- Main template with navigation
- home.html- Hero section, features, statistics, testimonials
- about.html - Company info, team, services, mission & values
- login.html - Professional login form with alerts
- register.html- Registration with 4 role selector, password strength indicator
- doctor_dashboard.html- Patient stats, recent patients, patient table
- patient_dashboard.html - Health metrics, appointments, medications
- staff_dashboard.html- Tasks, responsibilities, activity feed
- admin_dashboard.html - System metrics, user management, statistics
- patients.html - Patient CRUD, CSV data management, pagination
- 404.html & 500.html- Custom error pages

### Design Features
- Responsive grid layouts
-  Professional color gradients
-  Role-specific color themes




 Run the Application
```bash
python app.py
```

Output:
✓ MongoDB connection OK
Server running at http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off

**Access the app:** Open browser to `http://localhost:5000`

---

##  Test Credentials

**For Testing:**

```
Doctor Account:
  Username: doctor
  Password: password123

Patient Account:
  Username: patient
  Password: password123

Staff Account:
  Username: staff
  Password: password123

Admin Account:
  Username: admin
  Password: password123
```

---

## 📁 Project Structure

```
├── app.py                          # Main Flask application
├── mongo.py                        # MongoDB helper functions
├── test_app.py                     # Application tests (26 tests)
├── test_mongo.py                   # MongoDB tests (24 tests)
├── stroke_data.csv                 # Sample medical dataset
├── users.db                        # SQLite database (auto-created)
├── .gitignore                      # Git exclusions (sensitive files)
├── README.md                       # This file
├── templates/
│   ├── base.html                   # Base template
│   ├── home.html                   # Home page
│   ├── about.html                  # About page
│   ├── login.html                  # Login page
│   ├── register.html               # Registration (4 roles)
│   ├── doctor_dashboard.html       # Doctor dashboard
│   ├── patient_dashboard.html      # Patient dashboard
│   ├── staff_dashboard.html        # Staff dashboard
│   ├── admin_dashboard.html        # Admin dashboard
│   ├── patients.html               # Patient management
│   ├── 404.html                    # Not found page
│   └── 500.html                    # Error page
└── __pycache__/                    # Python cache (in .gitignore)
```

---

## 🚀 Key Accomplishments

### Phase 1: Core System
- ✅ Flask web framework setup
- ✅ SQLite database with users table
- ✅ User registration and authentication
- ✅ Basic login/logout functionality

### Phase 2: Enhanced Features
- ✅ 4 user roles (Doctor, Patient, Staff, Admin)
- ✅ Role-based access control (RBAC)
- ✅ Patient CRUD operations
- ✅ CSV data import and management

### Phase 3: Professional UI/UX
- ✅ Professional HTML templates for all roles
- ✅ Responsive CSS with gradients and animations
- ✅ Password strength indicator
- ✅ Real-time form validation
- ✅ Custom error pages

### Phase 4: MongoDB Integration
- ✅ MongoDB connection and collections
- ✅ Dual database synchronization
- ✅ Helper functions for CRUD operations
- ✅ Comprehensive error handling and logging

### Phase 5: Testing & Quality Assurance
- ✅ 26 application tests (all passing)
- ✅ 24 MongoDB integration tests (all passing)
- ✅ Unit and integration test coverage
- ✅ Test for all user roles

### Phase 6: DevOps & Security
- ✅ Comprehensive .gitignore
- ✅ Git version control
- ✅ Security best practices
- ✅ Production-ready code

---

##  Statistics

| Metric | Count |
|--------|-------|
| **Total Tests** | 50 |
| **Tests Passing** | 50 ✅ |
| **HTML Templates** | 11 |
| **User Roles** | 4 |
| **Database Integrations** | 2 (SQLite + MongoDB) |
| **Lines of Code** | 2000+ |
| **Security Features** | 8+ |

---

##  Configuration

### Flask Settings
```python
app.secret_key = "change_this_to_any_random_secret_string"
app.config["HOSPITAL_NAME"] = "CityCare Hospital"
```

### Database Configuration
- **SQLite:** `users.db` (auto-created)
- **MongoDB:** Configured via `.env` (MONGO_URI)

### Logging
- **Application:** `app.log`
- **MongoDB:** `mongo.log`
- **All logs excluded from Git** (in .gitignore)





