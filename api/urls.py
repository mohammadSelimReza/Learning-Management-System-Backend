from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api import views as api_views

urlpatterns = [
    path("user/token/", api_views.MyTokenObtainPairView.as_view(), name="token"),
    path("user/token/refresh/", TokenRefreshView.as_view(), name="refreshToken"),
    path("user/registration/", api_views.RegisterView.as_view(), name="registration"),
    path(
        "user/password-reset/<email>/",
        api_views.ResetPasswordView.as_view(),
        name="passwordReset",
    ),
    path(
        "user/password-change/",
        api_views.PasswordChangeAPIView.as_view(),
        name="passwordChange",
    ),
]
