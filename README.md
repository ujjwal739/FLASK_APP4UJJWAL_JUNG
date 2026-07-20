# SEC//BOARD: Security Tip & Awareness Board

A Flask web app I built for my ST5041CMD (The Internet and Web Technologies) module. It's basically a platform where users can read security tips, take quizzes to test what they know, comment on tips, check out security resources, and see announcements from admins.

## What it does

- Browse security tips organized by category and severity (low to critical)
- Take quizzes with multiple-choice questions and explanations
- Comment on tips and discuss with others
- Access a page of external security resources and downloads
- See announcements posted by admins
- Login system with separate user and admin roles
- Logs important actions like login attempts and admin activity

I also tried to follow some basic security practices while building it — things like setting security headers (X-Content-Type-Options, X-Frame-Options, etc.), password rules on registration, and input validation.

## Tech used

- **Backend:** Python, Flask, SQLite3
- **Frontend:** Plain HTML5 and CSS3, no frameworks
- **Testing:** Python's `unittest`, around 30 tests covering auth, routes, and permissions

## How to run it

Make sure you have Python 3.8+ installed.

```bash
git clone https://github.com/ujjwal739/FLASK_APP4UJJWAL_JUNG.git
cd FLASK_APP4UJJWAL_JUNG
pip install -r requirements.txt
```

Copy the example env file and fill in your own values:

```bash
cp .env.example .env
```

Then edit `.env`:
