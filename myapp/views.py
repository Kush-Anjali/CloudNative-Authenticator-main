import base64
import hashlib
import os
import secrets

from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse, JsonResponse

from .models import User, UserVerification
from .serializers import UserSerializer, CreateUserSerializer, UpdateUserSerializer
import json


def healthz(request):
    try:
        logger.debug(
            method=request.method,
            request_id=request.request_id,
            endpoint="healthz",
            event="health check requested",
            message="service health check."
        )
        if request.method == 'GET':
            if request.body:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="healthz",
                    event="bad_request_body",
                    message="Bad request, body received for healthz endpoint."
                )
                return HttpResponseBadRequest(status=400)
            elif request.GET:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="healthz",
                    event="bad_query_parameter",
                    message="Bad query parameter received for healthz endpoint."
                )
                return HttpResponseBadRequest(status=400)
            else:
                logger.debug(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="healthz",
                    event="service_health_check",
                    message="Service is healthy."
                )
                return HttpResponse(status=200)
        else:
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="healthz",
                event="method_not_allowed",
                message="Method not allowed for healthz endpoint."
            )
            return HttpResponseNotAllowed(['GET'])
    except Exception as e:
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="healthz",
            event="error_processing_healthz",
            message="An error occurred while processing healthz request.",
            error=str(e)
        )
        return HttpResponseBadRequest(status=400)


def ping(request):
    try:
        logger.debug(
            method=request.method,
            request_id=request.request_id,
            endpoint="ping",
            event="ping_accessed",
            message="Ping endpoint accessed."
        )
        if request.method == 'GET':
            if request.body:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="ping",
                    event="bad_request_body",
                    message="Bad request body received for ping endpoint."
                )
                return HttpResponseBadRequest(status=400)
            elif request.GET:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="ping",
                    event="bad_query_parameter",
                    message="Bad query parameter received for ping endpoint."
                )
                return HttpResponseBadRequest(status=400)
            else:
                logger.info(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="ping",
                    event="Ping successful",
                    message="service is healthy and ping successful."
                )
                return JsonResponse({'message': 'pong'}, status=200)
        else:
            logger.error(
                event="method_not_allowed",
                message=f"Method '{request.method}' not allowed for endpoint '{request.path}'.",
                method=request.method,
                request_id=request.request_id,
                path=request.path,
                user_agent=request.headers.get('User-Agent')
            )
            return HttpResponseNotAllowed(['GET'])
    except Exception as e:
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="ping",
            event="error_processing_ping",
            message="An error occurred while processing ping request.",
            error=str(e)
        )
        return HttpResponseBadRequest(status=400)

# def generate_unique_verification_code(username):
#     """
#     Generates a unique verification code for the given username.
#
#     This function uses the secrets module to generate a cryptographically
#     secure random string as the verification code.
#
#     Args:
#         username (str): The username of the user for whom to generate the code.
#
#     Returns:
#         str: The unique verification code.
#     """
#
#     # Securely generate a random string with length 32 (can be adjusted)
#     verification_code = secrets.token_urlsafe(32)
#     # Combine username (hashed for security) and random string
#     combined_string = f"{username}-{hashlib.sha256(username.encode('utf-8')).hexdigest()}"
#     # Encode the combined string and verification code for URL safety
#     return f"{base64.urlsafe_b64encode(combined_string.encode('utf-8')).decode('utf-8')}/{verification_code}"


# def track_email(verification_link, username):
#     """
#     Tracks information about the sent verification email.
#
#     This function attempts to create a new `UserVerification` model entry
#     with the provided username and verification link. It handles potential
#     errors like user not found.
#
#     Args:
#         username (str): The username of the user.
#         verification_link (str): The verification link sent to the user.
#     """
#
#     try:
#         user = User.objects.get(username=username)
#         verification_obj = UserVerification.objects.create(
#             user=user, verification_code=verification_link.split('/')[1]  # Extract code from link
#         )
#         print(f'Email sent to {username} tracked with verification object: {verification_obj}')
#     except Exception as e:
#         print(f'An error occurred while tracking email: {e}')


