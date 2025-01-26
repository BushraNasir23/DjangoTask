from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import RegisterView, LogoutView, VerifySignupEmail, UserLogin

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify_signup_email/<str:email>/<str:code>', VerifySignupEmail.as_view(), name='register'),
    path('login/', UserLogin.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
