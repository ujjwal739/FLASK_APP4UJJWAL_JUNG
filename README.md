 SEC//BOARD: Security Tip & Awareness Board

A robust, secure Flask web application built for cybersecurity education and awareness. This platform allows users to explore security tips, test their knowledge with security quizzes, share comments, access security resources, and stay up-to-date with announcements.

This project was developed as part of **ST5041CMD The Internet and Web Technologies**.

---

 Key Features

*   **Cybersecurity Tips**: Curated tips categorized by topic, complete with severity levels (`low`, `medium`, `high`, `critical`).
*   **Interactive Quizzes**: Test security awareness with multiple-choice questions and detailed explanations.
*   **Community Comments**: Engaging discussion section for security tips.
*   **Security Resources**: Central repository for external security articles, downloads, and documentation.
*   **Announcements Board**: Critical notifications and updates from the system administrators.
*   **Robust Authentication System**: Secure user and administrator accounts, session management, and access controls.
*   **Audit Logging**: Automatic security logging of user actions (login attempts, administration tasks).
*   **Enterprise-Grade Security**: Built-in protection against common web vulnerabilities (XSS, Clickjacking, Sniffing), robust password complexity policies, and brute-force protection.

---

Technology Stack

*   **Backend**: Python, Flask, SQLite3
*   **Frontend**: Semantic HTML5, Vanilla CSS3 (with responsive layouts)
*   **Security & Database**: PBKDF2 Password Hashing, SQLite3 Write-Ahead Logging (WAL) and Foreign Keys enabled, Custom HTTP security headers.
*   **Testing**: Python standard library `unittest` suite (30 comprehensive tests covering auth, routes, and permissions).

---

 Getting Started

### 1. Installation & Setup

Ensure you have Python 3.8+ installed on your system.

Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/ujjwal739/FLASK_APP4UJJWAL_JUNG.git
cd FLASK_APP4UJJWAL_JUNG

# Install required dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the `.env.example` file to `.env` and set a secure Flask secret key:

```bash
cp .env.example .env
```

Open `.env` in your text editor and adjust the settings:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this-in-production
PORT=5001
```

### 3. Running the Application

Start the Flask development server:

```bash
python run.py
```

The application will start on `http://localhost:5001`.

---

 Testing

To run the complete automated test suite (30 test cases):

```bash
python tests.py
```

---

 Codebase Structure

```text
.
├── .env.example            # Sample configuration file
├── .gitignore              # Git ignore rules for files/directories
├── run.py                  # Application entrypoint script
├── config.py               # Config parameters for development and testing
├── database.py             # SQLite3 schema initialization and helper queries
├── requirements.txt        # Python package dependencies
├── tests.py                # Comprehensive test suite
└── app/                    # Main application package
    ├── __init__.py         # Flask app factory and blueprint registration
    ├── controllers/        # Business logic for various resources
    ├── routes/             # URL blueprints mapping to controllers
    ├── middleware/         # Security checks (e.g. auth validation)
    ├── static/             # Static assets (custom stylesheet style.css)
    └── templates/          # HTML views (dashboard, forms, quizzes, admin panel)
```

---

 Security Practices Implemented

*   **Security Headers**: Integrated HTTP headers such as `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, and `Referrer-Policy: strict-origin-when-cross-origin`.
*   **Strict Auth Checks**: Custom session tokens and route decorator validation for user and admin namespaces.
*   **Robust Password Policies**: Enforces minimum length, capital letters, and special character presence during registration.
*   **Data Validation**: Protection against invalid input formats (e.g., email verification checks).

# Updated Security Guidelines
