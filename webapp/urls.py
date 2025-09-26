from django.urls import path, re_path
from django.http import HttpResponse

from myapp import views as myapp_view

urlpatterns = [
    path('healthz', myapp_view.healthz, name='healthz'),
    path('ping', myapp_view.ping, name='ping'),
    path('v1/user/self', myapp_view.user_info, name='user_info'),
    path('v1/user', myapp_view.create_user, name='create_user'),
    path('v1/verify', myapp_view.verify_user, name='verify_user'),

    # Add a catch-all path for undefined APIs
    re_path(r'^.*$', lambda request: HttpResponse(status=404)),
]