def create_user(request):
    try:
        logger.debug(
            method=request.method,
            request_id=request.request_id,
            endpoint="create_user",
            event="create_user_attempt",
            message="Create user endpoint accessed."
        )
        if request.method == 'POST':
            try:
                request_data = json.loads(request.body)
            except json.JSONDecodeError as e:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="create_user",
                    event="json_decode_error",
                    message="Error decoding JSON in create_user.",
                    error=str(e)
                )
                return HttpResponseBadRequest(status=400)

            # Check if the user already exists
            user = User.objects.filter(username=request_data.get('username')).first()
            if user:
                if user.is_verified:
                    logger.error(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="create_user",
                        event="user_already_exists",
                        message="User with this username already exists.",
                        username=request_data.get('username')
                    )
                    return JsonResponse({'error': 'User with this username already exists.'}, status=400)
                else:
                    hostname = os.getenv('DOMAIN_NAME')
                    verification_api = "v1/verify"

                    pubsub_topic = "verify_email"
                    pubsub_msg = {
                        "first_name": user.first_name,
                        "username": user.username,
                        "hostname": hostname,
                        "verification_api": verification_api
                    }

                    # verification_code = generate_unique_verification_code(user.username)
                    # verification_link = f"http://{hostname}:8000/{verification_api}?code={verification_code}"
                    #
                    # print(f"verification_link: {verification_link}")
                    # track_email(verification_code, user.username)

                    msg_publisher.send_message(pubsub_topic, pubsub_msg)
                    return JsonResponse({
                        'error': 'User with this username already exists. Please verify your email to activate your '
                                 'account.'},
                        status=400)

            serializer = CreateUserSerializer(data=request_data)
            if serializer.is_valid():
                user = serializer.save()
                logger.info(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="create_user",
                    event="user_created",
                    message="User created successfully.",
                    username=user.username,
                )
                hostname = os.getenv('DOMAIN_NAME')
                verification_api = "v1/verify"

                pubsub_topic = "verify_email"
                pubsub_msg = {
                    "first_name": user.first_name,
                    "username": user.username,
                    "hostname": hostname,
                    "verification_api": verification_api
                }
                msg_publisher.send_message(pubsub_topic, pubsub_msg)

                return JsonResponse(
                    {'message': 'User created successfully. Please verify your email to activate your account.',
                     'data': serializer.data}, status=201)

            else:
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="create_user",
                    event="serializer_errors",
                    message="Serializer errors in create_user.",
                    errors=serializer.errors,
                    request_data=request_data
                )
                return HttpResponseBadRequest(status=400)
        else:
            logger.error(
                event="method_not_allowed",
                message=f"Method '{request.method}' not allowed for endpoint '{request.path}'.",
                method=request.method,
                request_id=request.request_id,
                path=request.path,
                user_agent=request.headers.get('User-Agent')
            )
            return HttpResponseNotAllowed(['POST'])
    except Exception as e:
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="create_user",
            event="create_user_error",
            message="An error occurred while processing create user request.",
            error=str(e)
        )
        try:
            if "Table 'webApp.myapp_user' doesn't exist" in str(e):
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="create_user",
                    event="database_error",
                    message="Database error occurred while processing create user request.",
                    error=str(e)
                )
                return JsonResponse({'error': 'An internal server error occurred. Please try again later.'},
                                    status=500)
        except Exception as err:
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="create_user",
                event="error_processing_database_error",
                message="Error processing database error in create_user.",
                error=str(err)
            )
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="create_user",
            event="unknown_error",
            message="An error occurred while processing create user request.",
            error=str(e)
        )
        return HttpResponseBadRequest(status=400)


