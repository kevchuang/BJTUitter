import os
import unittest

from routes import *

class BasicTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        pass

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_login_false(self):
        response = self.app.post('/login', data=dict(username='Ceci est un test', password='Coucou'), follow_redirects=True)
        self.assertEqual(response.status_code, 403)

    def test_login_true(self):
        response = self.app.post('/login', data=dict(username='test', password='test'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()