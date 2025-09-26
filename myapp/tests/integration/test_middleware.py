# tests/integration/test_middleware.py
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from myapp.middleware import CustomHeadersMiddleware, DatabaseCheckMiddleware
import mock

class CustomHeadersMiddlewareTest(TestCase):
    def test_custom_headers_middleware(self):
        # Test CustomHeadersMiddleware
        middleware = CustomHeadersMiddleware(lambda req: HttpResponse())
        request = RequestFactory().get('/')
        response = middleware(request)
        self.assertIn('Cache-Control', response)
        self.assertEqual(response['Cache-Control'], 'no-cache, no-store, must-revalidate')
        self.assertIn('Pragma', response)
        self.assertEqual(response['Pragma'], 'no-cache')
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

class DatabaseCheckMiddlewareTest(TestCase):
    @mock.patch('myapp.middleware.connection.cursor')
    def test_database_check_middleware(self, mock_cursor):
        # Test DatabaseCheckMiddleware
        mock_execute = mock_cursor.return_value.execute
        mock_execute.return_value = None
        middleware = DatabaseCheckMiddleware(lambda req: HttpResponse())
        request = RequestFactory().get('/')
        response = middleware(request)
        self.assertEqual(response.status_code, 200)

    @mock.patch('myapp.middleware.connection.cursor')
    def test_database_unavailable(self, mock_cursor):
        # Test DatabaseCheckMiddleware when database is unavailable
        mock_cursor.side_effect = Exception('Database connection error')
        middleware = DatabaseCheckMiddleware(lambda req: HttpResponse())
        request = RequestFactory().get('/')
        request.request_id = 'test_request_id'
        response = middleware(request)
        self.assertEqual(response.status_code, 503)