def get_user_from_credentials(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Basic '):
        return None, "Invalid Request, Need Authorization header", 401

    encoded_credentials = auth_header[len('Basic '):]
    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
    username, password = decoded_credentials.split(':', 1)

    try:
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            if not user.is_verified:
                msg = f"Email verification required to access this API. for user: {username}"
                logger.warn(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="user_info",
                    event="Fetching user detail failed",
                    message=msg
                )
                return None, msg, 403
            return user, f"Authorisation successful for user: {username}", 1 # 1 denotes everything is okay
        else:
            msg = f"Authorisation failure for user: {username}"
            logger.warn(
                method=request.method,
                request_id=request.request_id,
                endpoint="user_info",
                event="Fetching user detail failed",
                message=msg
            )
            return None, msg, 401

    except User.DoesNotExist:
        msg = f"User: {username} not found."
        logger.warn(
            method=request.method,
            request_id=request.request_id,
            endpoint="user_info",
            event="Fetching user detail failed",
            message=msg
        )
        return None, msg, 401


def user_info(request):
    try:
        logger.debug(
            method=request.method,
            request_id=request.request_id,
            endpoint="user_info",
            event="get_user_info_accessed",
            message="Get user info endpoint accessed."
        )
        if request.method == 'GET' or request.method == 'PUT':
            user, msg, resp_status = get_user_from_credentials(request)
            if not user:
                return JsonResponse({'error': msg}, status=resp_status)

            if request.method == 'GET':
                if request.body:
                    logger.error(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        event="bad_request_body",
                        message="Bad request body received for get user info endpoint."
                    )
                    return HttpResponseBadRequest(status=400)
                elif request.GET:
                    logger.error(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        event="bad_query_parameter",
                        message="Bad query parameter received for get user info endpoint."
                    )
                    return HttpResponseBadRequest(status=400)
                else:
                    serializer = UserSerializer(user)
                    logger.info(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        user_name=user.username,
                        event="success event ",
                        message="user data fetched successfully."
                    )
                    return JsonResponse(serializer.data, status=200)
            elif request.method == 'PUT':
                if request.GET:
                    logger.error(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        event="bad_query_parameter",
                        message="Bad query parameter received for update user info endpoint."
                    )
                    return HttpResponseBadRequest(status=400)
                request_data = json.loads(request.body)

                # Check if any unexpected keys are present in request_data
                unexpected_keys = set(request_data.keys()) - {'first_name', 'last_name', 'password'}
                if unexpected_keys:
                    logger.warn(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        event="unexpected_keys",
                        message=f"Failed to update to user info for user: {user.username}",
                    )
                    return HttpResponseBadRequest(status=400)
                serializer = UpdateUserSerializer(user, data=request_data)
                if serializer.is_valid():
                    serializer.save()
                    logger.info(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        user_name=user.username,
                        event="success event ",
                        message="user data updated successfully."
                    )
                    return HttpResponse(status=204)
                else:
                    logger.error(
                        method=request.method,
                        request_id=request.request_id,
                        endpoint="user_info",
                        event="serializer_errors",
                        message=f"Failed to update to user info for user: {user.username}",
                        errors=serializer.errors
                    )
                    return HttpResponseBadRequest(status=400)

        else:
            logger.error(
                event="method_not_allowed",
                message=f"Method '{request.method}' not allowed for '{request.path}'.",
                method=request.method,
                request_id=request.request_id,
                path=request.path,
                user_agent=request.headers.get('User-Agent')
            )
            return HttpResponseNotAllowed(['GET', 'PUT'])
    except Exception as e:
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="user_info",
            event="error_processing_user_info",
            message="An error occurred while processing user info request.",
            error=str(e)
        )
        try:
            if "Table 'webApp.myapp_user' doesn't exist" in str(e):
                logger.error(
                    method=request.method,
                    request_id=request.request_id,
                    endpoint="user_info",
                    event="database_error",
                    message="Database error occurred while processing user info request.",
                    error=str(e)
                )
                return JsonResponse({'error': 'An internal server error occurred. Please try again later.'},
                                    status=500)
        except Exception as err:
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="user_info",
                event="error_processing_database_error",
                message="Error processing database error in user_info.",
                error=str(err)
            )
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="user_info",
            event="unknown_error",
            message="An error occurred while processing user info request.",
            error=str(e)
        )
        return HttpResponseBadRequest(status=400)


def verify_user(request):
    try:
        logger.debug(
            method=request.method,
            request_id=request.request_id,
            endpoint="verify_user",
            event="verify_user_accessed",
            message="Verify user endpoint accessed."
        )
        verification_code = request.GET.get('code')

        if not verification_code:
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="verify_user",
                event="verification_code_missing",
                message="Verification code is missing."
            )
            return JsonResponse({'error': 'Verification code is missing'}, status=400)

        try:
            verification_code = verification_code.split('/')[1]
            verification_obj = UserVerification.objects.get(verification_code=verification_code)
        except UserVerification.DoesNotExist:
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="verify_user",
                event="invalid_verification_code",
                message="Invalid verification code."
            )
            return JsonResponse({'error': 'Invalid verification code'}, status=404)
        except Exception as e:
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="verify_user",
                event="invalid_verification_code",
                message="Invalid verification code.",
                error=str(e)
            )
            return JsonResponse({'error': 'Invalid verification code'}, status=404)

        if verification_obj.expires_at < timezone.now():
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="verify_user",
                event="expired_verification_link",
                message="Verification link has expired."
            )
            return JsonResponse({'error': 'Verification link has expired'}, status=400)

        if verification_obj.is_used:
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="verify_user",
                event="check validity of verification link",
                message="Verification link has been used."
            )
            return JsonResponse({'error': 'Verification link has expired'}, status=400)
        verification_obj.is_used = True
        verification_obj.save()

        # verification_obj.delete()  # Optional: Delete verification entry after successful use

        user_id = verification_obj.user_id
        user = User.objects.filter(id=user_id).first()
        if user:
            user.is_verified = True
            user.save()
            logger.info(
                method=request.method,
                request_id=request.request_id,
                endpoint="verify_user",
                user_name=user.username,
                event="user_verified",
                message="User verified successfully."
            )
        else:
            logger.error(
                method=request.method,
                request_id=request.request_id,
                endpoint="verify_user",
                user_name=user.username,
                event="user not found",
                message="User verification failed."
            )

        return JsonResponse({'success': 'User verified successfully'})
    except Exception as e:
        logger.error(
            method=request.method,
            request_id=request.request_id,
            endpoint="verify_user",
            event="error_processing_verification",
            message="An error occurred while processing user verification.",
            error=str(e)
        )
        return JsonResponse({'error': 'An error occurred while processing verification. Please try again later.'},
                            status=500)
