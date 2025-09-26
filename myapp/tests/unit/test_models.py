# tests/unit/test_models.py
from django.test import TestCase
from myapp.models import User

class UserModelTest(TestCase):
    def test_create_user(self):
        # Test creating a user
        user = User.objects.create_user(username='test@example.com', first_name='Test', last_name='User', password='password123')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('password123'))
