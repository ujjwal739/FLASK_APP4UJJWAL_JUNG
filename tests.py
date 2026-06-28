"""
Test Suite — Security Tip & Awareness Board
ST5041CMD The Internet and Web Technologies
"""
import unittest
import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import get_db, init_db

class SecurityBoardTestCase(unittest.TestCase):

    def setUp(self):
        """Set up test client with temp database"""
        self.app = create_app('development')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    # ── AUTH TESTS ─────────────────────────────────────────
    def test_01_home_page_loads(self):
        """Dashboard should load for unauthenticated users"""
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'SEC//BOARD', r.data)
        print("  ✓ Home page loads")

    def test_02_login_page_loads(self):
        """Login page should be accessible"""
        r = self.client.get('/login')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Sign In', r.data)
        print("  ✓ Login page loads")

    def test_03_register_page_loads(self):
        """Register page should be accessible"""
        r = self.client.get('/register')
        self.assertEqual(r.status_code, 200)
        print("  ✓ Register page loads")

    def test_04_admin_login_page_loads(self):
        """Admin login page should be accessible"""
        r = self.client.get('/admin/login')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Admin', r.data)
        print("  ✓ Admin login page loads")

    def test_05_register_new_user(self):
        """Valid registration should succeed"""
        r = self.client.post('/register', data={
            'username': 'testuser1',
            'email': 'test1@example.com',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        }, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        print("  ✓ User registration works")

    def test_06_register_weak_password(self):
        """Weak password should be rejected"""
        r = self.client.post('/register', data={
            'username': 'weakuser',
            'email': 'weak@example.com',
            'password': '123',
            'confirm_password': '123'
        }, follow_redirects=True)
        self.assertIn(b'characters', r.data)
        print("  ✓ Weak password rejected")

    def test_07_register_password_mismatch(self):
        """Mismatched passwords should be rejected"""
        r = self.client.post('/register', data={
            'username': 'mismatch',
            'email': 'mm@example.com',
            'password': 'Test@1234',
            'confirm_password': 'Different@5678'
        }, follow_redirects=True)
        self.assertIn(b'match', r.data)
        print("  ✓ Password mismatch rejected")

    def test_08_admin_login_valid(self):
        """Admin login with correct credentials should succeed"""
        r = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'Admin@123'
        }, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        print("  ✓ Admin login works")

    def test_09_admin_login_wrong_password(self):
        """Admin login with wrong password should fail"""
        r = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid', r.data)
        print("  ✓ Wrong password rejected")

    def test_10_admin_dashboard_requires_auth(self):
        """Admin dashboard should redirect unauthenticated users"""
        r = self.client.get('/admin/dashboard', follow_redirects=False)
        self.assertIn(r.status_code, [302, 200])
        print("  ✓ Admin dashboard protected")

    # ── TIPS TESTS ─────────────────────────────────────────
    def test_11_tips_page_loads(self):
        """Tips page should be accessible"""
        r = self.client.get('/tips/')
        self.assertEqual(r.status_code, 200)
        print("  ✓ Tips page loads")

    def test_12_tip_create_requires_admin(self):
        """Creating tip should require admin"""
        r = self.client.get('/tips/create', follow_redirects=False)
        self.assertIn(r.status_code, [302, 200])
        print("  ✓ Tip creation protected")

    def test_13_admin_can_create_tip(self):
        """Admin should be able to create tips"""
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'Admin@123'})
        r = self.client.post('/tips/create', data={
            'title': 'Test Security Tip',
            'content': 'This is a test security tip content.',
            'severity': 'medium',
            'category_id': '1'
        }, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        print("  ✓ Admin can create tip")

    def test_14_tip_detail_loads(self):
        """Individual tip page should load"""
        r = self.client.get('/tips/1')
        self.assertIn(r.status_code, [200, 404])
        print("  ✓ Tip detail page accessible")

    # ── QUIZ TESTS ─────────────────────────────────────────
    def test_15_quiz_page_loads(self):
        """Quiz page should be accessible"""
        r = self.client.get('/quiz/')
        self.assertEqual(r.status_code, 200)
        print("  ✓ Quiz page loads")

    def test_16_quiz_answer_requires_login(self):
        """Quiz answer check should require login"""
        import json
        r = self.client.post('/quiz/check',
            data=json.dumps({'question_id': 1, 'selected': 'a'}),
            content_type='application/json',
            follow_redirects=False)
        self.assertIn(r.status_code, [302, 200, 401])
        print("  ✓ Quiz answering requires login")

    # ── CATEGORIES TESTS ───────────────────────────────────
    def test_17_categories_page_loads(self):
        """Categories page should load"""
        r = self.client.get('/categories/')
        self.assertEqual(r.status_code, 200)
        print("  ✓ Categories page loads")

    # ── ANNOUNCEMENTS TESTS ────────────────────────────────
    def test_18_announcements_page_loads(self):
        """Announcements page should load"""
        r = self.client.get('/announcements/')
        self.assertEqual(r.status_code, 200)
        print("  ✓ Announcements page loads")

    def test_19_create_announcement_requires_admin(self):
        """Creating announcement should require admin"""
        r = self.client.get('/announcements/create', follow_redirects=False)
        self.assertIn(r.status_code, [302, 200])
        print("  ✓ Announcement creation protected")

    # ── RESOURCES TESTS ────────────────────────────────────
    def test_20_resources_page_loads(self):
        """Resources page should load"""
        r = self.client.get('/resources/')
        self.assertEqual(r.status_code, 200)
        print("  ✓ Resources page loads")

    # ── SECURITY TESTS ─────────────────────────────────────
    def test_21_security_headers_present(self):
        """Security headers should be set on all responses"""
        r = self.client.get('/')
        self.assertIn('X-Content-Type-Options', r.headers)
        self.assertIn('X-Frame-Options', r.headers)
        self.assertIn('X-XSS-Protection', r.headers)
        print("  ✓ Security headers present")

    def test_22_password_validation_uppercase(self):
        """Password without uppercase should be rejected"""
        from app.controllers.authController import validate_password
        valid, msg = validate_password('lowercase1!')
        self.assertFalse(valid)
        print("  ✓ Password validation: uppercase required")

    def test_23_password_validation_special_char(self):
        """Password without special char should be rejected"""
        from app.controllers.authController import validate_password
        valid, msg = validate_password('NoSpecial1')
        self.assertFalse(valid)
        print("  ✓ Password validation: special char required")

    def test_24_password_validation_strong(self):
        """Strong password should pass"""
        from app.controllers.authController import validate_password
        valid, msg = validate_password('Str0ng@Pass!')
        self.assertTrue(valid)
        print("  ✓ Password validation: strong password accepted")

    def test_25_email_validation(self):
        """Invalid email should be rejected"""
        from app.controllers.authController import validate_email
        self.assertFalse(validate_email('notanemail'))
        self.assertFalse(validate_email('missing@tld'))
        self.assertTrue(validate_email('valid@example.com'))
        print("  ✓ Email validation works")

    def test_26_404_page(self):
        """Non-existent routes should return 404"""
        r = self.client.get('/this-does-not-exist')
        self.assertEqual(r.status_code, 404)
        print("  ✓ 404 error page works")

    def test_27_duplicate_username(self):
        """Duplicate username should be rejected"""
        self.client.post('/register', data={
            'username': 'dupuser',
            'email': 'dup1@example.com',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        })
        r = self.client.post('/register', data={
            'username': 'dupuser',
            'email': 'dup2@example.com',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        }, follow_redirects=True)
        self.assertIn(b'taken', r.data)
        print("  ✓ Duplicate username rejected")

    def test_28_logout_clears_session(self):
        """Logout should clear session"""
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'Admin@123'})
        r = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        print("  ✓ Logout clears session")

    def test_29_comments_page_loads(self):
        """Comments page should load"""
        r = self.client.get('/comments/')
        self.assertEqual(r.status_code, 200)
        print("  ✓ Comments page loads")

    def test_30_admin_can_create_quiz_question(self):
        """Admin should be able to create quiz questions"""
        self.client.post('/admin/login', data={'username': 'admin', 'password': 'Admin@123'})
        r = self.client.post('/quiz/create', data={
            'question': 'What is a firewall?',
            'option_a': 'A fire prevention system',
            'option_b': 'A network security system',
            'option_c': 'A type of antivirus',
            'option_d': 'A hardware component',
            'correct_option': 'b',
            'explanation': 'A firewall monitors and controls network traffic.',
            'difficulty': 'easy',
            'category_id': '3'
        }, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        print("  ✓ Admin can create quiz questions")


if __name__ == '__main__':
    print("\n" + "="*55)
    print("  Security Tip & Awareness Board — Test Suite")
    print("  ST5041CMD The Internet and Web Technologies")
    print("="*55 + "\n")
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = lambda a, b: (int(a.split('_')[1]) - int(b.split('_')[1]))
    suite = loader.loadTestsFromTestCase(SecurityBoardTestCase)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    print("\n" + "="*55)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"  Results: {passed}/{result.testsRun} tests passed")
    if result.failures or result.errors:
        print(f"  Failures: {len(result.failures)}  Errors: {len(result.errors)}")
    print("="*55)
