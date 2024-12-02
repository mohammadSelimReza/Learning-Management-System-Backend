from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import routers
from api import views as api_views
from django.urls import include, path

router = routers.DefaultRouter()

# router.register(r"teacher", api_views.TeacherView, basename="teacherView")

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
    path("teacher/", api_views.TeacherView.as_view()),
    path("category/", api_views.CategoryView.as_view()),
    path("course/list/", api_views.CourseView.as_view()),
    path("course/<slug>/", api_views.CourseDetailsAPIView.as_view()),
    path("cart/", api_views.CartAPIView.as_view()),
    path("variant/", api_views.VariantView.as_view()),
    path("variantItem/", api_views.VariantItemView.as_view()),
]
