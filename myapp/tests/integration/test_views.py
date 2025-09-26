import json
from base64 import b64encode
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from myapp.models import User


class HealthzEndpointTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_healthz_endpoint_get(self):
        response = self.client.get(reverse('healthz'))
        self.assertEqual(response.status_code, 200)

    def test_healthz_endpoint_post(self):
        response = self.client.post(reverse('healthz'))
        self.assertEqual(response.status_code, 405)


class PingEndpointTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_ping_endpoint_get(self):
        response = self.client.get(reverse('ping'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'pong'})

    def test_ping_endpoint_post(self):
        response = self.client.post(reverse('ping'))
        self.assertEqual(response.status_code, 405)


class CreateUserEndpointTest(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('utils.msg_publisher.PubSubMessagePublisher.send_message')
    def test_create_user_endpoint_success(self, mock_send_message):
        user_data = {
            'username': 'test@example.com',
            'password': 'password123',
            'first_name': 'first',
            'last_name': 'last'
        }

        response = self.client.post(reverse('create_user'), data=json.dumps(user_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username=user_data['username'])
        self.assertIsNotNone(user)
        self.assertUserAttributes(user, user_data)

    def test_create_user_endpoint_invalid_data(self):
        invalid_user_data = {'password': 'password123', 'first_name': 'first', 'last_name': 'last'}
        response = self.client.post(reverse('create_user'), data=invalid_user_data)
        self.assertEqual(response.status_code, 400)

    def assertUserAttributes(self, user, user_data):
        self.assertEqual(user.first_name, user_data['first_name'])
        self.assertEqual(user.last_name, user_data['last_name'])


class UserInfoEndpointTest(TestCase):
    @patch('utils.msg_publisher.PubSubMessagePublisher.send_message')
    def setUp(self, mock_send_message):
        self.client = Client()
        user_data = {
            'username': 'test@example.com',
            'password': 'password123',
            'first_name': 'first',
            'last_name': 'last'
        }
        response = self.client.post(reverse('create_user'), data=json.dumps(user_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.user = User.objects.get(username=user_data['username'])
        self.user.is_verified = True
        self.user.save()

    def test_user_info_endpoint_get_without_credentials(self):
        response = self.client.get(reverse('user_info'))
        self.assertEqual(response.status_code, 401)

    def test_user_info_endpoint_get_with_valid_credentials(self):
        response = self.get_user_info_response()
        self.assertEqual(response.status_code, 200)

    def test_user_info_endpoint_put_with_valid_credentials_and_valid_data(self):
        response = self.update_user_info_response({'first_name': 'John', 'last_name': 'Doe'})
        self.assertEqual(response.status_code, 204)

        response = self.get_user_info_response()
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['first_name'], 'John')
        self.assertEqual(response_data['last_name'], 'Doe')

    def test_user_info_endpoint_put_with_valid_credentials_and_invalid_data(self):
        response = self.update_user_info_response({'invalid_field': 'value'})
        self.assertEqual(response.status_code, 400)

    def test_user_info_endpoint_put_without_credentials(self):
        response = self.client.put(reverse('user_info'), data={'first_name': 'John', 'last_name': 'Doe'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_user_info_endpoint_invalid_method(self):
        response = self.client.post(reverse('user_info'))
        self.assertEqual(response.status_code, 405)

    def get_user_info_response(self):
        username = 'test@example.com'
        password = 'password123'
        auth_header = 'Basic ' + b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')
        return self.client.get(reverse('user_info'), HTTP_AUTHORIZATION=auth_header)

    def update_user_info_response(self, data):
        username = 'test@example.com'
        password = 'password123'
        auth_header = 'Basic ' + b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')
        return self.client.put(reverse('user_info'), data=json.dumps(data), content_type='application/json',
                               HTTP_AUTHORIZATION=auth_header)
