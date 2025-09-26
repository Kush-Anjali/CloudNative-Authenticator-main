# myapp/middleware.py
import uuid
from django.db import connection, DatabaseError
from django.http import HttpResponseServerError, HttpResponse


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate a unique request ID
        request.request_id = str(uuid.uuid4())

        # Pass the request to the next middleware or view
        response = self.get_response(request)

        return response


class CustomHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class DatabaseCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Check database connection before processing the request
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
        except DatabaseError as db_error:
            logger.error(
                event="database_error",
                message="Database connection error occurred.",
                exception=str(db_error),
                method=request.method,
                request_id=request.request_id,
                path=request.path,
                user_agent=request.headers.get('User-Agent')
            )
            return HttpResponse(status=503)
        except Exception as e:
            logger.error(
                event="unexpected_error",
                message="An unexpected error occurred. Try again after some time.",
                exception=str(e),
                method=request.method,
                request_id=request.request_id,
                path=request.path,
                user_agent=request.headers.get('User-Agent')
            )
            return HttpResponse(status=503)

        # Proceed with processing the request
        response = self.get_response(request)

        return response
