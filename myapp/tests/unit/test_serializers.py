# tests/unit/test_serializers.py
from django.test import TestCase

from myapp.models import User
from myapp.serializers import CreateUserSerializer, UpdateUserSerializer

class CreateUserSerializerTest(TestCase):
    def test_valid_data(self):
        # Test with valid data
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'john@example.com',
            'password': 'test1234'
        }
        serializer = CreateUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.username, 'john@example.com')

    def test_invalid_data(self):
        # Test with invalid data
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'test1234'
        }
        serializer = CreateUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())

class UpdateUserSerializerTest(TestCase):
    def test_valid_data(self):
        # Test with valid data
        user = User.objects.create(username='test@example.com', first_name='Test', last_name='User')
        data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'password': 'newpassword'
        }
        serializer = UpdateUserSerializer(instance=user, data=data)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'User')

    def test_invalid_data(self):
        # Test with invalid data
        user = User.objects.create(username='test@example.com', first_name='Test', last_name='User')
        data = {
            'first_name': '',  # Invalid data: Empty first name
            'last_name': 'User',
            'password': 'newpassword'
        }
        serializer = UpdateUserSerializer(instance=user, data=data)
        self.assertFalse(serializer.is_valid())
