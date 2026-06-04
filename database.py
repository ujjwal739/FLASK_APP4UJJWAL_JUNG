import sqlite3
import os
import hashlib
import secrets

DB_PATH = os.path.join(os.path.dirname(__file__), 'security_board.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        icon TEXT DEFAULT '🔒',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS tips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category_id INTEGER,
        severity TEXT CHECK(severity IN ('low','medium','high','critical')) DEFAULT 'medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS quiz_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT CHECK(correct_option IN ('a','b','c','d')) NOT NULL,
        explanation TEXT,
        category_id INTEGER,
        difficulty TEXT CHECK(difficulty IN ('easy','medium','hard')) DEFAULT 'medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_name TEXT NOT NULL,
        content TEXT NOT NULL,
        tip_id INTEGER,
        approved INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tip_id) REFERENCES tips(id) ON DELETE CASCADE
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT CHECK(role IN ('user','admin')) DEFAULT 'user',
        is_active INTEGER DEFAULT 1,
        last_login TIMESTAMP,
        failed_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_token TEXT NOT NULL UNIQUE,
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        action TEXT NOT NULL,
        details TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        severity TEXT CHECK(severity IN ('info','warning','high','critical')) DEFAULT 'info',
        is_active INTEGER DEFAULT 1,
        expires_at TEXT,
        created_by TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        description TEXT,
        resource_type TEXT CHECK(resource_type IN ('article','video','tool','guide','course')) DEFAULT 'article',
        category_id INTEGER,
        approved INTEGER DEFAULT 1,
        submitted_by TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    )''')

    # Indexes for performance
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tips_category ON tips(category_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tips_severity ON tips(severity)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_comments_tip ON comments(tip_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(resource_type)")

    # Seed categories
    categories = [
        ('Password Security', 'Best practices for strong passwords', '🔑'),
        ('Phishing Awareness', 'Identifying and avoiding phishing attacks', '🎣'),
        ('Network Security', 'Securing your network and connections', '🌐'),
        ('Social Engineering', 'Protecting against manipulation tactics', '🧠'),
        ('Data Privacy', 'Keeping personal data safe', '🛡️'),
    ]
    cur.executemany('INSERT OR IGNORE INTO categories (name, description, icon) VALUES (?,?,?)', categories)

    cur.execute("SELECT COUNT(*) FROM tips")
    if cur.fetchone()[0] == 0:
        tips = [
            ('Use Strong Passwords', 'Always use a combination of uppercase, lowercase, numbers, and symbols. Minimum 12 characters. Avoid dictionary words and personal information like birthdays.', 1, 'high'),
            ('Enable Two-Factor Authentication', 'Add an extra layer of security by enabling 2FA on all important accounts. Use authenticator apps rather than SMS when possible.', 1, 'critical'),
            ('Recognize Phishing Emails', 'Check sender email carefully. Hover over links before clicking. Never share credentials via email. Look for urgency tactics and spelling errors.', 2, 'high'),
            ('Secure Your Wi-Fi', 'Use WPA3 encryption, change default router passwords, and hide your SSID. Use a VPN on public networks.', 3, 'medium'),
            ('Be Careful What You Share Online', 'Limit personal information shared on social media to reduce social engineering risks. Oversharing can expose you to targeted attacks.', 4, 'medium'),
            ('Keep Software Updated', 'Enable automatic updates for your OS and applications. Most attacks exploit known vulnerabilities that patches have already fixed.', 3, 'high'),
            ('Use a Password Manager', 'Password managers generate and store complex unique passwords for every site. This eliminates password reuse — one of the biggest security risks.', 1, 'medium'),
            ('Regular Data Backups', 'Follow the 3-2-1 rule: 3 copies, 2 different media types, 1 offsite. This protects against ransomware and hardware failure.', 5, 'high'),
        ]
        cur.executemany('INSERT INTO tips (title, content, category_id, severity) VALUES (?,?,?,?)', tips)

    cur.execute("SELECT COUNT(*) FROM quiz_questions")
    if cur.fetchone()[0] == 0:
        questions = [
            ('What is the minimum recommended password length?', '6 characters', '8 characters', '12 characters', '4 characters', 'c', 'Security experts recommend at least 12 characters for strong passwords.', 1, 'easy'),
            ('Which of these is a sign of a phishing email?', 'Sender is your friend', 'Urgent request for personal info', 'Email has company logo', 'Email is short', 'b', 'Phishing emails often create urgency to trick you into acting without thinking.', 2, 'easy'),
            ('What does 2FA stand for?', 'Two-Factor Authentication', 'Two-File Access', 'Transfer Factor Analysis', 'Two-Form Authorization', 'a', '2FA adds an extra verification step beyond just a password.', 1, 'easy'),
            ('What is a VPN used for?', 'Speeding up internet', 'Encrypting internet traffic', 'Blocking advertisements', 'Storing passwords', 'b', 'A VPN encrypts your internet connection, protecting data on public networks.', 3, 'medium'),
            ('Which Wi-Fi encryption is most secure?', 'WEP', 'WPA', 'WPA2', 'WPA3', 'd', 'WPA3 is the latest and most secure Wi-Fi encryption standard.', 3, 'medium'),
            ('What is social engineering?', 'Building social networks', 'Manipulating people to reveal info', 'Engineering social media apps', 'A type of firewall', 'b', 'Social engineering exploits human psychology rather than technical vulnerabilities.', 4, 'medium'),
            ('What is the 3-2-1 backup rule?', '3 backups on 1 device', '3 copies, 2 media types, 1 offsite', '3 passwords, 2 emails, 1 phone', '3 files, 2 folders, 1 drive', 'b', 'The 3-2-1 rule ensures your data survives any single point of failure.', 5, 'hard'),
        ]
        cur.executemany('INSERT INTO quiz_questions (question,option_a,option_b,option_c,option_d,correct_option,explanation,category_id,difficulty) VALUES (?,?,?,?,?,?,?,?,?)', questions)

    cur.execute("SELECT COUNT(*) FROM announcements")
    if cur.fetchone()[0] == 0:
        anns = [
            ('⚠️ New Phishing Campaign Detected', 'A new phishing campaign is targeting users with fake IT support emails asking for credentials. Do NOT click any suspicious links or provide passwords. Report suspicious emails immediately to your IT department.', 'critical', 1, '2026-12-31', 'admin'),
            ('🔐 Password Policy Update', 'All users must update their passwords to meet the new 12-character minimum requirement by end of month. Use a password manager for best results.', 'warning', 1, '2026-12-31', 'admin'),
            ('ℹ️ Security Awareness Training', 'Monthly security awareness training sessions are now available. Check the Resources section for links to courses and guides.', 'info', 1, '2026-12-31', 'admin'),
        ]
        cur.executemany('INSERT INTO announcements (title,content,severity,is_active,expires_at,created_by) VALUES (?,?,?,?,?,?)', anns)

    cur.execute("SELECT COUNT(*) FROM resources")
    if cur.fetchone()[0] == 0:
        resources = [
            ('Have I Been Pwned', 'https://haveibeenpwned.com', 'Check if your email or phone has been exposed in a data breach', 'tool', 5, 1, 'admin'),
            ('OWASP Top 10', 'https://owasp.org/www-project-top-ten/', 'The top 10 most critical web application security risks', 'guide', 3, 1, 'admin'),
            ('Google Password Checkup', 'https://passwords.google.com', 'Check the security of your saved passwords', 'tool', 1, 1, 'admin'),
            ('CISA Cybersecurity Best Practices', 'https://www.cisa.gov/topics/cybersecurity-best-practices', 'Official US government cybersecurity best practices and guidelines', 'article', 5, 1, 'admin'),
            ('KnowBe4 Phishing Security Test', 'https://www.knowbe4.com/phishing-security-test', 'Free phishing security awareness test for your organization', 'tool', 2, 1, 'admin'),
            ('Cybrary - Free Security Courses', 'https://www.cybrary.it', 'Free and paid cybersecurity training courses for all levels', 'course', 5, 1, 'admin'),
            ('Troy Hunt Security Blog', 'https://www.troyhunt.com', 'Expert blog covering real-world security breaches and best practices', 'article', 5, 1, 'admin'),
        ]
        cur.executemany('INSERT INTO resources (title,url,description,resource_type,category_id,approved,submitted_by) VALUES (?,?,?,?,?,?,?)', resources)

    # Default admin (password: Admin@123)
    admin_pw = hashlib.sha256('Admin@123'.encode()).hexdigest()
    cur.execute("INSERT OR IGNORE INTO users (username,email,password_hash,role) VALUES (?,?,?,?)",
                ('admin', 'admin@secboard.com', admin_pw, 'admin'))

    conn.commit()
    conn.close()

def log_action(user_id, username, action, details='', ip_address=''):
    try:
        conn = get_db()
        conn.execute('INSERT INTO audit_log (user_id, username, action, details, ip_address) VALUES (?,?,?,?,?)',
                     (user_id, username, action, details, ip_address))
        conn.commit()
        conn.close()
    except:
        pass
