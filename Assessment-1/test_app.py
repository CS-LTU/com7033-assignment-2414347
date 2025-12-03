import unittest
from app import app, db, User
from flask import session

class BasicTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        
        # Create test user
        with app.app_context():
            db.drop_all()
            db.create_all()
            test_user = User(username="testuser", password_hash="hashedpassword")
            db.session.add(test_user)
            db.session.commit()

    def test_register_page_loads(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
